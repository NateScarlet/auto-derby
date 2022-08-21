# pyright: strict
# -*- coding=UTF-8 -*-
from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    Optional,
    Protocol,
    Set,
    Text,
    Tuple,
)

from ... import app, data, filetools, mathtools
from ...constants import RunningStyle
from . import race_score, running_style_score
from .globals import g

if TYPE_CHECKING:
    from ..context import Context


class _g:
    estimate_order_cache: Dict[Any, int] = {}
    cache_size = 64


def _estimate_order_cache_key(ctx: Context, race: Race):
    h = hashlib.md5()
    h.update(json.dumps(ctx.to_dict()).encode("utf-8"))
    h.update(json.dumps(race.id).encode("utf-8"))
    return h.digest()


class Course:

    GROUND_TURF = 1
    GROUND_DART = 2

    TRACK_MIDDLE = 1
    TRACK_IN = 2
    TRACK_OUT = 3
    TRACK_OUT_TO_IN = 4

    TURN_RIGHT = 1
    TURN_LEFT = 2
    TURN_NONE = 4

    TARGET_STATUS_SPEED = 1
    TARGET_STATUS_STAMINA = 2
    TARGET_STATUS_POWER = 3
    TARGET_STATUS_GUTS = 4
    TARGET_STATUS_WISDOM = 5

    def __init__(
        self,
        *,
        stadium: Text,
        ground: int,
        distance: int,
        track: int,
        turn: int,
        target_statuses: Tuple[int, ...] = (),
    ) -> None:
        self.stadium = stadium
        self.ground = ground
        self.distance = distance
        self.track = track
        self.turn = turn
        self.target_statuses = target_statuses

    def __str__(self):
        ground_text = {self.GROUND_DART: "dart", self.GROUND_TURF: "turf"}.get(
            self.ground, self.ground
        )
        return f"Course<{self.stadium} {ground_text} {self.distance}m>"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Course):
            return False
        return (
            self.stadium == o.stadium
            and self.distance == o.distance
            and self.ground == o.ground
            and self.track == o.track
            and self.turn == o.turn
            # not compare target status since it doesn't make a course different.
        )

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


class RaceFilters:
    def __init__(
        self,
        *,
        id: Tuple[Text, ...] = (),
        name: Tuple[Text, ...] = (),
        grade: Tuple[int, ...] = (),
    ) -> None:
        self.id = id
        self.name = name
        self.grade = grade


class Repository(Protocol):
    def replace_data(self, it: Iterator[Race], /) -> None:
        ...

    def get(self, id: Text) -> Race:
        ...

    def find(
        self,
        *,
        filter_by: Optional[RaceFilters] = None,
    ) -> Iterator[Race]:
        ...


