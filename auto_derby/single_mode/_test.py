from pathlib import Path
from typing import Text
import contextlib
import PIL.Image
from .. import template

DATA_PATH = Path(__file__).parent / "test_data"


@contextlib.contextmanager
def screenshot(name: Text):
    img = PIL.Image.open(DATA_PATH / name).convert("RGB")

    original_screenshot_width = template.g.screenshot_width
    template.g.screenshot_width = img.width
    try:
        yield img
    finally:
        template.g.screenshot_width = original_screenshot_width
