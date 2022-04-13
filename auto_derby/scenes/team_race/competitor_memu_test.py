from typing import Text

import pytest

from ... import _test
from .competitor_menu import CompetitorMenuScene


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "team_race").glob("competitor_menu_*.png"))
    ),
)
def test_recognize(name: Text):
    _test.use_screenshot(f"team_race/{name}.png")
    scene = CompetitorMenuScene()
    granted_reward = scene.locate_granted_reward()
    _test.snapshot_match(
        dict(granted_reward=granted_reward),
        name=name,
    )
