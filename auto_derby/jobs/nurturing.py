# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import time
from typing import Optional

from .. import action, config, template, templates, terminal
from ..single_mode import Context, event, go_out, race
from ..scenes import (
    SingleModeCommandScene as CommandScene,
    SingleModeRaceMenuScene as RaceMenuScene,
    SingleModeTrainingScene as TrainingScene,
    PaddockScene,
    RaceTurnsIncorrect,
)

LOGGER = logging.getLogger(__name__)


def _handle_training(ctx: Context) -> None:
    scene = TrainingScene.enter(ctx)
    scene.recognize()

    races_with_score = sorted(
        ((i, i.score(ctx)) for i in race.find(ctx)),
        key=lambda x: x[1],
        reverse=True,
    )

    trainings_with_score = [(i, i.score(ctx)) for i in scene.trainings]
    trainings_with_score = sorted(
        trainings_with_score, key=lambda x: x[1], reverse=True
    )

    expected_score = ctx.expected_score()
    LOGGER.info("expected score:\t%2.2f", expected_score)
    for r, s in races_with_score:
        LOGGER.info("score:\trace:\t%2.2f:\t%s", s, r)
    for t, s in trainings_with_score:
        LOGGER.info("score:\ttraining:\t%2.2f:\t%s", s, t)
    training, training_score = trainings_with_score[0]

    if races_with_score:
        r, s = races_with_score[0]
        if (s > expected_score and s > training_score) or (
            ctx.fan_count < ctx.target_fan_count and r.estimate_order(ctx) <= 3
        ):
            # go to race
            try:
                scene = RaceMenuScene.enter(ctx)
                scene.choose_race(ctx, r)
                _handle_race(ctx, r)
                return
            except RaceTurnsIncorrect:
                _handle_training(ctx)
                return

    if training_score < expected_score:
        # not worth, go rest
        CommandScene.enter(ctx)
        if action.tap_image(templates.SINGLE_MODE_COMMAND_HEALTH_CARE):
            return

        if ctx.mood < ctx.MOOD_VERY_GOOD:
            tmpl, pos = action.wait_image(
                templates.SINGLE_MODE_COMMAND_GO_OUT,
                templates.SINGLE_MODE_COMMAND_SUMMER_REST,
            )
            action.tap(pos)
            action.wait_image_disappear(tmpl)
        else:
            tmpl, pos = (
                action.wait_image(
                    templates.SINGLE_MODE_REST,
                    templates.SINGLE_MODE_COMMAND_SUMMER_REST,
                )
                if ctx.vitality < 0.8
                else action.wait_image(
                    templates.SINGLE_MODE_COMMAND_GO_OUT,
                    templates.SINGLE_MODE_COMMAND_SUMMER_REST,
                )
            )
            action.tap(pos)
            action.wait_image_disappear(tmpl)
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
                LOGGER.info("go out option:\t%s:\tscore:%.2f", option, score)
            action.tap(options_with_score[0][0].position)
        return
    x, y = training.confirm_position
    if scene.trainings[-1] != training:
        action.tap((x, y))
        time.sleep(0.1)
    action.tap((x, y))


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


def _choose_running_style(ctx: Context, race1: race.Race) -> None:
    scene = PaddockScene.enter(ctx)
    action.wait_tap_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
    scores = race1.style_scores(ctx)

    style_scores = sorted(
        zip(ctx.ALL_RUNING_STYLES, scores), key=lambda x: x[1], reverse=True
    )

    for style, score in style_scores:
        LOGGER.info(
            "running style score:\t%.2f:\t%s", score, ctx.runing_style_text(style)
        )

    scene.choose_runing_style(style_scores[0][0])


def _handle_race(ctx: Context, race1: Optional[race.Race] = None):
    scene = RaceMenuScene.enter(ctx)
    race1 = race1 or scene.first_race(ctx)
    estimate_order = race1.estimate_order(ctx)
    if estimate_order > config.pause_if_race_order_gt:
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
        config.on_single_mode_live(ctx)
    action.tap_image(templates.TEAM_RACE_NEXT_BUTTON)


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
            ctx.scene = CommandScene()
            ctx.scene.recognize(ctx)
            ctx.next_turn()
            _handle_race(ctx)
        elif name == templates.SINGLE_MODE_COMMAND_TRAINING:
            time.sleep(0.2)  # wait animation
            ctx.scene = CommandScene()
            ctx.scene.recognize(ctx)
            ctx.next_turn()
            LOGGER.info("update context: %s", ctx)
            if action.tap_image(templates.SINGLE_MODE_SCHEDULED_RACE_OPENING_BANNER):
                action.wait_tap_image(templates.SINGLE_MODE_GO_TO_SCHEDULED_RACE_BUTTON)
                _handle_race(ctx)
                continue

            TrainingScene.enter(ctx)
            _handle_training(ctx)
        elif name == templates.SINGLE_MODE_OPTION1:
            _handle_option()
        elif name == templates.SINGLE_MODE_CRANE_GAME_BUTTON:
            config.on_single_mode_crane_game(ctx)
        else:
            action.tap(pos)
