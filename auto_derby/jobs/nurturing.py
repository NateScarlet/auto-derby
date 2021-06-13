# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import time
from typing import List

from .. import action, template, templates
from ..single_mode import Context, Training, choice, race

LOGGER = logging.getLogger(__name__)


_TRAINING_CONFIRM = template.Specification(
    templates.SINGLE_MODE_TRAINING_CONFIRM, threshold=0.8
)


def _handle_training(ctx: Context):
    trainings: List[Training] = []

    action.wait_image(_TRAINING_CONFIRM)
    for x, y in ((78, 700), (158, 700), (234, 700), (314, 700), (402, 700)):
        action.drag((x, y - 100), dy=100)
        action.wait_image(_TRAINING_CONFIRM)
        t = Training.from_training_scene(template.screenshot())
        trainings.append(t)

    expected_score = 15 + ctx.turn_count() * 10 / 24
    if ctx.vitality > 0.5:
        expected_score *= 0.5
    if ctx.turn_count() >= ctx.total_turn_count() - 2:
        expected_score *= 0.1
    if ctx.date[1:] in ((6, 1),) and ctx.vitality < 0.8:
        expected_score += 10
    if ctx.date[1:] in ((6, 2),) and ctx.vitality < 0.9:
        expected_score += 20
    if ctx.date[1:] in ((7, 1), (7, 2), (8, 1)) and ctx.vitality < 0.8:
        expected_score += 10
    if ctx.date in ((4, 0, 0)):
        expected_score -= 20
    LOGGER.info("expected score:\t%2.2f", expected_score)
    trainings_with_score = [(i, i.score(ctx)) for i in trainings]
    trainings_with_score = sorted(
        trainings_with_score, key=lambda x: x[1], reverse=True
    )
    for t, s in trainings_with_score:
        LOGGER.info("score:\t%2.2f:\t%s", s, t)
    training, score = trainings_with_score[0]
    if score < expected_score:
        # not worth, go rest
        action.click_image(templates.RETURN_BUTTON)
        _, pos = (
            action.wait_image(
                templates.SINGLE_MODE_REST,  # TODO: rename this template
                templates.SINGLE_MODE_COMMAND_SUMMER_REST,
            )
            if ctx.vitality < 0.8
            else action.wait_image(
                templates.SINGLE_MODE_COMMAND_GO_OUT,
                templates.SINGLE_MODE_COMMAND_SUMMER_REST,
            )
        )
        action.click(pos)
    x, y = training.confirm_position
    action.drag((x, y - 100), dy=100)
    action.click((x, y))


def _handle_race_result():
    action.wait_click_image(templates.RACE_RESULT_BUTTON)

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
        if action.click_image(templates.GREEN_NEXT_BUTTON):
            break
        if action.click_image(templates.SINGLE_MODE_CONTINUE):
            _handle_race_result()
            return
        action.click(pos)


_RACE_DETAIL_BUTTON = template.Specification(
    templates.SINGLE_MODE_RACE_DETAIL_BUTTON, threshold=0.8
)


def _choose_running_style(ctx: Context, race1: race.Race) -> None:
    action.wait_click_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)

    names = ("last", "middle", "head", "lead")
    scores = race1.style_scores(ctx)
    button_pos = ((60, 500), (160, 500), (260, 500), (360, 500))

    style_scores = sorted(
        zip(names, scores, button_pos), key=lambda x: x[1], reverse=True
    )

    for name, score, _ in style_scores:
        LOGGER.info("running style score:\t%.2f:\t%s", score, name)

    _, pos = action.wait_image(templates.RACE_CONFIRM_BUTTON)
    action.click(style_scores[0][2])
    action.click(pos)


def _handle_race(ctx: Context):
    action.wait_click_image(templates.SINGLE_MODE_RACE_START_BUTTON)
    action.wait_click_image(templates.SINGLE_MODE_RACE_START_BUTTON)
    action.wait_image(templates.RACE_RESULT_BUTTON)

    action.wait_click_image(_RACE_DETAIL_BUTTON)
    race1 = race.find_by_race_detail_image(ctx, template.screenshot())
    action.wait_click_image(templates.CLOSE_BUTTON)

    _choose_running_style(ctx, race1)

    _handle_race_result()
    ctx.fan_count = 0  # request update in next turn
    action.wait_click_image(templates.SINGLE_MODE_RACE_NEXT_BUTTON)


