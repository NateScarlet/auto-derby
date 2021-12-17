# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any, Dict, Iterator, Text

from ..context import Context
from .globals import g
from .race import Race

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


def iterate() -> Iterator[RaceResult]:
    p = g.result_path
    if not p:
        return
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if not line:
                continue
            yield RaceResult.from_dict(json.loads(line))


def prune(time_lt: datetime.datetime) -> None:
    p = g.result_path
    tmp_path = p + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        for res in iterate():
            if res.time < time_lt:
                continue
            json.dump(res.to_dict(), f, ensure_ascii=False)
            f.write("\n")
    try:
        os.unlink(p + "~")
    except FileNotFoundError:
        pass
    os.rename(p, p + "~")
    os.rename(tmp_path, p)
