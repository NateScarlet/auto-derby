from typing import Text
from .go_out import Option

from .. import _test
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("go_out_menu_*.png"))
    ),
)
def test_from_menu(name: Text):
    img, _ = _test.use_screenshot(f"single_mode/{name}.png")
    res = Option.from_menu(img)

    res = sorted(res, key=lambda x: x.position[1])
    _test.snapshot_match(
        res,
        name=name,
    )
