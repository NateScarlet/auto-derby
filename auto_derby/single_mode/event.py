# -*- coding=UTF-8 -*-
# pyright: strict

import csv
import errno
import json
import logging
import os
import warnings
from pathlib import Path
from typing import Dict, Text

import cv2
import numpy as np
from PIL.Image import Image

from .. import imagetools, mathtools, terminal, app

LOGGER = logging.getLogger(__name__)


class g:
    event_image_path: str = ""
    data_path: str = ""
    choices: Dict[Text, int] = {}
    prompt_disabled = False


class _g:
    loaded_data_path = ""


def _set(event_id: Text, value: int) -> None:
    g.choices[event_id] = value

    def _do():
        with open(g.data_path, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow((event_id, value))

    try:
        _do()
    except FileNotFoundError:
        os.makedirs(os.path.dirname(g.data_path))
        _do()


def _migrate_json_to_csv() -> None:
    path = g.data_path
    if not path.endswith(".json"):
        return

    g.data_path = str(Path(path).with_suffix(".csv"))
    try:
        with open(path, "r", encoding="utf-8") as f:
            g.choices = json.load(f)
        warnings.warn(
            f"migrating json single mode choices to {g.data_path}, this support will be removed at next major version.",
            DeprecationWarning,
        )
        for k, v in g.choices.items():
            _set(k, v)
        os.rename(path, path + "~")
    except OSError as ex:
        if ex.errno == errno.ENOENT:
            pass
        else:
            raise


def reload() -> None:
    _migrate_json_to_csv()
    try:
        with open(g.data_path, "r", encoding="utf-8") as f:
            g.choices = dict((k, int(v)) for k, v in csv.reader(f))
    except OSError:
        pass
    _g.loaded_data_path = g.data_path


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()


def _prompt_choice(event_id: Text) -> int:
    if g.prompt_disabled:
        return 1
    ans = ""
    while ans not in ["1", "2", "3", "4", "5"]:
        ans = terminal.prompt("Choose event option(1/2/3/4/5):")
    ret = int(ans)
    _set(event_id, ret)
    return ret


def get_choice(event_screen: Image) -> int:
    rp = mathtools.ResizeProxy(event_screen.width)
    b_img = np.zeros((event_screen.height, event_screen.width))
    event_name_bbox = rp.vector4((75, 155, 305, 180), 466)
    options_bbox = rp.vector4((50, 200, 400, 570), 466)
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

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("option_mask", option_mask)
        cv2.imshow("cv_event_name_img", cv_event_name_img)
        cv2.imshow("cv_options_img", cv_options_img)
        cv2.imshow("b_img", b_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    reload_on_demand()
    if event_id in g.choices:
        ret = g.choices[event_id]
    else:
        ret = _prompt_choice(event_id)
    app.log.image("event: id=%s choice=%d" % (event_id, ret), event_screen)
    return ret
