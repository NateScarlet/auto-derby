# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


from typing import Callable, Dict, List, Tuple


from ...constants import TrainingType
from .effect import Effect


_effect_transforms: List[_EffectTransform] = []


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
        self.training_level: Dict[TrainingType, float] = {}
        self.training_buff: Dict[TrainingType, float] = {}
        self.training_vitality_debuff: Dict[TrainingType, float] = {}
        self.reset_parters = False
        self.no_training_failure = False
        self.race_fan_buff = 0
        self.race_reward_buff = 0

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
    return False
