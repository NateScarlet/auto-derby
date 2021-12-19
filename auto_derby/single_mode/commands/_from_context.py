# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Iterator

from ...scenes.single_mode import TrainingScene
from ...scenes.single_mode.command import CommandScene
from ...scenes.single_mode.race_menu import RaceMenuScene
from .. import Context, race
from .command import Command
from .globals import g
from .go_out import GoOutCommand
from .health_care import HealthCareCommand
from .race import RaceCommand
from .rest import RestCommand
from .sumer_rest import SummerRestCommand
from .training import TrainingCommand


def from_context(ctx: Context) -> Iterator[Command]:
    scene = CommandScene.enter(ctx)
    if scene.has_scheduled_race:
        scene = RaceMenuScene.enter(ctx)
        yield RaceCommand(scene.first_race(ctx), selected=True)
        return

    max_race_score = 0
    for i in race.find(ctx):
        max_race_score = max(max_race_score, i.score(ctx))
        yield RaceCommand(i)
    if ctx.target_fan_count > ctx.fan_count and max_race_score > 15:
        return

    if scene.has_health_care:
        yield HealthCareCommand()
    if ctx.is_summer_camp:
        yield SummerRestCommand()
    else:
        yield RestCommand()
        if ctx.go_out_options:
            for i in ctx.go_out_options:
                if i.disabled(ctx):
                    continue
                yield GoOutCommand(i)
        else:
            yield GoOutCommand()

    if not g.ignore_training_commands(ctx):
        scene = TrainingScene.enter(ctx)
        scene.recognize_v2(ctx)
        for i in scene.trainings:
            yield TrainingCommand(i)
