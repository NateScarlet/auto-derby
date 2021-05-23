# -*- coding=UTF-8 -*-
# pyright: strict

import numpy as np
import cv2
from typing import Text

from numpy.lib import math
from .. import action, templates, window, template, ocr
import time

from paddleocr import PaddleOCR


ALL_OPTIONS = [
    templates.NURTURING_OPTION1,
    templates.NURTURING_OPTION2,
]


def _handle_option(name: Text):
    if name not in ALL_OPTIONS:
        return
    screen_img = template.screenshot(window.get_game())
    event_name = ocr.text(screen_img.crop((63, 135, 280, 155)))
    print(event_name)

    for i in ALL_OPTIONS:
        match = template.match(screen_img, i)
        if not match:
            continue
        _, pos = match
        tmpl = template.load(i)
        option = ocr.text(
            screen_img.crop((pos[0] + tmpl.width, pos[1], 330, pos[1] + 30)))
        print(option)
    exit(1)


def nurturing():
    pass
    while True:
        name, pos = action.wait_image(
            templates.NURTURING_MOOD_NORMAL,
            templates.NURTURING_OPTION1,
            templates.NURTURING_OPTION1,
        )
        _handle_option(name)
        if name == templates.NURTURING_MOOD_NORMAL:
            action.click_image(templates.NURTURING_GO_OUT)

        time.sleep(1)
