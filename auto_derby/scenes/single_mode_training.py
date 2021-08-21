# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from concurrent import futures
from typing import Tuple

from .. import action, mathtools, template, templates
from ..single_mode import Training
from .scene import Scene, SceneHolder
from .single_mode_command import SingleModeCommandScene

_TRAINING_CONFIRM = template.Specification(
    templates.SINGLE_MODE_TRAINING_CONFIRM, threshold=0.8
)


def _iter_training_images():
    rp = action.resize_proxy()
    radius = rp.vector(30, 540)
    _, first_confirm_pos = action.wait_image(_TRAINING_CONFIRM)
    yield template.screenshot()
    for pos in (
        rp.vector2((78, 850), 540),
        rp.vector2((171, 850), 540),
        rp.vector2((268, 850), 540),
        rp.vector2((367, 850), 540),
        rp.vector2((461, 850), 540),
    ):
        if mathtools.distance(first_confirm_pos, pos) < radius:
            continue
        action.tap(pos)
        action.wait_image(_TRAINING_CONFIRM)
        yield template.screenshot()


class SingleModeTrainingScene(Scene):
    @classmethod
    def name(cls):
        return "single-mode-training"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        SingleModeCommandScene.enter(ctx)
        action.tap_image(templates.SINGLE_MODE_COMMAND_TRAINING)
        action.wait_image(_TRAINING_CONFIRM)
        return cls()

    def __init__(self):
        self.trainings: Tuple[Training, ...] = ()

    def recognize(self) -> None:
        with futures.ThreadPoolExecutor() as pool:
            self.trainings = tuple(
                i.result()
                for i in [
                    pool.submit(Training.from_training_scene, j)
                    for j in _iter_training_images()
                ]
            )
