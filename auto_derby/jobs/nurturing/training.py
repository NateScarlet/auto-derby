# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
import cv2
import numpy as np

from typing import Tuple

from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from ... import ocr, templates, template


def _gradient(colors: Tuple[
    Tuple[Tuple[int, int, int],  int],
    ...
]) -> np.ndarray:
    ret = np.linspace(
        (0, 0, 0),
        colors[0][0],
        colors[0][1],
    )
    for index, i in enumerate(colors[1:], 1):
        color, stop = i
        prev_color, prev_stop = colors[index-1]
        g = np.linspace(
            prev_color,
            color,
            stop-prev_stop+1,
        )
        ret = np.concatenate((ret, g[1:]))
    return ret


def _remove_area(img: np.ndarray, *, size_lt: int):
    contours, _ = cv2.findContours(
        (img * 255).astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE,
    )
    for i in contours:
        size = cv2.contourArea(i)
        if size < size_lt:
            cv2.drawContours(img, [i], -1, (0,), cv2.FILLED)


def _color_key(img: np.ndarray, color: np.ndarray, threshold: float = 0.8, bit_size: int = 8) -> np.ndarray:
    max_value = (1 << bit_size) - 1
    assert img.shape == color.shape, (img.shape, color.shape)

    # do this is somehow faster than
    # `numpy.linalg.norm(img.astype(int) - color.astype(int), axis=2,).clip(0, 255).astype(np.uint8)`
    diff_img = np.sqrt(
        np.sum(
            (img.astype(int) - color.astype(int)) ** 2,
            axis=2,
        ),
    ).clip(0, 255).astype(np.uint8)

    ret = max_value - diff_img
    mask_img = (ret > (max_value * threshold)).astype(np.uint8)
    ret *= mask_img
    ret = ret.clip(0, 255)
    ret = ret.astype(np.uint8)
    return ret


def _ocr_training_effect(img: Image) -> int:
    cv_img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    sharpened_img = cv2.filter2D(
        cv_img,
        8,
        np.array(
            (
                (-1, -1, -1),
                (-1, 9, -1),
                (-1, -1, -1),
            ),
        )
    )

    outline_img = _color_key(
        sharpened_img,
        np.full_like(
            sharpened_img,
            (255, 255, 255),
        ),
        0.9,
    )

    border_points = (
        *((0, i) for i in range(img.height)),
        *((i, 0) for i in range(img.width)),
        *((img.width-1, i) for i in range(img.height)),
        *((i, img.height-1) for i in range(img.width)),
    )

    fill_mask_img = cv2.copyMakeBorder(
        outline_img, 1, 1, 1, 1, cv2.BORDER_CONSTANT)
    bg_mask_img = outline_img.copy()
    for i in border_points:
        x, y = i
        if outline_img[y, x] != 0:
            continue
        cv2.floodFill(
            bg_mask_img,
            fill_mask_img,
            (x, y),
            (255, ),
            0,
            0,
        )

    fill_gradient = _gradient((
        ((140, 236, 255), 0),
        ((140, 236, 255), round(img.height * 0.25)),
        ((114, 229, 255), round(img.height * 0.35)),
        ((113, 198, 255), round(img.height * 0.55)),
        ((95, 179, 255), round(img.height * 0.63)),
        ((74, 157, 255), round(img.height * 0.70)),
        ((74, 117, 255), round(img.height * 0.83)),
        ((74, 117, 255), img.height),
    )).astype(np.uint8)
    fill_img = np.repeat(np.expand_dims(fill_gradient, 1), img.width, axis=1)
    assert fill_img.shape == cv_img.shape

    masked_img = cv2.copyTo(cv_img, cv2.dilate(
        255 - bg_mask_img, (3, 3), iterations=3))

    text_img = _color_key(
        masked_img,
        fill_img,
    )
    text_img = cv2.erode(text_img, (5, 5))
    _remove_area(text_img, size_lt=20)

    text = ocr.text(image_from_array(text_img))
    if not text:
        return 0
    return int(text.lstrip("+"))


class Training:
    def __init__(self):
        self.speed: int = 0
        self.stamina: int = 0
        self.power: int = 0
        self.perservance: int = 0
        self.intelligence: int = 0
        self.skill: int = 0
        # self.friendship: int = 0
        # self.failure_rate: float = 0.0
        self.confirm_position: Tuple[int, int] = (0, 0)

    @classmethod
    def from_training_scene(cls, img: Image) -> Training:
        self = cls()
        self.confirm_position = next(template.match(img, template.Specification(
            templates.NURTURING_TRAINING_CONFIRM,
            threshold=0.8
        )))[1]

        t, b = 503, 532
        self.speed = _ocr_training_effect(img.crop((18, t, 91, b)))
        self.stamina = _ocr_training_effect(img.crop((91, t, 163, b)))
        self.power = _ocr_training_effect(img.crop((163, t, 237, b)))
        self.perservance = _ocr_training_effect(img.crop((237, t, 309, b)))
        self.intelligence = _ocr_training_effect(img.crop((309, t, 382, b)))
        self.skill = _ocr_training_effect(img.crop((387, t, 450, b)))
        return self

    def __str__(self):

        named_data = (
            ("spd", self.speed,),
            ("sta", self.stamina,),
            ("pow", self.power,),
            ("per", self.perservance,),
            ("int", self.intelligence,),
            ("ski", self.skill,)
        )
        return (
            "Training<" +
            ", ".join(
                (
                    f"{name}={value}"
                    for name, value in
                    sorted(
                        named_data,
                        key=lambda x: x[1],
                        reverse=True,
                    )
                    if value
                ),
            ) +
            ">"
        )
