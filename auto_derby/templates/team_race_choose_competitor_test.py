from .. import mathtools, template, templates
from .. import _test

_EXPECTED_POS = (240, 154)


def test_match():
    img, rp = _test.use_screenshot("team_race_arena.png")
    res = tuple(template.match(img, templates.TEAM_RACE_CHOOSE_COMPETITOR))
    assert len(res) == 1
    (match1,) = res
    assert match1[1] == rp.vector2(_EXPECTED_POS, 540)


def test_match_issue135():
    img, rp = _test.use_screenshot("team_race_arena_issue144.png")
    res = tuple(template.match(img, templates.TEAM_RACE_CHOOSE_COMPETITOR))
    assert len(res) == 1
    (match1,) = res
    assert mathtools.distance(match1[1], rp.vector2(_EXPECTED_POS, 540)) < 8
