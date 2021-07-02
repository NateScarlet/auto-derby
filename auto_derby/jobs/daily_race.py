# -*- coding=UTF-8 -*-
# pyright: strict

from typing import Text

from .. import action, config, templates


def daily_race(race_name: Text):
    while True:
        tmpl, pos = action.wait_image(
            templates.DAILY_RACE_TICKET_NOT_ENOUGH,
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.DAILY_RACE,
            templates.DAILY_RACE_HARD,
            templates.RACE_START_BUTTON,
            templates.RACE_CONFIRM_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.RACE_RESULT_BUTTON,
            templates.RACE_AGAIN_BUTTON,
            templates.RACE_RESULT_NO1,
            templates.RACE_RESULT_NO2,
            templates.RACE_RESULT_NO3,
            templates.RACE_RESULT_NO4,
            templates.RACE_RESULT_NO5,
            templates.RACE_RESULT_NO6,
            templates.RACE_RESULT_NO8,
            templates.RACE_RESULT_NO10,
            race_name,
            templates.RACE_BUTTON,
            templates.LIMITED_SALE_OPEN,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            pass
        elif name == templates.DAILY_RACE_TICKET_NOT_ENOUGH:
            break
        elif name == templates.LIMITED_SALE_OPEN:
            config.on_limited_sale()
        else:
            action.tap(pos)
