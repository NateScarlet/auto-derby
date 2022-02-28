import os
from typing import Text

from auto_derby.single_mode import go_out
from ... import _test
from .command import CommandScene
from ...single_mode import Context
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("command_scene_*.png"))
    ),
)
def test_recognize_commands(name: Text):
    img, _ = _test.use_screenshot(f"single_mode/{name}.png")
    scene = CommandScene()
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    scene.recognize_commands(ctx)
    _test.snapshot_match(
        scene,
        name=name,
    )


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
