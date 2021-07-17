# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import time
from concurrent import futures
from typing import Optional

import cast_unknown as cast

from .. import action, config, imagetools, mathtools, template, templates, terminal
from ..single_mode import Context, Training, event, go_out, race

LOGGER = logging.getLogger(__name__)


_TRAINING_CONFIRM = template.Specification(
    templates.SINGLE_MODE_TRAINING_CONFIRM, threshold=0.8
)


_RACE_DETAIL_BUTTON = template.Specification(
    templates.SINGLE_MODE_RACE_DETAIL_BUTTON, threshold=0.8
)


def _current_race(ctx: Context) -> race.Race:
    action.wait_tap_image(_RACE_DETAIL_BUTTON)
    action.wait_image(templates.SINGLE_MODE_RACE_DETAIL_TITLE)
    race1 = race.find_by_race_detail_image(ctx, template.screenshot())
    action.wait_tap_image(templates.CLOSE_BUTTON)
    return race1


def _is_race_list_scroll_to_top() -> bool:
    rp = action.resize_proxy()
    color = template.screenshot(max_age=0).getpixel(rp.vector2((525, 525), 540))
    return (
        imagetools.compare_color((123, 121, 140), tuple(cast.list_(color, int))) > 0.9
    )


def _choose_race(ctx: Context, race1: race.Race) -> None:
    rp = action.resize_proxy()

    time.sleep(0.2)  # wait animation
    while not _is_race_list_scroll_to_top():
        action.swipe(rp.vector2((100, 500), 466), dy=rp.vector(100, 466), duration=0.2)
        time.sleep(0.2)
    action.tap(rp.vector2((100, 500), 466))

    if _current_race(ctx) == race1:
        return

    while True:
        action.tap(rp.vector2((100, 600), 466))
        if _current_race(ctx) == race1:
            return
        action.swipe(
            rp.vector2((100, 600), 466),
            dy=rp.vector(-50, 466),
            duration=0.2,
        )


def _iter_training_images():
    rp = action.resize_proxy()
    radius = rp.vector(30, 540)
    _, first_confirm_pos = action.wait_image(_TRAINING_CONFIRM)
    yield template.screenshot()
    for pos in (
        rp.vector2((78, 850), 540),
        rp.vector2((171, 850), 540),
        rp.vector2((268, 850), 540),
        rp.vector2((367, 850), 540),
        rp.vector2((461, 850), 540),
    ):
        if mathtools.distance(first_confirm_pos, pos) < radius:
            continue
        action.tap(pos)
        action.wait_image(_TRAINING_CONFIRM)
        yield template.screenshot()


def _handle_training(ctx: Context) -> None:
    with futures.ThreadPoolExecutor() as pool:
        trainings = [
            i.result()
            for i in [
                pool.submit(Training.from_training_scene, j)
                for j in _iter_training_images()
            ]
        ]

    races_with_score = sorted(
        ((i, i.score(ctx)) for i in race.find(ctx)),
        key=lambda x: x[1],
        reverse=True,
    )

    trainings_with_score = [(i, i.score(ctx)) for i in trainings]
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
            action.wait_tap_image(templates.RETURN_BUTTON)
            action.wait_tap_image(templates.SINGLE_MODE_COMMAND_RACE)
            tmpl, _ = action.wait_image(
                templates.SINGLE_MODE_RACE_START_BUTTON,
                templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE,
            )
            if tmpl.name == templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE:
                if ctx.continuous_race_count() >= 3:
                    action.wait_tap_image(templates.GREEN_OK_BUTTON)
                else:
                    # continuous race count incorrect, evaluate again:
                    ctx.race_turns.update(range(ctx.turn_count() - 3, ctx.turn_count()))
                    action.wait_tap_image(templates.CANCEL_BUTTON)
                    action.wait_tap_image(templates.SINGLE_MODE_COMMAND_TRAINING)
                    _handle_training(ctx)
                    return
            _choose_race(ctx, r)
            _handle_race(ctx, r)
            return

    if training_score < expected_score:
        # not worth, go rest
        action.tap_image(templates.RETURN_BUTTON)
        action.wait_image(templates.SINGLE_MODE_COMMAND_TRAINING)
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
    if trainings[-1] != training:
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
    action.wait_tap_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
    rp = action.resize_proxy()
    names = ("last", "middle", "head", "lead")
    scores = race1.style_scores(ctx)
    button_pos = (
        rp.vector2((60, 500), 466),
        rp.vector2((160, 500), 466),
        rp.vector2((260, 500), 466),
        rp.vector2((360, 500), 466),
    )

    style_scores = sorted(
        zip(names, scores, button_pos), key=lambda x: x[1], reverse=True
    )

    for name, score, _ in style_scores:
        LOGGER.info("running style score:\t%.2f:\t%s", score, name)

    _, pos = action.wait_image(templates.RACE_CONFIRM_BUTTON)
    time.sleep(0.5)
    action.tap(style_scores[0][2])
    action.tap(pos)


