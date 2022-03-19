# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from collections import defaultdict
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Sequence,
    Set,
    Tuple,
    TypeVar,
)

from ... import mathtools
from ...constants import Mood, TrainingType
from .. import condition
from ..context import Context
from ..race import Race
from ..training import Training
from .effect import Effect
from .globals import g

if TYPE_CHECKING:
    from .item import Item


_LOGGER = logging.getLogger(__name__)


_effect_reducers: List[_EffectReducer] = []


class Buff:
    def __init__(
        self,
        rate: float,
        *,
        turn_count: int,
        priority: int,
        unique_key: Any,
    ) -> None:
        self.rate = rate
        self.turn_count = turn_count
        self.priority = priority
        self.unique_key = unique_key

    def apply_to(self: T, s: Sequence[T]) -> Sequence[T]:
        if any(
            i
            for i in s
            if i.unique_key == self.unique_key and i.priority > self.priority
        ):
            return s
        return (*(i for i in s if i.unique_key != self.unique_key), self)


class BuffList:
    def __init__(self, v: Iterable[Buff] = ()) -> None:
        self._l: List[Buff] = list(v)

    def __iter__(self):
        yield from self._l

    def __len__(self):
        return len(self._l)

    def __bool__(self):
        return len(self) > 0

    def add(self, v: Buff) -> None:
        if v.unique_key is None:
            self._l.append(v)
            return
        if any(
            i
            for i in self._l
            if i.unique_key == v.unique_key and i.priority > v.priority
        ):
            return
        self._l = [*(i for i in self._l if i.unique_key != v.unique_key), v]

    def total_rate(self) -> float:
        return sum(i.rate for i in self)


