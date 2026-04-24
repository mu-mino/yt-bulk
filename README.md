# yt-bulk

Reusable Python tool for bulk-uploading videos to YouTube via the Data API v3.

Handles per-item metadata (multi-language titles & descriptions), thumbnail
upload, tag deduplication, resumable upload with retry/backoff, and an
idempotent upload log so interrupted batches can resume.

---

## Features

| Feature | Detail |
|---|---|
| Resumable upload | Chunked, retries on 5xx / timeout |
| Multi-language metadata | `localizations` block: any number of language codes |
| Tags | Deduplicated, capped to YouTube's ~500-char limit |
| Thumbnail | Per-item `001_<title>.{png,jpg,webp}` matched by numeric prefix |
| Upload log | `upload_log.jsonl` — already-uploaded items skipped automatically |
| Quota guard | Stops immediately on `quotaExceeded`, exit code 2 |

---

## Directory Layout

```
yt-bulk/
├── upload.py          # Core upload engine + CLI entrypoint
├── oauth.py           # OAuth2 authentication flow (token.pickle)
├── localizations.py   # Template: generate per-language title/description dicts
├── stream.sh          # ffprobe helper — inspect streams in a video directory
├── metadata_output/   # One JSON file per item: item_001.json … item_NNN.json
│   └── item_001.json  # Example structure (see below)
├── OAuth.json         # ← your Google OAuth client secret (gitignored)
├── token.pickle       # ← generated on first login (gitignored)
└── upload_log.jsonl   # ← created at runtime (gitignored)
```

---

## Metadata Format

Each video needs a `metadata_output/item_NNN.json` file (zero-padded, 3 digits):

```json
{
    "localizations": {
        "en": {
            "title": "Episode 1 | Your Series | Creator Name",
            "description": "Description text.\n\n#YourTag"
        },
        "de": {
            "title": "Folge 1 | Ihre Serie | Ersteller",
            "description": "Beschreibung.\n\n#IhrTag"
        }
    },
    "tags": ["Episode 1", "Your Series", "your keyword"],
    "default_language": "en",
    "default_audio_language": "en"
}
```

`default_language` / `default_audio_language` are optional (default: `"en"`).

---

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 httplib2
```

Place your OAuth 2.0 client secret from [Google Cloud Console](https://console.cloud.google.com/)
as `OAuth.json`. Scope required: `youtube.upload`.

---

## Usage

```bash
# First run opens a browser for channel selection → saves token.pickle
python upload.py \
    --video-dir      /path/to/videos/ \
    --thumbnail-dir  /path/to/thumbnails/ \
    [--metadata-dir  /path/to/metadata_output/]   # default: metadata_output/ next to script
    [--single-sura   1]                            # upload only item 001 (for testing)
    [--debug]                                      # print API request body, don't upload
    [--ignore-upload-log]                          # re-upload already-logged items
```

**Thumbnail naming:** `001_<any-name>.png` — matched by the three-digit prefix.

**Video naming:** any name containing the item number, e.g. `episode_001.mp4`,
`001_intro.mkv`. Numbers outside 1–999 are ignored.

---

## Localization Helper

`localizations.py` provides a function template for generating the
`localizations` dict programmatically when building many metadata files:

```python
from localizations import localizations

data = localizations(name_en="Episode 1", name_de="Folge 1", name_fr="Épisode 1")
# data["localizations"] → dict ready to embed in item_NNN.json
```

Adapt the title/description templates in `localizations.py` for your content.

---

## Legacy

The `legacy/quran-pipeline` branch contains the original implementation used to
bulk-upload 114 Quran recitation videos (Maher Al-Muaiqly) with full Arabic,
English, and 9 additional language localizations, Quran-specific SEO tags, and
surah-numbered metadata. See that branch for the production metadata_output
dataset and the AI-assisted metadata generation scripts.

---

## Author

Muhammed Emin Eser — muhammed.emin.eser.1@gmail.com
