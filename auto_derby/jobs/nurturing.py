# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import time
from typing import Callable, Iterator, List, Text, Tuple, Union

from .. import action, app, config, template, templates
from ..constants import RacePrediction
from ..scenes.single_mode import (
    AoharuBattleConfirmScene,
    AoharuCompetitorScene,
    AoharuMainScene,
    CommandScene,
    RaceMenuScene,
    RaceTurnsIncorrect,
    ShopScene,
)
from ..scenes.single_mode.item_menu import ItemMenuScene
from ..single_mode import Context, commands, event, item

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


def _handle_shop(ctx: Context, cs: CommandScene):
    if not (cs.has_shop and ctx.shop_coin):
        return
    scene = ShopScene.enter(ctx)
    scene.recognize(ctx)

    scores_of_items = sorted(
        (
            (i.exchange_score(ctx), i.expected_exchange_score(ctx), i)
            for i in scene.items
        ),
        key=lambda x: x[0] - x[1],
        reverse=True,
    )

    app.log.text("shop items")
    cart_items: List[item.Item] = []
    total_price = 0
    for s, es, i in scores_of_items:
        status = ""
        if (
            sum(1 for j in cart_items if j.id == i.id) + ctx.items.get(i.id).quantity
            >= i.max_quantity
        ):
            status = "<max quantity>"
        elif total_price + i.price > ctx.shop_coin:
            status = "<coin not enough>"
        elif s > es:
            status = "<in cart>"
            cart_items.append(i)
            total_price += i.price
        app.log.text("score:\t%2.2f/%2.2f:\t%s\t%s" % (s, es, i, status))
    scene.exchange_items(ctx, cart_items)

    cs.enter(ctx)
    if any(i.should_use_directly(ctx) for i in cart_items):
        cs.recognize(ctx)
    return


def _handle_item_list(ctx: Context, cs: CommandScene):
    if not cs.has_shop:
        return
    if ctx.items_last_updated_turn == 0:
        scene = ItemMenuScene.enter(ctx)
        scene.recognize(ctx)
    items = tuple(i for i in ctx.items if i.should_use_directly(ctx))
    if items:
        scene = ItemMenuScene.enter(ctx)
        scene.use_items(ctx, items)
    cs.enter(ctx)
    return


class _CommandPlan:
    def __init__(
        self,
        ctx: Context,
        command: commands.Command,
    ) -> None:
        self.command = command
        self.command_score = command.score(ctx)
        self.item_score, self.items = item.plan.compute(ctx, command)
        self.score = self.command_score + self.item_score

    def execute(self, ctx: Context):
        if self.items:
            scene = ItemMenuScene.enter(ctx)
            scene.use_items(ctx, self.items)
        self.command.execute(ctx)

    def explain(self) -> Text:
        msg = ""
        if self.items:
            msg += f"{self.item_score:.2f} by {','.join(str(i) for i in self.items)};"
        return msg


def _has_command_changing_effect(es: item.EffectSummary) -> bool:
    if es.training_levels:
        return True
    if es.training_partner_reassign:
        return True
    if es.training_effect_buff:
        return True
    if es.training_no_failure:
        return True
    if es.training_vitality_debuff:
        return True
    return False


def _handle_turn(ctx: Context):
    scene = CommandScene.enter(ctx)
    scene.recognize(ctx)
    # see training before use items
    turn_commands = tuple(commands.from_context(ctx))
    es_delta = ctx.item_history.effect_summary_delta()
    _handle_item_list(ctx, scene)
    _handle_shop(ctx, scene)
    while _has_command_changing_effect(es_delta()):
        turn_commands = tuple(commands.from_context(ctx))
        es_delta = ctx.item_history.effect_summary_delta()
        _handle_item_list(ctx, scene)
    ctx.next_turn()
    app.log.text("context: %s" % ctx)
    for i in ctx.items:
        app.log.text("item:\t#%s\tx%s\t%s" % (i.id, i.quantity, i.name))
    command_plans = sorted(
        (_CommandPlan(ctx, i) for i in turn_commands),
        key=lambda x: x.score,
        reverse=True,
    )
    for cp in command_plans:
        app.log.text(
            "score:\t%2.2f\t%s;%s" % (cp.score, cp.command.name(), cp.explain())
        )
    try:
        command_plans[0].execute(ctx)
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
    try:
        action.wait_image_stable(ac.tmpl, timeout=3)
    except TimeoutError:
        app.log.text("command scene enter timeout, return to main loop", level=app.WARN)
        return
    _handle_turn(ac.ctx)


class _SingleModeEnd(StopIteration):
    pass


def _handle_end(ac: _ActionContext):
    ctx = ac.ctx
    app.log.text("end: %s" % ctx)
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
    scene = CommandScene.enter(ctx)
    scene.recognize(ctx)
    _handle_item_list(ctx, scene)
    _handle_shop(ctx, scene)
    ctx.next_turn()
    try:
        scene = RaceMenuScene().enter(ctx)
    except RaceTurnsIncorrect:
        scene = RaceMenuScene().enter(ctx)
    _CommandPlan(
        ctx, commands.RaceCommand(scene.first_race(ctx), selected=True)
    ).execute(ctx)


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
        yield templates.SINGLE_MODE_TARGET_GRADE_POINT_NOT_ENOUGH, _set_scenario(
            ctx.SCENARIO_CLIMAX, _cancel
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


# DEPRECATED
globals()["LOGGER"] = logging.getLogger(__name__)
