from .nurturing import Context, Training

from pathlib import Path
import PIL.Image


_TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_context_update_by_command_scene_issue7():
    # TODO: fix typo comand -> command
    img = PIL.Image.open(
        _TEST_DATA_PATH / "nurturing_comand_scene_issue7.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0)
    assert ctx.vitality == 1
    assert ctx.speed == 158
    assert ctx.stamina == 190
    assert ctx.power == 67
    assert ctx.perservance == 95
    assert ctx.intelligence == 90


def test_training_update_by_command_scene_issue9():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "nurturing_training_scene_issue9.png").convert("RGB")
    # TODO: fix typo traning -> training
    training = Training.from_traning_scene(img)
    assert training.speed == 12
    assert training.stamina == 0
    assert training.power == 7
    assert training.perservance == 0
    assert training.intelligence == 0
    assert training.skill == 2
