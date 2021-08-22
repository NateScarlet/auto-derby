# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import action, templates
from ...scenes.single_mode.command import CommandScene
from .. import Context
from .command import Command
from .globals import g


class SummerRestCommand(Command):
    def execute(self, ctx: Context) -> None:
        CommandScene.enter(ctx)
        action.tap_image(
            templates.SINGLE_MODE_COMMAND_SUMMER_REST,
        )

    def score(self, ctx: Context) -> float:
        return g.summer_rest_score(ctx)


def default_score(ctx: Context) -> float:
    ret = 15 + ctx.turn_count() * 10 / 24
    if ctx.vitality > 0.5:
        ret *= 0.5
    if ctx.turn_count() >= ctx.total_turn_count() - 2:
        ret *= 0.1
    if ctx.vitality < 0.8:
        ret += 10
    ret += (ctx.MOOD_VERY_GOOD[0] - ctx.mood[0]) * 40 * 3
    return ret


g.summer_rest_score = default_score
