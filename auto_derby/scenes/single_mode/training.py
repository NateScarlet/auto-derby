# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import os
from concurrent import futures
from typing import Callable, Iterator, Optional, Tuple

import cast_unknown as cast
import cv2
import numpy as np
from auto_derby.single_mode.context import Context
from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from ... import action, imagetools, mathtools, ocr, template, templates
from ...single_mode import Training, training
from ...single_mode.training import Partner
from ..scene import Scene, SceneHolder
from .command import CommandScene

_LOGGER = logging.getLogger(__name__)

_TRAINING_CONFIRM = template.Specification(
    templates.SINGLE_MODE_TRAINING_CONFIRM, threshold=0.8
)


def _gradient(colors: Tuple[Tuple[Tuple[int, int, int], int], ...]) -> np.ndarray:
    ret = np.linspace((0, 0, 0), colors[0][0], colors[0][1])
    for index, i in enumerate(colors[1:], 1):
        color, stop = i
        prev_color, prev_stop = colors[index - 1]
        g = np.linspace(prev_color, color, stop - prev_stop + 1)
        ret = np.concatenate((ret, g[1:]))
    return ret


def _recognize_base_effect(img: Image) -> int:
    cv_img = imagetools.cv_image(imagetools.resize(img, height=32))
    sharpened_img = imagetools.sharpen(cv_img)
    sharpened_img = imagetools.mix(sharpened_img, cv_img, 0.65)

    white_outline_img = imagetools.constant_color_key(
        sharpened_img,
        (255, 255, 255),
    )
    white_outline_img = cv2.morphologyEx(
        white_outline_img,
        cv2.MORPH_DILATE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
    )

    bg_mask_img = imagetools.bg_mask_by_outline(white_outline_img)
    masked_img = cv2.copyTo(cv_img, 255 - bg_mask_img)

    brown_outline_img = imagetools.constant_color_key(
        cv_img,
        (29, 62, 194),
        (24, 113, 218),
        (30, 109, 216),
        (69, 104, 197),
        (119, 139, 224),
        (103, 147, 223),
        (59, 142, 226),
        threshold=0.85,
    )
    brown_outline_img = cv2.morphologyEx(
        brown_outline_img,
        cv2.MORPH_DILATE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
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

    text_img_extra = imagetools.constant_color_key(
        masked_img, (175, 214, 255), threshold=0.95
    )
    text_img = np.array(np.maximum(text_img, text_img_extra))
    imagetools.fill_area(text_img, (0,), size_lt=48)

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
    hash100 = "000000000000006600ee00ff00ff00ff004e0000000000000000000000000000"
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


def _recognize_red_effect(img: Image) -> int:
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


def _iter_training_images():
    rp = action.resize_proxy()
    radius = rp.vector(30, 540)
    _, first_confirm_pos = action.wait_image(_TRAINING_CONFIRM)
    yield template.screenshot()
    for pos in (
        rp.vector2((78, 850), 540),
        rp.vector2((171, 850), 540),
        rp.vector2((268, 850), 540),
        rp.vector2((367, 850), 540),
        rp.vector2((461, 850), 540),
    ):
        if mathtools.distance(first_confirm_pos, pos) < radius:
            continue
        action.tap(pos)
        action.wait_image(_TRAINING_CONFIRM)
        yield template.screenshot()


def _recognize_type_color(rp: mathtools.ResizeProxy, icon_img: Image) -> int:
    type_pos = rp.vector2((7, 18), 540)
    type_colors = (
        ((36, 170, 255), Partner.TYPE_SPEED),
        ((255, 106, 86), Partner.TYPE_STAMINA),
        ((255, 151, 27), Partner.TYPE_POWER),
        ((255, 96, 156), Partner.TYPE_GUTS),
        ((3, 191, 126), Partner.TYPE_WISDOM),
        ((255, 179, 22), Partner.TYPE_FRIEND),
    )
    for color, v in type_colors:
        if (
            imagetools.compare_color_near(
                imagetools.cv_image(icon_img), type_pos, color[::-1]
            )
            > 0.9
        ):
            return v
    return Partner.TYPE_OTHER


def _recognize_has_hint(rp: mathtools.ResizeProxy, icon_img: Image) -> bool:
    bbox = rp.vector4((50, 0, 58, 8), 540)
    hint_mark_color = (127, 67, 255)
    hint_mark_img = icon_img.crop(bbox)
    hint_mask = imagetools.constant_color_key(
        imagetools.cv_image(hint_mark_img), hint_mark_color
    )
    return np.average(hint_mask) > 200


def _recognize_has_training(
    ctx: Context, rp: mathtools.ResizeProxy, icon_img: Image
) -> bool:
    if ctx.scenario != ctx.SCENARIO_AOHARU:
        return False
    bbox = rp.vector4((52, 0, 65, 8), 540)
    mark_img = icon_img.crop(bbox)
    mask = imagetools.constant_color_key(
        imagetools.cv_image(mark_img),
        (67, 131, 255),
        (82, 171, 255),
        threshold=0.9,
    )

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("training_mark_mask", mask)
        cv2.waitKey()
        cv2.destroyAllWindows()
        _LOGGER.debug("training mark mask: avg=%0.2f", np.average(mask))
    return np.average(mask) > 80


def _recognize_has_soul_burst(
    ctx: Context, rp: mathtools.ResizeProxy, icon_img: Image
) -> bool:
    if ctx.scenario != ctx.SCENARIO_AOHARU:
        return False
    bbox = rp.vector4((52, 0, 65, 8), 540)
    mark_img = imagetools.cv_image(icon_img.crop(bbox))
    mask = imagetools.constant_color_key(
        mark_img,
        (198, 255, 255),
        threshold=0.9,
    )

    if os.getenv("DEBUG") == __name__ + "[partner]":
        cv2.imshow("soul_burst_mark", mark_img)
        cv2.imshow("soul_burst_mark_mask", mask)
        cv2.waitKey()
        cv2.destroyAllWindows()
        _LOGGER.debug("soul burst mark mask: avg=%0.2f", np.average(mask))
    return np.average(mask) > 80


def _recognize_partner_level(rp: mathtools.ResizeProxy, icon_img: Image) -> int:
    pos = (
        rp.vector2((10, 65), 540),  # level 1
        rp.vector2((20, 65), 540),  # level 2
        rp.vector2((33, 65), 540),  # level 3
        rp.vector2((43, 65), 540),  # level 4
        rp.vector2((55, 65), 540),  # level 5
    )
    colors = (
        (109, 108, 119),  # empty
        (42, 192, 255),  # level 1
        (42, 192, 255),  # level 2
        (162, 230, 30),  # level 3
        (255, 173, 30),  # level 4
        (255, 235, 120),  # level 5
    )
    spec: Tuple[Tuple[Tuple[Tuple[int, int], Tuple[int, int, int]], ...], ...] = (
        # level 0
        (
            (pos[0], colors[0]),
            (pos[1], colors[0]),
            (pos[2], colors[0]),
            (pos[3], colors[0]),
            (pos[4], colors[0]),
        ),
        # level 1
        (
            (pos[0], colors[1]),
            (pos[1], colors[0]),
            (pos[2], colors[0]),
            (pos[3], colors[0]),
            (pos[4], colors[0]),
        ),
        # level 2
        (
            (pos[0], colors[2]),
            (pos[1], colors[2]),
            (pos[3], colors[0]),
            (pos[4], colors[0]),
        ),
        # level 3
        (
            (pos[0], colors[3]),
            (pos[1], colors[3]),
            (pos[2], colors[3]),
            (pos[4], colors[0]),
        ),
        # level 4
        (
            (pos[0], colors[4]),
            (pos[1], colors[4]),
            (pos[2], colors[4]),
            (pos[3], colors[4]),
        ),
        # level 5
        (
            (pos[0], colors[5]),
            (pos[4], colors[5]),
        ),
    )

    for level, s in enumerate(spec):
        if all(
            imagetools.compare_color_near(
                imagetools.cv_image(icon_img),
                pos,
                color[::-1],
            )
            > 0.95
            for pos, color in s
        ):
            return level
    return -1


def _recognize_soul(
    rp: mathtools.ResizeProxy, screenshot: Image, icon_bbox: Tuple[int, int, int, int]
) -> float:
    right_bottom_icon_bbox = (
        icon_bbox[0] + rp.vector(49, 540),
        icon_bbox[1] + rp.vector(32, 540),
        icon_bbox[0] + rp.vector(74, 540),
        icon_bbox[1] + rp.vector(58, 540),
    )

    right_bottom_icon_img = screenshot.crop(right_bottom_icon_bbox)
    is_full = any(
        template.match(right_bottom_icon_img, templates.SINGLE_MODE_AOHARU_SOUL_FULL)
    )
    if is_full:
        return 1

    soul_bbox = (
        icon_bbox[0] - rp.vector(35, 540),
        icon_bbox[1] + rp.vector(33, 540),
        icon_bbox[0] + rp.vector(2, 540),
        icon_bbox[3] - rp.vector(0, 540),
    )
    img = screenshot.crop(soul_bbox)
    img = imagetools.resize(img, height=40)
    cv_img = imagetools.cv_image(img)
    blue_outline_img = imagetools.constant_color_key(
        cv_img,
        (251, 109, 0),
        (255, 178, 99),
        threshold=0.6,
    )
    bg_mask1 = imagetools.border_flood_fill(blue_outline_img)
    fg_mask1 = 255 - bg_mask1
    masked_img = cv2.copyTo(cv_img, fg_mask1)
    shapened_img = imagetools.mix(imagetools.sharpen(masked_img, 1), masked_img, 0.5)
    white_outline_img = imagetools.constant_color_key(
        shapened_img,
        (255, 255, 255),
        (252, 251, 251),
        (248, 227, 159),
        (254, 245, 238),
        (253, 233, 218),
        threshold=0.9,
    )
    bg_mask2 = imagetools.border_flood_fill(white_outline_img)
    fg_mask2 = 255 - bg_mask2
    imagetools.fill_area(fg_mask2, (0,), size_lt=100)
    fg_img = cv2.copyTo(masked_img, fg_mask2)
    empty_mask = imagetools.constant_color_key(fg_img, (126, 121, 121))
    if os.getenv("DEBUG") == __name__ + "[partner]":
        _LOGGER.debug(
            "soul: img=%s",
            imagetools.image_hash(img, save_path=training.g.image_path),
        )
        cv2.imshow("soul", cv_img)
        cv2.imshow("sharpened", shapened_img)
        cv2.imshow("right_bottom_icon", imagetools.cv_image(right_bottom_icon_img))
        cv2.imshow("blue_outline", blue_outline_img)
        cv2.imshow("white_outline", white_outline_img)
        cv2.imshow("fg_mask1", fg_mask1)
        cv2.imshow("fg_mask2", fg_mask2)
        cv2.imshow("empty_mask", empty_mask)
        cv2.waitKey()
        cv2.destroyAllWindows()

    fg_avg = np.average(fg_mask2)
    if fg_avg < 100:
        return -1
    empty_avg = np.average(empty_mask)
    outline_avg = 45
    return max(0, min(1, 1 - (empty_avg / (fg_avg - outline_avg))))


def _recognize_partner_icon(
    ctx: Context, img: Image, bbox: Tuple[int, int, int, int]
) -> Optional[training.Partner]:
    rp = mathtools.ResizeProxy(img.width)
    icon_img = img.crop(bbox)
    if os.getenv("DEBUG") == __name__ + "[partner]":
        _LOGGER.debug(
            "icon: img=%s",
            imagetools.image_hash(icon_img, save_path=training.g.image_path),
        )
        cv2.imshow("icon_img", imagetools.cv_image(icon_img))
        cv2.waitKey()
        cv2.destroyAllWindows()
    level = _recognize_partner_level(rp, icon_img)

    soul = -1
    has_training = False
    has_soul_burst = False
    if ctx.scenario == ctx.SCENARIO_AOHARU:
        has_soul_burst = _recognize_has_soul_burst(ctx, rp, icon_img)
        if has_soul_burst:
            has_training = True
            soul = 1
        else:
            has_training = _recognize_has_training(ctx, rp, icon_img)
            soul = _recognize_soul(rp, img, bbox)

    if level < 0 and soul < 0:
        return None
    self = Partner.new()
    self.icon_bbox = bbox
    self.level = level
    self.soul = soul
    self.has_hint = _recognize_has_hint(rp, icon_img)
    self.has_training = has_training
    self.has_soul_burst = has_soul_burst
    if self.has_soul_burst:
        self.has_training = True
        self.soul = 1
    self.type = _recognize_type_color(rp, icon_img)
    if soul >= 0 and self.type == Partner.TYPE_OTHER:
        self.type = Partner.TYPE_TEAMMATE
    _LOGGER.debug("partner: %s", self)
    return self


def _recognize_partners(ctx: Context, img: Image) -> Iterator[training.Partner]:
    rp = mathtools.ResizeProxy(img.width)

    icon_bbox, icon_y_offset = {
        ctx.SCENARIO_URA: (
            rp.vector4((448, 146, 516, 220), 540),
            rp.vector(90, 540),
        ),
        ctx.SCENARIO_AOHARU: (
            rp.vector4((448, 147, 516, 220), 540),
            rp.vector(86, 540),
        ),
        ctx.SCENARIO_CLIMAX: (
            rp.vector4((448, 147, 516, 220), 540),
            rp.vector(90, 540),
        ),
    }[ctx.scenario]
    icons_bottom = rp.vector(578, 540)
    while icon_bbox[2] < icons_bottom:
        v = _recognize_partner_icon(ctx, img, icon_bbox)
        if not v:
            break
        yield v
        icon_bbox = (
            icon_bbox[0],
            icon_bbox[1] + icon_y_offset,
            icon_bbox[2],
            icon_bbox[3] + icon_y_offset,
        )


_Vector4 = Tuple[int, int, int, int]


def _effect_recognitions(
    ctx: Context, rp: mathtools.ResizeProxy
) -> Iterator[
    Tuple[
        Tuple[_Vector4, _Vector4, _Vector4, _Vector4, _Vector4, _Vector4],
        Callable[[Image], int],
    ]
]:
    def _bbox_groups(t: int, b: int):
        return (
            rp.vector4((18, t, 104, b), 540),
            rp.vector4((104, t, 190, b), 540),
            rp.vector4((190, t, 273, b), 540),
            rp.vector4((273, t, 358, b), 540),
            rp.vector4((358, t, 441, b), 540),
            rp.vector4((448, t, 521, b), 540),
        )

    if ctx.scenario == ctx.SCENARIO_URA:
        yield _bbox_groups(582, 616), _recognize_base_effect
    elif ctx.scenario == ctx.SCENARIO_AOHARU:
        yield _bbox_groups(597, 625), _recognize_base_effect
        yield _bbox_groups(570, 595), _recognize_red_effect
    elif ctx.scenario == ctx.SCENARIO_CLIMAX:
        yield _bbox_groups(595, 623), _recognize_base_effect
        yield _bbox_groups(568, 593), _recognize_red_effect
    else:
        raise NotImplementedError(ctx.scenario)


def _recognize_training(ctx: Context, img: Image) -> Training:
    if training.g.image_path:
        image_id = imagetools.md5(
            imagetools.cv_image(img.convert("RGB")),
            save_path=training.g.image_path,
            save_mode="RGB",
        )
        _LOGGER.debug("from_training_scene: image=%s", image_id)
    rp = mathtools.ResizeProxy(img.width)

    self = Training.new()
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

    for bbox_group, recognize in _effect_recognitions(ctx, rp):
        self.speed += recognize(img.crop(bbox_group[0]))
        self.stamina += recognize(img.crop(bbox_group[1]))
        self.power += recognize(img.crop(bbox_group[2]))
        self.guts += recognize(img.crop(bbox_group[3]))
        self.wisdom += recognize(img.crop(bbox_group[4]))
        self.skill += recognize(img.crop(bbox_group[5]))

    # TODO: recognize vitality
    # plugin hook
    self._use_estimate_vitality = True  # type: ignore
    self.vitality = _estimate_vitality(ctx, self)
    self.failure_rate = _recognize_failure_rate(rp, self, img)
    self.partners = tuple(_recognize_partners(ctx, img))

    return self


class TrainingScene(Scene):
    @classmethod
    def name(cls):
        return "single-mode-training"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        CommandScene.enter(ctx)
        action.wait_tap_image(templates.SINGLE_MODE_COMMAND_TRAINING)
        action.wait_image(_TRAINING_CONFIRM)
        return cls()

    def __init__(self):
        self.trainings: Tuple[Training, ...] = ()

    def recognize(self) -> None:
        # TODO: remove old api at next major version
        import warnings

        warnings.warn(
            "use recognize_v2 instead",
            DeprecationWarning,
        )
        ctx = Context()
        ctx.scenario = ctx.SCENARIO_URA
        return self.recognize_v2(ctx)

    def recognize_v2(self, ctx: Context) -> None:
        with futures.ThreadPoolExecutor() as pool:
            self.trainings = tuple(
                i.result()
                for i in [
                    pool.submit(_recognize_training, ctx, j)
                    for j in _iter_training_images()
                ]
            )
        assert len(set(i.type for i in self.trainings)) == 5, "duplicated trainings"
        ctx.trainings = self.trainings
        if not ctx.is_summer_camp:
            ctx.training_levels = {i.type: i.level for i in self.trainings}
