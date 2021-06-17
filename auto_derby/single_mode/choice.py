# -*- coding=UTF-8 -*-
# pyright: strict

import json
import logging
from typing import Dict, Text

import cv2
import numpy as np
from auto_derby import imagetools, window
from PIL.Image import Image

LOGGER = logging.getLogger(__name__)


class g:
    event_image_path: str = ""
    data_path: str = ""
    choices: Dict[Text, int] = {}


def reload() -> None:
    try:
        with open(g.data_path, "r", encoding="utf-8") as f:
            g.choices = json.load(f)
    except OSError:
        pass


def _save() -> None:
    with open(g.data_path, "w", encoding="utf-8") as f:
        json.dump(g.choices, f, indent=2)


def get(event_screen: Image) -> int:
    b_img = np.zeros((event_screen.height, event_screen.width))
    event_name_bbox = (75, 155, 305, 180)
    options_bbox = (50, 200, 400, 570)
    cv_event_name_img = np.asarray(event_screen.crop(event_name_bbox).convert("L"))
    _, cv_event_name_img = cv2.threshold(cv_event_name_img, 220, 255, cv2.THRESH_TOZERO)

    l, t, r, b = event_name_bbox
    b_img[t:b, l:r] = cv_event_name_img

    cv_options_img = np.asarray(event_screen.crop(options_bbox).convert("L"))

    option_rows = (cv2.reduce(cv_options_img, 1, cv2.REDUCE_MAX) == 255).astype(
        np.uint8
    )

    option_mask = np.repeat(option_rows, cv_options_img.shape[1], axis=1)

    cv_options_img = 255 - cv_options_img
    cv_options_img *= option_mask

    _, cv_options_img = cv2.threshold(cv_options_img, 128, 255, cv2.THRESH_BINARY)

    l, t, r, b = options_bbox
    b_img[t:b, l:r] = cv_options_img

    event_id = imagetools.md5(b_img, save_path=g.event_image_path)
    if event_id not in g.choices:
        close = window.info("New event encountered\nplease choose option in terminal")
        while True:
            ans = input("Choose event option(1/2/3/4/5):")
            if ans in ["1", "2", "3", "4", "5"]:
                g.choices[event_id] = int(ans)
                _save()
                close()
                break
    ret = g.choices[event_id]
    LOGGER.info("event: id=%s choice=%d", event_id, ret)
    return ret
