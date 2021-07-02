# -*- coding=UTF-8 -*-
# pyright: strict

from auto_derby import imagetools

from .. import action, config, template, templates


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
            templates.TEAM_RACE_DRAW,
            templates.TEAM_RACE_HIGH_SCORE_UPDATED,
            templates.TEAM_RACE_NEXT_BUTTON,
            templates.LIMITED_SALE_OPEN,
            templates.RP_NOT_ENOUGH,
        )
        name = tmpl.name
        if name == templates.TEAM_RACE_CHOOSE_COMPETITOR:
            rp = action.resize_proxy()
            granted_reward_pos = rp.vector2((358, 300), 466)
            granted_reward_pos_color = template.screenshot().getpixel(
                granted_reward_pos
            )

            has_granted_reward = (
                imagetools.compare_color((209, 43, 36), granted_reward_pos_color) > 0.99
                or imagetools.compare_color((255, 255, 255), granted_reward_pos_color)
                > 0.99
            )
            if has_granted_reward:
                action.tap(granted_reward_pos)
                action.wait_tap_image(templates.GREEN_NEXT_BUTTON)
                action.wait_tap_image(templates.RACE_ITEM_PARFAIT)
            else:
                x, y = pos
                y += 300
                action.tap((x, y))
        elif name == templates.TEAM_RACE_NEXT_BUTTON:
            action.tap(pos)
        elif name == templates.RP_NOT_ENOUGH:
            break
        elif name == templates.CONNECTING:
            pass
        elif name == templates.LIMITED_SALE_OPEN:
            config.on_limited_sale()
        else:
            action.tap(pos)
