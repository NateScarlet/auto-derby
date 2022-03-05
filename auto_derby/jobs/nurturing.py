# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
from auto_derby.constants import RacePrediction

import logging
import time
from typing import Callable, Iterator, Text, Tuple, Union

from .. import action, config, template, templates
from ..scenes.single_mode import (
    AoharuBattleConfirmScene,
    AoharuCompetitorScene,
    AoharuMainScene,
    CommandScene,
    RaceMenuScene,
    RaceTurnsIncorrect,
    ShopScene,
)
from ..single_mode import Context, commands, event

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


def _handle_shop(ctx: Context):
    scene = ShopScene.enter(ctx)
    scene.recognize(ctx)
    CommandScene.enter(ctx)
    # TODO: exchange items
    # TODO: use items


def _handle_turn(ctx: Context):
    scene = CommandScene.enter(ctx)
    scene.recognize(ctx)
    if scene.has_shop:
        _handle_shop(ctx)
    ctx.next_turn()
    command_with_scores = sorted(
        ((i, i.score(ctx)) for i in commands.from_context(ctx)),
        key=lambda x: x[1],
        reverse=True,
    )
    # TODO: use items
    LOGGER.info("context: %s", ctx)
    for c, s in command_with_scores:
        LOGGER.info("score:\t%2.2f:\t%s", s, c.name())
    try:
        command_with_scores[0][0].execute(ctx)
    except RaceTurnsIncorrect:
        _handle_turn(ctx)


class _ActionContext:
    def __init__(
        self, ctx: Context, tmpl: template.Specification, pos: _Vector2
    ) -> None:
        self.ctx = ctx
        self.tmpl = tmpl
        self.pos = pos


_Template = Union[Text, template.Specification]
_Vector2 = Tuple[int, int]
_Handler = Callable[[_ActionContext], None]


def _pass(ac: _ActionContext):
    pass


def _tap(ac: _ActionContext):
    action.tap(ac.pos)


def _cancel(ac: _ActionContext):
    action.wait_tap_image(templates.CANCEL_BUTTON)


def _close(ac: _ActionContext):
    action.wait_tap_image(templates.CLOSE_BUTTON)


def _ac_handle_turn(ac: _ActionContext):
    _handle_turn(ac.ctx)


class _SingleModeEnd(StopIteration):
    pass


def _handle_end(ac: _ActionContext):
    ctx = ac.ctx
    LOGGER.info("end: %s", ctx)
    config.on_single_mode_end(ctx)
    raise _SingleModeEnd


def _handle_fan_not_enough(ac: _ActionContext):
    ctx = ac.ctx

    def _set_target_fan_count():
        ctx.target_fan_count = max(ctx.fan_count + 1, ctx.target_fan_count)

    ctx.defer_next_turn(_set_target_fan_count)
    action.wait_tap_image(templates.CANCEL_BUTTON)


def _handle_target_race(ac: _ActionContext):
    ctx = ac.ctx
    CommandScene().recognize(ctx)
    ctx.next_turn()
    try:
        scene = RaceMenuScene().enter(ctx)
    except RaceTurnsIncorrect:
        scene = RaceMenuScene().enter(ctx)
    commands.RaceCommand(scene.first_race(ctx), selected=True).execute(ctx)


def _ac_handle_option(ac: _ActionContext):
    _handle_option()


def _handle_crane_game(ac: _ActionContext):
    ctx = ac.ctx
    config.on_single_mode_crane_game(ctx)


def _set_scenario(scenario: Text, _handler: _Handler) -> _Handler:
    def _func(ac: _ActionContext):
        ac.ctx.scenario = scenario
        _handler(ac)

    return _func


