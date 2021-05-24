# -*- coding=UTF-8 -*-
# pyright: strict


import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, Text

import cv2
import numpy as np
from PIL.Image import Image, fromarray

from auto_derby import window

LOGGER = logging.getLogger(__name__)

EVENT_IMAGE_PATH = os.getenv(
    "AUTO_DERBY_NURTURING_EVENT_IMAGE_PATH") or "nurturing_event_images.local"


def _image_id(b_img: np.ndarray) -> Text:
    _id = hashlib.md5(b_img.tobytes()).hexdigest()

    if os.getenv("AUTO_DERBY_ID_IMAGE_SKIP_SAVE", "").lower() != "true":
        dst = Path(EVENT_IMAGE_PATH) / _id[0] / _id[1:3] / (_id[3:] + ".png")
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            fromarray(b_img).convert("1").save(dst)

    return _id


DATA_PATH = os.getenv(
    "AUTO_DERBY_NURTURING_CHOICE_PATH"
) or "nurturing_choices.json"


def _load() -> Dict[Text, int]:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


def _save() -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(_CHOICES, f, indent=2)


_CHOICES = _load()


def get(event_screen: Image) -> int:
    b_img = np.zeros((event_screen.height, event_screen.width))
    event_name_bbox = (75, 155, 305, 180)
    options_bbox = (50, 200, 400, 570)
    cv_event_name_img = np.asarray(
        event_screen.crop(event_name_bbox).convert("L"))
    _, cv_event_name_img = cv2.threshold(
        cv_event_name_img, 220, 255, cv2.THRESH_TOZERO)

    l, t, r, b = event_name_bbox
    b_img[
        t: b,
        l: r,
    ] = cv_event_name_img

    cv_options_img = np.asarray(event_screen.crop(options_bbox).convert("L"))

    def _has_white(x: np.ndarray) -> bool:
        return (x == 255).any()
    option_rows = np.apply_along_axis(
        _has_white, 1, cv_options_img).astype(np.uint8)
    option_mask = np.repeat(np.vstack(option_rows),
                            cv_options_img.shape[1], axis=1)

    cv_options_img = 255-cv_options_img
    cv_options_img *= option_mask

    _, cv_options_img = cv2.threshold(
        cv_options_img,
        128,
        255,
        cv2.THRESH_BINARY,
    )

    l, t, r, b = options_bbox
    b_img[
        t: b,
        l: r,
    ] = cv_options_img

    event_id = _image_id(b_img)
    if event_id not in _CHOICES:
        window.info("出现新选项\n请在终端中输入选项编号")
        while True:
            ans = input("选项编号(1/2/3/4/5）：")
            if ans in ["1", "2", "3", "4", "5"]:
                _CHOICES[event_id] = int(ans)
                _save()
                break
    ret = _CHOICES[event_id]
    LOGGER.info("event: id=%s choice=%d", event_id, ret)
    return ret
