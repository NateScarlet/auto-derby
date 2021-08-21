from pathlib import Path
from typing import Text

import PIL.Image

from .. import mathtools, template

DATA_PATH = Path(__file__).parent / "test_data"


def use_screenshot(name: Text):
    img = PIL.Image.open(DATA_PATH / name).convert("RGB")
    template.g.screenshot_width = img.width
    return img, mathtools.ResizeProxy(img.width)
