from typing import Text
from .go_out import Option

from .. import _test
import pytest


@pytest.mark.parametrize(
    "name",
    ("go_out_menu_1", "go_out_menu_2", "go_out_menu_3"),
)
def test_from_menu(name: Text):
    img, _ = _test.use_screenshot(f"single_mode/{name}.png")
    res = Option.from_menu(img)

    res = sorted(res, key=lambda x: x.position[1])
    _test.snapshot_match(
        res,
        name=name,
    )
