# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from ...constants import TrainingType
from .effect import Effect

_effect_transforms: List[_EffectTransform] = []


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
        self.add_conditions: Tuple[int, ...] = ()
        self.remove_conditions: Tuple[int, ...] = ()
        self.training_level: Dict[TrainingType, int] = {}
        self.training_effect_buff: Tuple[TrainingBuff, ...] = ()
        self.training_vitality_debuff: Tuple[TrainingBuff, ...] = ()
        self.reset_parters = False
        self.no_training_failure = False
        self.race_fan_buff = 0.0
        self.race_reward_buff = 0.0

        self.unknown_effects: Tuple[Effect, ...] = ()

    def add(self, effect: Effect):
        for i in _effect_transforms:
            if i(effect, self):
                break
        else:
            self.unknown_effects += (effect,)


_EffectTransform = Callable[[Effect, EffectSummary], bool]


def _only_effect_type(effect_type: int):
    def _wrapper(fn: _EffectTransform) -> _EffectTransform:
        def _func(effect: Effect, summary: EffectSummary) -> bool:
            if effect.type != effect_type:
                return False
            return fn(effect, summary)

        return _func

    return _wrapper


def _register_transform(fn: _EffectTransform):
    _effect_transforms.append(fn)
    return fn


@_register_transform
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


@_register_transform
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


@_register_transform
@_only_effect_type(Effect.TYPE_CONDITION)
def _(effect: Effect, summary: EffectSummary):
    action, value, _, _ = effect.values
    if action == Effect.CONDITION_ADD:
        summary.add_conditions += (value,)
        return True
    if action == Effect.CONDITION_REMOVE:
        summary.remove_conditions += (value,)
        return True
    return False


@_register_transform
@_only_effect_type(Effect.TYPE_RESET_PARTER)
def _(effect: Effect, summary: EffectSummary):
    if effect.values == (0, 0, 0, 0):
        summary.reset_parters = True
        return True
    return False


@_register_transform
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


@_register_transform
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


@_register_transform
@_only_effect_type(Effect.TYPE_TRAINING_NO_FAILURE)
def _(effect: Effect, summary: EffectSummary):
    if effect.values == (0, 0, 0, 0):
        summary.no_training_failure = True
        return True
    return False


@_register_transform
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
