from . import texttools


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
