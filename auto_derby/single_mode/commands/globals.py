# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .command import Command
    from .race import RaceResult

from .. import Context


def _default_on_winning_live(ctx: Context) -> None:
    pass


def _default_on_command(ctx: Context, command: Command) -> None:
    pass


def _default_on_race_result(ctx: Context, result: RaceResult) -> None:
    pass


def _default_should_retry_race(ctx: Context, result: RaceResult) -> bool:
    return ctx.date[0] == 4 or result.order > result.race.estimate_order(ctx)


class g:
    ignore_training_commands: Callable[[Context], bool]
    rest_score: Callable[[Context], float]
    summer_rest_score: Callable[[Context], float]
    health_care_score: Callable[[Context], float]
    pause_if_race_order_gt: int = -1
    on_winning_live: Callable[[Context], None] = _default_on_winning_live
    on_command: Callable[[Context, Command], None] = _default_on_command
    on_race_result: Callable[[Context, RaceResult], None] = _default_on_race_result
    should_retry_race: Callable[
        [Context, RaceResult], bool
    ] = _default_should_retry_race
