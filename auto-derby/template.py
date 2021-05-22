# -*- coding=UTF-8 -*-
# pyright: strict
"""template matching.  """

import logging
import pathlib
from typing import Dict, Optional, Text, Tuple

import cv2
import numpy as np
import win32gui
from PIL import ImageGrab
from PIL.Image import Image
from PIL.Image import open as openImage

from . import window

LOGGER = logging.getLogger(__name__)


def screenshot(h_wnd: int) -> Image:
    # XXX: BitBlt capture not work, only foreground window is supportted
    # Maybe use WindowsGraphicsCapture like obs do
    with window.foreground(h_wnd):
        # not use GetWindowRect to exclude border
        _, _, w, h = win32gui.GetClientRect(h_wnd)
        x, y = win32gui.ClientToScreen(h_wnd, (0, 0))
        left, top, right, bottom = x, y, x+w, y+h
        bbox = (left, top, right, bottom)
        return ImageGrab.grab(bbox, True, True)


_LOADED_TEMPLATES: Dict[Text, Image] = {}


def _cv_image(img: Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


# def _cv_gray_image(img: Image):
#     return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)


def load(name: Text) -> Image:
    if name not in _LOADED_TEMPLATES:
        _LOADED_TEMPLATES[name] = openImage(
            pathlib.Path(__file__).parent / "templates" / name)
    return _LOADED_TEMPLATES[name]


def match(img: Image, *name: Text, threshold: float = 0.95) -> Optional[Tuple[Text, Tuple[int, int]]]:
    for i in name:
        res = cv2.matchTemplate(_cv_image(img), _cv_image(
            load(i)), cv2.TM_SQDIFF_NORMED)
        res = 1 - res
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val > threshold:
            x, y = max_loc
            LOGGER.info(
                "found image: name=%s, pos=%s, similarity=%.2f", i, max_loc, max_val)
            return (i, (x, y))
    LOGGER.info("not found image: name=%s", name)
    return None
