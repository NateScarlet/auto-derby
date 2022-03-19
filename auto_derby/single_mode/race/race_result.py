# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any, Dict, Iterator, List, Optional, Text

from ..context import Context
from .globals import g
from .race import Race
from ... import filetools

_LOGGER = logging.getLogger(__name__)


class RaceResult:
    def __init__(self):
        self.time = datetime.datetime.utcnow()
        self.ctx = Context.new()
        self.race = Race.new()
        self.order = 0
        self.is_failed = False

    def __str__(self) -> str:
        return f"RaceResult<race={self.race} order={self.order} fail={self.is_failed}>"

    def to_dict(self) -> Dict[Text, Any]:
        return {
            "time": self.time.isoformat(),
            "order": self.order,
            "race": self.race.to_dict(),
            "ctx": self.ctx.to_dict(),
            "is_failed": self.is_failed,
        }

    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> RaceResult:
        ret = cls()
        ret.time = datetime.datetime.fromisoformat(data["time"])
        ret.race = Race.from_dict(data["race"])
        ret.ctx = Context.from_dict(data["ctx"])
        ret.order = data["order"]
        ret.is_failed = data["is_failed"]
        return ret

    def write(self) -> None:
        p = g.result_path
        if not p:
            return
        if g.result_max_bytes > 0:
            size = 0
            try:
                size = os.stat(p).st_size
            except FileNotFoundError:
                pass
            if size > g.result_max_bytes:
                _LOGGER.info(
                    "data file large than %.2fMiB, remove records that older than 90 days",
                    g.result_max_bytes / (1 << 20),
                )
                prune(datetime.datetime.now() - datetime.timedelta(days=-90))

        def _do():
            with open(g.result_path, "a", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False)
                f.write("\n")

        try:
            _do()
        except FileNotFoundError:
            os.makedirs(os.path.dirname(p))
            _do()

    def is_current(self, ctx: Context) -> Optional[bool]:
        """
        Whether is race result of current game.
        Returns None when result is unknown.
        """

        if self.ctx.date > ctx.date:
            return False

        if (
            self.ctx.scenario != Context.SCENARIO_UNKNOWN
            and ctx.scenario != Context.SCENARIO_UNKNOWN
            and self.ctx.scenario != ctx.scenario
        ):
            return False

        # fan count never reduce
        if self.ctx.fan_count > ctx.fan_count:
            return False

        # distance status never reduce
        if (
            self.ctx.sprint > ctx.sprint
            or self.ctx.intermediate > ctx.intermediate
            or self.ctx.mile > ctx.mile
            or self.ctx.long > ctx.long
        ):
            return False

        # ground status never reduce
        if self.ctx.dart > ctx.dart or self.ctx.turf > ctx.turf:
            return False

        # style status never reduce
        if (
            self.ctx.lead > ctx.lead
            or self.ctx.head > ctx.head
            or self.ctx.middle > ctx.middle
            or self.ctx.last > ctx.last
        ):
            return False


def iterate() -> Iterator[RaceResult]:
    p = g.result_path
    if not p:
        return
    try:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if not line:
                    continue
                yield RaceResult.from_dict(json.loads(line))
    except FileNotFoundError:
        return


def prune(time_lt: datetime.datetime) -> None:
    with filetools.atomic_save_path(
        g.result_path,
        backup_suffix="~",
    ) as p, open(p, "w", encoding="utf-8") as f:
        for res in iterate():
            if res.time < time_lt:
                continue
            json.dump(res.to_dict(), f, ensure_ascii=False)
            f.write("\n")


def iterate_current(ctx: Context) -> Iterator[RaceResult]:
    buf: List[RaceResult] = []
    for i in iterate():
        if i.is_current(ctx) == False:
            buf.clear()
            continue

        if buf and buf[-1].ctx.date > i.ctx.date:
            buf.clear()
        buf.append(i)
    for i in buf:
        yield i
