from auto_derby.single_mode.context import Context
import time
import timeit
from concurrent import futures
from typing import Text

from ... import _test
from .training import TrainingScene
import pytest


@pytest.mark.parametrize(
    "name",
    tuple(
        i.stem for i in ((_test.DATA_PATH / "single_mode").glob("training_scene_*.png"))
    ),
)
def test_recognize(name: Text):
    _test.use_screenshot(f"single_mode/{name}.png")
    ctx = Context.new()
    ctx.scenario = ctx.SCENARIO_URA
    if "+aoharu+" in name:
        ctx.scenario = ctx.SCENARIO_AOHARU
    if "+climax+" in name:
        ctx.scenario = ctx.SCENARIO_CLIMAX
    scene = TrainingScene()
    scene.recognize_v2(ctx, static=True)
    (training,) = scene.trainings
    _test.snapshot_match(training, name=name)


def benchmark_from_training_scene():
    RUN_COUNT = 10
    img, _ = _test.use_screenshot("single_mode/training_scene_5.png")

    def iter_images():
        for _ in range(5):
            time.sleep(1)  # simulate game wait
            yield img

    ctx = Context.new()
    ctx.scenario = ctx.SCENARIO_URA

    def recognize():
        scene = TrainingScene()
        scene.recognize_v2(ctx)

    def use_sync():
        for i in iter_images():
            recognize()

    def use_thread():
        with futures.ThreadPoolExecutor() as pool:
            [i.result() for i in [pool.submit(recognize) for j in iter_images()]]

    def use_process():
        with futures.ProcessPoolExecutor() as pool:
            [i.result() for i in [pool.submit(recognize) for j in iter_images()]]

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
