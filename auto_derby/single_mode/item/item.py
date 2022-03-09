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
from ... import mathtools
from .globals import g
import logging

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..commands import Command

# TODO: allow plugin override class
class Item:
    @staticmethod
    def new() -> Item:
        return g.item_class()

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
        if self.quantity:
            msg += f"x{self.quantity}"
        return f"Item<{self.name}#{self.id}{msg}>"

    def __bool__(self) -> bool:
        return self.name != ""

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
        v = cls.new()
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
        """Item will be used before command if score not less than expected effect score."""

        es = self.effect_summary()
        explain = ""

        from ..commands import TrainingCommand, RaceCommand

        ret = 0
        if isinstance(command, TrainingCommand):
            trn = es.apply_to_training(command.training)
            s_after = trn.score(ctx)
            s_before = command.training.score(ctx)
            s = s_after - s_before
            ret += s
            explain += (
                f"{s:.2f} by training score delta ({s_before:.2f} -> {s_after:.2f});"
            )

        if isinstance(command, RaceCommand):
            r = es.apply_to_race(command.race)
            s_after = r.score(ctx)
            s_before = command.race.score(ctx)
            s = s_after - s_before
            ret += s
            explain += f"{s:.2f} by race score delta ({s_before:.2f} -> {s_after:.2f});"
            # TODO: race reward effect

        _LOGGER.debug(
            "%s: effect score:\t%.2f\tfor %s\t%s", self, ret, command, explain
        )
        return ret

    def expected_effect_score(self, ctx: Context, command: Command) -> float:
        # TODO:
        return 0

    def exchange_score(self, ctx: Context) -> float:
        """
        Item will be exchanged if score not less than expected exchange score.
        """

        # FIXME: unexpected score for not supported effects

        es = self.effect_summary()
        ret = 0
        explain = ""

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
            s = float(np.percentile(training_scores, 90))
            explain += f"{s:.2f} from {len(sample_trainings)} sample trainings;"
            ret += s

        sample_races = tuple(race for _, race in ctx.race_history)
        if not sample_races:
            sample_races = tuple(i.race for i in race.race_result.iterate_current(ctx))
            explain += f"no history race, use saved race result;"
        race_scores = tuple(
            self.effect_score(ctx, RaceCommand(i)) for i in sample_races
        )
        if race_scores:
            s = float(np.percentile(race_scores, 90))
            explain += f"{s:.2f} from {len(sample_races)} sample races;"
            ret += s

        if es.training_no_failure:
            s = 10
            explain += f"{s:.2f} from training no fail effect;"
            ret += s

        f = mathtools.interpolate(
            ctx.items.get(self.id).quantity,
            (
                (0, 1.0),
                (1, 0.8),
                (2, 0.3),
                (3, 0.1),
                (5, 0.0),
            ),
        )
        explain += f"x{f:.2f} quantity penality;"
        ret *= f

        _LOGGER.debug("%s: exchange score:\t%.2f\t%s", self, ret, explain)
        # TODO: calculate other effect
        return ret

    def expected_exchange_score(self, ctx: Context) -> float:
        return self.price * mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 5),
                (24, 2),
                (48, 1),
                (72, 0),
            ),
        )

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


g.item_class = Item
