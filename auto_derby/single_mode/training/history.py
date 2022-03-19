# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Iterator, List, Tuple

from ..context import Context
from .training import Training


class History:
    def __init__(self) -> None:
        self._l: List[Tuple[int, Training]] = []

    def append(self, ctx: Context, training: Training):
        self._l.append(
            (
                ctx.turn_count_v2(),
                training,
            )
        )

    def iterate(self, *, last: int = 75) -> Iterator[Tuple[int, Training]]:
        yield from self._l[-last:]
