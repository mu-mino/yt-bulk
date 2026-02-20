from upload import _sanitize_localizations, _fit_youtube_title, YOUTUBE_TITLE_MAX_LEN


def test_sanitize_localizations_truncates_long_titles_and_forces_default():
    very_long = "Surah X | " + ("A" * 200)
    locs = {
        "en": {"title": very_long, "description": "desc"},
        "fr": {"title": very_long, "description": "desc"},
    }

    snippet_title = _fit_youtube_title(very_long)
    out = _sanitize_localizations(
        locs,
        default_lang="en",
        default_title=snippet_title,
        default_description="desc",
    )

    assert out["en"]["title"] == snippet_title
    assert len(out["en"]["title"]) <= YOUTUBE_TITLE_MAX_LEN
    assert len(out["fr"]["title"]) <= YOUTUBE_TITLE_MAX_LEN

