from typing import Text
from .. import _test, template, templates
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem
        for i in (
            (_test.DATA_PATH / "single_mode").glob("aoharu_competitor_menu_*.png")
        )
    ),
)
def test_recognize_predictions(name: Text):
    img, _ = _test.use_screenshot(f"single_mode/{name}.png")
    res = tuple(
        i[1]
        for i in template.match(
            img,
            template.Specification(
                templates.SINGLE_MODE_AOHARU_CHOOSE_COMPETITOR,
                threshold=0.8,
            ),
        )
    )
    _test.snapshot_match(res, name=name)
