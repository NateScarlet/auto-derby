from typing import Text
from ... import _test
from .aoharu_battle_confirm import AoharuBattleConfirmScene
from ...single_mode import Context
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem
        for i in (
            (_test.DATA_PATH / "single_mode").glob("aoharu_battle_confirm_menu_*.png")
        )
    ),
)
def test_recognize_predictions(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    scene = AoharuBattleConfirmScene()
    ctx = Context.new()
    scene.recognize_predictions()
    _test.snapshot_match(
        scene,
        name=name,
    )
