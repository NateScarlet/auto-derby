# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Dict, Iterator

from .item import Item
from . import game_data


class ItemList:
    def __init__(self) -> None:
        self._m: Dict[int, Item] = {}

    def __contains__(self, value: Item) -> bool:
        return self.get(value.id).quantity > 0

    def __bool__(self) -> bool:
        return bool(self._m)

    def __iter__(self) -> Iterator[Item]:
        yield from sorted(
            (i for i in self._m.values() if i.quantity > 0), key=lambda x: x.id
        )

    def __str__(self) -> str:
        return "[" + ",".join((str(i) for i in self)) + "]"

    def quantity(self) -> int:
        return sum(i.quantity for i in self)

    def get(self, id: int) -> Item:
        return self._m.get(id) or game_data.get(id)

    def update(self, *items: Item):
        for i in items:
            self._m[i.id] = i

    def put(self, id: int, quantity: int):
        v = self.get(id)
        v.quantity += quantity
        self._m[v.id] = v

    def remove(self, id: int, quantity: int):
        self.put(id, -quantity)
