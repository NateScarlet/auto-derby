# -*- coding=UTF-8 -*-
# pyright: strict

from auto_derby import imagetools
from .. import action, templates, template

from . import limited_sale


def team_race():
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.TEAM_RACE_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.TEAM_RACE_CHOOSE_COMPETITOR,
            templates.RACE_START_BUTTON,
            templates.TEAM_RACE_RESULT_BUTTON,
            templates.RACE_AGAIN_BUTTON,
            templates.TEAM_RACE_WIN,
            templates.TEAM_RACE_LOSE,
            templates.TEAM_RACE_HIGH_SCORE_UPDATED,
            templates.TEAM_RACE_NEXT_BUTTON,
            templates.LIMITED_SALE_OPEN,
            templates.RP_NOT_ENOUGH,
        )
        name = tmpl.name
        if name == templates.TEAM_RACE_CHOOSE_COMPETITOR:
            granted_reward_pos = (300, 300)
            has_granted_reward = imagetools.compare_color(
                (0, 0, 0), 
                template.screenshot().getpixel(granted_reward_pos),
            ) > 0.99 and False # TODO: need color sample
            if has_granted_reward:
                action.click(granted_reward_pos)
                action.wait_click_image(templates.GREEN_NEXT_BUTTON)
                action.wait_click_image(templates.RACE_ITEM_PARFAIT)
            else:
                x, y = pos
                y += 300
                action.click((x, y))
        elif name == templates.TEAM_RACE_NEXT_BUTTON:
            action.click(pos)
        elif name == templates.RP_NOT_ENOUGH:
            break
        elif name == templates.CONNECTING:
            pass
        elif name == templates.LIMITED_SALE_OPEN:
            limited_sale.buy_everything()
        else:
            action.click(pos)
