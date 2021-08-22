# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Text

import time

from ... import action
from ...scenes.single_mode import TrainingScene
from .. import Context, Training, race
from .command import Command
from .globals import g


class TrainingCommand(Command):
    def __init__(self, training: Training):
        self.training = training

    def name(self) -> Text:
        return str(self.training)

    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
        scene = TrainingScene.enter(ctx)
        x, y = self.training.confirm_position
        if scene.trainings[-1] != self.training:
            action.tap((x, y))
            time.sleep(0.1)
        action.tap((x, y))

    def score(self, ctx: Context) -> float:
        return self.training.score(ctx)


def default_ignore_training_commands(ctx: Context) -> bool:
    if ctx.vitality < 0.2:
        return True
    if ctx.target_fan_count > ctx.fan_count and any(
        i for i in race.find(ctx) if i.estimate_order(ctx) <= 3
    ):
        return True
    return False


g.ignore_training_commands = default_ignore_training_commands
