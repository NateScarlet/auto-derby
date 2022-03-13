# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Sequence, Set, Tuple

from ... import mathtools
from ...constants import TrainingType, Mood
from ..context import Context
from ..race import Race
from .. import condition
from ..training import Training
from .effect import Effect

if TYPE_CHECKING:
    from .item import Item


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
        self.condition_add: Set[int] = set()
        self.condition_remove: Set[int] = set()
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
        t_after = training.clone()
        explain = ""
        ctx_after = self.apply_to_context(ctx)

        effect_rate = 1
        # mood
        r = ctx_after.mood.training_rate - ctx.mood.training_rate
        if r:
            explain += f"{r*100:+.0f}% by mood;"
            effect_rate *= 1 + r

        # buff
        r = sum(i.rate for i in self.training_effect_buff if i.type == t_after.type)
        if r:
            explain += f"{r*100:+.0f}% by buff;"
            effect_rate *= 1 + r

        r = effect_rate
        if r != 1:
            t_after.speed = round(t_after.speed * r)
            t_after.stamina = round(t_after.stamina * r)
            t_after.power = round(t_after.power * r)
            t_after.guts = round(t_after.guts * r)
            t_after.wisdom = round(t_after.wisdom * r)

        # vitality debuff
        r = sum(i.rate for i in self.training_vitality_debuff if i.type == t_after.type)
        if r:
            explain += f"{r*100:+.0f}% vitality;"
            t_after.vitality *= 1 + r

        f_before = _estimate_failure_rate(ctx, training)
        f_after = _estimate_failure_rate(ctx_after, t_after)
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

    def reduce_on_training(self, training: Training) -> Tuple[Training, EffectSummary]:
        """Reduce effect for item score sample (remove buff so we can apply other conflicted buff)."""

        es_remains = self.clone()
        t_before = training.clone()
        explain = ""

        effect_rate = 1

        # buff
        r = sum(
            i.rate for i in es_remains.training_effect_buff if i.type == t_before.type
        )
        es_remains.training_effect_buff = tuple(
            i for i in es_remains.training_effect_buff if i.type != t_before.type
        )
        if r:
            explain += f"{r*100:+.0f}% by buff;"
            effect_rate *= 1 + r

        r = effect_rate
        if r != 1:
            t_before.speed = round(t_before.speed / r)
            t_before.stamina = round(t_before.stamina / r)
            t_before.power = round(t_before.power / r)
            t_before.guts = round(t_before.guts / r)
            t_before.wisdom = round(t_before.wisdom / r)

        # vitality debuff
        r = sum(
            i.rate
            for i in es_remains.training_vitality_debuff
            if i.type == t_before.type
        )
        es_remains.training_vitality_debuff = tuple(
            i for i in es_remains.training_vitality_debuff if i.type != t_before.type
        )
        if r:
            explain += f"{r*100:+.0f}% vitality;"
            t_before.vitality /= 1 + r

        if explain:
            _LOGGER.debug(
                "revert from training: %s->%s: %s", training, t_before, explain
            )
        return t_before, es_remains

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

        # mood
        all_moods = list(Mood)
        i_before = all_moods.index(ctx.mood)
        i_after = mathtools.clamp(i_before + self.mood, 0, len(all_moods) - 1)
        if i_before != i_after:
            ctx_after.mood = all_moods[i_after]
            explain += f"mood {ctx.mood} -> {ctx_after.mood};"

        if self.speed:
            explain += f"{self.speed} speed;"
            ctx_after.speed += self.speed
        if self.statmia:
            explain += f"{self.statmia} stamina;"
            ctx_after.stamina += self.statmia
        if self.power:
            explain += f"{self.power} power;"
            ctx_after.power += self.power
        if self.guts:
            explain += f"{self.guts} guts;"
            ctx_after.guts += self.guts
        if self.wisdom:
            explain += f"{self.wisdom} wisdom;"
            ctx_after.wisdom += self.wisdom
        if self.max_vitality:
            explain += f"{self.max_vitality} max vitality;"
            ctx_after.max_vitality += self.max_vitality
        if self.vitality:
            explain += f"{self.vitality} vitality;"
            ctx_after.vitality += self.vitality / ctx.max_vitality

        c = self.condition_add.difference(ctx.conditions)
        if c:
            explain += f"add condition {','.join(condition.get(i).name for i in c)};"
            ctx.conditions.update(self.condition_add)

        c = self.condition_remove.intersection(ctx.conditions)
        if c:
            explain += f"remove condition {','.join(condition.get(i).name for i in c)};"
            ctx.conditions.difference_update(c)
        if explain:
            _LOGGER.debug("apply to context: %s", explain)
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
    action, value, _, _ = effect.values
    if action == Effect.CONDITION_ADD:
        summary.condition_add.add(value)
        return True
    if action == Effect.CONDITION_REMOVE:
        summary.condition_remove.add(value)
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
