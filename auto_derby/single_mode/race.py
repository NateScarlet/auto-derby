# pyright: strict
# -*- coding=UTF-8 -*-
from __future__ import annotations

import json
import logging
import math
import os
import warnings
from typing import Any, Dict, Iterator, Optional, Set, Text, Tuple, Type

import cast_unknown as cast
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps

from .. import imagetools, mathtools, ocr, template, templates
from .context import Context

LOGGER = logging.getLogger(__name__)


class g:
    data_path: str = ""
    races: Tuple[Race, ...] = ()
    race_class: Type[Race]


class _g:
    loaded_data_path = ""


def _iter_races():
    with open(g.data_path, "r", encoding="utf-8") as f:
        for line in f:
            yield Race.new().from_dict(json.loads(line))


def _load_legacy_json():
    warnings.warn(
        "json race data support will be removed at next major version, use jsonl instead",
        DeprecationWarning,
    )
    with open(g.data_path, "r", encoding="utf-8") as f:
        g.races = tuple(Race.new().from_dict(i) for i in json.load(f))


def reload() -> None:
    if g.data_path.endswith(".json"):
        _load_legacy_json()
        return
    g.races = tuple(_iter_races())
    _g.loaded_data_path = g.data_path


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()


def _running_style_single_score(
    ctx: Context,
    race1: Race,
    status: Tuple[int, Text],
    block_factor: float,
    hp_factor: float,
    wisdom_factor: float,
) -> float:
    """Score standard:

    No1 P90: 10000
    No2 P90: 9000
    No3 P90: 7000
    No5 P90: 6500
    50% P90: 5000
    """
    spd = ctx.speed
    sta = ctx.stamina
    pow_ = ctx.power
    gut = ctx.guts
    wis = ctx.wisdom

    spd *= ctx.mood[1]
    sta *= ctx.mood[1]
    pow_ *= ctx.mood[1]
    gut *= ctx.mood[1]
    wis *= ctx.mood[1]

    base_speed_coefficient = 1
    for i in race1.target_statuses:
        base_speed_coefficient *= 1 + 0.1 * min(
            2,
            int(
                {
                    race1.TARGET_STATUS_SPEED: ctx.speed,
                    race1.TARGET_STATUS_POWER: ctx.power,
                    race1.TARGET_STATUS_STAMINA: ctx.stamina,
                    race1.TARGET_STATUS_GUTS: ctx.guts,
                    race1.TARGET_STATUS_WISDOM: ctx.wisdom,
                }[i]
                / 300
            ),
        )
    spd *= base_speed_coefficient

    # TODO: race field affect

    # https://bbs.nga.cn/read.php?tid=26010713
    single_mode_bonus = 400
    spd += single_mode_bonus
    sta += single_mode_bonus
    pow_ += single_mode_bonus
    gut += single_mode_bonus
    wis += single_mode_bonus

    # proper ground
    # from master.mdb `race_proper_ground_rate` table
    ground = race1.ground_status(ctx)
    ground_rate = {
        "S": 1.05,
        "A": 1.0,
        "B": 0.9,
        "C": 0.8,
        "D": 0.7,
        "E": 0.5,
        "F": 0.3,
        "G": 0.1,
    }[ground[1]]

    # proper distance
    # from master.mdb `race_proper_distance_rate` table
    distance = race1.distance_status(ctx)
    d_spd_rate, d_pow_rate = {
        "S": (1.05, 1.0),
        "A": (1.0, 1.0),
        "B": (0.9, 1.0),
        "C": (0.8, 1.0),
        "D": (0.6, 1.0),
        "E": (0.4, 0.6),
        "F": (0.2, 0.5),
        "G": (0.1, 0.4),
    }[distance[1]]

    # proper running style
    # from master.mdb `race_proper_runningstyle_rate` table

    style_rate = {
        "S": 1.1,
        "A": 1.0,
        "B": 0.85,
        "C": 0.75,
        "D": 0.6,
        "E": 0.4,
        "F": 0.2,
        "G": 0.1,
    }[status[1]]

    # https://umamusume.cygames.jp/#/help?p=3

    # 距離適性が低い距離のコースを走るとうまくスピードに乗れず、上位争いをすることが難しいことが多い。
    spd *= d_spd_rate
    pow_ *= d_pow_rate

    # 適性が低い作戦で走ろうとすると冷静に走れないことが多い。
    wis *= style_rate

    # バ場適性が合わないバ場を走ると力強さに欠けうまく走れないことが多い。
    pow_ *= ground_rate

    sta *= hp_factor
    wis *= wisdom_factor

    gut_as_sta = mathtools.interpolate(
        int(gut),
        (
            (0, 0),
            (1200, 100),
            (1600, 150),
        ),
    )
    sta += gut_as_sta
    wis_as_spd = mathtools.interpolate(
        int(gut),
        (
            (0, 0),
            (900, 200),
            (1600, 350),
        ),
    )
    spd += wis_as_spd
    wis_as_sta = mathtools.interpolate(
        int(gut),
        (
            (0, 0),
            (900, 100),
            (1600, 200),
        ),
    )
    sta += wis_as_sta

    hp = race1.distance + hp_factor * 0.8 * sta
    expected_spd = (
        mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 700),
                (24, 700),
                (48, 900),
                (72, 1100),
            ),
        )
        * {
            Race.GRADE_G1: 1,
            Race.GRADE_G2: 0.9,
            Race.GRADE_G3: 0.8,
            Race.GRADE_PRE_OP: 0.7,
            Race.GRADE_OP: 0.7,
            Race.GRADE_NOT_WINNING: 0.6,
            Race.GRADE_DEBUT: 0.6,
        }[race1.grade]
        * mathtools.interpolate(
            race1.distance,
            (
                (0, 1.1),
                (1200, 1.05),
                (1600, 1.0),
                (3200, 0.9),
            ),
        )
    )
    expected_hp = (
        race1.distance
        * mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 1.0),
                (24, 1.4),
                (48, 1.6),
                (72, 1.8),
                (75, 2.0),
            ),
        )
        * {
            Race.GRADE_G1: 1,
            Race.GRADE_G2: 0.9,
            Race.GRADE_G3: 0.85,
            Race.GRADE_PRE_OP: 0.8,
            Race.GRADE_OP: 0.8,
            Race.GRADE_NOT_WINNING: 0.7,
            Race.GRADE_DEBUT: 0.7,
        }[race1.grade]
    )
    expected_pow = (
        mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 550),
                (24, 700),
                (48, 850),
                (72, 1000),
            ),
        )
        * mathtools.interpolate(
            race1.distance,
            (
                (0, 0.8),
                (1600, 1),
                (3200, 1.2),
                (4800, 1.4),
            ),
        )
        * {
            Race.GRADE_G1: 1,
            Race.GRADE_G2: 0.95,
            Race.GRADE_G3: 0.9,
            Race.GRADE_PRE_OP: 0.8,
            Race.GRADE_OP: 0.8,
            Race.GRADE_NOT_WINNING: 0.6,
            Race.GRADE_DEBUT: 0.6,
        }[race1.grade]
    )

    expected_wis = mathtools.interpolate(
        ctx.turn_count(),
        (
            (0, 500),
            (24, 650),
            (48, 700),
            (72, 750),
        ),
    )

    block_rate = (
        mathtools.interpolate(
            int(pow_ / expected_pow * 10000),
            (
                (0, 10.0),
                (6000, 1.0),
                (7000, 0.6),
                (8000, 0.4),
                (10000, 0.1),
                (12000, 0.01),
            ),
        )
        * mathtools.interpolate(
            int(spd / expected_spd * 10000),
            (
                (6000, 10.0),
                (8000, 2.0),
                (10000, 1.0),
                (12000, 0.8),
            ),
        )
        * mathtools.interpolate(
            race1.distance,
            (
                (0, 2.0),
                (1200, 2.0),
                (2000, 1.0),
                (3200, 0.6),
            ),
        )
        * block_factor
    )
    block_rate = min(1.0, block_rate)
    block_penality = mathtools.interpolate(
        int(block_rate * 10000),
        (
            (0, 0),
            (1000, 0.2),
            (2000, 0.5),
            (3000, 0.7),
        ),
    )

    hp_penality = mathtools.interpolate(
        int(hp / expected_hp * 10000),
        (
            (0, 1.0),
            (5000, 0.6),
            (8000, 0.4),
            (9000, 0.2),
            (10000, 0),
        ),
    )
    hp_penality = min(1, hp_penality)

    wis_penality = mathtools.interpolate(
        int(wis / expected_wis * 10000),
        (
            (0, 0.3),
            (7000, 0.2),
            (9000, 0.1),
            (10000, 0.0),
        ),
    )

    ret = spd / expected_spd * 10000
    ret *= 1 - block_penality
    ret *= 1 - hp_penality
    ret *= 1 - wis_penality

    LOGGER.debug(
        (
            "style: "
            "score=%d "
            "block_rate=%.2f "
            "block_penality=%.2f "
            "hp_penality=%0.2f "
            "wis_penality=%0.2f "
            "spd=%0.2f/%0.2f "
            "sta=%0.2f "
            "hp=%0.2f/%0.2f "
            "pow=%0.2f/%0.2f "
            "gut=%0.2f "
            "wis=%0.2f"
        ),
        ret,
        block_rate,
        block_penality,
        hp_penality,
        wis_penality,
        spd,
        expected_spd,
        sta,
        hp,
        expected_hp,
        pow_,
        expected_pow,
        gut,
        wis,
    )
    return ret


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
        last = _running_style_single_score(ctx, self, ctx.last, 1.1, 0.995, 0.9)
        middle = _running_style_single_score(ctx, self, ctx.middle, 1.0, 1, 0.95)
        head = _running_style_single_score(ctx, self, ctx.head, 0.8, 0.89, 1.0)
        lead = _running_style_single_score(ctx, self, ctx.lead, 0.5, 0.95, 1.1)

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
        LOGGER.debug(
            "estimate order: race=%s, order=%d, style_scores=%s",
            self,
            estimate_order,
            " ".join(f"{i:.2f}" for i in style_scores),
        )
        return estimate_order

    def score(self, ctx: Context) -> float:
        estimate_order = self.estimate_order(ctx)
        if estimate_order == 1:
            prop, skill = {
                Race.GRADE_G1: (10, 45),
                Race.GRADE_G2: (8, 35),
                Race.GRADE_G3: (8, 35),
                Race.GRADE_OP: (5, 35),
                Race.GRADE_PRE_OP: (5, 35),
                Race.GRADE_NOT_WINNING: (0, 0),
                Race.GRADE_DEBUT: (0, 0),
            }[self.grade]
        elif 2 <= estimate_order <= 5:
            prop, skill = {
                Race.GRADE_G1: (5, 40),
                Race.GRADE_G2: (4, 30),
                Race.GRADE_G3: (4, 30),
                Race.GRADE_OP: (2, 20),
                Race.GRADE_PRE_OP: (2, 20),
                Race.GRADE_NOT_WINNING: (0, 0),
                Race.GRADE_DEBUT: (0, 0),
            }[self.grade]
        else:
            prop, skill = {
                Race.GRADE_G1: (4, 25),
                Race.GRADE_G2: (3, 20),
                Race.GRADE_G3: (3, 20),
                Race.GRADE_OP: (0, 10),
                Race.GRADE_PRE_OP: (0, 10),
                Race.GRADE_NOT_WINNING: (0, 0),
                Race.GRADE_DEBUT: (0, 0),
            }[self.grade]

        fan_count = self.fan_counts[estimate_order - 1]

        expected_fan_count = max(
            ctx.target_fan_count,
            mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 0),
                    # 朝日杯フューチュリティステークス
                    (18, 1000),
                    # 皐月賞
                    (30, 4500),
                    # 有馬記念
                    (46, 25000),
                    # valentine
                    (50, 60000),
                    # chrisman's
                    (71, 120000),
                ),
            ),
        )

        fan_score = mathtools.integrate(
            ctx.fan_count,
            fan_count,
            (
                (int(expected_fan_count * 0.1), 8.0),
                (int(expected_fan_count * 0.3), 6.0),
                (int(expected_fan_count * 0.5), 4.0),
                (int(expected_fan_count), 1.0),
            ),
        ) / mathtools.interpolate(
            ctx.speed,
            (
                (0, 2400),
                (300, 1800),
                (600, 800),
                (900, 600),
            ),
        )

        not_winning_score = 0 if ctx.is_after_winning else 1.5 * ctx.turn_count()

        continuous_race_penalty = mathtools.interpolate(
            ctx.continuous_race_count(),
            (
                (2, 0),
                (3, 5),
                (4, 25),
                (5, 50),
            ),
        )
        fail_penalty = mathtools.interpolate(
            estimate_order,
            (
                (5, 0),
                (6, 5),
                (12, 15),
            ),
        )

        status_penality = 0
        if self.distance_status(ctx) < ctx.STATUS_B:
            status_penality += 10
        if self.ground_status(ctx) < ctx.STATUS_B:
            status_penality += 10

        return (
            fan_score
            + prop
            + skill * 0.5
            + not_winning_score
            - continuous_race_penalty
            - fail_penalty
            - status_penality
        )

    def is_target_race(self, ctx: Context) -> Optional[bool]:
        """return None when result is unknown."""

        if not self.characters:
            return None
        if len(self.characters) < 10:
            return True


