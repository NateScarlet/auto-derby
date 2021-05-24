# -*- coding=UTF-8 -*-
# pyright: strict

from auto_derby import window
from .. import action, templates


def legend_race():
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.TEAM_RACE_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.RACE_START_BUTTON,
            templates.LEGEND_RACE_RACE_BUTTON,
            templates.LEGEND_RACE_START_BUTTON,
            templates.LEGEND_RACE_CONFIRM_BUTTON,
            templates.SKIP_BUTTON,
            templates.LIMITED_SALE_OPEN,
            templates.LEGEND_RACE_REWARD,
            templates.LEGEND_RACE_COLLECT_ALL_REWARD,
        )
        name = tmpl.name
        if name == templates.TEAM_RACE_CHOOSE_COMPETITOR:
            if action.click_image(templates.TEAM_RACE_GUARANTEED_WIN_REWARD):
                action.wait_click_image(templates.GREEN_NEXT_BUTTON)
                action.wait_click_image(templates.RACE_ITEM_PARFAIT)
            else:
                x, y = pos
                y += 300
                action.click((x, y))
        elif name == templates.TEAM_RACE_NEXT_BUTTON:
            action.click(pos)
        elif name == templates.CONNECTING:
            pass
        elif name == templates.LIMITED_SALE_OPEN:
            # TODO: better handle
            window.info("限定商店出现\n自动终止")
            break
        elif name == templates.LEGEND_RACE_COLLECT_ALL_REWARD:
            action.click(pos)
            return
        else:
            action.click(pos)
