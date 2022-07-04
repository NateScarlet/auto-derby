# -*- coding=UTF-8 -*-
# pyright: strict
"""template matching.  """
from __future__ import annotations

import logging
import os
import pathlib
from typing import Dict, Iterator, Optional, Set, Text, Tuple, Union

import cv2
import numpy as np
from PIL.Image import Image
from PIL.Image import open as open_image

from . import imagetools, mathtools, app


TARGET_WIDTH = 540


class g:
    last_screenshot_save_path: str = ""

    @property
    def _legacy_screenshot_width(self):
        import warnings

        warnings.warn("use app.device.width() instead", DeprecationWarning)
        return app.device.width()

    @_legacy_screenshot_width.setter
    def _legacy_screenshot_width(self, v: int):
        import warnings

        warnings.warn("use app.device.width() instead", DeprecationWarning)


_LOADED_TEMPLATES: Dict[Text, Image] = {}


def _cv_image(img: Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def load(name: Text) -> Image:
    if name not in _LOADED_TEMPLATES:
        app.log.text("load: %s" % name, level=app.DEBUG)
        img = open_image(pathlib.Path(__file__).parent / "templates" / name)
        _LOADED_TEMPLATES[name] = img
    return _LOADED_TEMPLATES[name]


_NOT_EXISTED_NAMES: Set[Text] = set()


def try_load(name: Text) -> Optional[Image]:
    if name in _NOT_EXISTED_NAMES:
        return None
    try:
        return load(name)
    except Exception as ex:
        app.log.text("can not load: %s: %s" % (name, ex), level=app.DEBUG)
        _NOT_EXISTED_NAMES.add(name)
        return None


def add_middle_ext(name: Text, value: Text) -> Text:
    parts = name.split(".")
    parts.insert(max(len(parts) - 1, 1), value)
    return ".".join(parts)


class Specification:
    @classmethod
    def from_input(cls, input: Input) -> Specification:
        if isinstance(input, Specification):
            return input
        return Specification(input)

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
            app.log.text(
                "lightness match: tmpl=%s, similarity=%.3f"
                % (self, lightness_similarity),
                level=app.DEBUG,
            )
            if lightness_similarity < self.threshold:
                return False
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"tmpl<{self.name}+{self.pos}>" if self.pos else f"tmpl<{self.name}>"


Input = Union[Text, Specification]
_DEBUG_TMPL = os.getenv("DEBUG_TMPL") or "debug.png"


def _match_one(
    img: Image, tmpl: Input
) -> Iterator[Tuple[Specification, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(TARGET_WIDTH)
    cv_img = _cv_image(
        imagetools.resize(
            img,
            width=rp.vector(
                img.width,
                app.device.width(),
            ),
        )
    )
    tmpl = Specification.from_input(tmpl)

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
        app.log.image(
            "match template",
            cv_img,
            layers={"tmpl": cv_tmpl, "match": res.astype(np.uint8)},
            level=app.DEBUG,
        )
    reverse_rp = mathtools.ResizeProxy(app.device.width())
    while True:
        mask = cv_pos[0 : res.shape[0], 0 : res.shape[1]]
        _, max_val, _, max_loc = cv2.minMaxLoc(res, mask=mask)
        x, y = max_loc
        client_pos = reverse_rp.vector2((x, y), TARGET_WIDTH)
        if max_val < tmpl.threshold or not tmpl.match(img, client_pos):
            app.log.text(
                "not match: tmpl=%s, pos=%s, similarity=%.3f"
                % (tmpl, max_loc, max_val),
                level=app.DEBUG,
            )
            break
        app.log.text(
            "match: tmpl=%s, pos=%s, similarity=%.2f" % (tmpl, max_loc, max_val)
        )
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
        app.log.text(f"no match: tmpl={tmpl}")


# DEPRECATED
# spell-checker: disable
def _legacy_screenshot(*, max_age: float = 1) -> Image:
    import warnings

    warnings.warn("use `app.device.screenshot` instead", DeprecationWarning)
    return app.device.screenshot(max_age=max_age)


def _legacy_invalidate_screenshot():
    import warnings

    warnings.warn(
        "screenshot invalidation is handled by device service", DeprecationWarning
    )


globals()["LOGGER"] = logging.getLogger(__name__)
globals()["invalidate_screeshot"] = _legacy_invalidate_screenshot
globals()["invalidate_screenshot"] = _legacy_invalidate_screenshot
globals()["screenshot"] = _legacy_screenshot
g.screenshot_width = g._legacy_screenshot_width  # type: ignore
