# -*- coding=UTF-8 -*-
# pyright: strict
"""template matching.  """

import logging
import pathlib
from typing import Dict, Iterator, Optional, Text, Tuple, Union

import cv2
import numpy as np
import win32gui
from PIL import ImageGrab
from PIL.Image import Image
from PIL.Image import open as open_image

from . import window

LOGGER = logging.getLogger(__name__)


def screenshot_window(h_wnd: int) -> Image:
    # XXX: BitBlt capture not work, background window is not supportted
    # Maybe use WindowsGraphicsCapture like obs do
    with window.topmost(h_wnd):
        # not use GetWindowRect to exclude border
        _, _, w, h = win32gui.GetClientRect(h_wnd)
        x, y = win32gui.ClientToScreen(h_wnd, (0, 0))
        left, top, right, bottom = x, y, x+w, y+h
        bbox = (left, top, right, bottom)
        return ImageGrab.grab(bbox, True, True)


def screenshot() -> Image:
    return screenshot_window(window.get_game())


_LOADED_TEMPLATES: Dict[Text, Image] = {}


def _cv_image(img: Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


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


def add_middle_ext(name: Text, value: Text) -> Text:
    parts = name.split(".")
    parts.insert(max(len(parts) - 1, 1), value)
    return ".".join(parts)


class Specification():
    def __init__(self, name: Text, pos: Optional[Text] = None):
        self.name = name
        self.pos = pos

    def load_pos(self) -> Optional[Image]:
        return try_load(self.pos or add_middle_ext(self.name, "pos"))

    def __str__(self):
        return f"tmpl<{self.name}&{self.pos}>"


def _match_one(img: Image, tmpl: Union[Text, Specification], threshold: float = 0.9) -> Iterator[Tuple[Text, Tuple[int, int]]]:
    cv_img = _cv_image(img)
    if not isinstance(tmpl, Specification):
        tmpl = Specification(tmpl)

    pos = tmpl.load_pos()
    cv_tmpl = _cv_image(load(tmpl.name))
    tmpl_h, tmpl_w = cv_tmpl.shape[:2]
    if pos:
        cv_pos = np.array(pos.convert("L"))
    else:
        cv_pos = np.full(
            cv_img.shape[:2],
            255.0,
            dtype=np.uint8,
        )
    res = cv2.matchTemplate(cv_img, cv_tmpl, cv2.TM_CCOEFF_NORMED)
    while True:
        mask = cv_pos[
            0:res.shape[0],
            0:res.shape[1],
        ]
        _, max_val, _, max_loc = cv2.minMaxLoc(
            res,
            mask=mask,
        )
        if max_val < threshold:
            break
        x, y = max_loc
        LOGGER.info(
            "match: name=%s, pos=%s, similarity=%.2f", tmpl.name, max_loc, max_val)
        yield (tmpl.name, (x, y))

        # mark position unavailable to avoid overlap
        cv_pos[
            max(0, y-tmpl_h): y+tmpl_h,
            max(0, x-tmpl_w): x+tmpl_w,
        ] = 0


def match(img: Image, *tmpl: Union[Text, Specification], threshold: float = 0.9) -> Iterator[Tuple[Text, Tuple[int, int]]]:
    match_count = 0
    for i in tmpl:
        for j in _match_one(
            img,
            i,
            threshold=threshold
        ):
            match_count += 1
            yield j
    if match_count == 0:
        LOGGER.info("no match: name=%s", tmpl)
