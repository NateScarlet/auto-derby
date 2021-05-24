

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


def _auto_level(img: np.ndarray) -> np.ndarray:
    black = np.percentile(img, 5)
    white = np.percentile(img, 95)

    return np.clip((img - black) / (white - black) * 255, 0, 255).astype(np.uint8)


def _crop_non_zero(img: np.ndarray) -> np.ndarray:
    points = cv2.findNonZero(img)
    x, y, w, h = cv2.boundingRect(points)
    h += 4
    w += 4
    x = max(0, x - 2)
    y = max(0, y - 2)
    return img[y:y+h, x:x+w]


def _binary_img(img: Image) -> np.ndarray:
    cv_img = np.asarray(img.convert("L"))
    cv_img = _auto_level(cv_img)
    if cv_img[0, 0] == 255:
        cv_img = 255 - cv_img

    _, binary_img = cv2.threshold(
        cv_img,
        220,
        255,
        cv2.THRESH_BINARY,
    )
    binary_img = _crop_non_zero(binary_img)
    assert binary_img.size > 0
    if os.getenv("DEBUG") == "nurturing_choice":
        cv2.imshow("binary", binary_img)
        cv2.waitKey()
    return binary_img


EVENT_IMAGE_PATH = os.getenv(
    "AUTO_DERBY_NURTURING_EVENT_IMAGE_PATH") or "nurturing_event_images.local"


def image_id(img: Image) -> Text:
    b_img = _binary_img(img)
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


def get(event_name: Image) -> int:
    event_id = image_id(event_name)
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