g.race_class = Race


def find_by_date(date: Tuple[int, int, int]) -> Iterator[Race]:
    reload_on_demand()
    year, month, half = date
    for i in g.races:
        if year not in i.years:
            continue
        if date == (1, 0, 0) and i.grade != Race.GRADE_DEBUT:
            continue
        if (month, half) not in ((i.month, i.half), (0, 0)):
            continue
        yield i


def find(ctx: Context) -> Iterator[Race]:
    if ctx.date[1:] == (0, 0):
        return
    for i in find_by_date(ctx.date):
        if i.grade == Race.GRADE_NOT_WINNING and (
            ctx.is_after_winning or ctx.fan_count == 1
        ):
            continue
        if i.grade < Race.GRADE_NOT_WINNING and not ctx.is_after_winning:
            continue
        if ctx.fan_count < i.min_fan_count:
            continue
        # target race should be excluded when finding available race
        if i.is_target_race(ctx):
            continue
        yield i


def _recognize_fan_count(img: PIL.Image.Image) -> int:
    cv_img = imagetools.cv_image(imagetools.resize(img.convert("L"), height=32))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 60, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text.rstrip("人").replace(",", ""))


def _recognize_spec(img: PIL.Image.Image) -> Tuple[Text, int, int, int, int]:
    cv_img = imagetools.cv_image(imagetools.resize(img.convert("L"), height=32))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 60, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    stadium, text = text[:2], text[2:]
    if text[0] == "芝":
        text = text[1:]
        ground = Race.GROUND_TURF
    elif text[0] == "ダ":
        text = text[3:]
        ground = Race.GROUND_DART
    else:
        raise ValueError("_recognize_spec: invalid spec: %s", text)

    distance, text = int(text[:4]), text[10:]

    turn, track = {
        "左·内": (Race.TURN_LEFT, Race.TRACK_IN),
        "右·内": (Race.TURN_RIGHT, Race.TRACK_IN),
        "左": (Race.TURN_LEFT, Race.TRACK_MIDDLE),
        "右": (Race.TURN_RIGHT, Race.TRACK_MIDDLE),
        "左·外": (Race.TURN_LEFT, Race.TRACK_OUT),
        "右·外": (Race.TURN_RIGHT, Race.TRACK_OUT),
        "直線": (Race.TURN_NONE, Race.TRACK_MIDDLE),
    }[text]

    return stadium, ground, distance, turn, track


