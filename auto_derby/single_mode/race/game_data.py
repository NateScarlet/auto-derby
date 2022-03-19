# pyright: strict
# -*- coding=UTF-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Text, Tuple

if TYPE_CHECKING:
    from ..context import Context

import json
import logging
import os
import warnings

import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps

from ... import imagetools, mathtools, ocr, template, templates, texttools
from .globals import g
from .race import Race

LOGGER = logging.getLogger(__name__)


class _g:
    loaded_data_path = ""


def _iter_races():
    with open(g.data_path, "r", encoding="utf-8") as f:
        for line in f:
            yield Race.new().from_dict(json.loads(line))


def _load_legacy_json():
    warnings.warn(
        "json race data support will be removed at next major version, use jsonl instead",
        DeprecationWarning,
    )
    with open(g.data_path, "r", encoding="utf-8") as f:
        g.races = tuple(Race.new().from_dict(i) for i in json.load(f))


def reload() -> None:
    if g.data_path.endswith(".json"):
        _load_legacy_json()
        return
    g.races = tuple(_iter_races())
    _g.loaded_data_path = g.data_path


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()


def find_by_date(date: Tuple[int, int, int]) -> Iterator[Race]:
    reload_on_demand()
    year, month, half = date
    for i in g.races:
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
        if i.is_avaliable(ctx) == False:
            continue
        # target race should be excluded when finding available race
        if i.is_target_race(ctx):
            continue
        yield i


def _recognize_fan_count(img: PIL.Image.Image) -> int:
    cv_img = imagetools.cv_image(imagetools.resize(img.convert("L"), height=32))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 60, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text.rstrip("人").replace(",", ""))


_TURN_TRACK_SPEC = {
    "左·内": (Race.TURN_LEFT, Race.TRACK_IN),
    "右·内": (Race.TURN_RIGHT, Race.TRACK_IN),
    "左": (Race.TURN_LEFT, Race.TRACK_MIDDLE),
    "右": (Race.TURN_RIGHT, Race.TRACK_MIDDLE),
    "左·外": (Race.TURN_LEFT, Race.TRACK_OUT),
    "右·外": (Race.TURN_RIGHT, Race.TRACK_OUT),
    "直線": (Race.TURN_NONE, Race.TRACK_MIDDLE),
    "右·外→内": (Race.TURN_RIGHT, Race.TRACK_OUT_TO_IN),
}


def _recognize_spec(img: PIL.Image.Image) -> Tuple[Text, int, int, int, int]:
    cv_img = imagetools.cv_image(imagetools.resize(img.convert("L"), height=32))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 60, 255, cv2.THRESH_BINARY_INV)
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

    turn, track = _TURN_TRACK_SPEC[texttools.choose(text, _TURN_TRACK_SPEC.keys())]

    return stadium, ground, distance, turn, track


def _recognize_grade(
    img: PIL.Image.Image, pos: Tuple[int, int], radius: int = 2
) -> Tuple[int, ...]:
    cv_img = imagetools.cv_image(img)
    # TODO: get dominance color, then find most similar match instead
    if imagetools.compare_color_near(cv_img, pos, (0, 140, 215), radius=radius) > 0.9:
        # EX(URA)
        return (Race.GRADE_G1,)
    if imagetools.compare_color_near(cv_img, pos, (228, 133, 54), radius=radius) > 0.8:
        return (Race.GRADE_G1,)
    if imagetools.compare_color_near(cv_img, pos, (129, 85, 244), radius=radius) > 0.8:
        return (Race.GRADE_G2,)
    if imagetools.compare_color_near(cv_img, pos, (85, 187, 57), radius=radius) > 0.8:
        return (Race.GRADE_G3,)
    if imagetools.compare_color_near(cv_img, pos, (5, 169, 252), radius=radius) > 0.8:
        return Race.GRADE_OP, Race.GRADE_PRE_OP
    if imagetools.compare_color_near(cv_img, pos, (8, 203, 148), radius=radius) > 0.8:
        return Race.GRADE_DEBUT, Race.GRADE_NOT_WINNING
    raise ValueError("_recognize_grade: unknown grade color: %s" % (img.getpixel(pos),))


def _match_scenario(ctx: Context, race: Race) -> bool:

    if ctx.scenario != ctx.SCENARIO_CLIMAX and race.name.startswith("トゥインクルスタークライマックス"):
        return False
    if ctx.scenario == ctx.SCENARIO_CLIMAX and race.name.startswith("URAファイナルズ"):
        return False
    return True


