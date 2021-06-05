from .training import Training

from pathlib import Path
import PIL.Image


_TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_update_by_training_scene():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "training_scene.png").convert("RGB")
    training = Training.from_training_scene(img)
    assert training.speed == 26
    assert training.stamina == 0
    assert training.power == 14
    assert training.perservance == 0
    assert training.intelligence == 0
    assert training.skill == 3


def test_update_by_training_scene_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "training_scene_2.png").convert("RGB")
    training = Training.from_training_scene(img)
    assert training.speed == 6
    assert training.stamina == 0
    assert training.power == 0
    assert training.perservance == 0
    assert training.intelligence == 24
    assert training.skill == 8


def test_update_by_training_scene_issue9():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "training_scene_issue9.png").convert("RGB")
    training = Training.from_training_scene(img)
    assert training.speed == 12
    assert training.stamina == 0
    assert training.power == 7
    assert training.perservance == 0
    assert training.intelligence == 0
    assert training.skill == 2
