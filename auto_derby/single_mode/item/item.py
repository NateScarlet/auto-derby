# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Text, Tuple

import numpy as np

from ..context import Context
from .effect import Effect
from .effect_summary import EffectSummary
from ..training import Training
from .. import race

if TYPE_CHECKING:
    from ..commands import Command


class Item:
    def __init__(self) -> None:
        self.id = 0
        self.name = ""
        self.description = ""
        self.original_price = 0
        self.max_quantity = 0
        self.effect_priority = 0
        self.effects: Tuple[Effect, ...] = ()

        # dynamic data
        self.price = 0
        self.quantity = 0
        self.disabled = False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Item) and self.id == other.id

    def __str__(self):
        msg = ""
        if self.price:
            msg += f"@{self.price}"
        return f"Item<{self.name}#{self.id}{msg}>"

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "originalPrice": self.original_price,
            "maxQuantity": self.max_quantity,
            "effectPriority": self.effect_priority,
            "effects": [i.to_dict() for i in self.effects],
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> Item:
        v = cls()
        v.id = d["id"]
        v.name = d["name"]
        v.description = d["description"]
        v.original_price = d["originalPrice"]
        v.max_quantity = d["maxQuantity"]
        v.effect_priority = d["effectPriority"]
        v.effects = tuple(Effect.from_dict(i) for i in d["effects"])
        return v

    def effect_summary(self) -> EffectSummary:
        es = EffectSummary()
        for i in self.effects:
            es.add(i)
        return es

    def effect_score(self, ctx: Context, command: Command) -> float:
        """Item will be used before command if score greater than 0."""

        es = self.effect_summary()

        from ..commands import TrainingCommand, RaceCommand

        if isinstance(command, TrainingCommand):
            trn = es.apply_to_training(command.training)
            delta = trn.score(ctx) - command.training.score(ctx)

            if delta < self.price / 3:
                return -1
            return delta

        if isinstance(command, RaceCommand):
            r = es.apply_to_race(command.race)
            delta = r.score(ctx) - command.race.score(ctx)
            # TODO: race reward effect
            if delta < self.price / 2:
                return -1
            return delta

        return 0

    def exchange_score(self, ctx: Context) -> float:
        """
        Item will be exchanged if score greater than 0.
        """

        es = self.effect_summary()
        ret = 0

        from ..commands import TrainingCommand, RaceCommand

        sample_trainings = (
            Training.new(),
            *(
                trn
                for turn_count, trn in ctx.training_history
                if turn_count > ctx.turn_count() - 12
            ),
            *ctx.trainings,
        )
        training_scores = (
            self.effect_score(ctx, TrainingCommand(i)) for i in sample_trainings
        )
        training_scores = tuple(i for i in training_scores if i > 0)
        if training_scores:
            ret += float(np.percentile(training_scores, 90))

        sample_races = tuple(race for _, race in ctx.race_history)
        if not sample_races:
            sample_races = tuple(i.race for i in race.race_result.iterate_current(ctx))
        race_scores = (self.effect_score(ctx, RaceCommand(i)) for i in sample_races)
        race_scores = tuple(i for i in race_scores if i > 0)
        if race_scores:
            ret += float(np.percentile(race_scores, 90))

        if es.training_no_failure:
            ret += 10

        # TODO: calculate other effect
        return ret / self.price

    def should_use_directly(self, ctx: Context) -> bool:
        """whether use for any command."""
        es = self.effect_summary()
        if es.unknown_effects:
            return False
        if es.condition_remove:
            return False
        if es.training_no_failure:
            return False
        if es.race_fan_buff or es.race_reward_buff:
            return False
        if es.training_effect_buff:
            return False
        if es.training_partner_reassign:
            return False
        max_mood = {
            ctx.MOOD_VERY_GOOD: 0,
            ctx.MOOD_GOOD: 1,
            ctx.MOOD_NORMAL: 2,
            ctx.MOOD_BAD: 3,
            ctx.MOOD_VERY_BAD: 4,
        }[ctx.mood]
        if es.mood > 0 and es.mood > max_mood:
            return False
        return True
