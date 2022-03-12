# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Sequence, Tuple

from ...constants import TrainingType
from ..race import Race
from ..training import Training
from .effect import Effect
from ... import mathtools

if TYPE_CHECKING:
    from .item import Item
    from ..context import Context


_LOGGER = logging.getLogger(__name__)


_effect_reducers: List[_EffectReducer] = []


class TrainingBuff:
    def __init__(
        self,
        type: TrainingType,
        rate: float,
        turn_count: int,
        priority: int,
        group: int,
    ) -> None:
        self.type = type
        self.rate = rate
        self.turn_count = turn_count
        self.priority = priority
        self.group = group

    def _unique_key(self):
        return (self.type, self.group)

    def apply_to(self, s: Sequence[TrainingBuff]) -> Sequence[TrainingBuff]:
        if any(
            i
            for i in s
            if i._unique_key() == self._unique_key() and i.priority > self.priority
        ):
            return s
        return (*(i for i in s if i._unique_key() != self._unique_key()), self)


def _estimate_failure_rate(ctx: Context, trn: Training) -> float:
    return mathtools.interpolate(
        int(ctx.vitality * 10000),
        (
            (0, 0.85),
            (1500, 0.7),
            (4000, 0.0),
        )
        if trn.wisdom > 0
        else (
            (0, 0.99),
            (1500, 0.8),
            (3000, 0.5),
            (5000, 0.15),
            (7000, 0.0),
        ),
    )


