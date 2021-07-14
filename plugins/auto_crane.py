import time

import auto_derby
from auto_derby import action, single_mode, templates


def play(ctx: single_mode.Context):
    _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
    action.swipe(pos, duration=2.8)
    time.sleep(1)
    _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
    action.swipe(pos, duration=1.8)
    time.sleep(1)
    _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
    action.swipe(pos, duration=1.2)
    time.sleep(1)
    action.wait_tap_image(templates.GREEN_OK_BUTTON)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.on_single_mode_crane_game = play


auto_derby.plugin.register(__name__, Plugin())
