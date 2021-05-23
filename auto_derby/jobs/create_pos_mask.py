# -*- coding=UTF-8 -*-
# pyright: strict


import cv2
from .. import window, template
import pathlib
import PIL.Image
import os
import numpy as np


def create_pos_mask():
    name = os.getenv("TEMPLATE_NAME")
    if not name:
        raise EnvironmentError("TEMPLATE_NAME not specified")

    game_img = template.screenshot(window.get_game())
    match_img = template.load(name)
    match = template.match(game_img, name)
    last_match = template.DEBUG_DATA["last_match"]
    if last_match is None:
        raise ValueError("missing debug data")

    out_img = np.zeros((game_img.height, game_img.width), dtype=float)

    if match:
        _, pos = match
        x, y = pos
        cv2.rectangle(out_img, pos, (x+match_img.width,
                                     y+match_img.height), (255,), -1)

    img = PIL.Image.fromarray(out_img).convert("1")
    dest = str(pathlib.Path(__file__).parent.parent /
               "templates" / template.add_middle_ext(name, "pos"))
    img.save(dest)
    cv2.imshow("out", out_img)
    cv2.waitKey()
