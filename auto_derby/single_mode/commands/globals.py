# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable

from .. import Context


def _default_on_winning_live(ctx: Context) -> None:
    pass


class g:
    ignore_training_commands: Callable[[Context], bool]
    rest_score: Callable[[Context], float]
    summer_rest_score: Callable[[Context], float]
    health_care_score: Callable[[Context], float]
    pause_if_race_order_gt: int = -1
    on_winning_live: Callable[[Context], None] = _default_on_winning_live
