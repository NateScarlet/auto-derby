from typing import Text

import pytest

from ... import _test
from ...single_mode import Context
from .command import CommandScene


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("command_scene_*.png"))
    ),
)
def test_recognize(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    scene = CommandScene()
    ctx = Context.new()
    scene.recognize(ctx, static=True)
    _test.snapshot_match(
        dict(ctx=ctx, scene=scene),
        name=name,
    )
