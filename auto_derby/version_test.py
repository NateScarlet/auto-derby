from . import version


def test_parse():
    assert version.parse("") == (0, 0, 0, "")
    assert version.parse("invalid") == (0, 0, 0, "invalid")
    assert version.parse("1.0") == (0, 0, 0, "1.0")
    assert version.parse("0.1.2") == (0, 1, 2, "")
    assert version.parse("v0.1.2") == (0, 1, 2, "")
    assert version.parse("0.1.2-rc.1") == (0, 1, 2, "rc.1")
    assert version.parse("0.1.2-rc.1-build1") == (0, 1, 2, "rc.1-build1")
