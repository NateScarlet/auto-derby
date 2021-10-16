# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import os
from typing import Tuple

import cast_unknown as cast
import cv2
import numpy as np
from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from ... import imagetools, mathtools, ocr, template, templates
from ..context import Context
from . import training_score
from .globals import g
from .partner import Partner

_LOGGER = logging.getLogger(__name__)


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

    white_outline_img = imagetools.constant_color_key(
        sharpened_img,
        (255, 255, 255),
        (234, 245, 240),
    )
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
        (103, 147, 223),
    )

    bg_mask_img = imagetools.bg_mask_by_outline(brown_outline_img)
    masked_img = cv2.copyTo(masked_img, 255 - bg_mask_img)

    fill_gradient = _gradient(
        (
            ((140, 236, 255), 0),
            ((140, 236, 255), round(cv_img.shape[0] * 0.25)),
            ((114, 229, 255), round(cv_img.shape[0] * 0.35)),
            ((113, 198, 255), round(cv_img.shape[0] * 0.55)),
            ((95, 179, 255), round(cv_img.shape[0] * 0.63)),
            ((74, 157, 255), round(cv_img.shape[0] * 0.70)),
            ((74, 117, 255), round(cv_img.shape[0] * 0.83)),
            ((74, 117, 255), cv_img.shape[0]),
        )
    ).astype(np.uint8)
    fill_img = np.repeat(np.expand_dims(fill_gradient, 1), cv_img.shape[1], axis=1)
    assert fill_img.shape == cv_img.shape

    text_img = imagetools.color_key(masked_img, fill_img)
    imagetools.fill_area(text_img, (0,), size_lt=8)

    text_img_extra = imagetools.constant_color_key(
        masked_img, (175, 214, 255), threshold=0.95
    )
    text_img = np.array(np.maximum(text_img, text_img_extra))
    h = cv_img.shape[0]
    imagetools.fill_area(text_img, (0,), size_lt=round(h * 0.2 ** 2))

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

    # +100 has different color
    hash100 = "0000000000006066607770ff70df60df00000000000000000000000000000000"
    if (
        imagetools.compare_hash(
            imagetools.image_hash(imagetools.pil_image(text_img)),
            hash100,
        )
        > 0.9
    ):
        return 100
    text = ocr.text(image_from_array(text_img))
    if not text:
        return 0
    return int(text.lstrip("+"))


