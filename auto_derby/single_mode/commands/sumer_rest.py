# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import action, templates
from ...scenes.single_mode.command import CommandScene
from .. import Context, go_out
from .command import Command
from .globals import g


class SummerRestCommand(Command):
    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
        CommandScene.enter(ctx)
        action.tap_image(
            templates.SINGLE_MODE_COMMAND_SUMMER_REST,
        )

    def score(self, ctx: Context) -> float:
        return g.summer_rest_score(ctx)


def default_score(ctx: Context) -> float:
    class _SummerGoOutOption(go_out.g.option_class):
        def vitality(self, ctx: Context) -> float:
            return 50 / ctx.max_vitality

        def mood_rate(self, ctx: Context) -> float:
            return 1

    o = _SummerGoOutOption()
    return o.score(ctx)


g.summer_rest_score = default_score
