# -*- coding=UTF-8 -*-

import auto_derby
from auto_derby import single_mode


from typing import Text, Dict, Tuple
import datetime

import logging

_LOGGER = logging.getLogger(__name__)

_ACTION_NONE = 0
_ACTION_BAN = 1
_ACTION_LESS = 2
_ACTION_MORE = 3
_ACTION_PICK = 4

_DEFAULT_ACTION = _ACTION_NONE

_RULES: Dict[Tuple[int, Text], int] = {}


JST = datetime.timezone(datetime.timedelta(hours=9), name="JST")


def _define_race_schedule(
    start: datetime.date, end: datetime.datetime, turn: int, race_name: Text
) -> None:

    now = datetime.datetime.now(JST)
    if not (start <= now <= end):
        return

    _RULES[(turn, race_name)] = _ACTION_PICK


# https://dmg.umamusume.jp/news/detail/?id=470
_define_race_schedule(
    datetime.datetime(2021, 12, 11, 5, 0, tzinfo=JST),
    datetime.datetime(2021, 12, 13, 4, 59, tzinfo=JST),
    22,
    "阪神ジュベナイルフィリーズ",
)

_define_race_schedule(
    datetime.datetime(2021, 12, 18, 5, 0, tzinfo=JST),
    datetime.datetime(2021, 12, 20, 4, 59, tzinfo=JST),
    22,
    "朝日杯フューチュリティステークス",
)

_define_race_schedule(
    datetime.datetime(2021, 12, 25, 5, 0, tzinfo=JST),
    datetime.datetime(2021, 12, 27, 4, 59, tzinfo=JST),
    47,
    "有馬記念",
)

_define_race_schedule(
    datetime.datetime(2021, 12, 27, 5, 0, tzinfo=JST),
    datetime.datetime(2021, 12, 29, 4, 59, tzinfo=JST),
    23,
    "ホープフルステークス",
)


class Plugin(auto_derby.Plugin):
    """Pick race by compagin."""

    def install(self) -> None:
        if not _RULES:
            _LOGGER.info("no race campaign today")
            return

        for i in _RULES.keys():
            _LOGGER.info("scheduled race: turn=%d name=%s", i[0], i[1])

        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                action = _RULES.get(
                    (ctx.turn_count(), self.name),
                    _DEFAULT_ACTION,
                )
                if action == _ACTION_BAN:
                    ret = 0
                elif action == _ACTION_LESS:
                    ret -= 5
                elif action == _ACTION_MORE:
                    ret += 5
                elif action == _ACTION_PICK:
                    ret += 100
                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())
