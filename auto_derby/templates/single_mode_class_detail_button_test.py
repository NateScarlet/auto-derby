from . import _test
from .. import template, templates, action


_EXPECTED_POS = (114, 165)


def test_match():
    img, rp = _test.use_screenshot("single_mode_command_scene.png")
    res = tuple(template.match(img, templates.SINGLE_MODE_CLASS_DETAIL_BUTTON))
    assert len(res) == 1
    (match1,) = res
    assert match1[1] == rp.vector2(_EXPECTED_POS, 540)


def test_match_issue135():
    img, rp = _test.use_screenshot("single_mode_command_scene_issue135.png")
    res = tuple(template.match(img, templates.SINGLE_MODE_CLASS_DETAIL_BUTTON))
    assert len(res) == 1
    (match1,) = res
    assert match1[1] == rp.vector2(_EXPECTED_POS, 540)