T = TypeVar("T", bound=Buff)


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
        self.training_levels: DefaultDict[TrainingType, int] = defaultdict(lambda: 0)
        self.training_effect_buff: DefaultDict[TrainingType, BuffList] = defaultdict(
            BuffList
        )
        self.training_vitality_debuff: DefaultDict[
            TrainingType, BuffList
        ] = defaultdict(BuffList)
        self.training_partner_reassign = False
        self.training_no_failure = False
        self.race_fan_buff = BuffList()
        self.race_reward_buff = BuffList()
        self.support_friendship = 0
        # SELECT t1."index", t1.text, t2.text from text_data as t1 LEFT JOIN text_data as t2 WHERE t1.category == 6 AND t2."index" == t1."index" AND t2.category = 170;
        # 9002 = 秋川理事長
        self.character_friendship: Dict[int, int] = {}

        self.unknown_effects: Sequence[Effect] = ()
        self.known_effects: Sequence[Effect] = ()

    def add(self, item: Item, age: int = 0):
        for effect in item.effects:
            if effect.turn_count < age:
                continue
            for i in _effect_reducers:
                if i(item, effect, self):
                    self.known_effects = (
                        *self.known_effects,
                        effect,
                    )
                    break
            else:
                self.unknown_effects = (
                    *self.unknown_effects,
                    effect,
                )

    def clone(self) -> EffectSummary:
        return deepcopy(self)

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
        r = self.training_effect_buff[training.type].total_rate()
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
        r = self.training_vitality_debuff[training.type].total_rate()
        if r:
            explain += f"{r*100:+.0f}% vitality;"
            t_after.vitality *= 1 + r

        f_before = _estimate_failure_rate(ctx, training)
        f_after = _estimate_failure_rate(ctx_after, t_after)
        f = mathtools.clamp(
            f_after - f_before, -training.failure_rate, 1 - training.failure_rate
        )
        if f:
            explain += f"{f*100:+.0f}% failure;"
            t_after.failure_rate += f

        if self.training_no_failure:
            explain += f"no failure;"
            t_after.failure_rate = 0
        if explain and g.explain_effect_summary:
            _LOGGER.debug("apply to training: %s->%s: %s", training, t_after, explain)
        assert 0.0 <= t_after.failure_rate <= 1.0, t_after.failure_rate
        return t_after

    def reduce_on_training(self, training: Training) -> Tuple[Training, EffectSummary]:
        """Reduce effect for item score sample (remove buff so we can apply other conflicted buff)."""

        es_remains = self.clone()
        t_before = training.clone()
        explain = ""

        # effect buff
        effect_rate = 1
        r = es_remains.training_effect_buff[t_before.type].total_rate()
        del es_remains.training_effect_buff[t_before.type]
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
        r = es_remains.training_vitality_debuff[t_before.type].total_rate()
        del es_remains.training_vitality_debuff[t_before.type]
        if r:
            explain += f"{r*100:+.0f}% vitality;"
            t_before.vitality /= 1 + r

        if explain and g.explain_effect_summary:
            _LOGGER.debug(
                "revert from training: %s->%s: %s", training, t_before, explain
            )
        return t_before, es_remains

    def apply_to_race(self, ctx: Context, race: Race) -> Race:
        r_after = race.clone()
        explain = ""
        r = self.race_fan_buff.total_rate()
        if r:
            explain = f"{r*100:+.0f}% fans;"
            r_after.fan_counts = tuple(round(i * (1 + r)) for i in r_after.fan_counts)
        r = self.race_reward_buff.total_rate()
        if r:
            explain = f"{r*100:+.0f}% reward;"
            r_after.raward_buff += r
        if explain and g.explain_effect_summary:
            _LOGGER.debug("apply to race: %s: %s", race, explain)
        return r_after

    def apply_to_context(self, ctx: Context) -> Context:
        ctx_after = ctx.clone()
        explain = ""

        # mood
        all_moods = list(Mood)
        i_before = all_moods.index(ctx.mood)
        i_after = mathtools.clamp(i_before + self.mood, 0, len(all_moods) - 1)
        if i_before != i_after:
            ctx_after.mood = all_moods[i_after]
            explain += f"mood {ctx.mood} -> {ctx_after.mood};"

        min_property = 1
        max_property = 1200
        if self.speed:
            ctx_after.speed = mathtools.clamp(
                ctx.speed + self.speed, min_property, max_property
            )
            explain += f"{ctx_after.speed - ctx.speed:+d} speed;"
        if self.statmia:
            ctx_after.stamina = mathtools.clamp(
                ctx.stamina + self.statmia, min_property, max_property
            )
            explain += f"{ctx_after.stamina - ctx.stamina:+d} stamina;"
        if self.power:
            ctx_after.power = mathtools.clamp(
                ctx.power + self.power, min_property, max_property
            )
            explain += f"{ctx_after.power - ctx.power:+d} power;"
        if self.guts:
            ctx_after.guts = mathtools.clamp(
                ctx.guts + self.guts, min_property, max_property
            )
            explain += f"{ctx_after.guts - ctx.guts:+d} guts;"
        if self.wisdom:
            ctx_after.wisdom = mathtools.clamp(
                ctx.wisdom + self.wisdom, min_property, max_property
            )
            explain += f"{ctx_after.wisdom - ctx.wisdom:+d} wisdom;"
        if self.max_vitality:
            ctx_after.max_vitality = mathtools.clamp(
                ctx.max_vitality + self.max_vitality, 1, 150
            )
            explain += f"{ctx_after.max_vitality - ctx.max_vitality:+d} max vitality;"
        if self.vitality:
            ctx_after.vitality = mathtools.clamp(
                ctx.vitality + self.vitality / ctx.max_vitality, 0.0, 1.0
            )
            explain += f"{ctx_after.vitality - ctx.vitality:+.2f} vitality;"

        for t, lv_effect in self.training_levels.items():
            lv_before = ctx.training_levels.get(t)
            if not lv_before:
                # ignore if training level unknown
                continue
            lv_after = mathtools.clamp(lv_before + lv_effect, 1, 5)
            ctx_after.training_levels[t] = lv_after
            explain += f"{lv_after - lv_before:+d} {t.name} training level;"

        c = self.condition_add.difference(ctx.conditions)
        if c:
            explain += f"add condition {','.join(condition.get(i).name for i in c)};"
            ctx_after.conditions.update(self.condition_add)

        c = self.condition_remove.intersection(ctx.conditions)
        if c:
            explain += f"remove condition {','.join(condition.get(i).name for i in c)};"
            ctx_after.conditions.difference_update(c)
        if explain and g.explain_effect_summary:
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
        summary.training_levels[t] = summary.training_levels.get(t, 0) + value

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
        summary.training_effect_buff[t].add(
            Buff(
                value / 100,
                turn_count=effect.turn_count,
                priority=item.effect_priority,
                unique_key=tp,
            )
        )

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
        summary.training_vitality_debuff[t].add(
            Buff(
                value / 100,
                turn_count=effect.turn_count,
                priority=item.effect_priority,
                unique_key=tp,
            )
        )

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
        summary.race_reward_buff.add(
            Buff(
                value / 100,
                turn_count=1,
                priority=item.effect_priority,
                unique_key=tp,
            )
        )
        return True
    if tp == Effect.RACE_BUFF_FAN:
        summary.race_fan_buff.add(
            Buff(
                value / 100,
                turn_count=1,
                priority=item.effect_priority,
                unique_key=tp,
            )
        )
        return True
    return False


@_register_reducer
@_only_effect_type(Effect.TYPE_FRIENDSHIP)
def _(item: Item, effect: Effect, summary: EffectSummary):
    tp, c, value, _ = effect.values
    if tp == Effect.FRIENDSHIP_SUPPORT:
        assert c == 0, 0
        summary.support_friendship += value
        return True
    if tp == Effect.FRIENDSHIP_CHARACTER:
        summary.character_friendship[c] = summary.character_friendship.get(c, 0) + value
        return True
    return False
