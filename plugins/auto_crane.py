import time

import auto_derby
from auto_derby import action, single_mode, templates


def play(ctx: single_mode.Context):
    for duration in (2, 1.6, 1):
        _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
        time.sleep(3)
        _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
        action.swipe(pos, duration=duration)
    action.wait_tap_image(templates.GREEN_TIGHT_OK_BUTTON)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.on_single_mode_crane_game = play


auto_derby.plugin.register(__name__, Plugin())
