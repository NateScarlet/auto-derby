# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import time
from typing import Text

from ... import action, templates, terminal
from ...constants import RuningStyle
from ...scenes import PaddockScene
from ...scenes.single_mode import RaceMenuScene
from .. import Context, Race
from .command import Command
from .globals import g

_LOGGER = logging.getLogger(__name__)


def _choose_running_style(ctx: Context, race1: Race) -> None:
    scene = PaddockScene.enter(ctx)
    action.wait_tap_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
    scores = race1.style_scores(ctx)

    style_scores = sorted(zip(RuningStyle, scores), key=lambda x: x[1], reverse=True)

    for style, score in style_scores:
        _LOGGER.info("running style score:\t%.2f:\t%s", score, style)

    scene.choose_runing_style(style_scores[0][0])


def _handle_race_result():
    action.wait_tap_image(templates.RACE_RESULT_BUTTON)

    _, pos = action.wait_image(
        templates.RACE_RESULT_NO1,
        templates.RACE_RESULT_NO2,
        templates.RACE_RESULT_NO3,
        templates.RACE_RESULT_NO4,
        templates.RACE_RESULT_NO5,
        templates.RACE_RESULT_NO6,
        templates.RACE_RESULT_NO8,
        templates.RACE_RESULT_NO10,
    )
    while True:
        time.sleep(1)
        if action.tap_image(templates.GREEN_NEXT_BUTTON):
            break
        if action.tap_image(templates.SINGLE_MODE_CONTINUE):
            _handle_race_result()
            return
        action.tap(pos)


class RaceCommand(Command):
    def __init__(self, race: Race, *, selected: bool = False):
        self.race = race
        self.selected = selected

    def name(self) -> Text:
        return str(self.race)

    def execute(self, ctx: Context) -> None:
        scene = RaceMenuScene.enter(ctx)
        if not self.selected:
            scene.choose_race(ctx, self.race)
            self.selected = True
        race1 = self.race
        estimate_order = race1.estimate_order(ctx)
        if g.pause_if_race_order_gt >= 0 and estimate_order > g.pause_if_race_order_gt:
            terminal.pause(
                "Race estimate result is No.%d\nplease learn skills before confirm in terminal"
                % estimate_order
            )

        while True:
            tmpl, pos = action.wait_image(
                templates.RACE_RESULT_BUTTON,
                templates.SINGLE_MODE_RACE_START_BUTTON,
                templates.RETRY_BUTTON,
            )
            if tmpl.name == templates.RACE_RESULT_BUTTON:
                break
            action.tap(pos)
        ctx.race_turns.add(ctx.turn_count())

        _choose_running_style(ctx, race1)

        _handle_race_result()
        ctx.fan_count = 0  # request update in next turn
        tmpl, pos = action.wait_image(
            templates.SINGLE_MODE_LIVE_BUTTON,
            templates.SINGLE_MODE_RACE_NEXT_BUTTON,
        )
        if tmpl.name == templates.SINGLE_MODE_LIVE_BUTTON:
            g.on_single_mode_live(ctx)
        action.tap_image(templates.TEAM_RACE_NEXT_BUTTON)

    def score(self, ctx: Context) -> float:
        return self.race.score(ctx)
