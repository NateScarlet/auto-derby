# pyright: strict
# -*- coding=UTF-8 -*-
from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Set, Text, Tuple

from auto_derby.constants import RuningStyle


import hashlib
import json
import logging
import math

from ... import mathtools
from . import race_score, runing_style_score
from .globals import g

if TYPE_CHECKING:
    from ..context import Context

_LOGGER = logging.getLogger(__name__)


class _g:
    estimate_order_cache: Dict[Any, int] = {}
    cache_size = 64


def _estimate_order_cache_key(ctx: Context, race: Race):
    h = hashlib.md5()
    h.update(json.dumps(ctx.to_dict()).encode("utf-8"))
    h.update(json.dumps(race.to_dict()).encode("utf-8"))
    return h.digest()


class Race:

    GROUND_TURF = 1
    GROUND_DART = 2

    TRACK_MIDDLE = 1
    TRACK_IN = 2
    TRACK_OUT = 3
    TRACK_OUT_TO_IN = 4

    TARGET_STATUS_SPEED = 1
    TARGET_STATUS_STAMINA = 2
    TARGET_STATUS_POWER = 3
    TARGET_STATUS_GUTS = 4
    TARGET_STATUS_WISDOM = 5

    PERMISSION_JUNIOR = 1
    PERMISSION_CLASSIC = 2
    PERMISSION_SENIOR_OR_CLASSIC = 3
    PERMISSION_SENIOR = 4
    PERMISSION_URA = 5

    GRADE_DEBUT = 900
    GRADE_NOT_WINNING = 800
    GRADE_PRE_OP = 700
    GRADE_OP = 400
    GRADE_G3 = 300
    GRADE_G2 = 200
    GRADE_G1 = 100

    TURN_RIGHT = 1
    TURN_LEFT = 2
    TURN_NONE = 4

    @staticmethod
    def new() -> Race:
        return g.race_class()

    def __init__(self):
        self.name: Text = ""
        self.stadium: Text = ""
        self.permission: int = 0
        self.month: int = 0
        self.half: int = 0
        self.grade: int = 0
        self.entry_count: int = 0
        self.distance: int = 0
        self.min_fan_count: int = 0

        self.ground: int = 0
        self.track: int = 0
        self.turn: int = 0
        self.target_statuses: Tuple[int, ...] = ()
        self.fan_counts: Tuple[int, ...] = ()
        self.characters: Set[Text] = set()
        self.grade_points: Tuple[int, ...] = ()
        self.shop_coins: Tuple[int, ...] = ()

        self.raward_buff = 0.0

    def clone(self):
        return deepcopy(self)

    def to_dict(self) -> Dict[Text, Any]:
        return {
            "stadium": self.stadium,
            "name": self.name,
            "grade": self.grade,
            "ground": self.ground,
            "distance": self.distance,
            "permission": self.permission,
            "month": self.month,
            "half": self.half,
            "entryCount": self.entry_count,
            "track": self.track,
            "turn": self.turn,
            "targetStatuses": self.target_statuses,
            "minFanCount": self.min_fan_count,
            "fanCounts": self.fan_counts,
            "gradePoints": self.grade_points,
            "shopCoins": self.shop_coins,
            "characters": sorted(self.characters),
        }

    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> Race:
        self = cls()
        self.name = data["name"]
        self.stadium = data["stadium"]
        self.permission = data["permission"]
        self.month = data["month"]
        self.half = data["half"]
        self.grade = data["grade"]
        self.entry_count = data["entryCount"]
        self.distance = data["distance"]
        self.ground = data["ground"]
        self.track = data["track"]
        self.turn = data["turn"]
        self.target_statuses = tuple(data["targetStatuses"])
        self.min_fan_count = data["minFanCount"]
        self.fan_counts = tuple(data["fanCounts"])
        self.shop_coins = tuple(data.get("shopCoins", []))
        self.grade_points = tuple(data.get("gradePoints", []))
        self.characters = set(data.get("characters", []))
        return self

    @property
    def years(self) -> Tuple[int, ...]:
        if self.permission == self.PERMISSION_JUNIOR:
            return (1,)
        if self.permission == self.PERMISSION_CLASSIC:
            return (2,)
        if self.permission == self.PERMISSION_SENIOR_OR_CLASSIC:
            return (2, 3)
        if self.permission == self.PERMISSION_SENIOR:
            return (3,)
        if self.permission == self.PERMISSION_URA:
            return (4,)
        raise ValueError("Race.year: unknown permission: %s" % self.permission)

    def __str__(self):
        ground_text = {Race.GROUND_DART: "dart", Race.GROUND_TURF: "turf"}.get(
            self.ground, self.ground
        )
        grade_text = {
            Race.GRADE_DEBUT: "Debut",
            Race.GRADE_NOT_WINNING: "Not-Winning",
            Race.GRADE_PRE_OP: "Pre-OP",
            Race.GRADE_OP: "OP",
            Race.GRADE_G3: "G3",
            Race.GRADE_G2: "G2",
            Race.GRADE_G1: "G1",
        }.get(self.grade, self.grade)
        return f"Race<{self.stadium} {ground_text} {self.distance}m {grade_text} {self.name}>"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Race):
            return False
        return self.to_dict() == o.to_dict()

    def distance_status(self, ctx: Context) -> Tuple[int, Text]:
        if self.distance <= 1400:
            return ctx.sprint
        elif self.distance <= 1800:
            return ctx.mile
        elif self.distance <= 2400:
            return ctx.intermediate
        else:
            return ctx.long

    def ground_status(self, ctx: Context) -> Tuple[int, Text]:
        if self.ground == self.GROUND_TURF:
            return ctx.turf
        else:
            return ctx.dart

    def style_scores(
        self,
        ctx: Context,
        *,
        _no_warn: bool = False,
    ) -> Tuple[float, float, float, float]:
        if not _no_warn:
            # TODO: remove old api at next major version
            import warnings

            warnings.warn(
                "use style_scores_v2 instead",
                DeprecationWarning,
            )

        last = runing_style_score.compute(ctx, self, ctx.last, 1.1, 0.995, 0.9)
        middle = runing_style_score.compute(ctx, self, ctx.middle, 1.0, 1, 0.95)
        head = runing_style_score.compute(ctx, self, ctx.head, 0.8, 0.89, 1.0)
        lead = runing_style_score.compute(ctx, self, ctx.lead, 0.5, 0.95, 1.1)

        return last, middle, head, lead

    def style_scores_v2(self, ctx: Context) -> Iterator[Tuple[RuningStyle, float]]:
        last, middle, head, lead = self.style_scores(ctx, _no_warn=True)
        yield RuningStyle.LEAD, lead
        yield RuningStyle.MIDDLE, middle
        yield RuningStyle.HEAD, head
        yield RuningStyle.LAST, last

    def _raw_estimate_order(self, ctx: Context) -> int:
        style_scores = tuple(i for _, i in self.style_scores_v2(ctx))
        best_style_score = sorted(style_scores, reverse=True)[0]
        estimate_order = math.ceil(
            mathtools.interpolate(
                int(best_style_score),
                (
                    (0, 100),
                    (5000, self.entry_count * 0.5),
                    (6500, 5),
                    (7000, 3),
                    (9000, 2),
                    (10000, 1),
                ),
            )
        )
        estimate_order = min(self.entry_count, estimate_order)
        _LOGGER.debug(
            "estimate order: race=%s, order=%d, style_scores=%s",
            self,
            estimate_order,
            " ".join(f"{i:.2f}" for i in style_scores),
        )
        return estimate_order

    def estimate_order(self, ctx: Context) -> int:
        key = _estimate_order_cache_key(ctx, self)
        if key not in _g.estimate_order_cache:
            if len(_g.estimate_order_cache) >= _g.cache_size:
                _g.estimate_order_cache.clear()
            _g.estimate_order_cache[key] = self._raw_estimate_order(ctx)
        return _g.estimate_order_cache[key]

    def score(self, ctx: Context) -> float:
        return race_score.compute(ctx, self)

    def is_target_race(self, ctx: Context) -> Optional[bool]:
        """return None when result is unknown."""

        if not self.characters:
            return None
        if len(self.characters) < 10:
            return True

    def is_avaliable(self, ctx: Context) -> Optional[bool]:
        """return None when result is unknown."""

        if ctx.date == (1, 0, 0) and self.grade != self.GRADE_DEBUT:
            return False
        if ctx.date[1:] not in ((self.month, self.half), (0, 0)):
            return False
        if ctx.date[0] not in self.years:
            return False
        if self.grade == Race.GRADE_NOT_WINNING:
            return not ctx.is_after_winning or ctx.fan_count == 1
        if self.grade < Race.GRADE_NOT_WINNING and not ctx.is_after_winning:
            return False
        if ctx.fan_count < self.min_fan_count:
            return False


g.race_class = Race


# Deprecated members, removal on v2
Race.TRACE_OUT_TO_IN = Race.TRACK_OUT_TO_IN  # type: ignore
