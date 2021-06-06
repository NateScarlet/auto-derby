# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import time
from typing import List, Tuple

from .. import action, template, templates
from ..single_mode import Context, Training, choice

LOGGER = logging.getLogger(__name__)


def _interpolate(value: int, value_map: Tuple[Tuple[int, float], ...]) -> float:
    if len(value_map) == 0:
        return 0
    if len(value_map) == 1:
        return value_map[0][1]
    low = (0, 0.0)
    high = (0, 0.0)
    for v, w in value_map:
        if v >= value:
            high = (v, w)
            break
        low = (v, w)
    v1, w1 = low
    v2, w2 = high
    if w2 == w1 or v1 == v2:
        return w2
    pos = (value - v1) / (v2 - v1)
    weight = w1 + (w2 - w1) * pos
    return weight


def _training_single_score(current: int, delta: int, value_map: Tuple[Tuple[int, float], ...]) -> float:

    ret = 0
    for i in range(current, current+delta):
        ret += _interpolate(
            i,
            value_map
        )
    return ret


def _training_score(ctx: Context, training: Training) -> float:
    spd = _training_single_score(
        ctx.speed,
        training.speed,
        (
            (0, 2.0),
            (300, 1.0),
            (600, 0.8),
            (900, 0.7),
            (1100, 0.5),
        )
    )

    sta = _training_single_score(
        ctx.stamina,
        training.stamina,
        (
            (0, 2.0),
            (300, ctx.speed / 600 + 0.3 *
             ctx.date[0] if ctx.speed > 600 else 1.0),
            (600, ctx.speed / 900 * 0.6 + 0.1 *
             ctx.date[0] if ctx.speed > 900 else 0.6),
            (900, ctx.speed / 900 * 0.3),
        )
    )
    pow = _training_single_score(
        ctx.power,
        training.power,
        (
            (0, 1.0),
            (300, 0.2 + ctx.speed / 600),
            (600, 0.1 + ctx.speed / 900),
            (900, ctx.speed / 900 / 3),
        )
    )
    per = _training_single_score(
        ctx.guts,
        training.guts,
        (
            (0, 2.0),
            (300, 1.0),
            (400, 0.3),
            (600, 0.1),
        ) if ctx.speed > 400 / 24 * ctx.turn_count() else (
            (0, 2.0),
            (300, 0.5),
            (400, 0.1),
        )
    )
    int_ = _training_single_score(
        ctx.intelligence,
        training.intelligence,
        (
            (0, 3.0),
            (300, 1.0),
            (400, 0.4),
            (600, 0.2),
        ) if ctx.vitality < 0.9 else (
            (0, 2.0),
            (300, 0.8),
            (400, 0.1),
        )
    )

    if ctx.vitality < 0.9:
        int_ += 5 if ctx.date[1:] in (
            (7, 1),
            (7, 2),
            (8, 1),
        ) else 3

    skill = training.skill * 0.5
    return spd + sta + pow + per + int_ + skill


_TRAINING_CONFIRM = template.Specification(
    templates.NURTURING_TRAINING_CONFIRM,
    threshold=0.8
)


def _handle_training(ctx: Context):
    trainings: List[Training] = []

    action.wait_image(_TRAINING_CONFIRM)
    for x, y in (
        (78, 700),
        (158, 700),
        (234, 700),
        (314, 700),
        (402, 700),
    ):
        action.drag((x, y-100), dy=100)
        action.wait_image(_TRAINING_CONFIRM)
        t = Training.from_training_scene(template.screenshot())
        trainings.append(t)

    expected_score = 15 + ctx.turn_count() * 10 / 24
    if ctx.vitality > 0.5:
        expected_score *= 0.5
    if ctx.turn_count() >= ctx.total_turn_count() - 2:
        expected_score *= 0.1
    if ctx.date[1:] in (
        (6, 1),
    ) and ctx.vitality < 0.8:
        expected_score += 10
    if ctx.date[1:] in (
        (6, 2),
    ) and ctx.vitality < 0.9:
        expected_score += 20
    if ctx.date[1:] in (
        (7, 1),
        (7, 2),
        (8, 1),
    ) and ctx.vitality < 0.8:
        expected_score += 10
    if ctx.date in (
        (4, 0, 0)
    ):
        expected_score -= 20
    LOGGER.info("expected score:\t%2.2f", expected_score)
    trainings_with_score = [(i, _training_score(ctx, i)) for i in trainings]
    trainings_with_score = sorted(
        trainings_with_score, key=lambda x: x[1], reverse=True)
    for t, s in trainings_with_score:
        LOGGER.info("score:\t%2.2f:\t%s", s, t)
    training, score = trainings_with_score[0]
    if score < expected_score:
        # not worth, go rest
        action.click_image(templates.RETURN_BUTTON)
        _, pos = action.wait_image(
            templates.NURTURING_REST,  # TODO: rename this template
            templates.NURTURING_COMMAND_SUMMER_REST,
        ) if ctx.vitality < 0.8 else action.wait_image(
            templates.NURTURING_COMMAND_GO_OUT,
            templates.NURTURING_COMMAND_SUMMER_REST,
        )
        action.click(pos)
    x, y = training.confirm_position
    action.drag((x, y-100), dy=100)
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
        if action.click_image(templates.NURTURING_CONTINUE):
            _handle_race_result()
            return
        action.click(pos)


