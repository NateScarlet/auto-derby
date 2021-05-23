# -*- coding=UTF-8 -*-
# pyright: strict


from PIL.Image import Image
import paddleocr
from . import template, window
from typing import Text, Tuple
import cv2

import numpy as np

OCR = paddleocr.PaddleOCR(lang='japan')


def _crop_non_zero(img: np.ndarray) -> np.ndarray:
    points = cv2.findNonZero(img)
    x, y, w, h = cv2.boundingRect(points)
    h += 4
    w += 4
    x = max(0, x - 2)
    y = max(0, y - 2)
    return img[y:y+h, x:x+w]


def _direct_ocr(img: Image) -> Text:
    cv_img = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_img = _auto_level(cv_img)
    lines = OCR.ocr(cv_img, det=False)
    return "\n".join(i for i, confidence in lines if confidence > 0.95)


def _auto_level(img: np.ndarray) -> np.ndarray:
    black = np.percentile(img, 5)
    white = np.percentile(img, 95)

    return np.clip((img - black) / (white - black) * 255, 0, 255).astype(np.uint8)


def _adaptive_threshold_ocr(img: Image) -> Text:
    cv_img = np.asarray(img.convert("L"))
    cv_img = _auto_level(cv_img)

    binary_img = cv2.adaptiveThreshold(
        cv_img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    if binary_img[0, 0] == 255:
        binary_img = 255 - binary_img
    binary_img = _crop_non_zero(binary_img)
    cv2.imshow("_adaptive_threshold_ocr", binary_img)
    cv2.waitKey()
    lines = OCR.ocr(cv_img, det=False)
    return "\n".join(i for i, confidence in lines if confidence > 0.9)


def _threshold_ocr(img: Image) -> Text:
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
    cv2.imshow("threshold", binary_img)
    cv2.waitKey()
    lines = OCR.ocr(cv_img, det=False)
    print(lines)
    return "\n".join(i for i, confidence in lines if confidence > 0.9)


def text(img: Image) -> Text:
    return  _threshold_ocr(img) or _adaptive_threshold_ocr(img) or _direct_ocr(img)
