# -*- coding=UTF-8 -*-
# pyright: strict

from .. import action, config, templates
from ..scenes.scene import Scene
from ..scenes.team_race import CompetitorMenuScene
from ..scenes.unknown import UnknownScene


class _Context:
    def __init__(self):
        self.scene: Scene = UnknownScene()


def team_race():
    ctx = _Context()
    while True:
        tmpl, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.TEAM_RACE_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.TEAM_RACE_CHOOSE_COMPETITOR,
            templates.RACE_START_BUTTON,
            templates.TEAM_RACE_ALL_RACE_RESULT_BUTTON,
            templates.TEAM_RACE_WHITE_SHORT_VERSION_BUTTON,
            templates.TEAM_RACE_RESULT_BUTTON,
            templates.RACE_AGAIN_BUTTON,
            templates.TEAM_RACE_WIN,
            templates.TEAM_RACE_LOSE,
            templates.TEAM_RACE_DRAW,
            templates.TEAM_RACE_HIGH_SCORE_UPDATED,
            templates.TEAM_RACE_NEXT_BUTTON,
            templates.LIMITED_SALE_OPEN,
            templates.SKIP_BUTTON,
            templates.RP_NOT_ENOUGH,
        )
        name = tmpl.name
        if name == templates.TEAM_RACE_CHOOSE_COMPETITOR:
            scene = CompetitorMenuScene.enter(ctx)
            granted_reward_pos = scene.locate_granted_reward()
            if granted_reward_pos:
                action.tap(granted_reward_pos)
                UnknownScene.enter(ctx)
                action.wait_tap_image(templates.GREEN_NEXT_BUTTON)
                action.wait_tap_image(templates.RACE_ITEM_PARFAIT)
            else:
                scene.choose(ctx, 1)
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
