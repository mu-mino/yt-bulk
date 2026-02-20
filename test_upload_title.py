import unittest

from upload import YOUTUBE_TITLE_MAX_LEN, _fit_youtube_title, _pick_video_title


class TestYoutubeTitleFitting(unittest.TestCase):
    def test_fit_title_truncates_to_limit(self):
        raw = (
            "Surah Al-Fatihah | The Opening | Emotional & Calm Recitation | "
            "Maher Al-Muaiqly | With English Translation"
        )
        fitted = _fit_youtube_title(raw)
        self.assertTrue(fitted)
        self.assertLessEqual(len(fitted), YOUTUBE_TITLE_MAX_LEN)

    def test_fit_title_keeps_reciter_when_possible(self):
        raw = (
            "Surah Al-Fatihah | The Opening | Emotional & Calm Recitation | "
            "Maher Al-Muaiqly | With English Translation"
        )
        fitted = _fit_youtube_title(raw)
        self.assertIn("Maher", fitted)

    def test_pick_title_falls_back_to_filename(self):
        metadata = {"localizations": {"en": {"title": "", "description": ""}}}
        title, was_truncated = _pick_video_title(metadata, "sura_001.mp4", 1)
        self.assertEqual(title, "sura_001")
        self.assertFalse(was_truncated)


if __name__ == "__main__":
    unittest.main()

