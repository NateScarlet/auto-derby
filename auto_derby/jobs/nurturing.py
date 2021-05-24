# -*- coding=UTF-8 -*-
# pyright: strict

import time

from auto_derby import template, nurturing_choice

from .. import action, templates


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
        template.Specification(templates.NURTURING_STATUS_C,
                               templates.NURTURING_STATUS_SPEED_POS),
        template.Specification(templates.NURTURING_STATUS_C,
                               templates.NURTURING_STATUS_STAMINA_POS),
        template.Specification(templates.NURTURING_STATUS_F,
                               templates.NURTURING_STATUS_PERSEVERANCE_POS),
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


def _handle_race():
    action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
    action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
    action.wait_click_image(templates.RACE_RESULT_BUTTON)

    _, pos = action.wait_image(
        templates.RACE_RESULT_NO1,
        templates.RACE_RESULT_NO2,
        templates.RACE_RESULT_NO3,
        templates.RACE_RESULT_NO4,
        templates.RACE_RESULT_NO8,
        templates.RACE_RESULT_NO10,
    )
    while True:
        time.sleep(1)
        if (
            action.click_image(templates.GREEN_NEXT_BUTTON) or
            action.click_image(templates.NURTURING_END_BUTTON)
        ):
            break
        action.click(pos)
    action.wait_click_image(templates.NURTURING_RACE_NEXT_BUTTON)


ALL_OPTIONS = [
    templates.NURTURING_OPTION1,
    templates.NURTURING_OPTION2,
    templates.NURTURING_OPTION3,
    templates.NURTURING_OPTION4,
    templates.NURTURING_OPTION5,
]


def _handle_option():
    event_name_img = template.screenshot().crop((75, 155, 305, 180))
    ans = nurturing_choice.get(event_name_img)
    action.click_image(ALL_OPTIONS[ans-1])


def nurturing():
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.NURTURING_TRAINING,
            templates.NURTURING_FANS_NOT_ENOUGH,
            templates.NURTURING_FINISH_BUTTON,
            templates.NURTURING_TARGET_RACE_BANNER,
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
            action.click_image(templates.CANCEL_BUTTON)
        elif name == templates.NURTURING_FINISH_BUTTON:
            break
        elif name == templates.NURTURING_TARGET_RACE_BANNER:
            x, y = pos
            y += 60
            action.click((x, y))
            _handle_race()
        elif name == templates.NURTURING_URA_FINALS:
            action.click(pos)
            _handle_race()
        elif name == templates.NURTURING_TRAINING:
            if action.count_image(templates.NURTURING_STAMINA_HALF_EMPTY):
                if action.click_image(template.Specification(templates.NURTURING_HEALTH_CARE, threshold=0.97)):
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