def _recognize_grade(rgb_color: Tuple[int, ...]) -> Tuple[int, ...]:
    if imagetools.compare_color((247, 209, 41), rgb_color) > 0.9:
        # EX(URA)
        return (Race.GRADE_G1,)
    if imagetools.compare_color((54, 133, 228), rgb_color) > 0.8:
        return (Race.GRADE_G1,)
    if imagetools.compare_color((244, 85, 129), rgb_color) > 0.8:
        return (Race.GRADE_G2,)
    if imagetools.compare_color((57, 187, 85), rgb_color) > 0.8:
        return (Race.GRADE_G3,)
    if imagetools.compare_color((252, 169, 5), rgb_color) > 0.8:
        return Race.GRADE_OP, Race.GRADE_PRE_OP
    if imagetools.compare_color((148, 203, 8), rgb_color) > 0.8:
        return Race.GRADE_DEBUT, Race.GRADE_NOT_WINNING
    raise ValueError("_recognize_grade: unknown grade color: %s" % (rgb_color,))


def _find_by_spec(
    date: Tuple[int, int, int],
    stadium: Text,
    ground: int,
    distance: int,
    turn: int,
    track: int,
    no1_fan_count: int,
    grades: Tuple[int, ...],
):
    full_spec = (stadium, ground, distance, turn, track, no1_fan_count)
    for i in find_by_date(date):
        if i.grade not in grades:
            continue
        if full_spec == (
            i.stadium,
            i.ground,
            i.distance,
            i.turn,
            i.track,
            i.fan_counts[0],
        ):
            yield i


