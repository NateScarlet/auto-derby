# -*- coding=UTF-8 -*-
# pyright: strict


import cv2
import numpy as np
from .. import action, templates, template


ALL_OPTIONS = [
    templates.NURTURING_OPTION1,
    templates.NURTURING_OPTION2,
]


def _count_friend() -> int:

    img = template.screenshot()
    img = img.crop((325, 105, 395, 460))

    cv_img = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    # cv_img = cv2.Canny(cv_img, 20, 40)
    cv_img = cv2.adaptiveThreshold(cv_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 10, 15)
    # cv_img = cv2.boxFilter(cv_img, -1, (80, 1))
    # cv_img = cv2.medianBlur(cv_img, 5)
    res =  cv2.HoughCircles(cv_img, cv2.HOUGH_GRADIENT, 4, 1, minRadius=25, maxRadius=30)
    print(res)
    preview_img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2BGR)
    for x, y, r in res[0]:
        cv2.circle(preview_img, (int(x), int(y)), int(r), (0, 0, 255))
    # _, cv_img = cv2.threshold(cv_img, 220, 255, cv2.THRESH_BINARY)
    # cv_img = cv2.sqrBoxFilter(cv_img, -1, (1, 1))
    # cv_img = cv2.GaussianBlur(cv_img, (0, 21), sigmaX=100, sigmaY=0)
    cv2.imshow("friends", preview_img)
    cv2.waitKey()
    exit(1)


def nurturing():
    while True:
        name, pos = action.wait_image(
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.NURTURING_TRAINING,
            templates.NURTURING_FANS_NOT_ENOUGH,
            templates.NURTURING_FINISH_BUTTON,
            templates.NURTURING_TARGET_RACE_BANNER,
            templates.NURTURING_RACE_NEXT_BUTTON,
            templates.NURTURING_OPTION1,
            templates.NURTURING_OPTION2,
            templates.NURTURING_REST,
            templates.GREEN_NEXT_BUTTON,
            templates.NURTURING_GENE_INHERIT,
            templates.NURTURING_END_BUTTON,
        )
        if name == templates.CONNECTING:
            pass
        elif name == templates.NURTURING_FANS_NOT_ENOUGH:
            action.click_image(templates.CANCEL_BUTTON)
        elif name == templates.NURTURING_FINISH_BUTTON:
            break
        elif name == templates.NURTURING_TARGET_RACE_BANNER:
            x, y = pos
            y += 60
            action.click((x, y))
            action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
            action.wait_click_image(templates.NURTURING_RACE_START_BUTTON)
            action.wait_click_image(templates.RACE_RESULT_BUTTON)

            _, pos = action.wait_image(
                templates.RACE_RESULT_NO1,
                templates.RACE_RESULT_FAIL,
            )
            action.click(pos)
            action.wait_click_image(templates.NURTURING_RACE_NEXT_BUTTON)
        elif name == templates.NURTURING_TRAINING:
            if action.count_image(templates.NURTURING_STAMINA_HALF_EMPTY):
                action.click_image(templates.NURTURING_REST)
                continue
            action.click(pos)
            action.drag((60, 400), dy=200)  # select speed
            action.click((60, 600))
            # action.drag((60, 600), dx=300)
        elif name == templates.NURTURING_REST:
            if action.count_image(templates.NURTURING_MOOD_NORMAL):
                action.click_image(templates.NURTURING_GO_OUT)
            else:
                action.click(pos)
        else:
            action.click(pos)
