import auto_derby
import PIL.Image
from auto_derby.clients import ADBClient


class ResizedADBClient(ADBClient):
    """Example adb client that all screenshot image is resized."""

    def screenshot(self) -> PIL.Image.Image:
        ret = super().screenshot()
        return ret.resize((1080, 1920))


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next_client = auto_derby.config.client

        def _client():
            if not auto_derby.config.ADB_ADDRESS:
                return _next_client()
            return ResizedADBClient(auto_derby.config.ADB_ADDRESS)

        auto_derby.config.client = _client


auto_derby.plugin.register(__name__, Plugin())
