# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import Callable, Dict, List, Tuple

from ...constants import TrainingType
from ..context import Context
from ..race import Race
from ..training import Training
from .effect import Effect

_LOGGER = logging.getLogger(__name__)


_effect_reducers: List[_EffectReducer] = []


class TrainingBuff:
    def __init__(self, type: TrainingType, rate: float, turn_count: int) -> None:
        self.type = type
        self.rate = rate
        self.turn_count = turn_count


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
        self.training_effect_buff: Tuple[TrainingBuff, ...] = ()
        self.training_vitality_debuff: Tuple[TrainingBuff, ...] = ()
        self.training_partner_reassign = False
        self.training_no_failure = False
        self.race_fan_buff = 0.0
        self.race_reward_buff = 0.0

        self.unknown_effects: Tuple[Effect, ...] = ()

    def add(self, effect: Effect):
        for i in _effect_reducers:
            if i(effect, self):
                break
        else:
            self.unknown_effects += (effect,)

    def apply_to_training(self, ctx: Context, training: Training) -> Training:
        """
        return a copy of given training with effect applied.
        """
        trn = Training.new()
        trn.__dict__.update(training.__dict__)
        explain = ""

        # effect buff
        r = sum(i.rate for i in self.training_effect_buff if i.type == trn.type)
        if r:
            explain += f"{r*100:+.0f}% effect;"
            trn.speed = round(trn.speed * (1 + r))
            trn.stamina = round(trn.stamina * (1 + r))
            trn.power = round(trn.power * (1 + r))
            trn.guts = round(trn.guts * (1 + r))
            trn.wisdom = round(trn.wisdom * (1 + r))

        # vitality debuff
        r = min(
            ctx.vitality - trn.vitality,
            sum(i.rate for i in self.training_vitality_debuff if i.type == trn.type),
        )
        if r:
            explain += f"{r*100:+.0f}% vitality;"
            trn.vitality *= 1 + r

        # property gain
        if self.speed:
            explain += f"{self.speed} speed;"
            trn.speed += self.speed
        if self.statmia:
            explain += f"{self.statmia} stamina;"
            trn.stamina += self.statmia
        if self.power:
            explain += f"{self.power} power;"
            trn.power += self.power
        if self.guts:
            explain += f"{self.guts} guts;"
            trn.guts += self.guts
        if self.wisdom:
            explain += f"{self.wisdom} wisdom;"
            trn.wisdom += self.wisdom
        if self.vitality:
            explain += f"{self.vitality} vitality;"
            # XXX: vitality convertion is not accure
            trn.vitality += self.vitality / 100

        if self.training_no_failure:
            explain += f"no failure;"
            trn.failure_rate = 0
        if explain:
            _LOGGER.debug("apply to training: %s->%s: %s", training, trn, explain)
        return trn

    def apply_to_race(self, ctx: Context, race: Race) -> Race:
        r = Race.from_dict(race.to_dict())
        explain = ""
        if self.race_fan_buff:
            explain = f"{self.race_fan_buff*100:+.0f}% fans"
            r.fan_counts = tuple(
                round(i * (1 + self.race_fan_buff)) for i in r.fan_counts
            )
        if explain:
            _LOGGER.debug("apply to race: %s: %s", race, explain)
        return r


_EffectReducer = Callable[[Effect, EffectSummary], bool]


def _only_effect_type(effect_type: int):
    def _wrapper(fn: _EffectReducer) -> _EffectReducer:
        def _func(effect: Effect, summary: EffectSummary) -> bool:
            if effect.type != effect_type:
                return False
            return fn(effect, summary)

        return _func

    return _wrapper


def _register_reducer(fn: _EffectReducer):
    _effect_reducers.append(fn)
    return fn


@_register_reducer
@_only_effect_type(Effect.TYPE_PROPERTY)
def _(effect: Effect, summary: EffectSummary):
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
def _(effect: Effect, summary: EffectSummary):
    lv, value, _, _ = effect.values

    def _add_value(t: TrainingType):
        summary.training_level[t] = summary.training_level.get(t, 0) + value

    if lv == Effect.TRAINING_LEVEL_SPEED:
        _add_value(TrainingType.SPEED)
        return True
    if lv == Effect.TRAINING_LEVEL_STAMINA:
        _add_value(TrainingType.SPEED)
        return True
    if lv == Effect.TRAINING_LEVEL_GUTS:
        _add_value(TrainingType.SPEED)
        return True
    if lv == Effect.TRAINING_LEVEL_POWER:
        _add_value(TrainingType.SPEED)
        return True
    if lv == Effect.TRAINING_LEVEL_WISDOM:
        _add_value(TrainingType.SPEED)
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_CONDITION)
def _(effect: Effect, summary: EffectSummary):
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
def _(effect: Effect, summary: EffectSummary):
    if effect.values == (0, 0, 0, 0):
        summary.training_partner_reassign = True
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_BUFF)
def _(effect: Effect, summary: EffectSummary):
    tp, value, _, _ = effect.values
    if tp == 0:
        summary.training_effect_buff += (
            TrainingBuff(TrainingType.SPEED, value / 100, effect.turn_count),
            TrainingBuff(TrainingType.STAMINA, value / 100, effect.turn_count),
            TrainingBuff(TrainingType.POWER, value / 100, effect.turn_count),
            TrainingBuff(TrainingType.GUTS, value / 100, effect.turn_count),
            TrainingBuff(TrainingType.WISDOM, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_SPEED:
        summary.training_effect_buff += (
            TrainingBuff(TrainingType.SPEED, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_STAMINA:
        summary.training_effect_buff += (
            TrainingBuff(TrainingType.STAMINA, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_POWER:
        summary.training_effect_buff += (
            TrainingBuff(TrainingType.POWER, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_GUTS:
        summary.training_effect_buff += (
            TrainingBuff(TrainingType.GUTS, value / 100, effect.turn_count),
        )
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_VITALITY_DEBUFF)
def _(effect: Effect, summary: EffectSummary):
    tp, value, _, _ = effect.values
    if tp == Effect.TRAINING_LEVEL_SPEED:
        summary.training_vitality_debuff += (
            TrainingBuff(TrainingType.SPEED, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_STAMINA:
        summary.training_vitality_debuff += (
            TrainingBuff(TrainingType.STAMINA, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_POWER:
        summary.training_vitality_debuff += (
            TrainingBuff(TrainingType.POWER, value / 100, effect.turn_count),
        )
        return True
    if tp == Effect.TRAINING_LEVEL_GUTS:
        summary.training_vitality_debuff += (
            TrainingBuff(TrainingType.GUTS, value / 100, effect.turn_count),
        )
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_TRAINING_NO_FAILURE)
def _(effect: Effect, summary: EffectSummary):
    if effect.values == (0, 0, 0, 0):
        summary.training_no_failure = True
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_RACE_BUFF)
def _(effect: Effect, summary: EffectSummary):
    tp, value, _, _ = effect.values
    if tp == Effect.RACE_BUFF_REWARD:
        summary.race_reward_buff = value / 100
        return True
    if tp == Effect.RACE_BUFF_FAN:
        summary.race_fan_buff = value / 100
        return True
    return False
