from . import texttools


def test_fill():
    assert list(texttools.fill("ab", 1)) == []
    assert list(texttools.fill("a", 1)) == ["a"]
    assert list(texttools.fill("a", 2)) == [" a", "a "]
    assert list(texttools.fill("a", 3)) == ["  a", " a ", "a  "]
    assert list(texttools.fill("a", 4)) == ["   a", "  a ", " a  ", "a   "]

    assert list(texttools.fill("ab", 3)) == [" ab", "a b", "ab "]
    assert list(texttools.fill("ab", 4)) == [
        "  ab",
        " a b",
        " ab ",
        "a  b",
        "a b ",
        "ab  ",
    ]


def test_compare():
    assert texttools.compare("", "") == 1
    assert texttools.compare("", "a") == 0
    assert texttools.compare("a ", "ab") == 0.5
    assert texttools.compare("a", "ab") == 0.5
    assert texttools.compare("ァ", "ア") == 0.95
    assert texttools.compare("ァ", "ア1") == 0.475
    assert texttools.compare("ア", "ァ") == 0.95
    assert texttools.compare("アフアイナルズ", "ァファイナルズ") == 0.9857142857142858
    assert texttools.compare("", "123456", max_missing_chars=5) == -1
