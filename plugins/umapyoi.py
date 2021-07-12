from auto_derby import template
import auto_derby
from auto_derby import single_mode, action, templates
import time


def _is_landscape() -> bool:
    img = template.screenshot()
    return img.width > img.height


def _handle_live(ctx: single_mode.Context) -> None:
    if ctx.date[0] != 4:
        return

    action.wait_tap_image(templates.SINGLE_MODE_LIVE_BUTTON)
    action.wait_tap_image(templates.GREEN_OK_BUTTON)
    time.sleep(10)  # wait possible orientation change.
    while _is_landscape():
        time.sleep(1)
    action.reset_client_size()


class Plugin(auto_derby.Plugin):
    """Auto play umapyoi legend."""

    def install(self) -> None:
        auto_derby.config.on_single_mode_live = _handle_live


auto_derby.plugin.register(__name__, Plugin())
