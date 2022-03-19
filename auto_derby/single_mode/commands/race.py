# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import Callable, Optional, Text

from ... import action, templates, terminal
from ...scenes import PaddockScene
from ...scenes.single_mode import RaceMenuScene
from .. import Context, Race, RaceResult
from .command import Command
from .globals import g

_LOGGER = logging.getLogger(__name__)


def _choose_running_style(ctx: Context, race1: Race) -> None:
    scene = PaddockScene.enter(ctx)
    style_scores = sorted(race1.style_scores_v2(ctx), key=lambda x: x[1], reverse=True)

    for style, score in style_scores:
        _LOGGER.info("running style score:\t%.2f:\t%s", score, style)

    scene.choose_runing_style(style_scores[0][0])


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


def _retry_method(ctx: Context) -> Optional[Callable[[], None]]:
    if action.count_image(templates.SINGLE_MODE_CLIMAX_WHITE_CONTINUE_BUTTON):

        def _retry():
            action.tap_image(templates.SINGLE_MODE_CLIMAX_WHITE_CONTINUE_BUTTON)
            action.wait_tap_image(templates.SINGLE_MODE_CLIMAX_GREEN_CONTINUE_BUTTON)

        return _retry


def _handle_race_result(ctx: Context, race: Race):
    action.wait_tap_image(templates.RACE_RESULT_BUTTON)

    res = RaceResult()
    res.ctx = ctx.clone()
    res.race = race

    tmpl, pos = action.wait_image(*_RACE_ORDER_TEMPLATES.keys())
    res.order = _RACE_ORDER_TEMPLATES[tmpl.name]
    action.tap(pos)

    if ctx.scenario == ctx.SCENARIO_CLIMAX and ctx.date[0] < 4:
        tmpl, pos = action.wait_image_stable(
            templates.CLOSE_BUTTON,
            templates.SINGLE_MODE_CLIMAX_RIVAL_RACE_WIN,
            templates.SINGLE_MODE_CLIMAX_RIVAL_RACE_DRAW,
            templates.SINGLE_MODE_CLIMAX_RIVAL_RACE_LOSE,
        )
        action.tap(pos)
        if tmpl.name != templates.CLOSE_BUTTON:
            action.wait_tap_image(templates.CLOSE_BUTTON)

    tmpl, pos = action.wait_image_stable(
        templates.GREEN_NEXT_BUTTON,
        templates.SINGLE_MODE_CONTINUE,
    )

    res.is_failed = tmpl.name == templates.SINGLE_MODE_CONTINUE
    _LOGGER.info("race result: %s", res)
    g.on_race_result(ctx, res)
    res.write()

    if res.order > 1:
        retry = _retry_method(ctx)
        if retry and g.should_retry_race(ctx, res):
            retry()
            _handle_race_result(ctx, race)
            return

    action.tap(pos)
    if res.is_failed:
        ctx.mood = {
            ctx.MOOD_VERY_BAD: ctx.MOOD_BAD,
            ctx.MOOD_BAD: ctx.MOOD_NORMAL,
            ctx.MOOD_NORMAL: ctx.MOOD_GOOD,
            ctx.MOOD_GOOD: ctx.MOOD_VERY_GOOD,
            ctx.MOOD_VERY_GOOD: ctx.MOOD_VERY_GOOD,
        }[ctx.mood]
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
        ctx.race_history.append(ctx, self.race)

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
