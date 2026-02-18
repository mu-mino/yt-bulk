import os
import json
import re
import subprocess
try:
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ModuleNotFoundError:
    # Allows running metadata/tag helpers without Google deps installed.
    MediaFileUpload = None
    HttpError = Exception
    InstalledAppFlow = None
    build = None


VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.mov', '.webm'}
import pickle

# Die Berechtigung, die du zum Hochladen benötigst
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

_PIPE_RE = re.compile(r"\s*\|\s*")


def _normalize_pipes(text: str) -> str:
    return _PIPE_RE.sub(" | ", text or "").strip()


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
    # YouTube UI/documentation: total tag characters are limited (commonly 500).
    # We keep a conservative cap to avoid API rejections.
    out = []
    total = 0
    for t in tags:
        extra = len(t) + (1 if out else 0)  # comma separator
        if total + extra > max_total_chars:
            break
        out.append(t)
        total += extra
    return out


def build_youtube_tags(metadata):
    """
    Build high-signal YouTube tags from our metadata_output conventions.

    Expected EN title format (after our chat edits):
      Surah <translit> | <english name> | Emotional & Calm Recitation | Maher Al-Muaiqly | With English Translation
    """
    locs = (metadata or {}).get("localizations", {})
    en_title = _normalize_pipes((locs.get("en") or {}).get("title", ""))
    ar_title = _normalize_pipes((locs.get("ar") or {}).get("title", ""))

    def extract_between(title, prefix):
        if not title or prefix not in title:
            return ""
        after = title.split(prefix, 1)[1]
        if " | " in after:
            return after.split(" | ", 1)[0].strip()
        return after.strip()

    en_segs = en_title.split(" | ") if en_title else []
    surah_translit = ""
    surah_en_name = ""
    if en_segs and en_segs[0].startswith("Surah "):
        surah_translit = en_segs[0].replace("Surah ", "", 1).strip()
    if len(en_segs) >= 2:
        surah_en_name = en_segs[1].strip()

    surah_ar_name = extract_between(ar_title, "سورة ")

    # Ordered by priority: surah-specific terms first, then content/reciter, then broader discovery terms.
    tags = [
        surah_translit,
        surah_en_name,
        surah_ar_name,
        f"Surah {surah_translit}" if surah_translit else "",
        f"Surah {surah_en_name}" if surah_en_name else "",
        "Quran",
        "Qur'an",
        "Al Quran",
        "Quran Recitation",
        "Surah Recitation",
        "Murattal",
        "Tilawah",
        "Tilawat",
        "Tajweed",
        "Tarteel",
        "Beautiful Recitation",
        "Calm Quran",
        "Relaxing Quran",
        "Emotional Recitation",
        "With English Translation",
        "English Translation",
        "Hilali Khan",
        "Maher Al-Muaiqly",
        "Maher al Muaiqly",
        "Al-Muaiqly",
        "Muaiqly",
        "Islam",
        "Islamic",
        "Koran",
        "القرآن",
    ]

    tags = _dedupe_tags(tags)
    tags = _cap_tags_by_total_chars(tags, max_total_chars=450)
    return tags


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

def upload_video_with_metadata_and_thumbnail(youtube, video_file_path, sura_num, debug=False):
    if MediaFileUpload is None:
        raise RuntimeError(
            "googleapiclient is not installed. "
            "Install dependencies (google-api-python-client) to upload."
        )
    # 1. Metadaten aus JSON laden
    sura_num_formatted = f"{int(sura_num):03d}"
    json_path = f"/home/muhammed-emin-eser/desk/apps/yt-bulk/metadata_output/sura_{sura_num_formatted}.json"

    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Basis-Sprache für das Haupt-Snippet (YouTube erfordert Default-Werte)
    # Wir nutzen 'en' als Standard, da es global am besten rankt
    base = metadata['localizations']['en']
    ar_local = metadata['localizations'].get('ar', {})

    def _extract_name(title, prefix):
        if not title or prefix not in title:
            return ""
        after = title.split(prefix, 1)[1]
        if " | " in after:
            return after.split(" | ", 1)[0].strip()
        return after.strip()

    en_name = _extract_name(base.get('title', ''), "Surah ")
    ar_name = _extract_name(ar_local.get('title', ''), "سورة ")

    # YouTube keywords/tags (bounded to avoid API rejections).
    all_tags = build_youtube_tags(metadata)

    body = {
        'snippet': {
            'title': base['title'],
            'description': base['description'],
            'tags': all_tags,
            'categoryId': '27',  # Education
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'ar'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        },
        'localizations': metadata['localizations']
    }

    if debug:
        print("DEBUG: request body preview:")
        print(json.dumps(body, ensure_ascii=False, indent=2))

    # 2. Video Upload starten
    print(f"Uploading Video: {os.path.basename(video_file_path)}...")
    media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)

    video_response = youtube.videos().insert(
        part="snippet,status,localizations",
        body=body,
        media_body=media
    ).execute()

    video_id = video_response['id']
    print(f"Video erfolgreich hochgeladen! ID: {video_id}")

    # 3. THUMBNAIL EXTRAKTION & UPLOAD
    # Wir extrahieren den attached_pic Stream (0:2) mit ffmpeg als temporäre Datei
    temp_thumb = f"temp_thumb_{video_id}.png"
    try:
        print("Extrahiere eingebettetes Thumbnail...")
        # -map 0:v:1 oder 0:2 je nach Stream-Index. Wir nehmen 0:2 für attached_pic
        subprocess.run([
            'ffmpeg', '-i', video_file_path, '-map', '0:2', '-frames:v', '1', temp_thumb, '-y'
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Thumbnail zu YouTube hochladen
        print(f"Lade Thumbnail für Video {video_id} hoch...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(temp_thumb)
        ).execute()
        print("Thumbnail erfolgreich gesetzt!")

    except HttpError as e:
        if getattr(e.resp, "status", None) == 403:
            print("Thumbnail übersprungen: keine Berechtigung für Custom-Thumbnails.")
        else:
            print(f"Fehler beim Thumbnail-Prozess: {e}")
    except Exception as e:
        print(f"Fehler beim Thumbnail-Prozess: {e}")
    finally:
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)

    return video_id


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


def upload_videos_in_dir(youtube, video_dir, process_single=False, single_sura=None, debug=False):
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
        entries.append((sura_num, name, file_path))
    for sura_num, name, file_path in sorted(entries, key=lambda x: x[0], reverse=True):
        if process_single and single_sura is not None and sura_num != single_sura:
            continue

        upload_video_with_metadata_and_thumbnail(
            youtube, file_path, sura_num, debug=debug
        )

        if process_single:
            return


if __name__ == "__main__":
    import argparse
    from oauth import youtube as youtube_client

    parser = argparse.ArgumentParser(description="Upload Quran videos with metadata and thumbnails.")
    parser.add_argument("--video-dir", required=True, help="Directory with video files.")
    parser.add_argument("--single-sura", type=int, help="Only upload one sura number for testing.")
    parser.add_argument("--debug", action="store_true", help="Preview request body before upload.")
    args = parser.parse_args()

    upload_videos_in_dir(
        youtube_client,
        args.video_dir,
        process_single=args.single_sura is not None,
        single_sura=args.single_sura,
        debug=args.debug,
    )
