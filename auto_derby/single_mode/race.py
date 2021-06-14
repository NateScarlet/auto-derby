# pyright: strict
# -*- coding=UTF-8 -*-
""".  """
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Iterator, Text, Tuple

import cast_unknown as cast
import cv2
import PIL.Image
import PIL.ImageOps

from .. import imagetools, ocr, templates, template, mathtools
from .context import Context

LOGGER = logging.getLogger(__name__)

DATA_PATH = os.getenv("AUTO_DERBY_SINGLE_MODE_RACE_DATA_PATH", "single_mode_races.json")


def _running_style_single_score(
    ctx: Context,
    race1: Race,
    status: Tuple[int, Text],
    factors: Tuple[int, int, int, int, int],
) -> float:
    assert sum(factors) == 10000, factors
    spd = ctx.speed
    sta = ctx.stamina
    pow = ctx.power
    gut = ctx.guts
    wis = ctx.wisdom

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
    pow *= d_pow_rate

    # 適性が低い作戦で走ろうとすると冷静に走れないことが多い。
    wis *= style_rate

    # バ場適性が合わないバ場を走ると力強さに欠けうまく走れないことが多い。
    pow *= ground_rate

    total_factor = 1
    for i in race1.target_statuses:
        total_factor *= 1 + 0.1 * int(
            {
                race1.TARGET_STATUS_SPEED: spd,
                race1.TARGET_STATUS_POWER: pow,
                race1.TARGET_STATUS_STAMINA: sta,
                race1.TARGET_STATUS_GUTS: gut,
                race1.TARGET_STATUS_WISDOM: wis,
            }[i]
            / 300
        )
    return (
        (
            spd * factors[0]
            + sta * factors[1]
            + pow * factors[2]
            + gut * factors[3]
            + wis * factors[4]
        )
        * total_factor
        / 10000
    )


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

    def to_dict(self) -> Dict[Text, Any]:
        return {
            "name": self.name,
            "stadium": self.stadium,
            "permission": self.permission,
            "month": self.month,
            "half": self.half,
            "grade": self.grade,
            "entryCount": self.entry_count,
            "distance": self.distance,
            "ground": self.ground,
            "track": self.track,
            "turn": self.turn,
            "targetStatuses": self.target_statuses,
            "minFanCount": self.min_fan_count,
            "fanCounts": self.fan_counts,
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
        lead = _running_style_single_score(
            ctx, self, ctx.lead, (5000, 3000, 500, 500, 1000)
        )
        head = _running_style_single_score(
            ctx, self, ctx.head, (4500, 2000, 2000, 500, 1000)
        )
        middle = _running_style_single_score(
            ctx, self, ctx.middle, (4500, 1800, 2000, 200, 1500)
        )
        last = _running_style_single_score(
            ctx, self, ctx.last, (4300, 1500, 2300, 200, 1700)
        )

        if (
            ctx.speed > ctx.turn_count() * 400 / 24
            and self.grade >= self.GRADE_G2
            and self.distance <= 1800
        ):
            lead += 40
        if self.distance >= 2400:
            lead *= 0.9

        return last, middle, head, lead

    def estimate_order(self, ctx: Context) -> int:
        best_style_score = sorted(self.style_scores(ctx), reverse=True)[0]
        difficulty = {
            Race.GRADE_DEBUT: 200,
            Race.GRADE_NOT_WINNING: 200,
            Race.GRADE_PRE_OP: 250,
            Race.GRADE_OP: 250,
            Race.GRADE_G3: 300,
            Race.GRADE_G2: 320,
            Race.GRADE_G1: 350,
        }[self.grade]
        if self.distance_status(ctx) < ctx.STATUS_B:
            difficulty += 120
        if self.ground_status(ctx) < ctx.STATUS_B:
            difficulty += 120
        difficulty = mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, difficulty * 0.8),
                (24, difficulty),
                (48, difficulty * 2),
                (72, difficulty * 2.5),
            ),
        )
        estimate_order = round(
            mathtools.interpolate(
                int(best_style_score * ctx.mood[1] / difficulty * 10000),
                (
                    (5000, 16),
                    (6500, 5),
                    (7000, 3),
                    (9000, 2),
                    (10000, 1),
                ),
            )
        )
        estimate_order = min(self.entry_count, estimate_order)
        LOGGER.debug(
            "estimate order: race=%s, order=%d, difficulty=%d, best_style_score=%.2f",
            self,
            estimate_order,
            difficulty,
            best_style_score,
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
                    (24, 8000),
                    (48, 10000),
                    (54, 100000),
                    (72, 150000),
                ),
            ),
        )

        fan_score = (
            mathtools.integrate(
                ctx.fan_count,
                fan_count,
                (
                    (int(expected_fan_count * 0.1), 8.0),
                    (int(expected_fan_count * 0.3), 6.0),
                    (int(expected_fan_count * 0.5), 4.0),
                    (int(expected_fan_count), 1.0),
                ),
            )
            / 600
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

        return (
            fan_score + prop + skill * 0.5 + not_winning_score - continuous_race_penalty
        )


def _load() -> Tuple[Race, ...]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return tuple(Race.from_dict(i) for i in json.load(f))


RACES = _load()


def find_by_date(date: Tuple[int, int, int]) -> Iterator[Race]:
    year, month, half = date
    for i in RACES:
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
        yield i


def _recognize_fan_count(img: PIL.Image.Image) -> int:
    cv_img = imagetools.cv_image(img.convert("L"))
    cv_img = imagetools.mix(cv_img, imagetools.sharpen(cv_img), 0.5)
    text = ocr.text(imagetools.pil_image(255 - cv_img))
    return int(text.rstrip("人").replace(",", ""))


def _recognize_spec(img: PIL.Image.Image) -> Tuple[Text, int, int, int, int]:
    cv_img = imagetools.cv_image(img.convert("L"))
    _, binary_img = cv2.threshold(255 - cv_img, 150, 255, cv2.THRESH_BINARY)
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
    if imagetools.compare_color((54, 133, 228), rgb_color) > 0.9:
        return (Race.GRADE_G1,)
    if imagetools.compare_color((244, 85, 129), rgb_color) > 0.9:
        return (Race.GRADE_G2,)
    if imagetools.compare_color((57, 187, 85), rgb_color) > 0.9:
        return (Race.GRADE_G3,)
    if imagetools.compare_color((252, 169, 5), rgb_color) > 0.9:
        return Race.GRADE_OP, Race.GRADE_PRE_OP
    if imagetools.compare_color((148, 203, 8), rgb_color) > 0.9:
        return Race.GRADE_DEBUT, Race.GRADE_NOT_WINNING
    if imagetools.compare_color((247, 209, 41), rgb_color) > 0.9:
        # EX(URA)
        return (Race.GRADE_G1,)
    raise ValueError("_recognize_grade: unknown grade color: %s" % (rgb_color,))


def find_by_race_detail_image(ctx: Context, screenshot: PIL.Image.Image) -> Race:
    rp = mathtools.ResizeProxy(screenshot.width)

    grade_color_pos = rp.vector2((10, 75), 466)
    spec_bbox = rp.vector4((27, 260, 302, 279), 466)
    _, no1_fan_count_pos = next(
        template.match(screenshot, templates.SINGLE_MODE_RACE_DETAIL_NO1_FAN_COUNT)
    )
    no1_fan_count_bbox = (
        150,
        no1_fan_count_pos[1] + 1,
        400,
        no1_fan_count_pos[1] + 1 + 18,
    )

    grades = _recognize_grade(
        tuple(cast.list_(screenshot.getpixel(grade_color_pos), int))
    )
    stadium, ground, distance, turn, track = _recognize_spec(screenshot.crop(spec_bbox))
    no1_fan_count = _recognize_fan_count(screenshot.crop(no1_fan_count_bbox))

    full_spec = (stadium, ground, distance, turn, track, no1_fan_count)
    for i in find_by_date(ctx.date):
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
            LOGGER.info("image match: %s", i)
            return i

    raise ValueError("find_by_race_details_image: can race match spec: %s", full_spec)
