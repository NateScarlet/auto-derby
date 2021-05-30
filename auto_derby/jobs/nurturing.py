# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
import cv2
import numpy as np

import time
from typing import List, Text, Tuple

from auto_derby import imagetools, nurturing_choice, template
from PIL.Image import Image
import PIL.ImageOps
from PIL.Image import fromarray as image_from_array

from .. import action, ocr, templates

import logging
LOGGER = logging.getLogger(__name__)


def _interpolate(value: int, value_map: Tuple[Tuple[int, float], ...]) -> float:
    if len(value_map) == 0:
        return 0
    if len(value_map) == 1:
        return value_map[0][1]
    low = (0, 0.0)
    high = (0, 0.0)
    for v, w in value_map:
        if v >= value:
            high = (v, w)
            break
        low = (v, w)
    v1, w1 = low
    v2, w2 = high
    if w2 == w1 or v1 == v2:
        return w2
    pos = (value - v1) / (v2 - v1)
    weight = w1 + (w2 - w1) * pos
    return weight


def _training_single_score(current: int, delta: int, value_map: Tuple[Tuple[int, float], ...]) -> float:

    ret = 0
    for i in range(current, current+delta):
        ret += _interpolate(
            i,
            value_map
        )
    return ret


def _training_score(ctx: Context, training: Training) -> float:
    spd = _training_single_score(
        ctx.speed,
        training.speed,
        (
            (0, 2.0),
            (300, 1.0),
            (600, 0.8),
            (900, 0.6),
            (1100, 0.5),
        )
    )

    sta = _training_single_score(
        ctx.stamina,
        training.stamina,
        (
            (0, 2.0),
            (300, ctx.speed / 600 + 0.3 *
             ctx.date[0] if ctx.speed > 600 else 1.0),
            (600, ctx.speed / 900 * 0.6 + 0.1 *
             ctx.date[0] if ctx.speed > 900 else 0.6),
            (900, ctx.speed / 900 * 0.3),
        )
    )
    pow = _training_single_score(
        ctx.power,
        training.power,
        (
            (0, 1.0),
            (300, 0.2 + ctx.speed / 600),
            (600, 0.1 + ctx.speed / 900),
            (900, ctx.speed / 900 / 3),
        )
    )
    per = _training_single_score(
        ctx.perservance,
        training.perservance,
        (
            (0, 2.0),
            (300, 1.0),
            (600, 0.1),
        ) if ctx.speed > 400 / 24 * ctx.turn_count() else (
            (0, 2.0),
            (300, 0.5),
        )
    )
    int_ = _training_single_score(
        ctx.intelligence,
        training.intelligence,
        (
            (0, 3.0),
            (300, 1.0),
            (600, 0.3),
        ) if ctx.vitality < 0.9 else (
            (0, 2.0),
            (300, 0.8),
            (600, 0.1),
        )
    )

    if ctx.vitality < 0.9:
        int_ += 5 if ctx.date[1:] in (
            (7, 1),
            (7, 2),
            (8, 1),
        ) else 3

    skill = training.skill * 0.5
    return spd + sta + pow + per + int_ + skill


