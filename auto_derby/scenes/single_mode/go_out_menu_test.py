from typing import Text
from .go_out_menu import GoOutMenuScene

from ... import _test
import pytest

from ...single_mode import Context


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("go_out_menu_*.png"))
    ),
)
def test_recognize(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    ctx = Context.new()
    scene = GoOutMenuScene()
    scene.recognize(ctx)
    _test.snapshot_match(
        {"options": ctx.go_out_options},
        name=name,
    )
