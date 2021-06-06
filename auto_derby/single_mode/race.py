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

from .. import imagetools, ocr, templates, template
from .context import Context

LOGGER = logging.getLogger(__name__)

DATA_PATH = os.getenv(
    "AUTO_DERBY_SINGLE_MODE_RACE_DATA_PATH",
    "single_mode_races.json",
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
        self.name: Text = ''
        self.stadium: Text = ''
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
            "fanCounts": self.fan_counts
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
        ground_text = {
            Race.GROUND_DART: 'dart',
            Race.GROUND_TURF: 'turf',
        }.get(self.ground, self.ground)
        return f"Race<{self.stadium} {ground_text} {self.distance}m {self.name}>"

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
        if (month, half) not in ((i.month, half), (0, 0)):
            continue
        yield i


def _recognize_fan_count(img: PIL.Image.Image) -> int:
    text = ocr.text(PIL.ImageOps.invert(img))
    return int(text.rstrip("人").replace(",", ""))


def _recognize_spec(img: PIL.Image.Image) -> Tuple[Text, int, int, int, int]:
    cv_img = imagetools.cv_image(img.convert("L"))
    _, binary_img = cv2.threshold(
        255 - cv_img,
        150,
        255,
        cv2.THRESH_BINARY,
    )
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
        '左·内': (Race.TURN_LEFT, Race.TRACK_IN),
        '右·内': (Race.TURN_RIGHT, Race.TRACK_IN),
        '左': (Race.TURN_LEFT, Race.TRACK_MIDDLE),
        '右': (Race.TURN_RIGHT, Race.TRACK_MIDDLE),
        '左·外': (Race.TURN_LEFT, Race.TRACK_OUT),
        '右·外': (Race.TURN_RIGHT, Race.TRACK_OUT),
    }[text]

    return stadium, ground, distance, turn, track


def _recognize_grade(rgb_color: Tuple[int, ...]) -> Tuple[int, ...]:
    if imagetools.compare_color((54, 133, 228),  rgb_color) > 0.9:
        return Race.GRADE_G1,
    if imagetools.compare_color((244, 85, 129),  rgb_color) > 0.9:
        return Race.GRADE_G2,
    if imagetools.compare_color((57, 187, 85),  rgb_color) > 0.9:
        return Race.GRADE_G3,
    if imagetools.compare_color((252, 169, 5),  rgb_color) > 0.9:
        return Race.GRADE_OP, Race.GRADE_PRE_OP
    if imagetools.compare_color((148, 203, 8),  rgb_color) > 0.9:
        return Race.GRADE_DEBUT, Race.GRADE_NOT_WINNING
    if imagetools.compare_color((247, 209, 41),  rgb_color) > 0.9:
        # EX(URA)
        return Race.GRADE_G1,
    raise ValueError(
        "_recognize_grade: unknown grade color: %s" % (rgb_color,))


def find_by_race_detail_image(ctx: Context, screenshot: PIL.Image.Image) -> Race:
    grade_color_pos = (10, 75)
    spec_bbox = (27, 260, 302, 279)
    _, no1_fan_count_pos = next(template.match(
        screenshot, templates.NURTURING_RACE_DETAIL_NO1_FAN_COUNT))
    no1_fan_count_bbox = (
        150,
        no1_fan_count_pos[1] + 1,
        400,
        no1_fan_count_pos[1] + 1 + 18,
    )

    grades = _recognize_grade(
        tuple(cast.list_(screenshot.getpixel(grade_color_pos), int)))
    stadium, ground, distance, turn, track = _recognize_spec(
        screenshot.crop(spec_bbox)
    )
    no1_fan_count = _recognize_fan_count(screenshot.crop(no1_fan_count_bbox))

    full_spec = (
        stadium,
        ground,
        distance,
        turn,
        track,
        no1_fan_count,
    )
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

    raise ValueError(
        "find_by_race_details_image: can race match spec: %s",
        full_spec,
    )
