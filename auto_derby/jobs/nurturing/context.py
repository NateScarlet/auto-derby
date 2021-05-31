# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
import cv2
import numpy as np

from typing import Tuple

from PIL.Image import Image
import PIL.ImageOps
from PIL.Image import fromarray as image_from_array

from ... import ocr, imagetools


def _ocr_date(img: Image) -> Tuple[int, int, int]:
    text = ocr.text(
        image_from_array(
            cv2.threshold(
                255 - np.asarray(img.convert("L")),
                128,
                255,
                cv2.THRESH_TOZERO,
            )[1],
        ),
    )

    if text == 'ジュニア級デビュー前':
        return (1, 0, 0)
    if text == 'ファイナルズ開催中':
        return (4, 0, 0)
    year_end = text.index("級") + 1
    month_end = year_end + text[year_end:].index("月") + 1
    year_text = text[:year_end]
    month_text = text[year_end:month_end]
    date_text = text[month_end:]

    year = {
        'ジュニア級': 1,
        'クラシック級': 2,
        'シニア級': 3,
    }[year_text]
    month = int(month_text[:-1])
    date = {
        '前半': 1,
        '後半': 2,
    }[date_text]
    return (year, month, date)


def _recognize_vitality(img: Image) -> float:
    cv_img = np.asarray(img)

    def _is_empty(v: np.ndarray) -> bool:
        assert v.shape == (3,), v.shape
        return imagetools.compare_color(
            (118, 117, 118),
            (int(v[0]), int(v[1]), int(v[2])),
        ) > 0.99

    return 1 - np.average(np.apply_along_axis(_is_empty, 1, cv_img[0, :]))


def _recognize_mood(rgb_color: Tuple[int, int, int]) -> float:
    if imagetools.compare_color((238, 60, 112),  rgb_color) > 0.9:
        return Context.MOOD_VERY_GOOD
    if imagetools.compare_color((254, 157, 60),  rgb_color) > 0.9:
        return Context.MOOD_GOOD
    if imagetools.compare_color((255, 251, 233),  rgb_color) > 0.9:
        return Context.MOOD_NORMAL
    if imagetools.compare_color((5, 107, 223),  rgb_color) > 0.9:
        return Context.MOOD_BAD
    if imagetools.compare_color((194, 115, 255),  rgb_color) > 0.9:
        return Context.MOOD_VERY_BAD
    raise ValueError("_recognize_mood: unknown mood color: %s" % (rgb_color,))


class Context:
    MOOD_VERY_BAD: float = 0.8
    MOOD_BAD: float = 0.9
    MOOD_NORMAL: float = 1.0
    MOOD_GOOD: float = 1.1
    MOOD_VERY_GOOD: float = 1.2

    def __init__(self) -> None:
        self.speed = 0
        self.stamina = 0
        self.power = 0
        self.perservance = 0
        self.intelligence = 0
        # (year, month, half-month), 1-base
        self.date = (0, 0, 0)
        self.vitality = 0.0
        self.mood = Context.MOOD_NORMAL

        self._extra_turn_count = 0

    def update_by_command_scene(self, screenshot: Image) -> None:

        vitality_bbox = (148, 106, 327, 108)
        speed_bbox = (45, 553, 90, 572)
        stamina_bbox = (125, 553, 162, 572)
        power_bbox = (192, 553, 234, 572)
        perservance_bbox = (264, 553, 308, 572)
        intelligence_bbox = (337, 553, 381, 572)
        date_bbox = (10, 28, 140, 43)

        self.date = _ocr_date(screenshot.crop(date_bbox))
        if self.date in ((1, 0, 0), (4, 0, 0)):
            self._extra_turn_count += 1
        else:
            self._extra_turn_count = 0

        self.vitality = _recognize_vitality(screenshot.crop(vitality_bbox))

        mood_color = screenshot.getpixel((360, 100))
        assert isinstance(mood_color, tuple), mood_color
        self.mood = _recognize_mood(
            (mood_color[0], mood_color[1], mood_color[2]),
        )

        self.speed = int(
            ocr.text(PIL.ImageOps.invert(screenshot.crop(speed_bbox))))
        self.stamina = int(
            ocr.text(PIL.ImageOps.invert(screenshot.crop(stamina_bbox))))
        self.power = int(
            ocr.text(PIL.ImageOps.invert(screenshot.crop(power_bbox))))
        self.perservance = int(
            ocr.text(PIL.ImageOps.invert(screenshot.crop(perservance_bbox))))
        self.intelligence = int(
            ocr.text(PIL.ImageOps.invert(screenshot.crop(intelligence_bbox))))


    def __str__(self):
        return (
            "Context<"
            f"turn={self.turn_count()},"
            f"mood={self.mood},"
            f"vit={self.vitality:.3f},"
            f"spd={self.speed},"
            f"sta={self.stamina},"
            f"pow={self.power},"
            f"per={self.perservance},"
            f"int={self.intelligence}"
            ">"
        )

    def turn_count(self) -> int:
        if self.date == (1, 0, 0):
            return self._extra_turn_count
        if self.date == (4, 0, 0):
            return self._extra_turn_count + 24 * 3
        return (self.date[0] - 1) * 24 + (self.date[1] - 1) * 2 + (self.date[2] - 1)

    def total_turn_count(self) -> int:
        return 24 * 3 + 3