def find_by_race_detail_image(ctx: Context, screenshot: PIL.Image.Image) -> Race:
    rp = mathtools.ResizeProxy(screenshot.width)

    grade_color_pos = rp.vector2((10, 75), 466)
    spec_bbox = rp.vector4((27, 260, 302, 279), 466)
    _, no1_fan_count_pos = next(
        template.match(screenshot, templates.SINGLE_MODE_RACE_DETAIL_NO1_FAN_COUNT)
    )
    no1_fan_count_bbox = (
        rp.vector(150, 466),
        no1_fan_count_pos[1],
        rp.vector(400, 466),
        no1_fan_count_pos[1] + rp.vector(18, 466),
    )

    grades = _recognize_grade(
        tuple(cast.list_(screenshot.getpixel(grade_color_pos), int))
    )
    stadium, ground, distance, turn, track = _recognize_spec(screenshot.crop(spec_bbox))
    no1_fan_count = _recognize_fan_count(screenshot.crop(no1_fan_count_bbox))

    full_spec = (
        ctx.date,
        stadium,
        ground,
        distance,
        turn,
        track,
        no1_fan_count,
        grades,
    )
    for i in _find_by_spec(*full_spec):
        LOGGER.info("image match: %s", i)
        return i

    raise ValueError("find_by_race_details_image: no race match spec: %s", full_spec)


