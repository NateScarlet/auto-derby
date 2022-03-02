# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import json
from typing import Any, Dict, Optional, Text, Tuple

from .. import data


class g:
    data_path: Text = data.path("single_mode_items.jsonl")
    items: Dict[int, Item] = {}


class _g:
    loaded_data_path: Text = ""


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

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> ItemEffect:
        v = cls()
        v.id = d["id"]
        v.group = d["group"]
        v.type = d["type"]
        v.values = tuple(d["values"])
        v.turn_count = d["turnCount"]

        return v


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

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> Item:
        v = cls()
        v.id = d["id"]
        v.name = d["name"]
        v.description = d["description"]
        v.original_price = d["originalPrice"]
        v.max_quantity = d["maxQuantity"]
        v.effect_priority = d["effectPriority"]
        v.effects = tuple(ItemEffect.from_dict(i) for i in d["effects"])
        return v


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield Item.from_dict(json.loads(i))


def reload():
    g.items = {i.id: i for i in _iter(g.data_path)}
    return


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()

def find_by_id(id: int) -> Optional[Item]:
    reload_on_demand()
    return g.items.get(id)
