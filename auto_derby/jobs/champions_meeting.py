# -*- coding=UTF-8 -*-
# pyright: strict

import time

from .. import action, templates


def champions_meeting():
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.SKIP_BUTTON,
            templates.RACE_START_BUTTON,
            templates.RACE_CONFIRM_BUTTON,
            templates.CHAMPIONS_MEETING_ENTRY_BUTTON_DISABLED,
            templates.CHAMPIONS_MEETING_ENTRY_BUTTON,
            templates.CHAMPIONS_MEETING_CONFIRM_TITLE,
            templates.CHAMPIONS_MEETING_REGISTER_BUTTON,
            templates.CHAMPIONS_MEETING_RACE_BUTTON,
            templates.CHAMPIONS_MEETING_REWARD_BUTTON,
            templates.LEGEND_RACE_START_BUTTON,
        )
        name = tmpl.name
        if name == templates.CONNECTING:
            time.sleep(1)
        elif name == templates.CHAMPIONS_MEETING_ENTRY_BUTTON_DISABLED:
            exit(0)
        elif name == templates.CHAMPIONS_MEETING_CONFIRM_TITLE:
            time.sleep(1)
            if not action.count_image(templates.CHAMPIONS_MEETING_USING_TICKET):
                exit(0)
            action.wait_tap_image(templates.GREEN_OK_BUTTON)
        else:
            action.tap(pos)
