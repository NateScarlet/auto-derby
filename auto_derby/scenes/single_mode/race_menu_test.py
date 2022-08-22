from typing import Text

from ... import _test
from .race_menu import RaceMenuScene
from ...single_mode import Context
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(i.stem for i in ((_test.DATA_PATH / "single_mode").glob("race_menu_*.png"))),
)
def test_visible_courses(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    scene = RaceMenuScene()
    ctx = Context.new()
    if "+climax+" in name:
        ctx.scenario = ctx.SCENARIO_CLIMAX
    res = tuple(scene.visible_courses(ctx))
    _test.snapshot_match(
        res,
        name=name,
    )
