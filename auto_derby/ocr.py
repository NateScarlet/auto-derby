# -*- coding=UTF-8 -*-
# pyright: strict


import os
from typing import Dict, List, Text, Tuple

import cv2
import numpy as np
from PIL.Image import Image, fromarray

from auto_derby import imagetools

from . import window
import json

import logging
LOGGER = logging.getLogger(__name__)


DATA_PATH = os.getenv("AUTO_DERBY_OCR_LABELS_PATH", "ocr_labels.json")
IMAGE_PATH = os.getenv("AUTO_DERBY_OCR_IMAGES_PATH", "ocr_images.local")


def _load() -> Dict[Text, Text]:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


def _save() -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(_LABELS, f, indent=2)


_LABELS = _load()


_PREVIEW_PADDING = 4


def _pad_img(img: np.ndarray, padding: int = _PREVIEW_PADDING) -> np.ndarray:
    p = padding
    return cv2.copyMakeBorder(img, p, p, p, p, cv2.BORDER_CONSTANT)


def _auto_level(img: np.ndarray) -> np.ndarray:
    black = np.percentile(img, 5)
    white = np.percentile(img, 95)

    return np.clip((img - black) / (white - black) * 255, 0, 255).astype(np.uint8)


def _query(h: Text) -> Tuple[Text, float]:
    # TODO: use a more efficient data structure, maybe vp-tree
    if not _LABELS:
        return "", 0
    return sorted(((v, imagetools.compare_hash(h, k)) for k, v in _LABELS.items()), key=lambda x: x[1],  reverse=True)[0]


def _text_from_image(img: np.ndarray) -> Text:
    hash_img = cv2.GaussianBlur(img, (3, 3), 2, borderType=cv2.BORDER_CONSTANT)
    h = imagetools.image_hash(fromarray(hash_img), save_path=IMAGE_PATH)
    match, similarity = _query(h)
    LOGGER.debug("match label: hash=%s, value=%s, similarity=%0.3f",
                 h, match, similarity)
    if similarity > 0.8:
        return match
    ans = ""
    close_img = imagetools.show(fromarray(_pad_img(img)), h)
    close_msg = window.info("遇到新文本\n请在终端中标注")
    try:
        while len(ans) != 1:
            ans = input("请输入当前显示图片对应的文本：")
        _LABELS[h] = ans
        LOGGER.info("labeled: hash=%s, value=%s", h, ans)
    finally:
        close_msg()
        close_img()
    _save()
    ret = _LABELS[h]
    LOGGER.debug("use label: hash=%s, value=%s", h, ret)
    return ret


def text(img: Image) -> Text:
    ret = ""

    w, h = img.width, img.height
    line_height = 32
    if img.height < line_height:
        w = int(line_height / h * w)
        h = line_height
    cv_img = np.asarray(img.convert("L"))
    cv_img = _auto_level(cv_img)
    if cv_img[0, 0] == 255:
        cv_img = 255 - cv_img
    _, binary_img = cv2.threshold(
        cv_img,
        0,
        255,
        cv2.THRESH_OTSU,
    )

    contours, _ = cv2.findContours(
        binary_img,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE,
    )

    if os.getenv("DEBUG") == __name__:
        preview = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
        for i in contours:
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(preview, (x, y), (x+w, y+h),
                          (0, 0, 255), thickness=1)
        cv2.imshow("ocr input", cv_img)
        cv2.imshow("ocr binary", binary_img)
        # cv2.imshow("ocr thin result", thin_img)
        cv2.imshow("ocr segmentation", preview)
        cv2.waitKey()
        cv2.destroyAllWindows()

    char_img_list: List[Tuple[int, np.ndarray]] = []
    for index, i in enumerate(contours):
        x, y, w, h = cv2.boundingRect(i)
        mask = np.zeros_like(binary_img)
        cv2.drawContours(mask, contours, index, (255,), thickness=cv2.FILLED)
        char_img = cv2.copyTo(binary_img, mask, dst=np.zeros((h, w), np.uint8))
        char_img = char_img[y:y+h, x:x+w]
        char_img_list.append((x, char_img))

    char_img_list = sorted(char_img_list, key=lambda x: x[0])
    for _, i in char_img_list:
        ret += _text_from_image(i)

    LOGGER.debug("ocr result: %s", ret)

    return ret
