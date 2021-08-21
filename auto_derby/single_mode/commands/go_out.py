# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import time

from ... import action, template, templates
from ...scenes.single_mode.command import CommandScene
from .. import Context, go_out
from .command import Command

_LOGGER = logging.getLogger(__name__)


class GoOutCommand(Command):
    def execute(self, ctx: Context) -> None:
        CommandScene.enter(ctx)
        action.tap_image(
            templates.SINGLE_MODE_COMMAND_GO_OUT,
        )
        time.sleep(0.5)
        if action.count_image(templates.SINGLE_MODE_GO_OUT_MENU_TITLE):
            options_with_score = sorted(
                [
                    (i, i.score(ctx))
                    for i in go_out.Option.from_menu(template.screenshot())
                ],
                key=lambda x: x[1],
            )
            for option, score in options_with_score:
                _LOGGER.info("go out option:\t%s:\tscore:%.2f", option, score)
            action.tap(options_with_score[0][0].position)
        return

    def score(self, ctx: Context) -> float:
        if ctx.mood == ctx.MOOD_VERY_GOOD:
            return 0
        ret = 15 + ctx.turn_count() * 10 / 24

        if ctx.vitality > 0.5:
            ret *= 0.7
        if ctx.turn_count() >= ctx.total_turn_count() - 2:
            ret *= 0.1
        if ctx.date[1:] in ((6, 1),) and ctx.vitality < 0.8:
            ret += 10
        if ctx.date[1:] in ((6, 2),) and ctx.vitality < 0.9:
            ret += 20
        if ctx.date in ((4, 0, 0)):
            ret -= 20
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
        ret += (ctx.MOOD_VERY_GOOD[0] - ctx.mood[0]) * 40 * 3
        return ret
