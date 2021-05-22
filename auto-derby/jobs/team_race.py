# -*- coding=UTF-8 -*-
# pyright: strict

from .. import action, templates
import time
import win32gui

def team_race_once():
    while True:
        name, pos = action.wait_image(
            templates.TEAM_RACE_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.TEAM_RACE_CHOOSE_COMPETITOR,
            templates.TEAM_RACE_START_BUTTON,
            templates.TEAM_RACE_SEE_RESULT_BUTTON,
            templates.TEAM_RACE_WIN,
            templates.TEAM_RACE_LOSE,
            templates.TEAM_RACE_NEXT_BUTTON,
            templates.LIMITED_SALE_OPEN,
        )
        if name == templates.TEAM_RACE_CHOOSE_COMPETITOR:
            x, y = pos
            y += 300
            action.click((x, y))
        elif name == templates.TEAM_RACE_NEXT_BUTTON:
            action.click(pos)
            break
        elif name == templates.LIMITED_SALE_OPEN:
            win32gui.MessageBox(0, "自动终止", "限定商店出现", 0)
            # TODO: better handle
            exit(0)
        else:
            action.click(pos)

def team_race():
    while True:
        name, pos = action.wait_image(
            templates.TEAM_RACE_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.TEAM_RACE_CHOOSE_COMPETITOR,
            templates.TEAM_RACE_START_BUTTON,
            templates.TEAM_RACE_SEE_RESULT_BUTTON,
            templates.TEAM_RACE_WIN,
            templates.TEAM_RACE_LOSE,
            templates.TEAM_RACE_NEXT_BUTTON,
            templates.LIMITED_SALE_OPEN,
            templates.RP_NOT_ENOUGH,
        )
        if name == templates.TEAM_RACE_CHOOSE_COMPETITOR:
            x, y = pos
            y += 300
            action.click((x, y))
        elif name == templates.TEAM_RACE_NEXT_BUTTON:
            action.click(pos)
        elif name == templates.RP_NOT_ENOUGH:
            break
        elif name == templates.LIMITED_SALE_OPEN:
            # TODO: better handle
            win32gui.MessageBox(0, "自动终止", "限定商店出现", 0)
            break
        else:
            action.click(pos)
