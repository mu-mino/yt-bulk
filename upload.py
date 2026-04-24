import os
import json
import re
import time
import random
try:
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    from googleapiclient.errors import ResumableUploadError
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ModuleNotFoundError:
    # Allows running metadata/tag helpers without Google deps installed.
    MediaFileUpload = None
    HttpError = Exception
    ResumableUploadError = Exception
    InstalledAppFlow = None
    build = None


VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.mov', '.webm'}
import pickle

# Die Berechtigung, die du zum Hochladen benötigst
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
UPLOAD_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload_log.jsonl")
DEFAULT_THUMBNAIL_DIR = None  # set via --thumbnail-dir CLI arg
THUMBNAIL_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

_PIPE_RE = re.compile(r"\s*\|\s*")
_WS_RE = re.compile(r"\s+")
YOUTUBE_TITLE_MAX_LEN = 100
YOUTUBE_DESCRIPTION_MAX_LEN = 5000


def _normalize_pipes(text: str) -> str:
    return _PIPE_RE.sub(" | ", text or "").strip()


def _normalize_spaces(text: str) -> str:
    return _WS_RE.sub(" ", (text or "").replace("\n", " ").replace("\r", " ")).strip()


def _fit_youtube_title(title: str, max_len: int = YOUTUBE_TITLE_MAX_LEN) -> str:
    title = _normalize_spaces(_normalize_pipes(title)).strip(" |")
    if len(title) <= max_len:
        return title

    segments = [s.strip() for s in title.split(" | ") if s.strip()]
    if segments:
        reciter = next((s for s in segments if re.search(r"(maher|muaiqly)", s, re.IGNORECASE)), "")
        translation = next((s for s in segments if "translation" in s.casefold()), "")

        # Heuristic: keep the most important info (surah + name + reciter) before dropping segments.
        preferred = []
        for s in [segments[0], segments[1] if len(segments) > 1 else "", reciter, translation]:
            if s and s not in preferred:
                preferred.append(s)

        variants = [
            preferred,
            [s for s in preferred if s != translation],
            [s for s in preferred if s not in (translation, reciter)],
            [segments[0], reciter] if reciter and reciter != segments[0] else [segments[0]],
        ]
        for v in variants:
            candidate = " | ".join([s for s in v if s]).strip(" |")
            if candidate and len(candidate) <= max_len:
                return candidate

    # Fallback: drop less-important trailing segments separated by pipes.
    while len(" | ".join(segments)) > max_len and len(segments) > 1:
        segments.pop()
    title = " | ".join(segments).strip(" |")

    if len(title) <= max_len:
        return title

    # Last resort: hard truncate.
    return title[:max_len].rstrip()

def _fit_youtube_description(text: str, max_len: int = YOUTUBE_DESCRIPTION_MAX_LEN) -> str:
    text = (text or "").replace("\r", "")
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip()


def _sanitize_localizations(localizations: dict, default_lang: str, default_title: str, default_description: str):
    """
    YouTube enforces the same title/description constraints on localized metadata.
    Keep only valid entries and ensure default language is present.
    """
    out = {}
    if isinstance(localizations, dict):
        for lang, loc in localizations.items():
            if not isinstance(lang, str) or not lang.strip():
                continue
            if not isinstance(loc, dict):
                continue

            title = loc.get("title", "")
            desc = loc.get("description", "")
            if title is None:
                title = ""
            if desc is None:
                desc = ""
            if not isinstance(title, str):
                title = str(title)
            if not isinstance(desc, str):
                desc = str(desc)

            title = _fit_youtube_title(_normalize_spaces(_normalize_pipes(title)).strip(" |"))
            desc = _fit_youtube_description(desc)

            if not title:
                continue

            out[lang] = {"title": title, "description": desc}

    # Force default language entry to match the snippet we send.
    if default_lang:
        out[default_lang] = {
            "title": _fit_youtube_title(_normalize_spaces(_normalize_pipes(default_title)).strip(" |")),
            "description": _fit_youtube_description(default_description or ""),
        }
    return out


