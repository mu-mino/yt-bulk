from upload import _cap_tags_by_total_chars


def test_cap_tags_accounts_for_quoted_space_tags():
    # YouTube counts tags with spaces as if quoted, so quotes count too.
    # "Foo Baz" has 7 chars, but counts as 9.
    tags = ["Foo Baz", "X"]
    capped = _cap_tags_by_total_chars(tags, max_total_chars=9)
    assert capped == ["Foo Baz"]


def test_cap_tags_counts_commas_between_items():
    # One comma between two tags counts as 1 char.
    tags = ["abc", "def"]
    capped = _cap_tags_by_total_chars(tags, max_total_chars=7)  # "abc,def" fits exactly
    assert capped == ["abc", "def"]
