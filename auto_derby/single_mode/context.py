# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
import cv2
import numpy as np

from typing import Text, Tuple

from PIL.Image import Image
import PIL.ImageOps
from PIL.Image import fromarray as image_from_array

from .. import ocr, imagetools, templates, template

import os


def _ocr_date(img: Image) -> Tuple[int, int, int]:
    img = imagetools.resize_by_heihgt(img, 32)
    cv_img = np.asarray(img.convert("L"))
    sharpened_img = imagetools.sharpen(cv_img)

    _, binary_img = cv2.threshold(sharpened_img, 100, 255, cv2.THRESH_BINARY_INV)
    imagetools.fill_area(binary_img, (0,), size_lt=3)

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


def _recognize_mood(rgb_color: Tuple[int, int, int]) -> float:
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
    cv_img = imagetools.mix(cv_img, imagetools.sharpen(cv_img), 0.5)
    text = ocr.text(imagetools.pil_image(255 - cv_img))
    return int(text.rstrip("人").replace(",", ""))


def _recognize_status(img: Image) -> Tuple[int, Text]:
    cv_img = imagetools.cv_image(imagetools.resize_by_heihgt(img.convert("L"), 32))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 5), np.percentile(cv_img, 95)
    )
    cv_img = cv2.copyMakeBorder(cv_img, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255,))

    blurred_img = imagetools.mix(cv2.blur(cv_img, (5, 5)), cv_img, 0.8)

    binary_img = cv2.adaptiveThreshold(
        blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, -1
    )

    contours, hierarchy = cv2.findContours(
        binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
    )
    if not contours:
        raise ValueError("_recognize_status: image is empty")

    text_img = np.zeros_like(binary_img)

    def _contour_level(h: np.ndarray) -> int:
        _, _, _, parent = h
        if parent < 0:
            return 0
        return _contour_level(hierarchy[0][parent]) + 1

    for index, h in enumerate(hierarchy[0]):
        level = _contour_level(h)
        if level < 2:
            continue
        is_white = level % 2 == 0
        if is_white and cv2.contourArea(contours[index]) < 40:
            continue
        color = (255,) if is_white else (0,)
        cv2.drawContours(text_img, contours, index, thickness=cv2.FILLED, color=color)
        if color == (0,):
            # use white border
            cv2.drawContours(text_img, contours, index, thickness=1, color=(255,))

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("blurred_img", blurred_img)
        cv2.imshow("binary_img", binary_img)
        cv2.imshow("text_img", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(imagetools.pil_image(text_img))
    for i in Context.ALL_STATUSES:
        if i[1] == text:
            return i

    raise ValueError("_recognize_status: unknown status: %s" % text)


class Context:
    MOOD_VERY_BAD: float = 0.8
    MOOD_BAD: float = 0.9
    MOOD_NORMAL: float = 1.0
    MOOD_GOOD: float = 1.1
    MOOD_VERY_GOOD: float = 1.2

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
        self.fan_count = 0

        self._extra_turn_count = 0

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

    def next_turn(self) -> None:
        if self.date in ((1, 0, 0), (4, 0, 0)):
            self._extra_turn_count += 1
        else:
            self._extra_turn_count = 0

    def update_by_command_scene(self, screenshot: Image) -> None:
        date_bbox = (10, 27, 140, 43)
        vitality_bbox = (148, 106, 327, 108)

        _, detail_button_pos = next(
            template.match(screenshot, templates.SINGLE_MODE_CHARACTER_DETAIL_BUTTON)
        )
        base_y = detail_button_pos[1] + 71
        speed_bbox = (45, base_y, 90, base_y + 19)
        stamina_bbox = (125, base_y, 162, base_y + 19)
        power_bbox = (192, base_y, 234, base_y + 19)
        guts_bbox = (264, base_y, 308, base_y + 19)
        wisdom_bbox = (337, base_y, 381, base_y + 19)

        self.date = _ocr_date(screenshot.crop(date_bbox))

        self.vitality = _recognize_vitality(screenshot.crop(vitality_bbox))

        mood_color = screenshot.getpixel((395, 113))
        assert isinstance(mood_color, tuple), mood_color
        self.mood = _recognize_mood((mood_color[0], mood_color[1], mood_color[2]))

        self.speed = int(ocr.text(PIL.ImageOps.invert(screenshot.crop(speed_bbox))))
        self.stamina = int(ocr.text(PIL.ImageOps.invert(screenshot.crop(stamina_bbox))))
        self.power = int(ocr.text(PIL.ImageOps.invert(screenshot.crop(power_bbox))))
        self.guts = int(ocr.text(PIL.ImageOps.invert(screenshot.crop(guts_bbox))))
        self.wisdom = int(ocr.text(PIL.ImageOps.invert(screenshot.crop(wisdom_bbox))))

    def update_by_class_detail(self, screenshot: Image) -> None:
        fan_count_bbox = (220, 523, 420, 540)
        self.fan_count = _recognize_fan_count(screenshot.crop(fan_count_bbox))

    def update_by_character_detail(self, screenshot: Image) -> None:
        grass_bbox = (158, 263, 173, 280)
        dart_bbox = (244, 263, 258, 280)

        sprint_bbox = (158, 289, 173, 305)
        mile_bbox = (244, 289, 258, 305)
        intermediate_bbox = (329, 289, 344, 305)
        long_bbox = (414, 289, 430, 305)

        lead_bbox = (158, 316, 173, 332)
        head_bbox = (244, 316, 258, 332)
        middle_bbox = (329, 316, 344, 332)
        last_bbox = (414, 316, 430, 332)

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
            f"style={''.join(i[1] for i in (self.last, self.middle, self.head, self.lead))}"
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