def _handle_aoharu_team_race(ac: _ActionContext):
    ctx = ac.ctx
    scene = AoharuMainScene.enter(ctx)
    scene.recognize()
    scene.go_race()

    if scene.is_final:
        action.wait_tap_image(templates.SINGLE_MODE_AOHARU_FINAL_BATTLE_BUTTON)
    else:
        for index in range(3):
            scene = AoharuCompetitorScene.enter(ctx)
            scene.choose_competitor(index)
            action.wait_tap_image(templates.GREEN_BATTLE_BUTTON)
            scene = AoharuBattleConfirmScene.enter(ctx)
            scene.recognize_predictions()
            if (
                len(
                    tuple(
                        i
                        for i in scene.predictions.values()
                        if i in (RacePrediction.HONNMEI, RacePrediction.TAIKOU)
                    )
                )
                >= 3
            ):
                break

    action.wait_tap_image(templates.GREEN_BATTLE_BUTTON)
    tmpl, pos = action.wait_image(
        templates.SINGLE_MODE_AOHARU_RACE_RESULT_BUTTON,
        templates.SINGLE_MODE_AOHARU_MAIN_RACE_BUTTON,
    )
    action.tap(pos)
    if tmpl.name == templates.SINGLE_MODE_AOHARU_MAIN_RACE_BUTTON:
        action.wait_tap_image(templates.GO_TO_RACE_BUTTON)
        action.wait_tap_image(templates.RACE_START_BUTTON)

    while True:
        tmpl, pos = action.wait_image(
            templates.SKIP_BUTTON,
            templates.SINGLE_MODE_RACE_NEXT_BUTTON,
        )
        action.tap(pos)
        if tmpl.name == templates.SINGLE_MODE_RACE_NEXT_BUTTON:
            break


def _template_actions(ctx: Context) -> Iterator[Tuple[_Template, _Handler]]:
    yield templates.CONNECTING, _pass
    yield templates.RETRY_BUTTON, _tap
    yield templates.SINGLE_MODE_COMMAND_TRAINING, _ac_handle_turn
    yield templates.SINGLE_MODE_FANS_NOT_ENOUGH, _handle_fan_not_enough
    yield templates.SINGLE_MODE_TARGET_RACE_NO_PERMISSION, _handle_fan_not_enough
    yield templates.SINGLE_MODE_TARGET_UNFINISHED, _cancel
    yield templates.SINGLE_MODE_FINISH_BUTTON, _handle_end
    yield templates.SINGLE_MODE_FORMAL_RACE_BANNER, _handle_target_race
    yield templates.SINGLE_MODE_RACE_NEXT_BUTTON, _tap
    yield templates.SINGLE_MODE_OPTION1, _ac_handle_option
    yield templates.GREEN_NEXT_BUTTON, _tap
    yield templates.SINGLE_MODE_URA_FINALS, _handle_target_race
    yield templates.SINGLE_MODE_GENE_INHERIT, _tap
    yield templates.SINGLE_MODE_CRANE_GAME_BUTTON, _handle_crane_game
    if ctx.scenario in (ctx.SCENARIO_AOHARU, ctx.SCENARIO_UNKNOWN):
        yield templates.SINGLE_MODE_AOHARU_AUTO_FORMATION_TITLE, _set_scenario(
            ctx.SCENARIO_AOHARU, _close
        )
        yield templates.SINGLE_MODE_AOHARU_FORMAL_RACE_BANNER, _set_scenario(
            ctx.SCENARIO_AOHARU, _handle_aoharu_team_race
        )
    if ctx.scenario in (ctx.SCENARIO_CLIMAX, ctx.SCENARIO_UNKNOWN):
        yield templates.SINGLE_MODE_GO_TO_SHOP_BUTTON, _set_scenario(
            ctx.SCENARIO_CLIMAX, _cancel
        )
        yield templates.SINGLE_MODE_TARGET_RACE_POINT_NOT_ENOUGH, _set_scenario(
            ctx.scenario, _cancel
        )


def _spec_key(tmpl: _Template) -> Text:
    if isinstance(tmpl, template.Specification):
        return tmpl.name
    return tmpl


def nurturing():
    ctx = Context.new()

    while True:
        spec = {_spec_key(k): v for k, v in _template_actions(ctx)}
        tmpl, pos = action.wait_image(*spec.keys())
        ac = _ActionContext(ctx, tmpl, pos)
        try:
            spec[_spec_key(tmpl)](ac)
        except _SingleModeEnd:
            break