class Race:

    repository: Repository

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

    @staticmethod
    def new() -> Race:
        return g.race_class()

    def __init__(self):
        self.id = ""
        self.name: Text = ""
        self.permission: int = 0
        self.month: int = 0
        self.half: int = 0
        self.grade: int = 0
        self.entry_count: int = 0
        self.min_fan_count: int = 0

        self.courses: Tuple[Course, ...] = ()
        self.fan_counts: Tuple[int, ...] = ()
        self.characters: Set[Text] = set()
        self.grade_points: Tuple[int, ...] = ()
        self.shop_coins: Tuple[int, ...] = ()

        self.reward_buff = 0.0

    def clone(self) -> Race:
        obj = copy.copy(self)
        return obj

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
        grade_text = {
            Race.GRADE_DEBUT: "Debut",
            Race.GRADE_NOT_WINNING: "Not-Winning",
            Race.GRADE_PRE_OP: "Pre-OP",
            Race.GRADE_OP: "OP",
            Race.GRADE_G3: "G3",
            Race.GRADE_G2: "G2",
            Race.GRADE_G1: "G1",
        }.get(self.grade, self.grade)
        return f"Race<{grade_text} {self.name}#{self.id}>"

    def __eq__(self, o: object) -> bool:
        if not self.id:
            return False
        if not isinstance(o, Race):
            return False
        return self.id == o.id

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

        last = running_style_score.compute(ctx, self, ctx.last, 1.1, 0.995, 0.9)
        middle = running_style_score.compute(ctx, self, ctx.middle, 1.0, 1, 0.95)
        head = running_style_score.compute(ctx, self, ctx.head, 0.8, 0.89, 1.0)
        lead = running_style_score.compute(ctx, self, ctx.lead, 0.5, 0.95, 1.1)

        return last, middle, head, lead

    def style_scores_v2(self, ctx: Context) -> Iterator[Tuple[RunningStyle, float]]:
        last, middle, head, lead = self.style_scores(ctx, _no_warn=True)
        yield RunningStyle.LEAD, lead
        yield RunningStyle.MIDDLE, middle
        yield RunningStyle.HEAD, head
        yield RunningStyle.LAST, last

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
        app.log.text(
            "estimate order: race=%s, order=%d, style_scores=%s"
            % (
                self,
                estimate_order,
                " ".join(f"{i:.2f}" for i in style_scores),
            ),
            level=app.DEBUG,
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

    def is_available(self, ctx: Context) -> Optional[bool]:
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

    def to_snapshot(self):
        return str(self)

    @property
    def _reward_buff_alias(self):
        return self.reward_buff

    @_reward_buff_alias.setter
    def _reward_buff_alias(self, v: float):
        self.reward_buff = v

    @property
    def _deprecated_stadium(self):
        return self.courses[0].stadium

    @property
    def _deprecated_ground(self):
        return self.courses[0].ground

    @property
    def _deprecated_track(self):
        return self.courses[0].track

    @property
    def _deprecated_turn(self):
        return self.courses[0].turn

    @property
    def _deprecated_distance(self):
        return self.courses[0].distance

    def _deprecated_to_dict(self) -> Dict[Text, Any]:
        return {
            "stadium": self._deprecated_stadium,
            "name": self.name,
            "grade": self.grade,
            "ground": self._deprecated_ground,
            "distance": self._deprecated_distance,
            "permission": self.permission,
            "month": self.month,
            "half": self.half,
            "entryCount": self.entry_count,
            "track": self._deprecated_track,
            "turn": self._deprecated_turn,
            "targetStatuses": self._deprecated_target_statuses,
            "minFanCount": self.min_fan_count,
            "fanCounts": self.fan_counts,
            "gradePoints": self.grade_points,
            "shopCoins": self.shop_coins,
            "characters": sorted(self.characters),
        }

    @classmethod
    def _deprecated_from_dict(cls, data: Dict[Text, Any]) -> Race:
        self = cls()
        self.name = data["name"]
        self.permission = data["permission"]
        self.month = data["month"]
        self.half = data["half"]
        self.grade = data["grade"]
        self.entry_count = data["entryCount"]
        self.courses = (
            Course(
                stadium=data["stadium"],
                ground=data["ground"],
                distance=data["course"],
                track=data["track"],
                turn=data["turn"],
                target_statuses=tuple(data["targetStatuses"]),
            ),
        )
        self.min_fan_count = data["minFanCount"]
        self.fan_counts = tuple(data["fanCounts"])
        self.shop_coins = tuple(data.get("shopCoins", []))
        self.grade_points = tuple(data.get("gradePoints", []))
        self.characters = set(data.get("characters", []))
        return self

    def _deprecated_distance_status(self, ctx: Context) -> Tuple[int, Text]:
        return self.courses[0].distance_status(ctx)

    def _deprecated_ground_status(self, ctx: Context) -> Tuple[int, Text]:
        return self.courses[0].ground_status(ctx)

    @property
    def _deprecated_target_statuses(self) -> Tuple[int, ...]:
        return self.courses[0].target_statuses


g.race_class = Race


class JSONLRepository(Repository):
    def __init__(self, path: Text) -> None:
        self.path = path
        self._data: Dict[Text, Race] = {}

    def _raw_iter(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    yield self._from_po(json.loads(line))
        except FileNotFoundError:
            return

    def _iter(self):
        if not self._data:
            self._data = {i.id: i for i in self._raw_iter()}
        yield from self._data.values()

    def _course_to_po(self, do: Course) -> Dict[Text, Any]:
        return {
            "stadium": do.stadium,
            "distance": do.distance,
            "ground": do.ground,
            "track": do.track,
            "turn": do.turn,
            "targetStatuses": do.target_statuses,
        }

    def _to_po(self, do: Race) -> Dict[Text, Any]:
        return {
            "id": do.id,
            "permission": do.permission,
            "month": do.month,
            "half": do.half,
            "grade": do.grade,
            "name": do.name,
            "courses": tuple(self._course_to_po(i) for i in do.courses),
            "entryCount": do.entry_count,
            "minFanCount": do.min_fan_count,
            "fanCounts": do.fan_counts,
            "gradePoints": do.grade_points,
            "shopCoins": do.shop_coins,
            "characters": sorted(do.characters),
            # deprecated fields
            "stadium": do._deprecated_stadium,  # type: ignore
            "distance": do._deprecated_distance,  # type: ignore
            "ground": do._deprecated_ground,  # type: ignore
            "track": do._deprecated_track,  # type: ignore
            "turn": do._deprecated_turn,  # type: ignore
        }

    def _course_from_po(self, po: Dict[Text, Any]) -> Course:

        return Course(
            stadium=po["stadium"],
            ground=po["ground"],
            distance=po["distance"],
            track=po["track"],
            turn=po["turn"],
            target_statuses=tuple(po["targetStatuses"]),
        )

    def _from_po(self, data: Dict[Text, Any]) -> Race:
        do = Race.new()

        do.id = data["id"]
        do.grade = data["grade"]
        do.name = data["name"]
        do.permission = data["permission"]
        do.month = data["month"]
        do.half = data["half"]
        do.grade = data["grade"]
        do.entry_count = data["entryCount"]
        do.courses = tuple(self._course_from_po(i) for i in data["courses"])
        do.min_fan_count = data["minFanCount"]
        do.fan_counts = tuple(data["fanCounts"])
        do.shop_coins = tuple(data.get("shopCoins", []))
        do.grade_points = tuple(data.get("gradePoints", []))
        do.characters = set(data.get("characters", []))
        return do

    def replace_data(self, it: Iterator[Race], /) -> None:
        with filetools.atomic_save_path(self.path) as save_path, open(
            save_path, "w", encoding="utf-8"
        ) as f:
            for i in it:
                json.dump(self._to_po(i), f, ensure_ascii=False)
                f.write("\n")

    def find(
        self,
        *,
        filter_by: Optional[RaceFilters] = None,
    ) -> Iterator[Race]:
        f = filter_by or RaceFilters()
        for do in self._iter():
            if f.name and do.name not in f.name:
                continue
            if f.grade and do.grade not in f.grade:
                continue
            yield do

    def get(self, id: Text) -> Race:
        return self._data[id]


Race.repository = JSONLRepository(data.path("single_mode_races.jsonl"))


# Deprecated members, removal on v2
# spell-checker: disable

Race.turn = Race._deprecated_turn  # type: ignore
Race.stadium = Race._deprecated_stadium  # type: ignore
Race.ground = Race._deprecated_ground  # type: ignore
Race.track = Race._deprecated_track  # type: ignore
Race.turn = Race._deprecated_turn  # type: ignore
Race.distance = Race._deprecated_distance  # type: ignore
Race.distance_status = Race._deprecated_distance_status  # type: ignore
Race.ground_status = Race._deprecated_ground_status  # type: ignore
Race.GROUND_TURF = Course.GROUND_TURF  # type: ignore
Race.GROUND_DART = Course.GROUND_DART  # type: ignore
Race.TRACK_MIDDLE = Course.TRACK_MIDDLE  # type: ignore
Race.TRACK_IN = Course.TRACK_IN  # type: ignore
Race.TRACK_OUT = Course.TRACK_OUT  # type: ignore
Race.TRACK_OUT_TO_IN = Course.TRACK_OUT_TO_IN  # type: ignore
Race.TURN_RIGHT = Course.TURN_RIGHT  # type: ignore
Race.TURN_LEFT = Course.TURN_LEFT  # type: ignore
Race.TURN_NONE = Course.TURN_NONE  # type: ignore
Race.target_statuses = Race._deprecated_target_statuses  # type: ignore
Race.TARGET_STATUS_SPEED = Course.TARGET_STATUS_SPEED  # type: ignore
Race.TARGET_STATUS_STAMINA = Course.TARGET_STATUS_STAMINA  # type: ignore
Race.TARGET_STATUS_POWER = Course.TARGET_STATUS_POWER  # type: ignore
Race.TARGET_STATUS_GUTS = Course.TARGET_STATUS_GUTS  # type: ignore
Race.TARGET_STATUS_WISDOM = Course.TARGET_STATUS_WISDOM  # type: ignore
Race.from_dict = Race._deprecated_from_dict  # type: ignore
Race.to_dict = Race._deprecated_to_dict  # type: ignore


Race.TRACE_OUT_TO_IN = Race.TRACK_OUT_TO_IN  # type: ignore
Race.is_avaliable = Race.is_available  # type: ignore
Race.raward_buff = Race._reward_buff_alias  # type: ignore