def _handle_training(ctx: Context):
    trainings: List[Training] = []
    names = iter(["spd", "sta", "pow", "per", "int"])
    screenshots: List[Image] = []
    action.wait_image(
        template.Specification(
            templates.NURTURING_TRAINING_CONFIRM,
            threshold=0.8
        )
    )
    for x, y in (
        (78, 700),
        (158, 700),
        (234, 700),
        (314, 700),
        (402, 700),
    ):
        action.drag((x, y-100), dy=100)
        screenshots.append(template.screenshot())
    for name, screenshot in zip(names, screenshots):
        t = Training.from_traning_scene(screenshot)
        t.name = name
        trainings.append(t)

    expected_score = 15 + ctx.turn_count() * 10 / 24
    if ctx.vitality > 0.5:
        expected_score *= 0.5
    if ctx.turn_count() == 75:
        expected_score *= 0.1
    if ctx.date[1:] in (
        (6, 1),
    ) and ctx.vitality < 0.8:
        expected_score += 10
    if ctx.date[1:] in (
        (6, 2),
    ) and ctx.vitality < 0.9:
        expected_score += 20
    if ctx.date[1:] in (
        (7, 1),
        (7, 2),
        (8, 1),
    ) and ctx.vitality < 0.8:
        expected_score += 10
    if ctx.date in (
        (4, 0, 0)
    ):
        expected_score -= 20
    LOGGER.info("expected score:\t%2.2f", expected_score)
    trainings_with_score = [(i, _training_score(ctx, i)) for i in trainings]
    trainings_with_score = sorted(
        trainings_with_score, key=lambda x: x[1], reverse=True)
    for t, s in trainings_with_score:
        LOGGER.info("score:\t%2.2f:\t%s", s, t)
    training, score = trainings_with_score[0]
    if score < expected_score:
        # not worth, go rest
        action.click_image(templates.RETURN_BUTTON)
        _, pos = action.wait_image(
            templates.NURTURING_REST,  # TODO: rename this template
            templates.NURTURING_COMMAND_SUMMER_REST,
        ) if ctx.vitality < 0.8 else action.wait_image(
            templates.NURTURING_COMMAND_GO_OUT,
            templates.NURTURING_COMMAND_SUMMER_REST,
        )
        action.click(pos)
    x, y = training.confirm_position
    action.drag((x, y-100), dy=100)
    action.click((x, y))


def _handle_race_result():
    action.wait_click_image(templates.RACE_RESULT_BUTTON)

    _, pos = action.wait_image(
        templates.RACE_RESULT_NO1,
        templates.RACE_RESULT_NO2,
        templates.RACE_RESULT_NO3,
        templates.RACE_RESULT_NO4,
        templates.RACE_RESULT_NO5,
        templates.RACE_RESULT_NO6,
        templates.RACE_RESULT_NO8,
        templates.RACE_RESULT_NO10,
    )
    while True:
        time.sleep(1)
        if action.click_image(templates.GREEN_NEXT_BUTTON):
            break
        if action.click_image(templates.NURTURING_CONTINUE):
            _handle_race_result()
            return
        action.click(pos)


def _handle_race():
    action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
    action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
    _handle_race_result()
    action.wait_click_image(templates.NURTURING_RACE_NEXT_BUTTON)


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