def _find_by_race_menu_item(ctx: Context, img: PIL.Image.Image) -> Iterator[Race]:
    rp = mathtools.ResizeProxy(img.width)
    spec_bbox = rp.vector4((221, 12, 478, 32), 492)
    no1_fan_count_bbox = rp.vector4((207, 54, 360, 72), 492)
    grade_color_pos = rp.vector2((182, 14), 492)

    stadium, ground, distance, turn, track = _recognize_spec(img.crop(spec_bbox))
    no1_fan_count = _recognize_fan_count(img.crop(no1_fan_count_bbox))
    grades = _recognize_grade(tuple(cast.list_(img.getpixel(grade_color_pos), int)))
    full_spec = (
        ctx.date,
        stadium,
        ground,
        distance,
        turn,
        track,
        no1_fan_count,
        grades,
    )
    match_count = 0
    for i in _find_by_spec(*full_spec):
        LOGGER.info("image match: %s", i)
        yield i
        match_count += 1
    if not match_count:
        raise ValueError("_find_by_race_menu_item: no race match spec: %s", full_spec)


def find_by_race_menu_image(
    ctx: Context, screenshot: PIL.Image.Image
) -> Iterator[Tuple[Race, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(screenshot.width)
    for _, pos in template.match(screenshot, templates.SINGLE_MODE_RACE_MENU_FAN_ICON):
        _, y = pos
        bbox = (
            rp.vector(23, 540),
            y - rp.vector(51, 540),
            rp.vector(515, 540),
            y + rp.vector(46, 540),
        )
        for i in _find_by_race_menu_item(ctx, screenshot.crop(bbox)):
            yield i, pos
