# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import List, Tuple

from ..context import Context
from .item import Item

from .effect_summary import EffectSummary


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

    def effect_summary(self, ctx: Context) -> EffectSummary:
        es = EffectSummary()
        t_now = ctx.turn_count()
        for t_start, item in self._l:
            es.add(item, t_now - t_start)
        return es
