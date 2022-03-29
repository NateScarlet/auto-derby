# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time
from typing import Text

from ... import action, template
from ...scenes import UnknownScene
from ...scenes.single_mode import TrainingScene
from .. import Context, Training, item
from .command import Command
from .globals import g


class TrainingCommand(Command):
    def __init__(self, training: Training):
        self.training = training

    def name(self) -> Text:
        return str(self.training)

    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
        TrainingScene.enter(ctx)
        x, y = self.training.confirm_position
        current_training = Training.from_training_scene_v2(ctx, template.screenshot())
        if current_training.type != self.training.type:
            action.tap((x, y))
            time.sleep(0.1)
        action.tap((x, y))
        ctx.training_history.append(ctx, current_training)
        UnknownScene.enter(ctx)

    def score(self, ctx: Context) -> float:
        return self.training.score(ctx)


def _item_can_improve_failure_rate(i: item.Item):
    es = i.effect_summary()
    return es.vitality > 0 or es.training_no_failure


def default_ignore_training_commands(ctx: Context) -> bool:
    if any(_item_can_improve_failure_rate(i) for i in ctx.items):
        return False
    if ctx.vitality < 0.2:
        return True
    return False


g.ignore_training_commands = default_ignore_training_commands