def _find_by_spec(
    ctx: Context,
    stadium: Text,
    ground: int,
    distance: int,
    turn: int,
    track: int,
    no1_fan_count: int,
    grades: Tuple[int, ...],
):
    full_spec = (stadium, ground, distance, turn, track, no1_fan_count)
    for i in find_by_date(ctx.date):
        if i.grade not in grades:
            continue
        if not _match_scenario(ctx, i):
            continue
        if full_spec == (
            i.stadium,
            i.ground,
            i.distance,
            i.turn,
            i.track,
            i.fan_counts[0],
        ):
            yield i


def find_by_race_detail_image(ctx: Context, screenshot: PIL.Image.Image) -> Race:
    rp = mathtools.ResizeProxy(screenshot.width)

    grade_color_pos = rp.vector2((45, 92), 466)
    spec_bbox = rp.vector4((27, 260, 302, 279), 466)
    _, no1_fan_count_pos = next(
        template.match(screenshot, templates.SINGLE_MODE_RACE_DETAIL_NO1_FAN_COUNT)
    )
    no1_fan_count_bbox = (
        rp.vector(150, 466),
        no1_fan_count_pos[1],
        rp.vector(400, 466),
        no1_fan_count_pos[1] + rp.vector(18, 466),
    )

    grades = _recognize_grade(
        screenshot,
        grade_color_pos,
    )
    stadium, ground, distance, turn, track = _recognize_spec(screenshot.crop(spec_bbox))
    no1_fan_count = _recognize_fan_count(screenshot.crop(no1_fan_count_bbox))

    full_spec = (
        stadium,
        ground,
        distance,
        turn,
        track,
        no1_fan_count,
        grades,
    )
    for i in _find_by_spec(ctx, *full_spec):
        LOGGER.info("image match: %s", i)
        return i

    raise ValueError("find_by_race_details_image: no race match spec: %s", full_spec)


def _spec_bbox(ctx: Context, rp: mathtools.ResizeProxy):
    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        return rp.vector4((221, 21, 477, 41), 492)
    return rp.vector4((221, 12, 488, 30), 492)


def _no1_fan_count_bbox(ctx: Context, rp: mathtools.ResizeProxy):
    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        return rp.vector4((208, 78, 361, 95), 492)
    return rp.vector4((207, 54, 360, 72), 492)


def _grade_color_pos(ctx: Context, rp: mathtools.ResizeProxy):
    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        return rp.vector2((198, 39), 540)
    return rp.vector2((198, 29), 540)


def _find_by_race_menu_item(ctx: Context, img: PIL.Image.Image) -> Iterator[Race]:
    rp = mathtools.ResizeProxy(img.width)
    spec_bbox = _spec_bbox(ctx, rp)
    no1_fan_count_bbox = _no1_fan_count_bbox(ctx, rp)
    grade_color_pos = _grade_color_pos(ctx, rp)

    stadium, ground, distance, turn, track = _recognize_spec(img.crop(spec_bbox))
    no1_fan_count = _recognize_fan_count(img.crop(no1_fan_count_bbox))
    grades = _recognize_grade(img, grade_color_pos)
    full_spec = (
        stadium,
        ground,
        distance,
        turn,
        track,
        no1_fan_count,
        grades,
    )
    match_count = 0
    for i in _find_by_spec(ctx, *full_spec):
        LOGGER.info("image match: %s", i)
        yield i
        match_count += 1
    if not match_count:
        raise ValueError("_find_by_race_menu_item: no race match spec: %s", full_spec)


def _menu_item_bbox(
    ctx: Context, fan_icon_pos: Tuple[int, int], rp: mathtools.ResizeProxy
):
    _, y = fan_icon_pos

    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        return (
            rp.vector(23, 540),
            y - rp.vector(72, 540),
            rp.vector(515, 540),
            y + rp.vector(33, 540),
        )

    return (
        rp.vector(23, 540),
        y - rp.vector(51, 540),
        rp.vector(515, 540),
        y + rp.vector(46, 540),
    )


def find_by_race_menu_image(
    ctx: Context, screenshot: PIL.Image.Image
) -> Iterator[Tuple[Race, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(screenshot.width)
    for _, pos in template.match(screenshot, templates.SINGLE_MODE_RACE_MENU_FAN_ICON):
        bbox = _menu_item_bbox(ctx, pos, rp)
        for i in _find_by_race_menu_item(ctx, screenshot.crop(bbox)):
            yield i, pos
