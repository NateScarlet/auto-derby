# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import List, Tuple

from .item import Item

from ..context import Context


class History:
    def __init__(self) -> None:
        self._l: List[Tuple[int, Item]] = []

    def append(self, ctx: Context, item: Item):
        self._l.append(
            (
                ctx.turn_count(),
                item,
            )
        )
