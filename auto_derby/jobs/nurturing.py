# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import time

from PIL.Image import Image

from auto_derby import template, nurturing_choice

from .. import action, templates, ocr


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
    pass

class Status:
    
    def __init__(self) -> None:
        self.speed = 0
        self.stamina = 0
        self.power = 0
        self.perservance = 0
        self.intelligence = 0

    @classmethod
    def from_screen(cls, img: Image) -> Status:
        speed_bbox = (45, 553, 90, 572)
        stamina_bbox = (125, 553, 162, 572)
        power_bbox = (192, 553, 234, 572)
        perservance_bbox = (264, 553, 308, 572)
        intelligence_bbox = (337, 553, 381, 572)
        self = cls()
        self.speed = int(ocr.text(template.screenshot().crop(speed_bbox)))
        self.stamina = int(ocr.text(template.screenshot().crop(stamina_bbox)))
        self.power = int(ocr.text(template.screenshot().crop(power_bbox)))
        self.perservance = int(ocr.text(template.screenshot().crop(perservance_bbox)))
        self.intelligence = int(ocr.text(template.screenshot().crop(intelligence_bbox)))
        return self

    def __str__(self):
        return f"Status<spd={self.speed}, sta={self.stamina}, pow={self.power}, per={self.perservance}, int={self.intelligence}>"


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
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.NURTURING_TRAINING,
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
        elif name == templates.NURTURING_TRAINING:
            status = Status.from_screen(template.screenshot())
            print(status) # TODO: use status
            if action.count_image(templates.NURTURING_VITALITY_HALF_EMPTY):
                if action.click_image(templates.NURTURING_HEALTH_CARE):
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
                        templates.NURTURING_GO_OUT,
                        templates.NURTURING_SUMMER_REST,
                    )
                    action.click(pos)
                else:
                    _, pos = action.wait_image(
                        templates.NURTURING_REST,
                        templates.NURTURING_SUMMER_REST,
                    )
                    action.click(pos)
            else:
                action.click(pos)
                _handle_training()
        elif name == templates.NURTURING_OPTION1:
            _handle_option()
        else:
            action.click(pos)