def _pick_video_title(metadata: dict, video_file_path: str, sura_num: int) -> tuple[str, bool]:
    """
    Returns (title, was_truncated). Ensures a non-empty, <=100 char title for YouTube API.
    """
    localizations = (metadata or {}).get("localizations") or {}
    en = localizations.get("en") or {}

    raw_title = en.get("title", "")
    normalized = _normalize_spaces(_normalize_pipes(raw_title)).strip(" |")

    if not normalized:
        # Try any localization title as a fallback.
        for loc in localizations.values():
            candidate = _normalize_spaces(_normalize_pipes((loc or {}).get("title", ""))).strip(" |")
            if candidate:
                normalized = candidate
                break

    if not normalized:
        basename = os.path.splitext(os.path.basename(video_file_path or ""))[0].strip()
        normalized = basename or f"Item {int(sura_num):03d}"

    fitted = _fit_youtube_title(normalized, max_len=YOUTUBE_TITLE_MAX_LEN)
    return fitted, len(fitted) != len(normalized)


def _dedupe_tags(tags):
    # YouTube tags are limited; keep order, dedupe case-insensitively.
    out = []
    seen = set()
    for t in tags:
        if not t:
            continue
        t = str(t).strip()
        if not t:
            continue
        # Avoid accidental multi-part tags.
        t = t.replace("\n", " ").replace("\r", " ").strip()
        if not t:
            continue
        key = t.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def _cap_tags_by_total_chars(tags, max_total_chars=450):
    """
    Cap tags to YouTube's documented 500-character limit for snippet.tags[].

    Docs nuance: commas between list items count toward the limit, and tags containing spaces
    are treated as if quoted, so the quotes count too.
    """

    def _effective_len(tag: str) -> int:
        # See videos resource docs for snippet.tags[] character counting rules.
        return len(tag) + (2 if " " in tag else 0)

    out = []
    total = 0
    for t in tags:
        extra = _effective_len(t) + (1 if out else 0)  # comma separator
        if total + extra > max_total_chars:
            break
        out.append(t)
        total += extra
    return out


def build_youtube_tags(metadata):
    """
    Build YouTube tags from metadata["tags"] list.
    Deduplicates case-insensitively and caps to YouTube's ~500-char limit.
    """
    raw_tags = (metadata or {}).get("tags", [])
    tags = _dedupe_tags(raw_tags)
    # The API's documented limit is 500 chars (counting commas and quoting tags with spaces).
    # Stay slightly under to reduce risk of edge-case rejections.
    tags = _cap_tags_by_total_chars(tags, max_total_chars=495)
    return tags


def _find_matching_thumbnail(thumbnail_dir: str, sura_num: int) -> str:
    """
    Find a thumbnail file in `thumbnail_dir` that matches the sura number prefix.

    Expected filenames: "001_Al-Fatiha.png", "114_An-Nas.png", etc.
    """
    if not thumbnail_dir:
        raise ValueError("thumbnail_dir is required")
    if not os.path.isdir(thumbnail_dir):
        raise FileNotFoundError(f"Thumbnail dir not found: {thumbnail_dir}")

    prefix = f"{int(sura_num):03d}_"
    matches = []
    for name in os.listdir(thumbnail_dir):
        if not name.startswith(prefix):
            continue
        if not name.lower().endswith(THUMBNAIL_EXTENSIONS):
            continue
        path = os.path.join(thumbnail_dir, name)
        if os.path.isfile(path):
            matches.append(path)

    matches.sort()
    if not matches:
        raise FileNotFoundError(
            f"No thumbnail found for sura {int(sura_num):03d} in {thumbnail_dir} "
            f"(expected prefix {prefix}*{THUMBNAIL_EXTENSIONS})"
        )
    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple thumbnails found for sura {int(sura_num):03d}: {matches}. "
            "Keep exactly one file per sura."
        )
    return matches[0]


def get_authenticated_service():
    if InstalledAppFlow is None or build is None:
        raise RuntimeError(
            "Google API client libraries are not installed. "
            "Install dependencies (google-api-python-client, google-auth-oauthlib) to upload."
        )
    credentials = None
    # Token-Datei speichert deine Kanal-Wahl (so musst du dich nur 1x einloggen)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # Wenn kein gültiges Token da ist, starte den Login-Prozess
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'OAuth.json', SCOPES)
        credentials = flow.run_local_server(port=8080)
        # Hier wählst du im Browser den Ziel-Kanal aus!
        # Speichere das Token für die nächsten 113 Videos
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)