def _ocr_red_training_effect(img: Image) -> int:
    cv_img = imagetools.cv_image(
        imagetools.resize(
            imagetools.resize(img, height=24),
            height=48,
        )
    )
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

    white_outline_img = imagetools.constant_color_key(
        sharpened_img,
        (255, 255, 255),
        (222, 220, 237),
        (252, 254, 202),
        (236, 249, 105),
        (243, 220, 160),
    )

    masked_img = imagetools.inside_outline(cv_img, white_outline_img)

    red_outline_img = imagetools.constant_color_key(
        cv_img,
        (15, 18, 216),
        (34, 42, 234),
        (56, 72, 218),
        (20, 18, 181),
        (27, 35, 202),
    )
    red_outline_img = cv2.morphologyEx(
        red_outline_img,
        cv2.MORPH_CLOSE,
        np.ones((3, 3)),
    )

    masked_img = imagetools.inside_outline(masked_img, red_outline_img)

    height = cv_img.shape[0]
    fill_gradient = _gradient(
        (
            ((129, 211, 255), 0),
            ((126, 188, 255), round(height * 0.5)),
            ((82, 134, 255), round(height * 0.75)),
            ((36, 62, 211), height),
        )
    ).astype(np.uint8)
    fill_img = np.repeat(np.expand_dims(fill_gradient, 1), cv_img.shape[1], axis=1)
    assert fill_img.shape == cv_img.shape

    text_img_base = imagetools.color_key(masked_img, fill_img)
    imagetools.fill_area(text_img_base, (0,), size_lt=8)

    text_img_extra = imagetools.constant_color_key(
        masked_img,
        (128, 196, 253),
        (136, 200, 255),
        (144, 214, 255),
        (58, 116, 255),
        (64, 111, 238),
        (114, 174, 251),
        (89, 140, 240),
        (92, 145, 244),
        (91, 143, 238),
        (140, 228, 254),
        threshold=0.95,
    )
    text_img = np.array(np.maximum(text_img_base, text_img_extra))
    h = cv_img.shape[0]
    imagetools.fill_area(text_img, (0,), size_lt=round(h * 0.2 ** 2))

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("sharpened_img", sharpened_img)
        cv2.imshow("white_outline_img", white_outline_img)
        cv2.imshow("red_outline_img", red_outline_img)
        cv2.imshow("masked_img", masked_img)
        cv2.imshow("fill", fill_img)
        cv2.imshow("text_img_base", text_img_base)
        cv2.imshow("text_img_extra", text_img_extra)
        cv2.imshow("text_img", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    # +100 has different color
    hash100 = "0000000000006066607770ff70df60df00000000000000000000000000000000"
    if (
        imagetools.compare_hash(
            imagetools.image_hash(imagetools.pil_image(text_img)),
            hash100,
        )
        > 0.9
    ):
        return 100
    text = ocr.text(image_from_array(text_img))
    if not text:
        return 0
    return int(text.lstrip("+"))


def _recognize_level(rgb_color: Tuple[int, ...]) -> int:
    if imagetools.compare_color((49, 178, 22), rgb_color) > 0.9:
        return 1
    if imagetools.compare_color((46, 139, 244), rgb_color) > 0.9:
        return 2
    if imagetools.compare_color((255, 134, 0), rgb_color) > 0.9:
        return 3
    if imagetools.compare_color((244, 69, 132), rgb_color) > 0.9:
        return 4
    if imagetools.compare_color((165, 78, 255), rgb_color) > 0.9:
        return 5
    raise ValueError("_recognize_level: unknown level color: %s" % (rgb_color,))


def _recognize_failure_rate(
    rp: mathtools.ResizeProxy, trn: Training, img: Image
) -> float:
    x, y = trn.confirm_position
    bbox = (
        x + rp.vector(20, 540),
        y + rp.vector(-155, 540),
        x + rp.vector(70, 540),
        y + rp.vector(-120, 540),
    )
    rate_img = imagetools.cv_image(imagetools.resize(img.crop(bbox), height=48))
    outline_img = imagetools.constant_color_key(
        rate_img,
        (252, 150, 14),
        (255, 183, 89),
        (0, 150, 255),
        (0, 69, 255),
    )
    fg_img = imagetools.inside_outline(rate_img, outline_img)
    text_img = imagetools.constant_color_key(
        fg_img,
        (255, 255, 255),
        (18, 218, 255),
    )
    if __name__ == os.getenv("DEBUG"):
        cv2.imshow("rate", rate_img)
        cv2.imshow("outline", outline_img)
        cv2.imshow("fg", fg_img)
        cv2.imshow("text", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(text_img))
    return int(text.strip("%")) / 100


def _estimate_vitality(ctx: Context, trn: Training) -> float:
    # https://gamewith.jp/uma-musume/article/show/257432
    vit_data = {
        trn.TYPE_SPEED: (-21, -22, -23, -25, -27),
        trn.TYPE_STAMINA: (-19, -20, -21, -23, -25),
        trn.TYPE_POWER: (-20, -21, -22, -24, -26),
        trn.TYPE_GUTS: (-22, -23, -24, -26, -28),
        trn.TYPE_WISDOM: (5, 5, 5, 5, 5),
    }

    if trn.type not in vit_data:
        return 0
    return vit_data[trn.type][trn.level - 1] / ctx.max_vitality


class Training:
    TYPE_SPEED: int = 1
    TYPE_STAMINA: int = 2
    TYPE_POWER: int = 3
    TYPE_GUTS: int = 4
    TYPE_WISDOM: int = 5

    ALL_TYPES = (
        TYPE_SPEED,
        TYPE_STAMINA,
        TYPE_POWER,
        TYPE_GUTS,
        TYPE_WISDOM,
    )

    @staticmethod
    def new() -> Training:
        return g.training_class()

    def __init__(self):
        self.level = 0
        self.type = 0

        self.speed: int = 0
        self.stamina: int = 0
        self.power: int = 0
        self.guts: int = 0
        self.wisdom: int = 0
        self.skill: int = 0
        self.vitality: float = 0.0
        self._use_estimate_vitality = False
        self.failure_rate: float = 0.0
        self.confirm_position: Tuple[int, int] = (0, 0)
        self.partners: Tuple[Partner, ...] = tuple()

    @classmethod
    def from_training_scene(
        cls,
        img: Image,
    ) -> Training:
        # TODO: remove old api at next major version
        import warnings

        warnings.warn(
            "use from_training_scene_v2 instead",
            DeprecationWarning,
        )
        ctx = Context()
        ctx.scenario = ctx.SCENARIO_URA
        return cls.from_training_scene_v2(ctx, img)

    @classmethod
    def from_training_scene_v2(
        cls,
        ctx: Context,
        img: Image,
    ) -> Training:

        if g.image_path:
            image_id = imagetools.md5(
                imagetools.cv_image(img.convert("RGB")),
                save_path=g.image_path,
                save_mode="RGB",
            )
            _LOGGER.debug("from_training_scene: image=%s", image_id)
        rp = mathtools.ResizeProxy(img.width)

        self = cls.new()
        self.confirm_position = next(
            template.match(
                img,
                template.Specification(
                    templates.SINGLE_MODE_TRAINING_CONFIRM, threshold=0.8
                ),
            )
        )[1]
        radius = rp.vector(30, 540)
        for t, center in zip(
            Training.ALL_TYPES,
            (
                rp.vector2((78, 850), 540),
                rp.vector2((171, 850), 540),
                rp.vector2((268, 850), 540),
                rp.vector2((367, 850), 540),
                rp.vector2((461, 850), 540),
            ),
        ):
            if mathtools.distance(self.confirm_position, center) < radius:
                self.type = t
                break
        else:
            raise ValueError(
                "unknown type for confirm position: %s" % self.confirm_position
            )

        self.level = _recognize_level(
            tuple(cast.list_(img.getpixel(rp.vector2((10, 200), 540)), int))
        )

        bbox_group = {
            ctx.SCENARIO_URA: (
                rp.vector4((18, 503, 91, 532), 466),
                rp.vector4((91, 503, 163, 532), 466),
                rp.vector4((163, 503, 237, 532), 466),
                rp.vector4((237, 503, 309, 532), 466),
                rp.vector4((309, 503, 382, 532), 466),
                rp.vector4((387, 503, 450, 532), 466),
            ),
            ctx.SCENARIO_AOHARU: (
                rp.vector4((18, 597, 104, 625), 540),
                rp.vector4((104, 597, 190, 625), 540),
                rp.vector4((190, 597, 273, 625), 540),
                rp.vector4((273, 597, 358, 625), 540),
                rp.vector4((358, 597, 441, 625), 540),
                rp.vector4((448, 597, 521, 625), 540),
            ),
        }[ctx.scenario]

        self.speed = _ocr_training_effect(img.crop(bbox_group[0]))
        self.stamina = _ocr_training_effect(img.crop(bbox_group[1]))
        self.power = _ocr_training_effect(img.crop(bbox_group[2]))
        self.guts = _ocr_training_effect(img.crop(bbox_group[3]))
        self.wisdom = _ocr_training_effect(img.crop(bbox_group[4]))
        self.skill = _ocr_training_effect(img.crop(bbox_group[5]))

        extra_bbox_group = {
            ctx.SCENARIO_AOHARU: (
                rp.vector4((18, 570, 104, 595), 540),
                rp.vector4((104, 570, 190, 595), 540),
                rp.vector4((190, 570, 273, 595), 540),
                rp.vector4((273, 570, 358, 595), 540),
                rp.vector4((358, 570, 441, 595), 540),
                rp.vector4((448, 570, 521, 595), 540),
            )
        }.get(ctx.scenario)
        if extra_bbox_group:
            self.speed += _ocr_red_training_effect(img.crop(extra_bbox_group[0]))
            self.stamina += _ocr_red_training_effect(img.crop(extra_bbox_group[1]))
            self.power += _ocr_red_training_effect(img.crop(extra_bbox_group[2]))
            self.guts += _ocr_red_training_effect(img.crop(extra_bbox_group[3]))
            self.wisdom += _ocr_red_training_effect(img.crop(extra_bbox_group[4]))
            self.skill += _ocr_red_training_effect(img.crop(extra_bbox_group[5]))

        # TODO: recognize vitality
        self._use_estimate_vitality = True
        self.failure_rate = _recognize_failure_rate(rp, self, img)
        self.partners = tuple(Partner.from_training_scene_v2(ctx, img))
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
        partner_text = ",".join(i.to_short_text() for i in self.partners)
        return (
            "Training<"
            f"lv={self.level} "
            + (f"fail={int(self.failure_rate*100)}% ")
            + " ".join(
                (
                    f"{name}={value}"
                    for name, value in sorted(
                        named_data, key=lambda x: x[1], reverse=True
                    )
                    if value
                )
            )
            + (f" ptn={partner_text}" if partner_text else "")
            + ">"
        )

    def score(self, ctx: Context) -> float:
        if self._use_estimate_vitality:
            self.vitality = _estimate_vitality(ctx, self)
        return training_score.compute(ctx, self)


g.training_class = Training
