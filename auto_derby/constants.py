# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import enum
import functools


class RuningStyle(enum.Enum):
    LEAD = 1
    HEAD = 2
    MIDDLE = 3
    LAST = 4


class RaceType(enum.Enum):
    """
    ・距離
    レースごとに競走を行う距離は決まっており、以下の4つのカテゴリーに区分されます。

    短距離：1400m以下
    マイル：1401m～1800m
    中距離：1801m～2400m
    長距離：2401m以上

    https://umamusume.cygames.jp/#/help?p=3
    """

    SPRINT = 1
    MILE = 2
    INTERMEDIATE = 3
    LONG = 4

    DART = 5


class RacePrediction(enum.Enum):
    """
    ウマ娘が出走する前のパドックなどで、どれくらいの着順に入りそうかを記者などが予想して発表したもの。
    予想を発表するのは3人だが、予想した人によって何を重視するかが異なるため、同じ予想内容になるとは限らない。
    予想内容は記号で表される。

    ◎：本命。一番能力が高いと思われること。
    ○：対抗。本命に対抗できる2番手の能力を持っていること。
    ▲：単穴（たんあな）。場合によっては本命・対抗に勝てるかもしれない3番手のこと。
    △：連下（れんした）。3着以内であれば入れるかもしれない4番手・5番手のこと。

    https://umamusume.cygames.jp/#/help?p=3
    """

    HONNMEI = 1
    TAIKOU = 2
    TANNANA = 3
    RENNSHITA = 4


class TrainingType(enum.Enum):
    UNKNOWN = 0
    SPEED = 1
    STAMINA = 2
    POWER = 3
    GUTS = 4
    WISDOM = 5


@functools.total_ordering
class Mood(enum.Enum):
    VERY_BAD = (0.8, 0.95)
    BAD = (0.9, 0.98)
    NORMAL = (1.0, 1.0)
    GOOD = (1.1, 1.05)
    VERY_GOOD = (1.2, 1.1)

    def __getitem__(self, key: int) -> float:
        import warnings

        warnings.warn(
            "Mood as a tuple is depreacted, use Mood.training_rate or Mood.race_rate instead",
            DeprecationWarning,
        )
        if key == 0:
            return self.value[0]
        if key == 1:
            return self.value[1]
        raise KeyError(key)

    def __lt__(self, other: Mood) -> bool:
        return self.training_rate < other.training_rate

    @property
    def training_rate(self):
        return self.value[0]

    @property
    def race_rate(self):
        return self.value[1]
