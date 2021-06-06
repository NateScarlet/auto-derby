# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
from auto_derby import imagetools
import cv2
import numpy as np

from typing import Tuple

from PIL.Image import Image
from PIL.Image import fromarray as image_from_array
import os
from .. import ocr, templates, template


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


def _ocr_training_effect(img: Image) -> int:
    cv_img = cv2.cvtColor(
        np.asarray(imagetools.resize_by_heihgt(img, 32)),
        cv2.COLOR_RGB2BGR,
    )
    sharpened_img = imagetools.sharpen(cv_img)
    sharpened_img = ((sharpened_img / 2.0 + cv_img / 2.0)).astype(np.uint8)

    outline_img = imagetools.color_key(
        sharpened_img,
        np.full_like(
            cv_img,
            (255, 255, 255),
        )
    ).clip(0, 255)

    bg_mask_img = imagetools.bg_mask_by_outline(outline_img)

    fill_gradient = _gradient((
        ((140, 236, 255), 0),
        ((140, 236, 255), round(img.height * 0.25)),
        ((114, 229, 255), round(img.height * 0.35)),
        ((113, 198, 255), round(img.height * 0.55)),
        ((95, 179, 255), round(img.height * 0.63)),
        ((74, 157, 255), round(img.height * 0.70)),
        ((74, 117, 255), round(img.height * 0.83)),
        ((74, 117, 255), cv_img.shape[0]),
    )).astype(np.uint8)
    fill_img = np.repeat(
        np.expand_dims(fill_gradient, 1),
        cv_img.shape[1],
        axis=1,
    )
    assert fill_img.shape == cv_img.shape

    fg_mask_img = 255 - bg_mask_img
    masked_img = cv2.copyTo(cv_img, fg_mask_img)

    text_img = imagetools.color_key(
        masked_img,
        fill_img,
    )

    text_img_extra = imagetools.constant_color_key(
        masked_img,
        (175, 214, 255),
        threshold=0.95,
    )
    text_img = np.array(np.maximum(text_img, text_img_extra))
    imagetools.fill_area(text_img, (0,), size_lt=20)

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("sharpened_img", sharpened_img)
        # cv2.imshow("fill_diff_img", imagetools.color_key(
        #     masked_img,
        #     fill_img,
        #     threshold=0,
        # ))
        cv2.imshow("outline_img", outline_img)
        cv2.imshow("bg_mask_img", bg_mask_img)
        cv2.imshow("fg_mask_img", fg_mask_img)
        cv2.imshow("masked_img", masked_img)
        cv2.imshow("text_img_extra", text_img_extra)
        cv2.imshow("text_img", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(image_from_array(text_img))
    if not text:
        return 0
    return int(text.lstrip("+"))


class Training:
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
        self = cls()
        self.confirm_position = next(template.match(img, template.Specification(
            templates.SINGLE_MODE_TRAINING_CONFIRM,
            threshold=0.8
        )))[1]

        t, b = 503, 532
        self.speed = _ocr_training_effect(img.crop((18, t, 91, b)))
        self.stamina = _ocr_training_effect(img.crop((91, t, 163, b)))
        self.power = _ocr_training_effect(img.crop((163, t, 237, b)))
        self.guts = _ocr_training_effect(img.crop((237, t, 309, b)))
        self.wisdom = _ocr_training_effect(img.crop((309, t, 382, b)))
        self.skill = _ocr_training_effect(img.crop((387, t, 450, b)))
        return self

    def __str__(self):

        named_data = (
            ("spd", self.speed,),
            ("sta", self.stamina,),
            ("pow", self.power,),
            ("gut", self.guts,),
            ("wis", self.wisdom,),
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
