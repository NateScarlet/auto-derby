# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import enum


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
