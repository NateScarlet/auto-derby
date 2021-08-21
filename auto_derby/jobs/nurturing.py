# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
from auto_derby.scenes.single_mode.race_menu import RaceMenuScene

import logging
import time

from .. import action, config, template, templates
from ..scenes.single_mode import (
    CommandScene,
)
from ..single_mode import Context, event, commands

LOGGER = logging.getLogger(__name__)


ALL_OPTIONS = [
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
]


def _handle_option():
    time.sleep(0.2)  # wait animation
    ans = event.get_choice(template.screenshot(max_age=0))
    action.tap_image(ALL_OPTIONS[ans - 1])


def _handle_turn(ctx: Context):
    time.sleep(0.2)  # wait animation
    ctx.scene = CommandScene()
    ctx.scene.recognize(ctx)
    ctx.next_turn()
    command_with_scores = sorted(
        ((i, i.score(ctx)) for i in commands.from_context(ctx)),
        key=lambda x: x[1],
        reverse=True,
    )
    LOGGER.info("context: %s", ctx)
    for c, s in command_with_scores:
        LOGGER.info("score:\t%2.2f:\t%s", s, c.name())
    command_with_scores[0][0].execute(ctx)


def nurturing():
    ctx = Context.new()

    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.SINGLE_MODE_COMMAND_TRAINING,
            templates.SINGLE_MODE_FANS_NOT_ENOUGH,
            templates.SINGLE_MODE_TARGET_RACE_NO_PERMISSION,
            templates.SINGLE_MODE_TARGET_UNFINISHED,
            templates.SINGLE_MODE_FINISH_BUTTON,
            templates.SINGLE_MODE_FORMAL_RACE_BANNER,
            templates.SINGLE_MODE_RACE_NEXT_BUTTON,
            templates.SINGLE_MODE_OPTION1,
            templates.GREEN_NEXT_BUTTON,
            templates.SINGLE_MODE_URA_FINALS,
            templates.SINGLE_MODE_GENE_INHERIT,
            templates.SINGLE_MODE_CRANE_GAME_BUTTON,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            pass
        elif name == templates.SINGLE_MODE_TARGET_UNFINISHED:
            action.wait_tap_image(templates.CANCEL_BUTTON)
        elif name in (
            templates.SINGLE_MODE_FANS_NOT_ENOUGH,
            templates.SINGLE_MODE_TARGET_RACE_NO_PERMISSION,
        ):

            def _set_target_fan_count():
                ctx.target_fan_count = max(ctx.fan_count + 1, ctx.target_fan_count)

            ctx.defer_next_turn(_set_target_fan_count)
            action.wait_tap_image(templates.CANCEL_BUTTON)
        elif name == templates.SINGLE_MODE_FINISH_BUTTON:
            break
        elif name in (
            templates.SINGLE_MODE_FORMAL_RACE_BANNER,
            templates.SINGLE_MODE_URA_FINALS,
        ):
            CommandScene().recognize(ctx)
            ctx.next_turn()
            scene = RaceMenuScene().enter(ctx)
            commands.RaceCommand(scene.first_race(ctx), selected=True).execute(ctx)
        elif name == templates.SINGLE_MODE_COMMAND_TRAINING:
            _handle_turn(ctx)
        elif name == templates.SINGLE_MODE_OPTION1:
            _handle_option()
        elif name == templates.SINGLE_MODE_CRANE_GAME_BUTTON:
            config.on_single_mode_crane_game(ctx)
        else:
            action.tap(pos)
