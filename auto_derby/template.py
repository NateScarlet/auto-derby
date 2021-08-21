# -*- coding=UTF-8 -*-
# pyright: strict
"""template matching.  """

import datetime as dt
import logging
import os
import pathlib
from typing import Dict, Iterator, Optional, Set, Text, Tuple, Union

import cv2
import numpy as np
from PIL.Image import Image
from PIL.Image import open as open_image

from . import clients, imagetools, mathtools

LOGGER = logging.getLogger(__name__)

TARGET_WIDTH = 540


class _g:
    cached_screenshot = (dt.datetime.fromtimestamp(0), Image())


def invalidate_screeshot():
    _g.cached_screenshot = (dt.datetime.fromtimestamp(0), Image())


class g:
    last_screenshot_save_path: str = ""
    screenshot_width = TARGET_WIDTH


def screenshot(*, max_age: float = 1) -> Image:
    cached_time, _ = _g.cached_screenshot
    if cached_time < dt.datetime.now() - dt.timedelta(seconds=max_age):
        new_img = clients.current().screenshot()
        g.screenshot_width = new_img.width
        new_img = new_img.convert("RGB")
        if g.last_screenshot_save_path:
            new_img.save(g.last_screenshot_save_path)
        LOGGER.debug("screenshot")
        _g.cached_screenshot = (dt.datetime.now(), new_img)
    return _g.cached_screenshot[1]


_LOADED_TEMPLATES: Dict[Text, Image] = {}


def _cv_image(img: Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def load(name: Text) -> Image:
    if name not in _LOADED_TEMPLATES:
        LOGGER.debug("load: %s", name)
        # rp = mathtools.ResizeProxy(_g.screenshot_width)
        img = open_image(pathlib.Path(__file__).parent / "templates" / name)
        # img = imagetools.resize(img, width=rp.vector(img.width, TARGET_WIDTH))
        _LOADED_TEMPLATES[name] = img
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


class Specification:
    def __init__(
        self,
        name: Text,
        pos: Optional[Text] = None,
        *,
        threshold: float = 0.9,
        lightness_sensitive: bool = True,
    ):
        self.name = name
        self.pos = pos
        self.threshold = threshold
        self.lightness_sensitive = lightness_sensitive

    def load_pos(self) -> Optional[Image]:
        return try_load(self.pos or add_middle_ext(self.name, "pos"))

    def match(self, img: Image, pos: Tuple[int, int]) -> bool:
        x, y = pos
        if self.lightness_sensitive:
            tmpl_img = load(self.name)
            match_img = img.crop((x, y, x + tmpl_img.width, y + tmpl_img.height))

            cv_tmpl_img = np.asarray(tmpl_img.convert("L"))
            cv_match_img = np.asarray(match_img.convert("L"))
            match_min, match_max, _, _ = cv2.minMaxLoc(cv_match_img)
            tmpl_min, tmpl_max, _, _ = cv2.minMaxLoc(cv_tmpl_img)

            max_diff = (match_max - tmpl_max) / 255.0
            min_diff = (match_min - tmpl_min) / 255.0
            if max_diff < 0:
                max_diff *= -1
                min_diff *= -1

            lightness_similarity = 1 - (abs(max_diff + min_diff) / 2)
            LOGGER.debug(
                "lightness match: tmpl=%s, similarity=%.3f", self, lightness_similarity
            )
            if lightness_similarity < self.threshold:
                return False
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"tmpl<{self.name}+{self.pos}>" if self.pos else f"tmpl<{self.name}>"


_DEBUG_TMPL = os.getenv("DEBUG_TMPL") or "debug.png"


def _match_one(
    img: Image, tmpl: Union[Text, Specification]
) -> Iterator[Tuple[Specification, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(TARGET_WIDTH)
    cv_img = _cv_image(
        imagetools.resize(
            img,
            width=rp.vector(
                img.width,
                g.screenshot_width,
            ),
        )
    )
    if not isinstance(tmpl, Specification):
        tmpl = Specification(tmpl)

    pos = tmpl.load_pos()
    pil_tmpl = load(tmpl.name)
    cv_tmpl = _cv_image(pil_tmpl)
    tmpl_h, tmpl_w = cv_tmpl.shape[:2]
    if pos:
        cv_pos = np.array(pos.convert("L"))
    else:
        cv_pos = np.full(cv_img.shape[:2], 255.0, dtype=np.uint8)
    res = cv2.matchTemplate(cv_img, cv_tmpl, cv2.TM_CCOEFF_NORMED)
    if tmpl.name == _DEBUG_TMPL:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("cv_tmpl", cv_tmpl)
        cv2.imshow("match", res)
        cv2.waitKey()
        cv2.destroyAllWindows()
    reverse_rp = mathtools.ResizeProxy(g.screenshot_width)
    while True:
        mask = cv_pos[0 : res.shape[0], 0 : res.shape[1]]
        _, max_val, _, max_loc = cv2.minMaxLoc(res, mask=mask)
        x, y = max_loc
        client_pos = reverse_rp.vector2((x, y), TARGET_WIDTH)
        if max_val < tmpl.threshold or not tmpl.match(img, client_pos):
            LOGGER.debug(
                "not match: tmpl=%s, pos=%s, similarity=%.3f", tmpl, max_loc, max_val
            )
            break
        LOGGER.info("match: tmpl=%s, pos=%s, similarity=%.2f", tmpl, max_loc, max_val)
        yield (tmpl, client_pos)

        # mark position unavailable to avoid overlap
        cv_pos[max(0, y - tmpl_h) : y + tmpl_h, max(0, x - tmpl_w) : x + tmpl_w] = 0


def match(
    img: Image, *tmpl: Union[Text, Specification]
) -> Iterator[Tuple[Specification, Tuple[int, int]]]:
    match_count = 0
    for i in tmpl:
        for j in _match_one(img, i):
            match_count += 1
            yield j
    if match_count == 0:
        LOGGER.info("no match: tmpl=%s", tmpl)
