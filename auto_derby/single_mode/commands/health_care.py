# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import action, templates
from ...scenes.single_mode.command import CommandScene
from .. import Context
from .command import Command
from .globals import g


class HealthCareCommand(Command):
    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
        CommandScene.enter(ctx)
        action.tap_image(
            templates.SINGLE_MODE_COMMAND_HEALTH_CARE,
        )

    def score(self, ctx: Context) -> float:
        return g.health_care_score(ctx)


def default_score(ctx: Context) -> float:
    ret = 15 + ctx.turn_count() * 10 / 24
    ret += (
        len(
            set(
                (
                    Context.CONDITION_HEADACHE,
                    Context.CONDITION_OVERWEIGHT,
                )
            ).intersection(ctx.conditions)
        )
        * 20
    )

    if ctx.turn_count() >= ctx.total_turn_count() - 2:
        ret *= 0.1
    if ctx.date[1:] in ((6, 1),):
        ret += 10
    if ctx.date[1:] in ((6, 2),):
        ret += 20
    if ctx.date in ((4, 0, 0)):
        ret -= 20
    return ret


g.health_care_score = default_score
