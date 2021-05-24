# -*- coding=UTF-8 -*-
# pyright: strict
"""template matching.  """

import os
import logging
import pathlib
from typing import Dict, Iterator, List, Optional, Set, Text, Tuple, Union

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
        LOGGER.debug("load: %s", name)
        _LOADED_TEMPLATES[name] = open_image(
            pathlib.Path(__file__).parent / "templates" / name)
    return _LOADED_TEMPLATES[name]


_NOT_EXISTED_NAMES: Set[Text] = set()


def try_load(name: Text) -> Optional[Image]:
    if name in _NOT_EXISTED_NAMES:
        return None
    try:
        return load(name)
    except Exception as ex:
        LOGGER.debug("can not load: %s: %s", name, ex)
        _NOT_EXISTED_NAMES.add(name)
        return None


def add_middle_ext(name: Text, value: Text) -> Text:
    parts = name.split(".")
    parts.insert(max(len(parts) - 1, 1), value)
    return ".".join(parts)


class Specification():
    def __init__(self, name: Text, pos: Optional[Text] = None, *, threshold: float = 0.9):
        self.name = name
        self.pos = pos
        self.threshold = threshold

    def load_pos(self) -> Optional[Image]:
        return try_load(self.pos or add_middle_ext(self.name, "pos"))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"tmpl<{self.name}+{self.pos}>" if self.pos else f"tmpl<{self.name}>"


_DEBUG_TMPL = os.getenv("DEBUG_TMPL") or "debug.png"


def _match_one(img: Image, tmpl: Union[Text, Specification]) -> Iterator[Tuple[Specification, Tuple[int, int]]]:
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
    if tmpl.name == _DEBUG_TMPL:
        cv2.imshow("match", res)
        cv2.waitKey()
        cv2.destroyWindow("match")
    while True:
        mask = cv_pos[
            0:res.shape[0],
            0:res.shape[1],
        ]
        _, max_val, _, max_loc = cv2.minMaxLoc(
            res,
            mask=mask,
        )
        if max_val < tmpl.threshold:
            LOGGER.debug(
                "not match: tmpl=%s, pos=%s, similarity=%.3f", tmpl, max_loc, max_val)
            break
        x, y = max_loc
        LOGGER.info(
            "match: tmpl=%s, pos=%s, similarity=%.2f", tmpl, max_loc, max_val)
        yield (tmpl, (x, y))

        # mark position unavailable to avoid overlap
        cv_pos[
            max(0, y-tmpl_h): y+tmpl_h,
            max(0, x-tmpl_w): x+tmpl_w,
        ] = 0


def match(img: Image, *tmpl: Union[Text, Specification]) -> Iterator[Tuple[Specification, Tuple[int, int]]]:
    match_count = 0
    for i in tmpl:
        for j in _match_one(img, i):
            match_count += 1
            yield j
    if match_count == 0:
        LOGGER.info("no match: tmpl=%s", tmpl)