class EffectSummary:
    def __init__(self) -> None:
        self.speed = 0
        self.statmia = 0
        self.power = 0
        self.guts = 0
        self.wisdom = 0
        self.vitality = 0
        self.max_vitality = 0
        self.mood = 0
        self.condition_add: Tuple[int, ...] = ()
        self.condition_remove: Tuple[int, ...] = ()
        self.training_level: Dict[TrainingType, int] = {}
        self.training_effect_buff: Sequence[TrainingBuff] = ()
        self.training_vitality_debuff: Sequence[TrainingBuff] = ()
        self.training_partner_reassign = False
        self.training_no_failure = False
        self.race_fan_buff = 0.0
        self.race_reward_buff = 0.0

        self.unknown_effects: Sequence[Effect] = ()

    def add(self, item: Item, age: int = 0):
        for effect in item.effects:
            if effect.turn_count < age:
                continue
            for i in _effect_reducers:
                if i(item, effect, self):
                    break
            else:
                self.unknown_effects = (
                    *self.unknown_effects,
                    effect,
                )

    def clone(self) -> EffectSummary:
        c = self.__class__()
        c.__dict__.update(self.__dict__)
        return c

    def apply_to_training(self, ctx: Context, training: Training) -> Training:
        """
        return a copy of given training with effect applied.
        """
        t_after = Training.new()
        t_after.__dict__.update(training.__dict__)
        explain = ""
        ctx_after = self.apply_to_context(ctx)

        effect_rate = 0
        # mood
        r = ctx_after.mood[0] - ctx.mood[0]
        if r:
            explain += f"{r*100:+.0f}% by mood;"
            effect_rate += r

        # buff
        r = sum(i.rate for i in self.training_effect_buff if i.type == t_after.type)
        if r:
            explain += f"{r*100:+.0f}% by buff;"
            effect_rate += r

        r = effect_rate
        if r:
            t_after.speed = round(t_after.speed * (1 + r))
            t_after.stamina = round(t_after.stamina * (1 + r))
            t_after.power = round(t_after.power * (1 + r))
            t_after.guts = round(t_after.guts * (1 + r))
            t_after.wisdom = round(t_after.wisdom * (1 + r))

        # vitality debuff
        r = min(
            ctx.vitality - t_after.vitality,
            sum(
                i.rate for i in self.training_vitality_debuff if i.type == t_after.type
            ),
        )
        if r:
            explain += f"{r*100:+.0f}% vitality;"
            t_after.vitality *= 1 + r

        # property gain
        if self.speed:
            explain += f"{self.speed} speed;"
            t_after.speed += self.speed
        if self.statmia:
            explain += f"{self.statmia} stamina;"
            t_after.stamina += self.statmia
        if self.power:
            explain += f"{self.power} power;"
            t_after.power += self.power
        if self.guts:
            explain += f"{self.guts} guts;"
            t_after.guts += self.guts
        if self.wisdom:
            explain += f"{self.wisdom} wisdom;"
            t_after.wisdom += self.wisdom
        if self.vitality:
            # XXX: vitality convertion is not accure
            explain += f"{self.vitality} vitality;"
            t_after.vitality += self.vitality / 100

        f_before = _estimate_failure_rate(ctx, training)
        f_after = _estimate_failure_rate(ctx, t_after)
        f = mathtools.clamp(
            f_after - f_before, -t_after.failure_rate, 1 - t_after.failure_rate
        )
        if f:
            explain += f"{f*100:+.0f}% failure;"
            t_after.failure_rate += f

        if self.training_no_failure:
            explain += f"no failure;"
            t_after.failure_rate = 0
        if explain:
            _LOGGER.debug("apply to training: %s->%s: %s", training, t_after, explain)
        assert 0.0 <= t_after.failure_rate <= 1.0, t_after.failure_rate
        return t_after

    def apply_to_race(self, ctx: Context, race: Race) -> Race:
        r_after = Race.from_dict(race.to_dict())
        explain = ""
        if self.race_fan_buff:
            explain = f"{self.race_fan_buff*100:+.0f}% fans"
            r_after.fan_counts = tuple(
                round(i * (1 + self.race_fan_buff)) for i in r_after.fan_counts
            )
        if explain:
            _LOGGER.debug("apply to race: %s: %s", race, explain)
        return r_after

    def apply_to_context(self, ctx: Context) -> Context:
        ctx_after = ctx.from_dict(ctx.to_dict())
        explain = ""

        i_before = Context.ALL_MOODS.index(ctx.mood)
        i_after = mathtools.clamp(0, i_before + self.mood, len(Context.ALL_MOODS) - 1)
        if i_before != i_after:
            ctx_after.mood = Context.ALL_MOODS[i_after]
            explain += f"mood change {ctx.mood} -> {ctx_after.mood}"

        if explain:
            _LOGGER.debug("apply to context: %s", ctx, explain)
        return ctx_after


if TYPE_CHECKING:
    _EffectReducer = Callable[[Item, Effect, EffectSummary], bool]


def _only_effect_type(effect_type: int):
    def _wrapper(fn: _EffectReducer) -> _EffectReducer:
        def _func(item: Item, effect: Effect, summary: EffectSummary) -> bool:
            if effect.type != effect_type:
                return False
            return fn(item, effect, summary)

        return _func

    return _wrapper


def _register_reducer(fn: _EffectReducer):
    _effect_reducers.append(fn)
    return fn


