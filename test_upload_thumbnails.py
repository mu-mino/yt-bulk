import os
import tempfile

import pytest

from upload import _find_matching_thumbnail


def test_find_matching_thumbnail_by_prefix():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "001_Al-Fatiha.png")
        with open(p, "wb") as f:
            f.write(b"x")
        assert _find_matching_thumbnail(d, 1) == p


def test_find_matching_thumbnail_errors_on_missing():
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(FileNotFoundError):
            _find_matching_thumbnail(d, 1)


def test_find_matching_thumbnail_errors_on_multiple():
    with tempfile.TemporaryDirectory() as d:
        p1 = os.path.join(d, "001_Al-Fatiha.png")
        p2 = os.path.join(d, "001_Al-Fatiha.webp")
        for p in (p1, p2):
            with open(p, "wb") as f:
                f.write(b"x")
        with pytest.raises(RuntimeError):
            _find_matching_thumbnail(d, 1)

