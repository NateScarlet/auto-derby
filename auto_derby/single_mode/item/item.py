# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Text, Tuple

import numpy as np

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
    from ..context import Context


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
        return isinstance(other, Item) and self._equal_key() == other._equal_key()

    def _equal_key(self):
        return (self.id, self.price)

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
        es.add(self)
        return es

    def effect_score(
        self, ctx: Context, command: Command, summary: EffectSummary
    ) -> float:
        """Item will be used before command if score not less than expected effect score."""

        es_before = summary
        es_after = es_before.clone()
        es_after.add(self)

        ctx_before = es_before.apply_to_context(ctx)
        ctx_after = es_after.apply_to_context(ctx)
        explain = ""

        from ..commands import TrainingCommand, RaceCommand

        ret = 0
        if isinstance(command, TrainingCommand):
            t_before = es_before.apply_to_training(ctx, command.training)
            t_after = es_after.apply_to_training(ctx, command.training)
            s_before = t_before.score(ctx_before)
            s_after = t_after.score(ctx_after)
            s = s_after - s_before
            if s:
                explain += f"{s:.2f} by training score delta ({s_before:.2f} -> {s_after:.2f});"
                ret += s

        if isinstance(command, RaceCommand):
            r_before = es_before.apply_to_race(ctx, command.race)
            r_after = es_after.apply_to_race(ctx, command.race)
            s_before = r_before.score(ctx_before)
            s_after = r_after.score(ctx_after)
            s = s_after - s_before
            if s:
                explain += (
                    f"{s:.2f} by race score delta ({s_before:.2f} -> {s_after:.2f});"
                )
                ret += s
            # TODO: race reward effect

        s = (ctx_after.max_vitality - ctx_before.max_vitality) * mathtools.interpolate(
            ctx.turn_count_v2(),
            (
                (1, 3),
                (25, 2),
                (49, 1),
                (73, 0.1),
            ),
        )
        if s:
            explain = "{s:.2f} by max vitality"

        if explain:
            _LOGGER.debug(
                "%s effect score: %.2f for %s: %s", self, ret, command, explain
            )
        return ret

    def expected_effect_score(self, ctx: Context, command: Command) -> float:
        ret = 0
        explain = ""
        s = self.original_price * 0.8
        if s:
            explain += f"{s:.2f} by price;"
            ret += s
        r = mathtools.interpolate(
            ctx.turn_count_v2(),
            (
                (0, 0),
                (24, -0.3),
                (48, -0.7),
                (72, -1.0),
            ),
        )
        if r:
            explain += f"{r*100:+.0f}% by turns;"
            ret *= 1 + r

        r = mathtools.interpolate(
            ctx.items.get(self.id).quantity,
            (
                (0, 0),
                (1, -0.1),
                (2, -0.3),
                (3, -0.5),
                (self.max_quantity, -0.8),
            ),
        )
        if r:
            explain += f"{r*100:+.0f}% by quantity;"
            ret *= 1 + r

        if explain:
            _LOGGER.debug("%s expected effect score: %.2f: %s", self, ret, explain)
        assert ret >= 0, ret
        return ret

    def exchange_score(self, ctx: Context) -> float:
        """
        Item will be exchanged if score not less than expected exchange score.
        """

        ret = 0
        explain = ""

        from ..commands import TrainingCommand, RaceCommand

        # by context
        es = self.effect_summary()
        ctx_after = es.apply_to_context(ctx)
        t = Training.new()
        t.speed = ctx_after.speed - ctx.speed
        t.stamina = ctx_after.stamina - ctx.stamina
        t.power = ctx_after.power - ctx.power
        t.guts = ctx_after.guts - ctx.guts
        t.wisdom = ctx_after.wisdom - ctx.wisdom
        t.vitality = ctx_after.vitality - ctx.vitality
        s = t.score(ctx)
        if s:
            explain += f"{s:.2f} by property"
            ret += s
        s = (ctx_after.max_vitality - ctx.max_vitality) * mathtools.interpolate(
            ctx.turn_count_v2(),
            (
                (1, 4),
                (25, 2),
                (49, 1),
                (73, 0.1),
            ),
        )
        if s:
            explain += f"{s:.2f} by max vitality"
            ret += s

        # by training
        sample_trainings = (
            (Training.new(), EffectSummary()),
            *(
                (trn, ctx.item_history.effect_summary_at(turn_count))
                for turn_count, trn in ctx.training_history
                if turn_count > ctx.turn_count_v2() - 12
            ),
            *((t, ctx.item_history.effect_summary(ctx)) for t in ctx.trainings),
        )
        training_scores = (
            self.effect_score(ctx, TrainingCommand(t), es) for t, es in sample_trainings
        )
        training_scores = tuple(i for i in training_scores if i > 0)
        s = float(np.percentile(training_scores, 90)) if training_scores else 0
        if s:
            explain += f"{s:.2f} by {len(training_scores)} sample trainings;"
            ret += s

        # by race
        sample_races = tuple(race for _, race in ctx.race_history)
        sample_source = "history"
        if not sample_races:
            sample_races = tuple(i.race for i in race.race_result.iterate_current(ctx))
            sample_source = "saved race result"
        race_scores = tuple(
            self.effect_score(ctx, RaceCommand(i), EffectSummary())
            for i in sample_races
        )
        s = float(np.percentile(race_scores, 90)) if race_scores else 0
        if s:
            explain += (
                f"{s:.2f} by {len(race_scores)} sample races from {sample_source};"
            )
            ret += s

        # TODO: by condition

        # by quantity
        r = mathtools.interpolate(
            ctx.items.get(self.id).quantity,
            (
                (0, 0),
                (1, -0.2),
                (2, -0.7),
                (3, -0.9),
                (self.max_quantity, -1.0),
            ),
        )
        if r:
            explain += f"{r*100:+.0f}% by quantity;"
            ret *= 1 + r

        if explain:
            _LOGGER.debug("%s exchange score: %.2f: %s", self, ret, explain)
        # TODO: calculate other effect
        return ret

    def expected_exchange_score(self, ctx: Context) -> float:
        ret = 0
        explain = ""
        s = self.price * 0.8
        if s:
            explain += f"{s:.2f} by price;"
            ret += s

        s = max(
            min(-ret + 5, 0),
            mathtools.interpolate(
                ctx.shop_coin,
                (
                    (0, 0),
                    (200, -10),
                    (1000, -100),
                ),
            ),
        )
        if s:
            explain += f"{s:.2f} by shop coin;"
            ret += s

        r = mathtools.interpolate(
            ctx.turn_count_v2(),
            (
                (1, 0),
                (25, -0.3),
                (49, -0.7),
                (73, -1.0),
            ),
        )
        if r:
            explain += f"{r*100:+.0f}% by turns;"
            ret *= 1 + r

        if explain:
            _LOGGER.debug("%s expected exchange score: %.2f: %s", self, ret, explain)
        assert ret >= 0, ret
        return ret

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
        if es.vitality > 0:
            return False
        ctx_after = es.apply_to_context(ctx)
        if es.mood and ctx_after.mood <= ctx.mood:
            return False
        return True


g.item_class = Item