def _handle_race(ctx: Context, race1: Optional[race.Race] = None):
    race1 = race1 or _current_race(ctx)
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


def _update_context_by_class_menu(ctx: Context):
    action.wait_tap_image(templates.SINGLE_MODE_CLASS_DETAIL_BUTTON)
    time.sleep(0.2)  # wait animation
    action.wait_image(templates.SINGLE_MODE_CLASS_DETAIL_TITLE)
    ctx.update_by_class_detail(template.screenshot())
    action.wait_tap_image(templates.CLOSE_BUTTON)


def _update_context_by_status_menu(ctx: Context):
    action.wait_tap_image(templates.SINGLE_MODE_CHARACTER_DETAIL_BUTTON)
    time.sleep(0.2)  # wait animation
    action.wait_image(templates.SINGLE_MODE_CHARACTER_DETAIL_TITLE)
    ctx.update_by_character_detail(template.screenshot())
    action.wait_tap_image(templates.CLOSE_BUTTON)


def _update_context_by_command_scene(ctx: Context):
    action.reset_client_size()
    ctx.update_by_command_scene(template.screenshot(max_age=0))
    if not ctx.fan_count:
        _update_context_by_class_menu(ctx)
    if ctx.turf == ctx.STATUS_NONE or ctx.date[1:] == (4, 1):
        _update_context_by_status_menu(ctx)


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
        elif name == templates.SINGLE_MODE_FORMAL_RACE_BANNER:
            _update_context_by_command_scene(ctx)
            ctx.next_turn()
            x, y = pos
            y += 60
            action.tap((x, y))
            action.wait_image_disappear(tmpl)
            if action.count_image(templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE):
                action.wait_tap_image(templates.GREEN_OK_BUTTON)
            _handle_race(ctx)
        elif name == templates.SINGLE_MODE_URA_FINALS:
            _update_context_by_command_scene(ctx)
            ctx.next_turn()
            action.tap(pos)
            _handle_race(ctx)
        elif name == templates.SINGLE_MODE_COMMAND_TRAINING:
            time.sleep(0.2)  # wait animation
            _update_context_by_command_scene(ctx)
            ctx.next_turn()
            LOGGER.info("update context: %s", ctx)
            if action.tap_image(templates.SINGLE_MODE_SCHEDULED_RACE_OPENING_BANNER):
                action.wait_tap_image(templates.SINGLE_MODE_GO_TO_SCHEDULED_RACE_BUTTON)
                _handle_race(ctx)
                continue

            action.tap(pos)
            _handle_training(ctx)
        elif name == templates.SINGLE_MODE_OPTION1:
            _handle_option()
        elif name == templates.SINGLE_MODE_CRANE_GAME_BUTTON:
            config.on_single_mode_crane_game(ctx)
        else:
            action.tap(pos)
