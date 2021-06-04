from .context import Context

from pathlib import Path
import PIL.Image


_TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_update_by_command_scene_issue7():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue7.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0)
    assert ctx.vitality == 1
    assert ctx.speed == 158
    assert ctx.stamina == 190
    assert ctx.power == 67
    assert ctx.perservance == 95
    assert ctx.intelligence == 90
    assert ctx.mood == ctx.MOOD_NORMAL


def test_update_by_command_scene_issue12():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue12.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 12, 2), ctx.date
    assert ctx.vitality == 0.7932960893854748, ctx.vitality
    assert ctx.speed == 266, ctx.speed
    assert ctx.stamina == 228, ctx.stamina
    assert ctx.power == 196, ctx.power
    assert ctx.perservance == 200, ctx.perservance
    assert ctx.intelligence == 176, ctx.intelligence
    assert ctx.mood == ctx.MOOD_BAD, ctx.mood


def test_update_by_command_scene_issue12_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue12_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 10, 1), ctx.date
    assert ctx.vitality == 0.7877094972067039, ctx.vitality
    assert ctx.speed == 241, ctx.speed
    assert ctx.stamina == 237, ctx.stamina
    assert ctx.power == 144, ctx.power
    assert ctx.perservance == 187, ctx.perservance
    assert ctx.intelligence == 184, ctx.intelligence
    assert ctx.mood == ctx.MOOD_GOOD, ctx.mood


def test_update_by_command_scene_issue17():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue17.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0), ctx.date
    assert ctx.vitality == 0.5139664804469274, ctx.vitality
    assert ctx.speed == 195, ctx.speed
    assert ctx.stamina == 150, ctx.stamina
    assert ctx.power == 119, ctx.power
    assert ctx.perservance == 115, ctx.perservance
    assert ctx.intelligence == 91, ctx.intelligence
    assert ctx.mood == ctx.MOOD_GOOD, ctx.mood


def test_update_by_command_scene_issue17_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue17_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 11, 2), ctx.date
    assert ctx.vitality == 1, ctx.vitality
    assert ctx.speed == 262, ctx.speed
    assert ctx.stamina == 266, ctx.stamina
    assert ctx.power == 142, ctx.power
    assert ctx.perservance == 156, ctx.perservance
    assert ctx.intelligence == 233, ctx.intelligence
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood
