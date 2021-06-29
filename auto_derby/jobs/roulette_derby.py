# -*- coding=UTF-8 -*-
# pyright: strict


from .. import action, templates
import time


def roulette_derby():
    while True:
        tmpl, pos = action.wait_image(
            templates.CLOSE_BUTTON,
            templates.ROULETTE_DERBY_TAP_BUTTON,
            templates.ROULETTE_DERBY_SKIP_BUTTON,
            templates.ROULETTE_DERBY_GET,
            templates.ROULETTE_DERBY_BINGO,
            templates.ROULETTE_DERBY_REWARD_TEXT,
            templates.ROULETTE_DERBY_TAP_BUTTON_DISABLED,
        )
        if tmpl.name == templates.ROULETTE_DERBY_TAP_BUTTON_DISABLED:
            # wait animation
            time.sleep(1)
            if not action.count_image(templates.ROULETTE_DERBY_TAP_BUTTON_DISABLED):
                continue
            return
        action.tap(pos)