class Context:

    def __init__(self) -> None:
        self.speed = 0
        self.stamina = 0
        self.power = 0
        self.perservance = 0
        self.intelligence = 0
        # (year, month, half-month), 1-base
        self.date = (0, 0, 0)
        self.vitality = 0.0
        self._extra_turn_count = 0

    def update_by_command_scene(self, screnshot: Image) -> None:
        speed_bbox = (45, 553, 90, 572)
        stamina_bbox = (125, 553, 162, 572)
        power_bbox = (192, 553, 234, 572)
        perservance_bbox = (264, 553, 308, 572)
        intelligence_bbox = (337, 553, 381, 572)
        date_bbox = (10, 28, 140, 43)
        vitality_bbox = (148, 106, 327, 108)
        self.date = _ocr_date(screnshot.crop(date_bbox))
        self.speed = int(
            ocr.text(PIL.ImageOps.invert(screnshot.crop(speed_bbox))))
        self.stamina = int(
            ocr.text(PIL.ImageOps.invert(screnshot.crop(stamina_bbox))))
        self.power = int(
            ocr.text(PIL.ImageOps.invert(screnshot.crop(power_bbox))))
        self.perservance = int(
            ocr.text(PIL.ImageOps.invert(screnshot.crop(perservance_bbox))))
        self.intelligence = int(
            ocr.text(PIL.ImageOps.invert(screnshot.crop(intelligence_bbox))))
        self.vitality = _recognize_vitality(screnshot.crop(vitality_bbox))

        if self.date in ((1, 0, 0), (4, 0, 0)):
            self._extra_turn_count += 1
        else:
            self._extra_turn_count = 0

    def __str__(self):
        return (
            "Context<"
            f"turn={self.turn_count()},"
            f"vit={self.vitality*100:.1f}%,"
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


def _ocr_traning_effect(img: Image) -> int:
    cv_img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    sharpened_img = cv2.filter2D(
        cv_img,
        8,
        np.array(
            (
                (0, -1, 0),
                (-1, 5, -1),
                (0, -1, 0),
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
        self.name: Text = ""
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
    def from_traning_scene(cls, img: Image) -> Training:
        self = cls()
        self.confirm_position = next(template.match(img, template.Specification(
            templates.NURTURING_TRAINING_CONFIRM,
            threshold=0.8
        )))[1]

        t, b = 505, 530
        self.speed = _ocr_traning_effect(img.crop((18, t, 91, b)))
        self.stamina = _ocr_traning_effect(img.crop((91, t, 163, b)))
        self.power = _ocr_traning_effect(img.crop((163, t, 237, b)))
        self.perservance = _ocr_traning_effect(img.crop((237, t, 309, b)))
        self.intelligence = _ocr_traning_effect(img.crop((309, t, 382, b)))
        self.skill = _ocr_traning_effect(img.crop((387, t, 450, b)))
        return self

    def __str__(self):
        return (
            "Traning<"
            f"name={self.name},"
            f"spd={self.speed},"
            f"sta={self.stamina},"
            f"pow={self.power},"
            f"per={self.perservance},"
            f"int={self.intelligence},"
            f"skill={self.skill}"
            ">"
        )


ALL_OPTIONS = [
    templates.NURTURING_OPTION1,
    templates.NURTURING_OPTION2,
    templates.NURTURING_OPTION3,
    templates.NURTURING_OPTION4,
    templates.NURTURING_OPTION5,
]


def _handle_option():
    ans = nurturing_choice.get(template.screenshot())
    action.click_image(ALL_OPTIONS[ans-1])


def nurturing():
    ctx = Context()
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.NURTURING_COMMAND_TRAINING,
            templates.NURTURING_FANS_NOT_ENOUGH,
            templates.NURTURING_FINISH_BUTTON,
            templates.NURTURING_FORMAL_RACE_BANNER,
            templates.NURTURING_RACE_NEXT_BUTTON,
            templates.NURTURING_OPTION1,
            templates.GREEN_NEXT_BUTTON,
            templates.NURTURING_URA_FINALS,
            templates.NURTURING_GENE_INHERIT,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            pass
        elif name == templates.NURTURING_FANS_NOT_ENOUGH:
            # TODO: handle this
            exit(1)
        elif name == templates.NURTURING_FINISH_BUTTON:
            break
        elif name == templates.NURTURING_FORMAL_RACE_BANNER:
            x, y = pos
            y += 60
            action.click((x, y))
            _handle_race()
        elif name == templates.NURTURING_URA_FINALS:
            action.click(pos)
            _handle_race()
        elif name == templates.NURTURING_COMMAND_TRAINING:
            ctx.update_by_command_scene(template.screenshot())
            LOGGER.info("update context: %s", ctx)
            if action.click_image(templates.NURTURING_SCHEDULED_RACE_OPENING_BANNER):
                action.wait_click_image(
                    templates.NURTURING_GO_TO_SCHEDULED_RACE_BUTTON)
                _handle_race()
                continue

            if ctx.turn_count() == 75:
                if ctx.vitality < 0.4:
                    action.click_image(templates.NURTURING_COMMAND_GO_OUT)
                else:
                    action.click(pos)
                    _handle_training(ctx)
            elif ctx.vitality <= 0.5:
                if action.click_image(templates.NURTURING_COMMAND_HEALTH_CARE):
                    time.sleep(2)
                    if action.count_image(templates.NURTURING_HEALTH_CARE_CONFIRM):
                        action.click_image(templates.GREEN_OK_BUTTON)
                    continue

                if action.count_image(
                    templates.NURTURING_MOOD_NORMAL,
                    templates.NURTURING_MOOD_BAD,
                    templates.NURTURING_MOOD_VERY_BAD,
                ):
                    _, pos = action.wait_image(
                        templates.NURTURING_COMMAND_GO_OUT,
                        templates.NURTURING_COMMAND_SUMMER_REST,
                    )
                    action.click(pos)
                else:
                    _, pos = action.wait_image(
                        templates.NURTURING_REST,
                        templates.NURTURING_COMMAND_SUMMER_REST,
                    )
                    action.click(pos)
            else:
                action.click(pos)
                _handle_training(ctx)
        elif name == templates.NURTURING_OPTION1:
            _handle_option()
        else:
            action.click(pos)
