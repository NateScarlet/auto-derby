from auto_derby import single_mode, action, template, templates
import auto_derby


def play(ctx: single_mode.Context):
    _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
    action.swipe(pos, duration=2.8)
    _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
    action.swipe(pos, duration=1.8)
    _, pos = action.wait_image(templates.SINGLE_MODE_CRANE_GAME_BUTTON)
    action.swipe(pos, duration=1.2)
    action.wait_tap_image(templates.GREEN_OK_BUTTON)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.on_single_mode_crane_game = play


auto_derby.plugin.register(__name__, Plugin())
