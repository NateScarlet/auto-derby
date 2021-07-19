# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import functools
import os
from typing import Callable, List, Set, Text, Tuple, Type

import cast_unknown as cast
import cv2
import numpy as np
from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from .. import imagetools, mathtools, ocr, template, templates


class g:
    context_class: Type[Context]


def _ocr_date(img: Image) -> Tuple[int, int, int]:
    img = imagetools.resize(img, height=32)
    cv_img = np.asarray(img.convert("L"))
    cv_img = imagetools.level(
        cv_img,
        np.array(10),
        np.array(240),
    )
    sharpened_img = imagetools.sharpen(cv_img)
    sharpened_img = imagetools.mix(sharpened_img, cv_img, 0.5)
    _, binary_img = cv2.threshold(sharpened_img, 120, 255, cv2.THRESH_BINARY_INV)
    imagetools.fill_area(binary_img, (0,), size_lt=2)

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("sharpened_img", sharpened_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(image_from_array(binary_img))

    if text == "ジュニア級デビュー前":
        return (1, 0, 0)
    if text == "ファイナルズ開催中":
        return (4, 0, 0)
    year_end = text.index("級") + 1
    month_end = year_end + text[year_end:].index("月") + 1
    year_text = text[:year_end]
    month_text = text[year_end:month_end]
    date_text = text[month_end:]

    year = {"ジュニア級": 1, "クラシック級": 2, "シニア級": 3}[year_text]
    month = int(month_text[:-1])
    date = {"前半": 1, "後半": 2}[date_text]
    return (year, month, date)


def _recognize_vitality(img: Image) -> float:
    cv_img = np.asarray(img)

    def _is_empty(v: np.ndarray) -> bool:
        assert v.shape == (3,), v.shape
        return (
            imagetools.compare_color((118, 117, 118), (int(v[0]), int(v[1]), int(v[2])))
            > 0.99
        )

    return 1 - np.average(np.apply_along_axis(_is_empty, 1, cv_img[0, :]))


def _recognize_mood(rgb_color: Tuple[int, int, int]) -> Tuple[float, float]:
    if imagetools.compare_color((250, 68, 126), rgb_color) > 0.9:
        return Context.MOOD_VERY_GOOD
    if imagetools.compare_color((255, 124, 57), rgb_color) > 0.9:
        return Context.MOOD_GOOD
    if imagetools.compare_color((255, 162, 0), rgb_color) > 0.9:
        return Context.MOOD_NORMAL
    if imagetools.compare_color((16, 136, 247), rgb_color) > 0.9:
        return Context.MOOD_BAD
    if imagetools.compare_color((170, 81, 255), rgb_color) > 0.9:
        return Context.MOOD_VERY_BAD
    raise ValueError("_recognize_mood: unknown mood color: %s" % (rgb_color,))


def _recognize_fan_count(img: Image) -> int:
    cv_img = imagetools.cv_image(img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text.rstrip("人").replace(",", ""))


def _recognize_status(img: Image) -> Tuple[int, Text]:
    cv_img = imagetools.cv_image(imagetools.resize(img.convert("L"), height=64))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 5), np.percentile(cv_img, 95)
    )
    cv_img = cv2.copyMakeBorder(cv_img, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255,))

    blurred_img = cv2.medianBlur(cv_img, 7)

    text_img = cv2.adaptiveThreshold(
        blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -1
    )
    text_img = 255 - cast.instance(
        np.maximum(text_img, imagetools.border_flood_fill(text_img)), np.ndarray
    )
    text_img = cv2.medianBlur(text_img, 5)
    h = cv_img.shape[0]
    imagetools.fill_area(
        text_img, (0,), mode=cv2.RETR_LIST, size_lt=round(h * 0.2 ** 2)
    )

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("blurred_img", blurred_img)
        cv2.imshow("text_img", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(imagetools.pil_image(text_img))
    for i in Context.ALL_STATUSES:
        if i[1] == text:
            return i

    raise ValueError("_recognize_status: unknown status: %s" % text)


def _recognize_property(img: Image) -> int:
    img = imagetools.resize(img, height=32)
    max_match = imagetools.constant_color_key(
        imagetools.cv_image(img),
        (210, 249, 255),
        threshold=0.95,
    )
    if np.average(max_match) > 5:
        return 1200

    cv_img = np.asarray(img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 160, 255, cv2.THRESH_BINARY_INV)
    imagetools.fill_area(binary_img, (0,), size_lt=3)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return int(ocr.text(imagetools.pil_image(binary_img)))


class Context:
    MOOD_VERY_BAD = (0.8, 0.95)
    MOOD_BAD = (0.9, 0.98)
    MOOD_NORMAL = (1.0, 1.0)
    MOOD_GOOD = (1.1, 1.05)
    MOOD_VERY_GOOD = (1.2, 1.1)

    CONDITION_HEADACHE = 1 << 0
    CONDITION_OVERWEIGHT = 1 << 1

    STATUS_S = (8, "S")
    STATUS_A = (7, "A")
    STATUS_B = (6, "B")
    STATUS_C = (5, "C")
    STATUS_D = (4, "D")
    STATUS_E = (3, "E")
    STATUS_F = (2, "F")
    STATUS_G = (1, "G")
    STATUS_NONE: Tuple[int, Text] = (0, "")

    ALL_STATUSES = (
        STATUS_S,
        STATUS_A,
        STATUS_B,
        STATUS_C,
        STATUS_D,
        STATUS_E,
        STATUS_F,
        STATUS_G,
    )

    @staticmethod
    def new() -> Context:
        return g.context_class()

    def __init__(self) -> None:
        self.speed = 0
        self.stamina = 0
        self.power = 0
        self.guts = 0
        self.wisdom = 0
        # (year, month, half-month), 1-base
        self.date = (0, 0, 0)
        self.vitality = 0.0
        self.mood = Context.MOOD_NORMAL
        self.conditions: Set[int] = set()
        self.fan_count = 0
        self.is_after_winning = False

        self._extra_turn_count = 0
        self.target_fan_count = 0
        self.race_turns: Set[int] = set()

        self.turf = Context.STATUS_NONE
        self.dart = Context.STATUS_NONE

        # Distance statuses
        # https://umamusume.cygames.jp/#/help?p=3
        # 短距離：1400m以下
        self.sprint = Context.STATUS_NONE
        # マイル：1401m～1800m
        self.mile = Context.STATUS_NONE
        # 中距離：1801m～2400m
        self.intermediate = Context.STATUS_NONE
        # 長距離：2401m以上
        self.long = Context.STATUS_NONE

        # Runing style status
        # https://umamusume.cygames.jp/#/help?p=3
        # 作戦には以下の4つがあります。
        # ・逃げ：スタート直後から先頭に立ち、そのまま最後まで逃げ切る作戦。
        self.lead = Context.STATUS_NONE
        # ・先行：なるべく前に付けて、先頭を狙っていく作戦。
        self.head = Context.STATUS_NONE
        # ・差し：後方につけ、レース後半に加速して先頭に立つ作戦。
        self.middle = Context.STATUS_NONE
        # ・追込：最後方に控え、最後に勝負をかける作戦。
        self.last = Context.STATUS_NONE

        self._next_turn_cb: List[Callable[[], None]] = []

    def next_turn(self) -> None:
        if self.date in ((1, 0, 0), (4, 0, 0)):
            self._extra_turn_count += 1
        else:
            self._extra_turn_count = 0

        while self._next_turn_cb:
            self._next_turn_cb.pop()()

    def defer_next_turn(self, cb: Callable[[], None]) -> None:
        self._next_turn_cb.append(cb)

    def update_by_command_scene(self, screenshot: Image) -> None:
        rp = mathtools.ResizeProxy(screenshot.width)
        date_bbox = rp.vector4((10, 27, 140, 43), 466)
        vitality_bbox = rp.vector4((148, 106, 327, 108), 466)

        _, detail_button_pos = next(
            template.match(screenshot, templates.SINGLE_MODE_CHARACTER_DETAIL_BUTTON)
        )
        base_y = detail_button_pos[1] + rp.vector(71, 466)
        t, b = base_y, base_y + rp.vector(19, 466)
        speed_bbox = (rp.vector(45, 466), t, rp.vector(90, 466), b)
        stamina_bbox = (rp.vector(125, 466), t, rp.vector(162, 466), b)
        power_bbox = (rp.vector(192, 466), t, rp.vector(234, 466), b)
        guts_bbox = (rp.vector(264, 466), t, rp.vector(308, 466), b)
        wisdom_bbox = (rp.vector(337, 466), t, rp.vector(381, 466), b)

        self.date = _ocr_date(screenshot.crop(date_bbox))

        self.vitality = _recognize_vitality(screenshot.crop(vitality_bbox))

        mood_color = screenshot.getpixel(rp.vector2((395, 113), 466))
        assert isinstance(mood_color, tuple), mood_color
        self.mood = _recognize_mood((mood_color[0], mood_color[1], mood_color[2]))

        self.speed = _recognize_property(screenshot.crop(speed_bbox))
        self.stamina = _recognize_property(screenshot.crop(stamina_bbox))
        self.power = _recognize_property(screenshot.crop(power_bbox))
        self.guts = _recognize_property(screenshot.crop(guts_bbox))
        self.wisdom = _recognize_property(screenshot.crop(wisdom_bbox))

    def update_by_class_detail(self, screenshot: Image) -> None:
        rp = mathtools.ResizeProxy(screenshot.width)
        winning_color_pos = rp.vector2((150, 470), 466)
        fan_count_bbox = rp.vector4((220, 523, 420, 540), 466)

        self.is_after_winning = (
            imagetools.compare_color(
                screenshot.getpixel(winning_color_pos),
                (244, 205, 52),
            )
            > 0.95
        )

        self.fan_count = _recognize_fan_count(screenshot.crop(fan_count_bbox))

    def update_by_character_detail(self, screenshot: Image) -> None:
        rp = mathtools.ResizeProxy(screenshot.width)
        grass_bbox = rp.vector4((158, 263, 173, 280), 466)
        dart_bbox = rp.vector4((244, 263, 258, 280), 466)

        sprint_bbox = rp.vector4((158, 289, 173, 305), 466)
        mile_bbox = rp.vector4((244, 289, 258, 305), 466)
        intermediate_bbox = rp.vector4((329, 289, 344, 305), 466)
        long_bbox = rp.vector4((414, 289, 430, 305), 466)

        lead_bbox = rp.vector4((158, 316, 173, 332), 466)
        head_bbox = rp.vector4((244, 316, 258, 332), 466)
        middle_bbox = rp.vector4((329, 316, 344, 332), 466)
        last_bbox = rp.vector4((414, 316, 430, 332), 466)

        conditions_bbox = rp.vector4((13, 506, 528, 832), 540)

        self.turf = _recognize_status(screenshot.crop(grass_bbox))
        self.dart = _recognize_status(screenshot.crop(dart_bbox))

        self.sprint = _recognize_status(screenshot.crop(sprint_bbox))
        self.mile = _recognize_status(screenshot.crop(mile_bbox))
        self.intermediate = _recognize_status(screenshot.crop(intermediate_bbox))
        self.long = _recognize_status(screenshot.crop(long_bbox))

        self.lead = _recognize_status(screenshot.crop(lead_bbox))
        self.head = _recognize_status(screenshot.crop(head_bbox))
        self.middle = _recognize_status(screenshot.crop(middle_bbox))
        self.last = _recognize_status(screenshot.crop(last_bbox))

        self.conditions = _recognize_conditions(screenshot.crop(conditions_bbox))

    def __str__(self):
        return (
            "Context<"
            f"turn={self.turn_count()},"
            f"mood={self.mood},"
            f"vit={self.vitality:.3f},"
            f"spd={self.speed},"
            f"sta={self.stamina},"
            f"pow={self.power},"
            f"gut={self.guts},"
            f"wis={self.wisdom},"
            f"fan={self.fan_count},"
            f"ground={''.join(i[1] for i in (self.turf, self.dart))},"
            f"distance={''.join(i[1] for i in (self.sprint, self.mile, self.intermediate, self.long))},"
            f"style={''.join(i[1] for i in (self.last, self.middle, self.head, self.lead))},"
            f"condition={functools.reduce(lambda a, b: a | b, self.conditions, 0)}"
            ">"
        )

    def turn_count(self) -> int:
        if self.date == (1, 0, 0):
            return self._extra_turn_count
        if self.date == (4, 0, 0):
            return self._extra_turn_count + 24 * 3
        return (self.date[0] - 1) * 24 + (self.date[1] - 1) * 2 + (self.date[2] - 1)

    def total_turn_count(self) -> int:
        return 24 * 3 + 6

    def continuous_race_count(self) -> int:
        ret = 1
        turn = self.turn_count() - 1
        while turn in self.race_turns:
            ret += 1
            turn -= 1
        return ret

    @property
    def is_summer_camp(self) -> bool:
        return self.date[1:] in ((7, 1), (7, 2), (8, 1))

    def expected_score(self) -> float:
        expected_score = 15 + self.turn_count() * 10 / 24

        can_heal_condition = not self.is_summer_camp
        if self.vitality > 0.5:
            expected_score *= 0.5
        if self.turn_count() >= self.total_turn_count() - 2:
            expected_score *= 0.1
        if self.date[1:] in ((6, 1),) and self.vitality < 0.8:
            expected_score += 10
        if self.date[1:] in ((6, 2),) and self.vitality < 0.9:
            expected_score += 20
        if self.is_summer_camp and self.vitality < 0.8:
            expected_score += 10
        if self.date in ((4, 0, 0)):
            expected_score -= 20
        if can_heal_condition:
            expected_score += (
                len(
                    set(
                        (
                            Context.CONDITION_HEADACHE,
                            Context.CONDITION_OVERWEIGHT,
                        )
                    ).intersection(self.conditions)
                )
                * 20
            )
        expected_score += (self.MOOD_VERY_GOOD[0] - self.mood[0]) * 40 * 3

        return expected_score


g.context_class = Context

_CONDITION_TEMPLATES = {
    templates.SINGLE_MODE_CONDITION_HEADACHE: Context.CONDITION_HEADACHE,
    templates.SINGLE_MODE_CONDITION_OVERWEIGHT: Context.CONDITION_OVERWEIGHT,
}


def _recognize_conditions(img: Image) -> Set[int]:
    ret: Set[int] = set()
    for tmpl, _ in template.match(
        img,
        *_CONDITION_TEMPLATES.keys(),
    ):
        ret.add(_CONDITION_TEMPLATES[tmpl.name])
    return ret
