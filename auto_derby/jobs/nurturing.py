# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
import cv2
import numpy as np

import time
from typing import Tuple

from auto_derby import imagetools, nurturing_choice, template
from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from .. import action, ocr, templates


def _handle_training():
    tmpl, pos = action.wait_image(
        template.Specification(templates.NURTURING_STATUS_F,
                               templates.NURTURING_STATUS_SPEED_POS),
        template.Specification(templates.NURTURING_STATUS_F,
                               templates.NURTURING_STATUS_STAMINA_POS),
        template.Specification(templates.NURTURING_STATUS_E,
                               templates.NURTURING_STATUS_SPEED_POS),
        template.Specification(templates.NURTURING_STATUS_E,
                               templates.NURTURING_STATUS_STAMINA_POS),
        template.Specification(templates.NURTURING_STATUS_D,
                               templates.NURTURING_STATUS_SPEED_POS),
        template.Specification(templates.NURTURING_STATUS_D,
                               templates.NURTURING_STATUS_STAMINA_POS),
        template.Specification(templates.NURTURING_STATUS_F,
                               templates.NURTURING_STATUS_INTELLIGENCE_POS),
        template.Specification(templates.NURTURING_STATUS_F,
                               templates.NURTURING_STATUS_POWER_POS),
        template.Specification(templates.NURTURING_STATUS_C,
                               templates.NURTURING_STATUS_SPEED_POS),
        template.Specification(templates.NURTURING_STATUS_C,
                               templates.NURTURING_STATUS_STAMINA_POS),
        template.Specification(templates.NURTURING_STATUS_E,
                               templates.NURTURING_STATUS_INTELLIGENCE_POS),
        template.Specification(templates.NURTURING_STATUS_E,
                               templates.NURTURING_STATUS_POWER_POS),
        template.Specification(templates.NURTURING_STATUS_F,
                               templates.NURTURING_STATUS_PERSEVERANCE_POS),
        template.Specification(templates.NURTURING_STATUS_B,
                               templates.NURTURING_STATUS_SPEED_POS),
        template.Specification(templates.NURTURING_STATUS_D,
                               templates.NURTURING_STATUS_POWER_POS),
        template.Specification(templates.NURTURING_STATUS_C,
                               templates.NURTURING_STATUS_POWER_POS),
        template.Specification(templates.NURTURING_STATUS_B,
                               templates.NURTURING_STATUS_POWER_POS),
    )
    x, y = pos
    if tmpl.pos == templates.NURTURING_STATUS_SPEED_POS:
        x += 45
    elif tmpl.pos == templates.NURTURING_STATUS_STAMINA_POS:
        x += 60
    elif tmpl.pos == templates.NURTURING_STATUS_POWER_POS:
        x += 70
    elif tmpl.pos == templates.NURTURING_STATUS_PERSEVERANCE_POS:
        x += 75
    elif tmpl.pos == templates.NURTURING_STATUS_INTELLIGENCE_POS:
        x += 80

    action.drag((x, y), dy=100)  # select course
    action.click((x, y+100))


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


def _schedule_next_race():
    return


def _ocr_date(img: Image) -> Tuple[int, int, int]:
    text = ocr.text(
        image_from_array(
            cv2.threshold(
                1 - np.asarray(img.convert("L")),
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

    def update_by_command_scene(self, screnshot: Image) -> None:
        speed_bbox = (45, 553, 90, 572)
        stamina_bbox = (125, 553, 162, 572)
        power_bbox = (192, 553, 234, 572)
        perservance_bbox = (264, 553, 308, 572)
        intelligence_bbox = (337, 553, 381, 572)
        date_bbox = (10, 28, 140, 43)
        vitality_bbox = (148, 106, 327, 108)
        self.date = _ocr_date(screnshot.crop(date_bbox))
        self.speed = int(ocr.text(screnshot.crop(speed_bbox)))
        self.stamina = int(ocr.text(screnshot.crop(stamina_bbox)))
        self.power = int(ocr.text(screnshot.crop(power_bbox)))
        self.perservance = int(ocr.text(screnshot.crop(perservance_bbox)))
        self.intelligence = int(ocr.text(screnshot.crop(intelligence_bbox)))
        self.vitality = _recognize_vitality(screnshot.crop(vitality_bbox))

    def __str__(self):
        return (
            "Status<"
            f"date={self.date},"
            f"vitality={self.vitality*100:.1f}%,"
            f"spd={self.speed},"
            f"sta={self.stamina},"
            f"pow={self.power},"
            f"per={self.perservance},"
            f"int={self.intelligence}"
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
            templates.NURTURING_SCHEDULED_RACE_OPENING,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            pass
        elif name == templates.NURTURING_FANS_NOT_ENOUGH:
            action.click_image(templates.CANCEL_BUTTON)
        elif name == templates.NURTURING_FINISH_BUTTON:
            break
        elif name == templates.NURTURING_FORMAL_RACE_BANNER:
            x, y = pos
            y += 60
            action.click((x, y))
            _handle_race()
            _schedule_next_race()
        elif name == templates.NURTURING_URA_FINALS:
            action.click(pos)
            _handle_race()
        elif name == templates.NURTURING_SCHEDULED_RACE_OPENING:
            action.click_image(templates.NURTURING_GO_TO_SCHEDULED_RACE_BUTTON)
            _handle_race()
            _schedule_next_race()
        elif name == templates.NURTURING_COMMAND_TRAINING:
            ctx.update_by_command_scene(template.screenshot())
            print(ctx)  # TODO: use status
            if ctx.vitality <= 0.5:
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
                _handle_training()
        elif name == templates.NURTURING_OPTION1:
            _handle_option()
        else:
            action.click(pos)
