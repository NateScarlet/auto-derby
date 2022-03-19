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
                ctx.turn_count_v2(),
                item,
            )
        )

    def effect_summary_at(self, turn_count: int) -> EffectSummary:
        es = EffectSummary()
        t_now = turn_count
        for t_start, item in self._l:
            if t_start > t_now:
                break
            es.add(item, t_now - t_start)
        return es

    def effect_summary(self, ctx: Context) -> EffectSummary:
        return self.effect_summary_at(ctx.turn_count_v2())
