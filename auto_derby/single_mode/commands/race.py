# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
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


class RaceResult:
    def __init__(self) -> None:
        self.race = Race()
        self.order = 0
        self.is_failed = False

    def __str__(self) -> str:
        return f"RaceResult<race={self.race} order={self.order} fail={self.is_failed}>"


_RACE_ORDER_TEMPLATES = {
    templates.RACE_RESULT_NO1: 1,
    templates.RACE_RESULT_NO2: 2,
    templates.RACE_RESULT_NO3: 3,
    templates.RACE_RESULT_NO4: 4,
    templates.RACE_RESULT_NO5: 5,
    templates.RACE_RESULT_NO6: 6,
    templates.RACE_RESULT_NO8: 8,
    templates.RACE_RESULT_NO10: 10,
}


def _handle_race_result(ctx: Context, race: Race):
    action.wait_tap_image(templates.RACE_RESULT_BUTTON)

    res = RaceResult()
    res.race = race

    tmpl, pos = action.wait_image(*_RACE_ORDER_TEMPLATES.keys())
    res.order = _RACE_ORDER_TEMPLATES[tmpl.name]
    action.tap(pos)

    tmpl, pos = action.wait_image(
        templates.GREEN_NEXT_BUTTON,
        templates.SINGLE_MODE_CONTINUE,
    )
    res.is_failed = tmpl.name == templates.SINGLE_MODE_CONTINUE
    _LOGGER.info("race result: %s", res)
    g.on_race_result(ctx, res)
    action.tap(pos)
    if res.is_failed:
        _handle_race_result(ctx, race)


class RaceCommand(Command):
    def __init__(self, race: Race, *, selected: bool = False):
        self.race = race
        self.selected = selected

    def name(self) -> Text:
        return str(self.race)

    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
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

        _handle_race_result(ctx, race1)
        ctx.fan_count = 0  # request update in next turn
        tmpl, pos = action.wait_image(
            templates.SINGLE_MODE_LIVE_BUTTON,
            templates.SINGLE_MODE_RACE_NEXT_BUTTON,
        )
        if tmpl.name == templates.SINGLE_MODE_LIVE_BUTTON:
            g.on_winning_live(ctx)
        action.tap_image(templates.TEAM_RACE_NEXT_BUTTON)

    def score(self, ctx: Context) -> float:
        return self.race.score(ctx)