def _handle_race(ctx: Context):
    # TODO: change running style
    action.wait_click_image(templates.NURTURING_RACE_DETAIL_BUTTON)
    exit(1)
    action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
    action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
    _handle_race_result()
    _, pos = action.wait_image(templates.NURTURING_RACE_NEXT_BUTTON)

    with action.recover_cursor():
        action.move((pos[0], pos[1]-100))
        action.wheel(10)
        ctx.update_by_race_result_scene(template.screenshot())
        action.click(pos)


ALL_OPTIONS = [
    templates.NURTURING_OPTION1,
    templates.NURTURING_OPTION2,
    templates.NURTURING_OPTION3,
    templates.NURTURING_OPTION4,
    templates.NURTURING_OPTION5,
]


def _handle_option():
    ans = choice.get(template.screenshot())
    action.click_image(ALL_OPTIONS[ans-1])


def _update_context_by_class_menu(ctx: Context):
    action.wait_click_image(templates.NURTURING_CHARACTER_CLASS_MENU_BUTTON)
    action.wait_image(templates.NURTURING_CHARACTER_CLASS_MENU_TITLE)
    ctx.update_by_character_class_menu(template.screenshot())
    action.wait_click_image(templates.CLOSE_BUTTON)


def _update_context_by_status_menu(ctx: Context):
    action.wait_click_image(templates.NURTURING_CHARACTER_STATUS_MENU_BUTTON)
    action.wait_image(templates.NURTURING_CHARACTER_STATUS_MENU_TITLE)
    ctx.update_by_character_status_menu(template.screenshot())
    action.wait_click_image(templates.CLOSE_BUTTON)


def nurturing():
    ctx = Context()
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.NURTURING_COMMAND_TRAINING,
            templates.NURTURING_FANS_NOT_ENOUGH,
            templates.NURTURING_FINISH_BUTTON,
            templates.NURTURING_FORMAL_RACE_BANNER,
            templates.NURTURING_RACE_NEXT_BUTTON,
            templates.NURTURING_OPTION1,
            templates.GREEN_NEXT_BUTTON,
            templates.NURTURING_URA_FINALS,
            templates.NURTURING_GENE_INHERIT,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            pass
        elif name == templates.NURTURING_FANS_NOT_ENOUGH:
            # TODO: handle this
            exit(1)
        elif name == templates.NURTURING_FINISH_BUTTON:
            break
        elif name == templates.NURTURING_FORMAL_RACE_BANNER:
            x, y = pos
            y += 60
            action.click((x, y))
            _handle_race(ctx)
        elif name == templates.NURTURING_URA_FINALS:
            ctx.next_turn()
            action.click(pos)
            _handle_race(ctx)
        elif name == templates.NURTURING_COMMAND_TRAINING:
            time.sleep(0.2)  # wait animation
            ctx.update_by_command_scene(template.screenshot(max_age=0))
            if not ctx.fan_count:
                _update_context_by_class_menu(ctx)
            if ctx.grass == ctx.STATUS_NONE or ctx.date[1:] == (4, 1):
                _update_context_by_status_menu(ctx)

            ctx.next_turn()
            LOGGER.info("update context: %s", ctx)
            if action.click_image(templates.NURTURING_SCHEDULED_RACE_OPENING_BANNER):
                action.wait_click_image(
                    templates.NURTURING_GO_TO_SCHEDULED_RACE_BUTTON)
                _handle_race(ctx)
                continue

            if ctx.turn_count() >= ctx.total_turn_count() - 2:
                if ctx.vitality < 0.4:
                    action.click_image(templates.NURTURING_COMMAND_GO_OUT)
                else:
                    action.click(pos)
                    _handle_training(ctx)
            elif ctx.vitality <= 0.5:
                if action.click_image(templates.NURTURING_COMMAND_HEALTH_CARE):
                    time.sleep(2)
                    if action.count_image(templates.NURTURING_HEALTH_CARE_CONFIRM):
                        action.click_image(templates.GREEN_OK_BUTTON)
                    continue

                if ctx.mood < ctx.MOOD_GOOD:
                    _, pos = action.wait_image(
                        templates.NURTURING_COMMAND_GO_OUT,
                        templates.NURTURING_COMMAND_SUMMER_REST,
                    )
                    action.click(pos)
                else:
                    _, pos = action.wait_image(
                        templates.NURTURING_REST,
                        templates.NURTURING_COMMAND_SUMMER_REST,
                    )
                    action.click(pos)
            else:
                action.click(pos)
                _handle_training(ctx)
        elif name == templates.NURTURING_OPTION1:
            _handle_option()
        else:
            action.click(pos)
