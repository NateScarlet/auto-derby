# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import os
from typing import Tuple, Type

import cv2
import numpy as np
from auto_derby import imagetools
from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from .. import ocr, template, templates, mathtools
from .context import Context


class g:
    training_class: Type[Training]


def _gradient(colors: Tuple[Tuple[Tuple[int, int, int], int], ...]) -> np.ndarray:
    ret = np.linspace((0, 0, 0), colors[0][0], colors[0][1])
    for index, i in enumerate(colors[1:], 1):
        color, stop = i
        prev_color, prev_stop = colors[index - 1]
        g = np.linspace(prev_color, color, stop - prev_stop + 1)
        ret = np.concatenate((ret, g[1:]))
    return ret


def _ocr_training_effect(img: Image) -> int:
    cv_img = imagetools.cv_image(imagetools.resize(img, height=32))
    sharpened_img = cv2.filter2D(
        cv_img,
        8,
        np.array(
            (
                (0, -1, 0),
                (-1, 5, -1),
                (0, -1, 0),
            )
        ),
    )
    sharpened_img = imagetools.mix(sharpened_img, cv_img, 0.5)

    white_outline_img = imagetools.constant_color_key(sharpened_img, (255, 255, 255))
    white_outline_img = cv2.dilate(
        white_outline_img,
        cv2.getStructuringElement(
            cv2.MORPH_DILATE,
            (2, 2),
        ),
    )

    bg_mask_img = imagetools.bg_mask_by_outline(white_outline_img)

    masked_img = cv2.copyTo(cv_img, 255 - bg_mask_img)

    brown_outline_img = imagetools.constant_color_key(
        masked_img,
        (29, 62, 194),
        (24, 113, 218),
        (30, 109, 216),
        (69, 104, 197),
        (119, 139, 224),
    )

    bg_mask_img = imagetools.bg_mask_by_outline(brown_outline_img)
    masked_img = cv2.copyTo(masked_img, 255 - bg_mask_img)

    fill_gradient = _gradient(
        (
            ((140, 236, 255), 0),
            ((140, 236, 255), round(img.height * 0.25)),
            ((114, 229, 255), round(img.height * 0.35)),
            ((113, 198, 255), round(img.height * 0.55)),
            ((95, 179, 255), round(img.height * 0.63)),
            ((74, 157, 255), round(img.height * 0.70)),
            ((74, 117, 255), round(img.height * 0.83)),
            ((74, 117, 255), cv_img.shape[0]),
        )
    ).astype(np.uint8)
    fill_img = np.repeat(np.expand_dims(fill_gradient, 1), cv_img.shape[1], axis=1)
    assert fill_img.shape == cv_img.shape

    text_img = imagetools.color_key(masked_img, fill_img)

    text_img_extra = imagetools.constant_color_key(
        masked_img, (175, 214, 255), threshold=0.95
    )
    text_img = np.array(np.maximum(text_img, text_img_extra))
    imagetools.fill_area(text_img, (0,), size_lt=20)

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("sharpened_img", sharpened_img)
        cv2.imshow("white_outline_img", white_outline_img)
        cv2.imshow("brown_outline_img", brown_outline_img)
        cv2.imshow("bg_mask_img", bg_mask_img)
        cv2.imshow("masked_img", masked_img)
        cv2.imshow("text_img_extra", text_img_extra)
        cv2.imshow("text_img", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(image_from_array(text_img))
    if not text:
        return 0
    return int(text.lstrip("+"))


def _training_single_score(
    current: int, delta: int, value_map: Tuple[Tuple[int, float], ...]
) -> float:
    ret = 0
    for i in range(current, current + delta):
        ret += mathtools.interpolate(i, value_map)
    return ret


class Training:
    @staticmethod
    def new() -> Training:
        return g.training_class()

    def __init__(self):
        self.speed: int = 0
        self.stamina: int = 0
        self.power: int = 0
        self.guts: int = 0
        self.wisdom: int = 0
        self.skill: int = 0
        # self.friendship: int = 0
        # self.failure_rate: float = 0.0
        self.confirm_position: Tuple[int, int] = (0, 0)

    @classmethod
    def from_training_scene(cls, img: Image) -> Training:
        self = cls.new()
        self.confirm_position = next(
            template.match(
                img,
                template.Specification(
                    templates.SINGLE_MODE_TRAINING_CONFIRM, threshold=0.8
                ),
            )
        )[1]

        rp = mathtools.ResizeProxy(img.width)

        t, b = 503, 532
        self.speed = _ocr_training_effect(img.crop(rp.vector4((18, t, 91, b), 466)))
        self.stamina = _ocr_training_effect(img.crop(rp.vector4((91, t, 163, b), 466)))
        self.power = _ocr_training_effect(img.crop(rp.vector4((163, t, 237, b), 466)))
        self.guts = _ocr_training_effect(img.crop(rp.vector4((237, t, 309, b), 466)))
        self.wisdom = _ocr_training_effect(img.crop(rp.vector4((309, t, 382, b), 466)))
        self.skill = _ocr_training_effect(img.crop(rp.vector4((387, t, 450, b), 466)))
        return self

    def __str__(self):

        named_data = (
            ("spd", self.speed),
            ("sta", self.stamina),
            ("pow", self.power),
            ("gut", self.guts),
            ("wis", self.wisdom),
            ("ski", self.skill),
        )
        return (
            "Training<"
            + ", ".join(
                (
                    f"{name}={value}"
                    for name, value in sorted(
                        named_data, key=lambda x: x[1], reverse=True
                    )
                    if value
                )
            )
            + ">"
        )

    def score(self, ctx: Context) -> float:
        spd = _training_single_score(
            ctx.speed,
            self.speed,
            ((0, 2.0), (300, 1.0), (600, 0.8), (900, 0.7), (1100, 0.5)),
        )
        if ctx.speed < ctx.turn_count() / 24 * 300:
            spd *= 1.5

        sta = _training_single_score(
            ctx.stamina,
            self.stamina,
            (
                (0, 2.0),
                (300, ctx.speed / 600 + 0.3 * ctx.date[0] if ctx.speed > 600 else 1.0),
                (
                    600,
                    ctx.speed / 900 * 0.6 + 0.1 * ctx.date[0]
                    if ctx.speed > 900
                    else 0.6,
                ),
                (900, ctx.speed / 900 * 0.3),
            ),
        )
        pow = _training_single_score(
            ctx.power,
            self.power,
            (
                (0, 1.0),
                (300, 0.2 + ctx.speed / 600),
                (600, 0.1 + ctx.speed / 900),
                (900, ctx.speed / 900 / 3),
            ),
        )
        per = _training_single_score(
            ctx.guts,
            self.guts,
            ((0, 2.0), (300, 1.0), (400, 0.3), (600, 0.1))
            if ctx.speed > 400 / 24 * ctx.turn_count()
            else ((0, 2.0), (300, 0.5), (400, 0.1)),
        )
        int_ = _training_single_score(
            ctx.wisdom,
            self.wisdom,
            ((0, 3.0), (300, 1.0), (400, 0.4), (600, 0.2))
            if ctx.vitality < 0.9
            else ((0, 2.0), (300, 0.8), (400, 0.1)),
        )

        if ctx.vitality < 0.9:
            int_ += 5 if ctx.date[1:] in ((7, 1), (7, 2), (8, 1)) else 3

        skill = self.skill * 0.5

        success_rate = mathtools.interpolate(
            int(ctx.vitality * 10000),
            (
                (0, 0.15),
                (1500, 0.3),
                (4000, 1.0),
            )
            if self.wisdom > 0
            else (
                (0, 0.01),
                (1500, 0.2),
                (3000, 0.5),
                (5000, 0.85),
                (7000, 1.0),
            ),
        )
        return (spd + sta + pow + per + int_ + skill) * success_rate


g.training_class = Training