ALL_OPTIONS = [
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
]


def _handle_option():
    ans = choice.get(template.screenshot())
    action.click_image(ALL_OPTIONS[ans - 1])


def _update_context_by_class_menu(ctx: Context):
    action.wait_click_image(templates.SINGLE_MODE_CLASS_DETAIL_BUTTON)
    action.wait_image(templates.SINGLE_MODE_CLASS_DETAIL_TITLE)
    ctx.update_by_class_detail(template.screenshot())
    action.wait_click_image(templates.CLOSE_BUTTON)


def _update_context_by_status_menu(ctx: Context):
    action.wait_click_image(templates.SINGLE_MODE_CHARACTER_DETAIL_BUTTON)
    action.wait_image(templates.SINGLE_MODE_CHARACTER_DETAIL_TITLE)
    ctx.update_by_character_detail(template.screenshot())
    action.wait_click_image(templates.CLOSE_BUTTON)


def _update_context_by_command_scene(ctx: Context):
    ctx.update_by_command_scene(template.screenshot(max_age=0))
    if not ctx.fan_count:
        _update_context_by_class_menu(ctx)
    if ctx.turf == ctx.STATUS_NONE or ctx.date[1:] == (4, 1):
        _update_context_by_status_menu(ctx)


def nurturing():
    ctx = Context()

    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.SINGLE_MODE_COMMAND_TRAINING,
            templates.SINGLE_MODE_FANS_NOT_ENOUGH,
            templates.SINGLE_MODE_FINISH_BUTTON,
            templates.SINGLE_MODE_FORMAL_RACE_BANNER,
            templates.SINGLE_MODE_RACE_NEXT_BUTTON,
            templates.SINGLE_MODE_OPTION1,
            templates.GREEN_NEXT_BUTTON,
            templates.SINGLE_MODE_URA_FINALS,
            templates.SINGLE_MODE_GENE_INHERIT,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            pass
        elif name == templates.SINGLE_MODE_FANS_NOT_ENOUGH:
            # TODO: handle this
            exit(1)
        elif name == templates.SINGLE_MODE_FINISH_BUTTON:
            break
        elif name == templates.SINGLE_MODE_FORMAL_RACE_BANNER:
            _update_context_by_command_scene(ctx)
            ctx.next_turn()
            x, y = pos
            y += 60
            action.click((x, y))
            _handle_race(ctx)
        elif name == templates.SINGLE_MODE_URA_FINALS:
            ctx.next_turn()
            action.click(pos)
            _handle_race(ctx)
        elif name == templates.SINGLE_MODE_COMMAND_TRAINING:
            time.sleep(0.2)  # wait animation
            _update_context_by_command_scene(ctx)
            ctx.next_turn()
            LOGGER.info("update context: %s", ctx)
            if action.click_image(templates.SINGLE_MODE_SCHEDULED_RACE_OPENING_BANNER):
                action.wait_click_image(
                    templates.SINGLE_MODE_GO_TO_SCHEDULED_RACE_BUTTON
                )
                _handle_race(ctx)
                continue

            if ctx.turn_count() >= ctx.total_turn_count() - 2:
                if ctx.vitality < 0.4:
                    action.click_image(templates.SINGLE_MODE_COMMAND_GO_OUT)
                else:
                    action.click(pos)
                    _handle_training(ctx)
            elif ctx.vitality <= 0.5:
                if action.click_image(templates.SINGLE_MODE_COMMAND_HEALTH_CARE):
                    time.sleep(2)
                    if action.count_image(templates.SINGLE_MODE_HEALTH_CARE_CONFIRM):
                        action.click_image(templates.GREEN_OK_BUTTON)
                    continue

                if ctx.mood < ctx.MOOD_GOOD:
                    _, pos = action.wait_image(
                        templates.SINGLE_MODE_COMMAND_GO_OUT,
                        templates.SINGLE_MODE_COMMAND_SUMMER_REST,
                    )
                    action.click(pos)
                else:
                    _, pos = action.wait_image(
                        templates.SINGLE_MODE_REST,
                        templates.SINGLE_MODE_COMMAND_SUMMER_REST,
                    )
                    action.click(pos)
            else:
                action.click(pos)
                _handle_training(ctx)
        elif name == templates.SINGLE_MODE_OPTION1:
            _handle_option()
        else:
            action.click(pos)
