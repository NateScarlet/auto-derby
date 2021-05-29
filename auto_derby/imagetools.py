# -*- coding=UTF-8 -*-
# pyright: strict
"""tools for image processing.  """


import colorsys
import hashlib
import os
import threading
from pathlib import Path
from typing import Callable, Dict, Literal, Optional, Text, Tuple, Union

import cast_unknown as cast
import cv2
import cv2.img_hash
import numpy as np
from PIL.Image import Image, fromarray

SKIP_SAVE = os.getenv("AUTO_DERBY_IMAGE_SKIP_SAVE", "").lower() == "true"


def image_path(save_path: Text, _id: Text) -> Path:
    return Path(save_path) / _id[0] / _id[1:3] / (_id[3:] + ".png")


def md5(b_img: np.ndarray, *, save_path: Optional[Text] = None) -> Text:
    _id = hashlib.md5(b_img.tobytes()).hexdigest()

    if save_path and not SKIP_SAVE:
        dst = image_path(save_path, _id)
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            fromarray(b_img).convert("1").save(dst)

    return _id


_HASH_ALGORITHM = cv2.img_hash.BlockMeanHash_create()


def image_hash(img: Image, *, save_path: Optional[Text] = None) -> Text:
    cv_img = np.asarray(img.convert("L"))
    h = _HASH_ALGORITHM.compute(cv_img).tobytes().hex()

    if save_path and not SKIP_SAVE:
        md5_hash = hashlib.md5(img.tobytes()).hexdigest()
        dst = Path(save_path) / h[0] / h[1:3] / h[3:] / (md5_hash + ".png")
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.convert("RGB").save(dst)

    return h


def compare_hash(a: Text, b: Text) -> float:
    if a == b:
        return 1.0
    cv_a = np.array(list(bytes.fromhex(a)), np.uint8)
    cv_b = np.array(list(bytes.fromhex(b)), np.uint8)
    res = _HASH_ALGORITHM.compare(cv_a, cv_b)
    return 1 - (res / (len(a) * 2))


def _rgb_to_hsv(v: Tuple[int, int, int], max_value: int) -> Tuple[int, int, int]:
    h, l, s = colorsys.rgb_to_hsv(
        v[0] / max_value, v[1] / max_value, v[2] / max_value)
    return int(h * max_value), int(l * max_value), int(s * max_value)


def compare_color(a: Union[Tuple[int, ...], int], b: Union[Tuple[int, ...], int], *, bit_size: int = 8) -> float:
    max_value = (1 << bit_size) - 1
    t_a = tuple(cast.list_(a, (int,)))
    t_b = tuple(cast.list_(b, (int,)))
    if len(t_a) != len(t_b):
        return 0

    if len(t_a) == 3:
        t_a = _rgb_to_hsv((t_a[0], t_a[1], t_a[2]), max_value)
        t_b = _rgb_to_hsv((t_b[0], t_b[1], t_b[2]), max_value)
    return 1 - np.sqrt(np.sum((np.array(t_a)-np.array(t_b)) ** 2, axis=0)) / max_value


_WINDOW_ID: Dict[Literal["value"], int] = {"value": 0}


def show(img: Image, title: Text = "") -> Callable[[], None]:

    stop_event = threading.Event()
    stop_event.is_set()
    _WINDOW_ID["value"] += 1
    title = f"{title} - {_WINDOW_ID['value']}"

    def _run():
        cv_img = np.asarray(img)
        try:
            cv2.imshow(title, cv_img)
            while not stop_event.is_set() and cv2.getWindowProperty(title, 0) >= 0:
                if cv2.pollKey() == "q":
                    break
        finally:
            cv2.destroyWindow(title)
    t = threading.Thread(target=_run, daemon=True)
    t.start()

    def _close():
        stop_event.set()
        t.join()

    return _close
