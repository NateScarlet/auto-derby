# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Iterator, List, Tuple

from ..context import Context
from .race import Race


class History:
    def __init__(self) -> None:
        self._l: List[Tuple[int, Race]] = []

    def append(self, ctx: Context, race: Race):
        self._l.append(
            (
                ctx.turn_count_v2(),
                race,
            )
        )

    def iterate(self, *, last: int = 75) -> Iterator[Tuple[int, Race]]:
        yield from self._l[-last:]
