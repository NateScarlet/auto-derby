# -*- coding=UTF-8 -*-
# pyright: strict


from .. import action, templates


ALL_OPTIONS = [
    templates.NURTURING_OPTION1,
    templates.NURTURING_OPTION2,
]


def nurturing():
    while True:
        name, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.NURTURING_FANS_NOT_ENOUGH,
            templates.NURTURING_FINISH_BUTTON,
            templates.NURTURING_TARGET_RACE_BANNER,
            templates.NURTURING_OPTION1,
            templates.NURTURING_OPTION2,
            templates.NURTURING_REST,
            templates.GREEN_NEXT_BUTTON,
        )
        if name == templates.CONNECTING:
            pass
        elif name == templates.NURTURING_FANS_NOT_ENOUGH:
            action.click_image(templates.CANCEL_BUTTON)
        elif name == templates.NURTURING_FINISH_BUTTON:
            break
        elif name == templates.NURTURING_TARGET_RACE_BANNER:
            x, y = pos
            y += 60
            action.click((x,y))
            action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
            action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
            action.wait_click_image(templates.RACE_RESULT_BUTTON)

            _, pos = action.wait_image(
                templates.RACE_RESULT_NO1,
            )
            action.click(pos)
            action.wait_click_image(templates.NURTURING_RACE_NEXT_BUTTON)
        elif name == templates.NURTURING_REST:
            if action.count_image(templates.NURTURING_MOOD_NORMAL):
                action.click_image(templates.NURTURING_GO_OUT)
            else:
                action.click(pos)
        else:
            action.click(pos)
