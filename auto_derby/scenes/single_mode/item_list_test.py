from typing import Text

from ... import _test
from .item_list import ItemListScene
from ...single_mode import Context
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(i.stem for i in ((_test.DATA_PATH / "single_mode").glob("item_list_*.png"))),
)
def test_recognize(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    scene = ItemListScene()
    ctx = Context.new()
    scene.recognize(ctx, static=True)
    _test.snapshot_match(
        scene,
        name=name,
    )
