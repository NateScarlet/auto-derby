# -*- coding=UTF-8 -*-
# pyright: strict

from .. import action, templates


def buy_everything():
    rp = action.resize_proxy()
    action.wait_click_image(templates.GO_TO_LIMITED_SALE)
    action.wait_image(templates.CLOSE_NOW_BUTTON)
    for _, pos in action.match_image_until_disappear(
        templates.EXCHANGE_BUTTON, sort=lambda x: sorted(x, key=lambda i: i[1][1])
    ):
        action.click(pos)
        action.wait_click_image(templates.EXCHANGE_CONFIRM_BUTTON)
        for _ in action.match_image_until_disappear(templates.CONNECTING):
            pass
        action.wait_click_image(templates.CLOSE_BUTTON)
        action.wait_image(templates.CLOSE_NOW_BUTTON)
        action.swipe(pos, dx=rp.vector(-80, 540))

    action.wait_click_image(templates.CLOSE_NOW_BUTTON)
    action.wait_click_image(templates.GREEN_OK_BUTTON)
    action.wait_image(templates.RETURN_BUTTON)
    for _, pos in action.match_image_until_disappear(templates.RETURN_BUTTON):
        action.click(pos)
