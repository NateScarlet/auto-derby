# -*- coding=UTF-8 -*-
# pyright: strict
"""tools for image processing.  """


import hashlib
import os
import threading
from pathlib import Path
from typing import Callable, Dict, Literal, Optional, Text

import cv2
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


_WINDOW_ID: Dict[Literal["value"], int] = { "value": 0}


def show(img: Image, title: Text = "") -> Callable[[], None]:

    stop_event = threading.Event()
    stop_event.is_set()
    _WINDOW_ID["value"] += 1
    title = f"{title} - {_WINDOW_ID}"

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
