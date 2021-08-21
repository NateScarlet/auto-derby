# pyright: strict
# -*- coding=UTF-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Text, Tuple

if TYPE_CHECKING:
    from ..context import Context

import logging
import math

from ... import mathtools
from . import race_score, runing_style_score
from .globals import g

_LOGGER = logging.getLogger(__name__)


class Race:

    GROUND_TURF = 1
    GROUND_DART = 2

    TRACK_MIDDLE = 1
    TRACK_IN = 2
    TRACK_OUT = 3

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
    ) -> Tuple[float, float, float, float]:
        last = runing_style_score.compute(ctx, self, ctx.last, 1.1, 0.995, 0.9)
        middle = runing_style_score.compute(ctx, self, ctx.middle, 1.0, 1, 0.95)
        head = runing_style_score.compute(ctx, self, ctx.head, 0.8, 0.89, 1.0)
        lead = runing_style_score.compute(ctx, self, ctx.lead, 0.5, 0.95, 1.1)

        return last, middle, head, lead

    def estimate_order(self, ctx: Context) -> int:
        style_scores = self.style_scores(ctx)
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

    def score(self, ctx: Context) -> float:
        return race_score.compute(ctx, self)

    def is_target_race(self, ctx: Context) -> Optional[bool]:
        """return None when result is unknown."""

        if not self.characters:
            return None
        if len(self.characters) < 10:
            return True


g.race_class = Race
