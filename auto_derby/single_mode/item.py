# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Any, Dict, Text, Tuple

from .. import data


class g:
    data_path: str = data.path("single_mode_items.jsonl")


class ItemEffect:
    def __init__(self) -> None:
        self.id = 0
        self.group = 0
        self.type = 0
        self.values = (0, 0, 0, 0)
        self.turn_count = 0

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "id": self.id,
            "group": self.group,
            "type": self.type,
            "values": self.values,
            "turnCount": self.turn_count,
        }
        return d


class Item:
    def __init__(self) -> None:
        self.id = 0
        self.name = ""
        self.description = ""
        self.original_price = 0
        self.max_quantity = 0
        self.effect_priority = 0
        self.effects: Tuple[ItemEffect, ...] = ()

        # dynamic data
        self.price = 0
        self.quantity = 0

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
