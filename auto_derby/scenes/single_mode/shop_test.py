from typing import Text

from ... import _test
from .shop import ShopScene
from ...single_mode import Context
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(i.stem for i in ((_test.DATA_PATH / "single_mode").glob("shop_scene_*.png"))),
)
def test_recognize(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    scene = ShopScene()
    ctx = Context.new()
    scene.recognize(ctx, static=True)
    _test.snapshot_match(
        scene,
        name=name,
    )
