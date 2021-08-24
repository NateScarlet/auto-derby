from typing import Text
from .. import template, templates
from .. import _test
import pytest


_ALL_OPTIONS = (
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
)


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("event_options_*.png"))
    ),
)
def test_match(name: Text):
    img, _ = _test.use_screenshot(f"single_mode/{name}.png")
    res = tuple(tuple(pos for _, pos in template.match(img, i)) for i in _ALL_OPTIONS)
    _test.snapshot_match(res, name=name)