# NOTE: Do not create the YouTube service at import time.
# The CLI entrypoint below wires in the authenticated client.

def upload_video_with_metadata_and_thumbnail(
    youtube,
    video_file_path,
    sura_num,
    debug=False,
    thumbnail_dir: str = DEFAULT_THUMBNAIL_DIR,
    metadata_dir: str = None,
):
    if MediaFileUpload is None:
        raise RuntimeError(
            "googleapiclient is not installed. "
            "Install dependencies (google-api-python-client) to upload."
        )
    if thumbnail_dir is None:
        raise ValueError("thumbnail_dir is required")

    item_num_formatted = f"{int(sura_num):03d}"
    base_dir = metadata_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata_output")
    json_path = os.path.join(base_dir, f"item_{item_num_formatted}.json")

    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    localizations = metadata.get("localizations") or {}
    if not localizations:
        raise ValueError(f"Missing 'localizations' in metadata: {json_path}")

    base = localizations.get("en") or {}

    # YouTube keywords/tags (bounded to avoid API rejections).
    all_tags = build_youtube_tags(metadata)

    title, was_truncated = _pick_video_title(metadata, video_file_path, sura_num)
    if not title:
        raise ValueError(f"Refusing to upload with empty title. Metadata: {json_path}")
    if was_truncated:
        print(f"NOTE: Title exceeded {YOUTUBE_TITLE_MAX_LEN} chars and was truncated: {title}")

    thumbnail_path = _find_matching_thumbnail(thumbnail_dir, sura_num)
    if os.path.getsize(thumbnail_path) <= 0:
        raise RuntimeError(f"Thumbnail file is empty: {thumbnail_path}")

    description = _fit_youtube_description(base.get("description", ""))
    sanitized_localizations = _sanitize_localizations(
        localizations,
        default_lang="en",
        default_title=title,
        default_description=description,
    )

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': all_tags,
            'categoryId': '27',  # Education
            'defaultLanguage': metadata.get('default_language', 'en'),
            'defaultAudioLanguage': metadata.get('default_audio_language', 'en')
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        },
        'localizations': sanitized_localizations
    }

    if debug:
        print("DEBUG: request body preview:")
        print(json.dumps(body, ensure_ascii=False, indent=2))

    try:
        # 2. Video Upload starten
        print(f"Uploading Video: {os.path.basename(video_file_path)}...")
        media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)

        insert_request = youtube.videos().insert(
            part="snippet,status,localizations",
            body=body,
            media_body=media
        )

        # Resumable upload with retry/backoff for transient network issues/timeouts.
        response = None
        retries = 0
        max_retries = 10
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if status is not None:
                    progress = int(status.progress() * 100)
                    print(f"Upload progress: {progress}%")
            except Exception as e:
                retryable = isinstance(e, TimeoutError)
                if isinstance(e, HttpError):
                    code = getattr(getattr(e, "resp", None), "status", None)
                    retryable = code in (500, 502, 503, 504)

                if not retryable or retries >= max_retries:
                    raise

                retries += 1
                sleep_s = min(2 ** retries, 60) + random.random()
                print(
                    f"Transient upload error ({type(e).__name__}); retry {retries}/{max_retries} in {sleep_s:.1f}s..."
                )
                time.sleep(sleep_s)

        video_id = response['id']
        print(f"Video uploaded. ID: {video_id}")

        print(f"Setting thumbnail for video {video_id}...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute(num_retries=5)
        print("Thumbnail set.")
    finally:
        pass

    return video_id


def _parse_google_error_reason(exc) -> str:
    """
    Best-effort extraction of Google API error reason from HttpError/ResumableUploadError payloads.
    """
    content = None
    if hasattr(exc, "content"):
        content = getattr(exc, "content")
    elif hasattr(exc, "args") and exc.args:
        # Some errors stuff the raw response content in args.
        content = exc.args[-1]

    if isinstance(content, bytes):
        try:
            content = content.decode("utf-8", "replace")
        except Exception:
            content = None

    if isinstance(content, str) and content.strip():
        try:
            payload = json.loads(content)
            err = (payload or {}).get("error") or {}
            errors = err.get("errors") or []
            if errors and isinstance(errors, list):
                reason = (errors[0] or {}).get("reason")
                if isinstance(reason, str) and reason:
                    return reason
        except Exception:
            pass

    # Fallback: attempt to read the reason from stringified exception.
    msg = str(exc)
    if "quotaExceeded" in msg:
        return "quotaExceeded"
    if "uploadRateLimitExceeded" in msg:
        return "uploadRateLimitExceeded"
    return ""


def _is_quota_exceeded(exc) -> bool:
    return _parse_google_error_reason(exc) == "quotaExceeded"


def _load_uploaded_suras(log_path: str) -> set[int]:
    out = set()
    if not os.path.exists(log_path):
        return out
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = (line or "").strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                n = rec.get("sura_num")
                if isinstance(n, int):
                    out.add(n)
    except Exception:
        return out
    return out


def _append_upload_log(log_path: str, sura_num: int, video_file_path: str, video_id: str):
    rec = {
        "ts": int(time.time()),
        "sura_num": int(sura_num),
        "file": os.path.basename(video_file_path or ""),
        "video_id": str(video_id or ""),
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _extract_sura_num(filename):
    match = re.search(r'sura[_-]?(\d{1,3})', filename, re.IGNORECASE)
    if not match:
        match = re.search(r'(\d{1,3})', filename)
    if not match:
        return None
    sura_num = int(match.group(1))
    if 1 <= sura_num <= 114:
        return sura_num
    return None


def upload_videos_in_dir(
    youtube,
    video_dir,
    process_single=False,
    single_sura=None,
    debug=False,
    ignore_upload_log=False,
    thumbnail_dir: str = DEFAULT_THUMBNAIL_DIR,
    metadata_dir: str = None,
):
    uploaded = set() if ignore_upload_log else _load_uploaded_suras(UPLOAD_LOG_PATH)
    entries = []
    for name in os.listdir(video_dir):
        file_path = os.path.join(video_dir, name)
        if not os.path.isfile(file_path):
            continue
        if os.path.splitext(name)[1].lower() not in VIDEO_EXTENSIONS:
            continue

        sura_num = _extract_sura_num(name)
        if sura_num is None:
            continue
        if not ignore_upload_log and (not process_single and sura_num in uploaded):
            continue
        entries.append((sura_num, name, file_path))
    for sura_num, name, file_path in sorted(entries, key=lambda x: x[0], reverse=False):
        if process_single and single_sura is not None and sura_num != single_sura:
            continue

        try:
            video_id = upload_video_with_metadata_and_thumbnail(
                youtube, file_path, sura_num, debug=debug,
                thumbnail_dir=thumbnail_dir, metadata_dir=metadata_dir,
            )
            _append_upload_log(UPLOAD_LOG_PATH, sura_num, file_path, video_id)
        except (HttpError, ResumableUploadError) as e:
            if _is_quota_exceeded(e):
                print("ERROR: YouTube Data API quotaExceeded. Stopping batch without retry.")
                print("Next step: wait for quota reset or request more quota in Google Cloud Console, then rerun.")
                raise SystemExit(2)
            raise

        if process_single:
            return


if __name__ == "__main__":
    import argparse
    from oauth import youtube as youtube_client

    parser = argparse.ArgumentParser(description="Bulk-upload videos to YouTube with per-item metadata and thumbnails.")
    parser.add_argument("--video-dir", required=True, help="Directory containing video files.")
    parser.add_argument("--thumbnail-dir", required=True, help="Directory with thumbnails named 001_<title>.{png,jpg,webp}.")
    parser.add_argument("--metadata-dir", default=None, help="Directory with item_NNN.json metadata files (default: metadata_output/ next to script).")
    parser.add_argument("--single-sura", type=int, help="Upload only one item number (for testing).")
    parser.add_argument("--debug", action="store_true", help="Preview API request body before upload.")
    parser.add_argument(
        "--ignore-upload-log",
        action="store_true",
        help="Ignore upload_log.jsonl and re-upload already-uploaded items.",
    )
    args = parser.parse_args()

    upload_videos_in_dir(
        youtube_client,
        args.video_dir,
        process_single=args.single_sura is not None,
        single_sura=args.single_sura,
        debug=args.debug,
        ignore_upload_log=args.ignore_upload_log,
        thumbnail_dir=args.thumbnail_dir,
        metadata_dir=args.metadata_dir,
    )
