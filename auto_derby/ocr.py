# -*- coding=UTF-8 -*-
# pyright: strict


import csv
import errno
import json
import logging
import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Text, Tuple

import cv2
import numpy as np
from PIL.Image import Image, fromarray

from . import imagetools, terminal

LOGGER = logging.getLogger(__name__)


class g:
    data_path: str = ""
    image_path: str = ""
    prompt_disabled = False

    labels: Dict[Text, Text] = {}


class _g:
    loaded_data_path = ""


def _migrate_json_to_csv() -> None:
    path = g.data_path
    if not path.endswith(".json"):
        return

    g.data_path = str(Path(path).with_suffix(".csv"))
    try:
        with open(path, "r", encoding="utf-8") as f:
            g.labels = json.load(f)
        warnings.warn(
            f"migrating json ocr labels to {g.data_path}, this support will be removed at next major version.",
            DeprecationWarning,
        )
        for k, v in g.labels.items():
            _label(k, v)
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
            g.labels = dict((k, v) for k, v in csv.reader(f))
    except OSError:
        pass
    _g.loaded_data_path = g.data_path


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()


def _label(image_hash: Text, value: Text) -> None:
    g.labels[image_hash] = value
    with open(g.data_path, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow((image_hash, value))


_PREVIEW_PADDING = 4


def _pad_img(img: np.ndarray, padding: int = _PREVIEW_PADDING) -> np.ndarray:
    p = padding
    return cv2.copyMakeBorder(img, p, p, p, p, cv2.BORDER_CONSTANT)


def _query(h: Text) -> Tuple[Text, Text, float]:
    reload_on_demand()
    # TODO: use a more efficient data structure, maybe vp-tree
    if not g.labels:
        return "", "", 0
    return sorted(
        ((k, v, imagetools.compare_hash(h, k)) for k, v in g.labels.items()),
        key=lambda x: x[2],
        reverse=True,
    )[0]


def _prompt(img: np.ndarray, h: Text, value: Text, similarity: float) -> Text:
    if g.prompt_disabled:
        LOGGER.warning(
            "using low similarity label: hash=%s, value=%s, similarity=%s",
            h,
            value,
            similarity,
        )
        return value

    ret = ""
    close_img = imagetools.show(fromarray(_pad_img(img)), h)
    try:
        while len(ret) != 1:
            ans = ""
            while value and ans not in ("Y", "N"):
                ans = terminal.prompt(
                    f"Matching current displaying image: value={value}, similarity={similarity:0.3f}.\n"
                    "Is this correct? (Y/N)"
                ).upper()
            if ans == "Y":
                ret = value
            else:
                ret = terminal.prompt(
                    "Corresponding text for current displaying image:"
                )
    finally:
        close_img()
    _label(h, ret)
    LOGGER.info("labeled: hash=%s, value=%s", h, ret)
    return ret


def _text_from_image(img: np.ndarray, threshold: float = 0.8) -> Text:
    hash_img = cv2.GaussianBlur(img, (7, 7), 1, borderType=cv2.BORDER_CONSTANT)
    h = imagetools.image_hash(fromarray(hash_img), save_path=g.image_path)
    match, value, similarity = _query(h)
    LOGGER.debug(
        "match label: value=%s, current=%s, match=%s, similarity=%0.3f",
        value,
        h,
        match,
        similarity,
    )
    if similarity > threshold:
        return value
    return _prompt(img, h, value, similarity)


def _union_bbox(
    *bbox: Optional[Tuple[int, int, int, int]]
) -> Tuple[int, int, int, int]:
    b = [i for i in bbox if i]
    ret = b[0]
    for i in b[1:]:
        ret = (
            min(ret[0], i[0]),
            min(ret[1], i[1]),
            max(ret[2], i[2]),
            max(ret[3], i[3]),
        )
    return ret


def _rect2bbox(rect: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    x, y, w, h = rect
    l, t, r, b = x, y, x + w, y + h
    return l, t, r, b


def _pad_bbox(v: Tuple[int, int, int, int], padding: int) -> Tuple[int, int, int, int]:
    l, t, r, b = v
    l -= padding
    t -= padding
    r += padding
    b += padding
    return (l, t, r, b)


def _bbox_contains(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> bool:
    return a[0] <= b[0] and a[1] <= b[1] and a[2] >= b[2] and a[3] >= b[3]


_LINE_HEIGHT = 32


def text(img: Image, *, threshold: float = 0.8) -> Text:
    """Regcognize text line, background color should be black.

    Args:
        img (Image): Preprocessed text line.

    Returns:
        Text: Text content
    """
    ret = ""

    w, h = img.width, img.height

    if img.height < _LINE_HEIGHT:
        w = round(_LINE_HEIGHT / h * w)
        h = _LINE_HEIGHT
        img = img.resize((w, h))
    cv_img = np.asarray(img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 0, 255, cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 0:
        LOGGER.debug("ocr result is empty")
        return ""

    contours_with_bbox = sorted(
        ((i, _rect2bbox(cv2.boundingRect(i))) for i in contours), key=lambda x: x[1][0]
    )

    max_char_width = max(bbox[2] - bbox[0] for _, bbox in contours_with_bbox)
    max_char_height = max(bbox[3] - bbox[1] for _, bbox in contours_with_bbox)
    max_char_width = max(max_char_height, max_char_width)

    char_img_list: List[Tuple[Tuple[int, int, int, int], np.ndarray]] = []
    char_parts: List[np.ndarray] = []
    char_bbox = contours_with_bbox[0][1]
    char_non_zero_bbox = contours_with_bbox[0][1]

    def _push_char():
        if not char_parts:
            return
        mask = np.zeros_like(binary_img)
        cv2.drawContours(mask, char_parts, -1, (255,), thickness=cv2.FILLED)
        char_img = cv2.copyTo(binary_img, mask)
        l, t, r, b = char_non_zero_bbox
        if r - l < max_char_width * 0.5 or b - t < max_char_height * 0.8:
            l, t, r, b = char_bbox
        char_img = char_img[t:b, l:r]
        char_img_list.append((char_bbox, char_img))

    def _get_expanded_bbox(index: int) -> Tuple[int, int, int, int]:
        _, bbox = contours_with_bbox[index]
        if index + 1 < len(contours_with_bbox):
            _, next_bbox = contours_with_bbox[index + 1]
            if next_bbox[0] - bbox[2] < 2:
                bbox = _union_bbox(bbox, _get_expanded_bbox(index + 1))
        return bbox

    for index, v in enumerate(contours_with_bbox):
        i, _ = v
        bbox = _get_expanded_bbox(index)

        l, t, r, b = bbox
        is_new_char = (
            char_parts
            and l > char_non_zero_bbox[2]
            and (
                l - char_non_zero_bbox[0] > max_char_width * 0.7
                or l - char_non_zero_bbox[2] > max_char_width * 0.2
                or r - char_non_zero_bbox[0] > max_char_width
                or (
                    # previous is punctuation
                    char_non_zero_bbox[3] - char_non_zero_bbox[1]
                    < max_char_height * 0.6
                    and (
                        r - l > max_char_width * 0.6
                        or l - char_non_zero_bbox[2] > max_char_width * 0.1
                    )
                )
                or (
                    # current is punctuation
                    b - t < max_char_height * 0.4
                    and l > char_non_zero_bbox[2] + 1
                    and l > char_non_zero_bbox[0] + max_char_width * 0.3
                )
            )
            and not _bbox_contains(_pad_bbox(char_bbox, 2), bbox)
        )
        if is_new_char:
            space_w = l - char_bbox[2]
            divide_x = int(l - space_w * 0.5 - 1)
            last_r = min(divide_x, char_bbox[0] + max_char_width)
            char_bbox = _union_bbox(char_bbox, (last_r, t, last_r, b))
            _push_char()
            char_parts = []
            char_bbox = (
                max(last_r + 1, r - max_char_width),
                char_bbox[1],
                r,
                int(char_bbox[1] + max_char_height),
            )
            char_non_zero_bbox = bbox
        char_parts.append(i)
        char_non_zero_bbox = _union_bbox(char_non_zero_bbox, bbox)
        char_bbox = _union_bbox(char_bbox, bbox)
    _push_char()

    if os.getenv("DEBUG") == __name__:
        segmentation_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
        for i in contours:
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(
                segmentation_img, (x, y), (x + w, y + h), (0, 0, 255), thickness=1
            )
        chars_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
        for bbox, _ in char_img_list:
            l, t, r, b = bbox
            cv2.rectangle(chars_img, (l, t), (r, b), (0, 0, 255), thickness=1)
        cv2.imshow("ocr input", cv_img)
        cv2.imshow("ocr binary", binary_img)
        cv2.imshow("ocr segmentation", segmentation_img)
        cv2.imshow("ocr chars", chars_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    for _, i in char_img_list:
        ret += _text_from_image(i, threshold)

    LOGGER.debug("ocr result: %s", ret)

    return ret