@_register_reducer
@_only_effect_type(Effect.TYPE_PROPERTY)
def _(item: Item, effect: Effect, summary: EffectSummary):
    prop, value, _, _ = effect.values
    if prop == Effect.PROPERTY_SPEED:
        summary.speed += value
        return True
    if prop == Effect.PROPERTY_STAMINA:
        summary.statmia += value
        return True
    if prop == Effect.PROPERTY_POWER:
        summary.power += value
        return True
    if prop == Effect.PROPERTY_GUTS:
        summary.guts += value
        return True
    if prop == Effect.PROPERTY_WISDOM:
        summary.wisdom += value
        return True
    if prop == Effect.PROPERTY_STAMINA:
        summary.statmia += value
        return True
    if prop == Effect.PROPERTY_MAX_VITALITY:
        summary.max_vitality += value
        return True
    if prop == Effect.PROPERTY_VITALITY:
        summary.vitality += value
        return True
    if prop == Effect.PROPERTY_MOOD:
        summary.mood += value
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_LEVEL)
def _(item: Item, effect: Effect, summary: EffectSummary):
    lv, value, _, _ = effect.values

    def _add_value(t: TrainingType):
        summary.training_level[t] = summary.training_level.get(t, 0) + value

    if lv == Effect.TRAINING_LEVEL_SPEED:
        _add_value(TrainingType.SPEED)
        return True
    if lv == Effect.TRAINING_LEVEL_STAMINA:
        _add_value(TrainingType.STAMINA)
        return True
    if lv == Effect.TRAINING_LEVEL_GUTS:
        _add_value(TrainingType.GUTS)
        return True
    if lv == Effect.TRAINING_LEVEL_POWER:
        _add_value(TrainingType.POWER)
        return True
    if lv == Effect.TRAINING_LEVEL_WISDOM:
        _add_value(TrainingType.WISDOM)
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_CONDITION)
def _(item: Item, effect: Effect, summary: EffectSummary):
    # TODO: handle duplicated effect
    action, value, _, _ = effect.values
    if action == Effect.CONDITION_ADD:
        summary.condition_add += (value,)
        return True
    if action == Effect.CONDITION_REMOVE:
        summary.condition_remove += (value,)
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_PARTNER_REASSIGN)
def _(item: Item, effect: Effect, summary: EffectSummary):
    if effect.values == (0, 0, 0, 0):
        summary.training_partner_reassign = True
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_BUFF)
def _(item: Item, effect: Effect, summary: EffectSummary):
    tp, value, _, _ = effect.values

    def add(t: TrainingType):
        summary.training_effect_buff = TrainingBuff(
            t, value / 100, effect.turn_count, item.effect_priority, tp
        ).apply_to(summary.training_effect_buff)

    if tp == 0:
        add(TrainingType.SPEED)
        add(TrainingType.STAMINA)
        add(TrainingType.POWER)
        add(TrainingType.GUTS)
        add(TrainingType.WISDOM)
        return True
    if tp == Effect.TRAINING_LEVEL_SPEED:
        add(TrainingType.SPEED)
        return True
    if tp == Effect.TRAINING_LEVEL_STAMINA:
        add(TrainingType.STAMINA)
        return True
    if tp == Effect.TRAINING_LEVEL_POWER:
        add(TrainingType.POWER)
        return True
    if tp == Effect.TRAINING_LEVEL_GUTS:
        add(TrainingType.GUTS)
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_VITALITY_DEBUFF)
def _(item: Item, effect: Effect, summary: EffectSummary):
    tp, value, _, _ = effect.values

    def add(t: TrainingType):
        summary.training_vitality_debuff = TrainingBuff(
            t, value / 100, effect.turn_count, item.effect_priority, tp
        ).apply_to(summary.training_vitality_debuff)

    if tp == Effect.TRAINING_LEVEL_SPEED:
        add(TrainingType.SPEED)
        return True
    if tp == Effect.TRAINING_LEVEL_STAMINA:
        add(TrainingType.STAMINA)
        return True
    if tp == Effect.TRAINING_LEVEL_POWER:
        add(TrainingType.POWER)
        return True
    if tp == Effect.TRAINING_LEVEL_GUTS:
        add(TrainingType.GUTS)
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_NO_FAILURE)
def _(item: Item, effect: Effect, summary: EffectSummary):
    if effect.values == (0, 0, 0, 0):
        summary.training_no_failure = True
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_RACE_BUFF)
def _(item: Item, effect: Effect, summary: EffectSummary):
    tp, value, _, _ = effect.values
    if tp == Effect.RACE_BUFF_REWARD:
        summary.race_reward_buff = value / 100
        return True
    if tp == Effect.RACE_BUFF_FAN:
        summary.race_fan_buff = value / 100
        return True
    return False
