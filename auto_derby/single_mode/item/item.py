# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Text, Tuple

from ..context import Context
from .effect import Effect

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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Item) and self.id == other.id

    def __str__(self):
        return f"Item<{self.id}:{self.name}>"

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

    def exchange_score(self, ctx: Context) -> float:
        """
        Item will be exchanged if score greater than 0.
        """
        return 0

    def effect_score(self, ctx: Context, command: Command) -> float:
        """Item will be used before command if score greater than 0."""
        return 0

    def should_use_directly(self, ctx: Context) -> bool:
        """whether use after exchange."""
        return False
