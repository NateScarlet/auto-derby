# -*- coding=UTF-8 -*-
# pyright: strict
"""template matching.  """

import logging
import pathlib
from typing import Dict, Optional, Text, Tuple, TypedDict

import cv2
import numpy as np
import win32gui
from PIL import ImageGrab
from PIL.Image import Image
from PIL.Image import open as open_image

from . import window

LOGGER = logging.getLogger(__name__)


def screenshot(h_wnd: int) -> Image:
    # XXX: BitBlt capture not work, background window is not supportted
    # Maybe use WindowsGraphicsCapture like obs do
    with window.topmost(h_wnd):
        # not use GetWindowRect to exclude border
        _, _, w, h = win32gui.GetClientRect(h_wnd)
        x, y = win32gui.ClientToScreen(h_wnd, (0, 0))
        left, top, right, bottom = x, y, x+w, y+h
        bbox = (left, top, right, bottom)
        return ImageGrab.grab(bbox, True, True)


_LOADED_TEMPLATES: Dict[Text, Image] = {}


def _cv_image(img: Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _cv_gray_image(img: Image):
    return np.array(img.convert("L"))


def load(name: Text) -> Image:
    if name not in _LOADED_TEMPLATES:
        _LOADED_TEMPLATES[name] = open_image(
            pathlib.Path(__file__).parent / "templates" / name)
    return _LOADED_TEMPLATES[name]


def try_load(name: Text) -> Optional[Image]:
    try:
        return load(name)
    except Exception as ex:
        LOGGER.debug("can not load: %s: %s", name, ex)
        return None


def _cv_mask(cv_img: np.ndarray, mask: Image) -> np.ndarray:
    cv_mask = _cv_gray_image(mask)
    return cv2.bitwise_and(cv_img, cv_img, mask=cv_mask)


def add_middle_ext(name: Text, value: Text) -> Text:
    parts = name.split(".")
    parts.insert(max(len(parts) - 1, 1), value)
    return ".".join(parts)

class DebugDict(TypedDict):
    last_match: Optional[np.ndarray]

DEBUG_DATA = DebugDict(last_match=None)


def _match_one(img: Image, name: Text, threshold: float = 0.95) -> Optional[Tuple[Text, Tuple[int, int]]]:
    cv_img = _cv_image(img)
    img_mask = try_load(add_middle_ext(name, "pos"))
    if img_mask:
        cv_img = _cv_mask(cv_img, img_mask)
    res = cv2.matchTemplate(
        _cv_image(img),
        _cv_image(load(name)),
        cv2.TM_SQDIFF_NORMED,
    )
    res = 1 - res
    DEBUG_DATA['last_match'] = res
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        x, y = max_loc
        LOGGER.info(
            "match: name=%s, pos=%s, similarity=%.2f", name, max_loc, max_val)
        return (name, (x, y))
    return None


def match(img: Image, *name: Text, threshold: float = 0.95) -> Optional[Tuple[Text, Tuple[int, int]]]:
    for i in name:
        match = _match_one(
            img,
            i,
            threshold=threshold
        )
        if match:
            return match
    LOGGER.info("no match: name=%s", name)
    return None
