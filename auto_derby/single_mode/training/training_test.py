from auto_derby.single_mode.context import Context
import time
import timeit
from concurrent import futures
from typing import Text

from ... import _test
from . import Partner, Training
import pytest

# TODO: move to scenes/single_mode/


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("training_scene_*.png"))
    ),
)
def test_from_training_scene(name: Text):
    img, _ = _test.use_screenshot(f"single_mode/{name}.png")
    ctx = Context.new()
    ctx.scenario = ctx.SCENARIO_URA
    if "+aoharu+" in name:
        ctx.scenario = ctx.SCENARIO_AOHARU
    if "+climax+" in name:
        ctx.scenario = ctx.SCENARIO_CLIMAX
    training = Training.from_training_scene_v2(ctx, img)
    _test.snapshot_match(training, name=name)


def test_update_by_training_scene_1():
    img, _ = _test.use_screenshot("single_mode/training_scene_1.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 5
    assert training.speed == 26
    assert training.stamina == 0
    assert training.power == 14
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 3

    assert len(training.partners) == 1
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_SPEED
    assert partner1.level == 4
    assert partner1.has_hint == False


def test_update_by_training_scene_2():
    img, _ = _test.use_screenshot("single_mode/training_scene_2.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_WISDOM
    assert training.level == 3
    assert training.speed == 6
    assert training.stamina == 0
    assert training.power == 0
    assert training.guts == 0
    assert training.wisdom == 24
    assert training.skill == 8

    assert len(training.partners) == 3, len(training.partners)
    (partner1, partner2, partner3) = training.partners
    assert partner1.type == Partner.TYPE_OTHER
    assert partner1.level == 4
    assert partner1.has_hint == False
    assert partner2.type == Partner.TYPE_SPEED
    assert partner2.level == 5
    assert partner2.has_hint == False
    assert partner3.type == Partner.TYPE_WISDOM
    assert partner3.level == 5
    assert partner3.has_hint == False


def test_update_by_training_scene_3():
    img, _ = _test.use_screenshot("single_mode/training_scene_3.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_GUTS
    assert training.level == 5
    assert training.speed == 6
    assert training.stamina == 0
    assert training.power == 6
    assert training.guts == 17
    assert training.wisdom == 0
    assert training.skill == 2

    assert len(training.partners) == 1, len(training.partners)
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_STAMINA
    assert partner1.level == 5
    assert partner1.has_hint == False


def test_update_by_training_scene_4():
    img, _ = _test.use_screenshot("single_mode/training_scene_4.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_GUTS
    assert training.level == 5
    assert training.speed == 7
    assert training.stamina == 0
    assert training.power == 6
    assert training.guts == 16
    assert training.wisdom == 0
    assert training.skill == 2

    assert len(training.partners) == 1, len(training.partners)
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_SPEED
    assert partner1.level == 5
    assert partner1.has_hint == True


def test_update_by_training_scene_5():
    img, _ = _test.use_screenshot("single_mode/training_scene_5.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_WISDOM
    assert training.level == 2
    assert training.speed == 2
    assert training.stamina == 0
    assert training.power == 0
    assert training.guts == 0
    assert training.wisdom == 13
    assert training.skill == 4

    assert len(training.partners) == 0, len(training.partners)


def test_update_by_training_scene_6():
    img, _ = _test.use_screenshot("single_mode/training_scene_6.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 4
    assert training.speed == 22
    assert training.stamina == 0
    assert training.power == 10
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 3

    assert len(training.partners) == 1, len(training.partners)
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_SPEED
    assert partner1.level == 5
    assert partner1.has_hint == False


def test_update_by_training_scene_7():
    img, _ = _test.use_screenshot("single_mode/training_scene_7.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_STAMINA
    assert training.level == 5
    assert training.speed == 0
    assert training.stamina == 15
    assert training.power == 0
    assert training.guts == 6
    assert training.wisdom == 0
    assert training.skill == 2

    assert len(training.partners) == 4
    partner1, partner2, partner3, partner4 = training.partners
    assert partner1.type == Partner.TYPE_WISDOM
    assert partner1.level == 5
    assert partner1.has_hint == False
    assert partner2.type == Partner.TYPE_POWER
    assert partner2.level == 5
    assert partner2.has_hint == False
    assert partner3.type == Partner.TYPE_POWER
    assert partner3.level == 3
    assert partner3.has_hint == False
    assert partner4.type == Partner.TYPE_POWER
    assert partner4.level == 3
    assert partner4.has_hint == False


def test_update_by_training_scene_8():
    img, _ = _test.use_screenshot("single_mode/training_scene_8.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_STAMINA
    assert training.level == 1
    assert training.speed == 0
    assert training.stamina == 15
    assert training.power == 0
    assert training.guts == 6
    assert training.wisdom == 0
    assert training.skill == 3

    assert len(training.partners) == 3, len(training.partners)
    partner1, partner2, partner3 = training.partners
    assert partner1.type == Partner.TYPE_OTHER
    assert partner1.level == 1
    assert partner1.has_hint == False
    assert partner2.type == Partner.TYPE_POWER
    assert partner2.level == 4
    assert partner2.has_hint == False
    assert partner3.type == Partner.TYPE_POWER
    assert partner3.level == 2
    assert partner3.has_hint == False


def test_update_by_training_scene_9():
    img, _ = _test.use_screenshot("single_mode/training_scene_9.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 2
    assert training.speed == 19
    assert training.stamina == 0
    assert training.power == 10
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 3

    assert len(training.partners) == 2, len(training.partners)
    partner1, partner2 = training.partners
    assert partner1.type == Partner.TYPE_FRIEND
    assert partner1.level == 4
    assert partner1.has_hint == False
    assert partner2.type == Partner.TYPE_WISDOM
    assert partner2.level == 5
    assert partner2.has_hint == False


def test_update_by_training_scene_issue9():
    img, _ = _test.use_screenshot("single_mode/training_scene_issue9.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 1
    assert training.speed == 12
    assert training.stamina == 0
    assert training.power == 7
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 2

    assert len(training.partners) == 1, len(training.partners)
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_SPEED
    assert partner1.level == 2
    assert partner1.has_hint == False


def test_update_by_training_scene_issue24():
    img, _ = _test.use_screenshot("single_mode/training_scene_issue24.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_STAMINA
    assert training.level == 1
    assert training.speed == 0
    assert training.stamina == 9
    assert training.power == 0
    assert training.guts == 4
    assert training.wisdom == 0
    assert training.skill == 2

    assert len(training.partners) == 0, len(training.partners)


def test_update_by_training_scene_issue51():
    img, _ = _test.use_screenshot("single_mode/training_scene_issue51.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 5
    assert training.speed == 21
    assert training.stamina == 0
    assert training.power == 10
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 3

    assert len(training.partners) == 1, len(training.partners)
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_SPEED
    assert partner1.level == 5
    assert partner1.has_hint == False


def test_update_by_training_scene_issue55():
    img, _ = _test.use_screenshot("single_mode/training_scene_issue55.png")

    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 5
    assert training.speed == 30
    assert training.stamina == 0
    assert training.power == 17
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 4

    assert len(training.partners) == 2, len(training.partners)
    (partner1, partner2) = training.partners
    assert partner1.type == Partner.TYPE_SPEED
    assert partner1.level == 5
    assert partner1.has_hint == False
    assert partner2.type == Partner.TYPE_WISDOM
    assert partner2.level == 3
    assert partner2.has_hint == False


def test_update_by_training_scene_issue130():
    img, _ = _test.use_screenshot("single_mode/training_scene_issue130.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_POWER
    assert training.level == 5
    assert training.speed == 0
    assert training.stamina == 9
    assert training.power == 17
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 2

    assert len(training.partners) == 1, len(training.partners)
    (partner1,) = training.partners
    assert partner1.type == Partner.TYPE_POWER
    assert partner1.level == 3
    assert partner1.has_hint == False


def test_update_by_training_scene_issue156():
    img, _ = _test.use_screenshot("single_mode/training_scene_issue156.png")
    training = Training.from_training_scene(img)
    _test.snapshot_match(training)
    assert training.type == training.TYPE_SPEED
    assert training.level == 1
    assert training.speed == 21
    assert training.stamina == 0
    assert training.power == 13
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 4

    assert len(training.partners) == 3, len(training.partners)
    partner1, partner2, partner3 = training.partners
    assert partner1.type == Partner.TYPE_FRIEND
    assert partner1.level == 2
    assert partner1.has_hint == False
    assert partner2.type == Partner.TYPE_SPEED
    assert partner2.level == 4
    assert partner2.has_hint == False
    assert partner3.type == Partner.TYPE_STAMINA
    assert partner3.level == 4
    assert partner3.has_hint == False


def benchmark_from_training_scene():
    RUN_COUNT = 10
    img, _ = _test.use_screenshot("single_mode/training_scene_5.png")

    def iter_images():
        for _ in range(5):
            time.sleep(1)  # simulate game wait
            yield img

    def use_sync():
        for i in iter_images():
            Training.from_training_scene(i)

    def use_thread():
        with futures.ThreadPoolExecutor() as pool:
            [
                i.result()
                for i in [
                    pool.submit(Training.from_training_scene, j) for j in iter_images()
                ]
            ]

    def use_process():
        with futures.ProcessPoolExecutor() as pool:
            [
                i.result()
                for i in [
                    pool.submit(Training.from_training_scene, j) for j in iter_images()
                ]
            ]

    print("sync:")
    print(timeit.timeit(use_sync, number=RUN_COUNT) / RUN_COUNT)
    print("thread:")
    print(timeit.timeit(use_thread, number=RUN_COUNT) / RUN_COUNT)
    print("process:")
    print(timeit.timeit(use_process, number=RUN_COUNT) / RUN_COUNT)
    # sync:
    # 5.7888625
    # thread:
    # 5.17410499
    # process:
    # 5.811807080000001
