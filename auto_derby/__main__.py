# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """


import argparse
import os
from auto_derby import templates
import ctypes
import time
import webbrowser

import win32con
import win32gui

from . import window, jobs

import logging
import logging.handlers

LOGGER = logging.getLogger(__name__)


def main():
    avaliable_jobs = {
        "team_race": jobs.team_race,
        "legend_race": jobs.legend_race,
        "nurturing": jobs.nurturing,
        "daily_race_money": lambda: jobs.daily_race(templates.MOONLIGHT_PRIZE),
        "daily_race_sp": lambda: jobs.daily_race(templates.JUPITER_CUP),
        "roulette_derby": jobs.roulette_derby,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("job")
    args = parser.parse_args()
    job = avaliable_jobs.get(args.job)

    if not job:
        LOGGER.error(
            "unknown job: %s\navaliable jobs:\n  %s",
            args.job,
            "\n  ".join(avaliable_jobs.keys()),
        )
        exit(1)

    h_wnd = window.get_game()
    if not h_wnd:
        if (
            win32gui.MessageBox(
                0, "Launch DMM umamusume?", "Can not found window", win32con.MB_YESNO
            )
            == 6
        ):
            webbrowser.open("dmmgameplayer://umamusume/cl/general/umamusume")
            while not h_wnd:
                time.sleep(1)
                LOGGER.info("waiting game launch")
                h_wnd = window.get_game()
        else:
            exit(1)
    window.set_game_size()
    LOGGER.info("game window: %s", h_wnd)
    job()


def is_admin():
    # https://stackoverflow.com/a/41930586
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    LOG_PATH = os.getenv("AUTO_DERBY_LOG_PATH", "auto_derby.log")
    if LOG_PATH and LOG_PATH != "-":
        handler = logging.handlers.RotatingFileHandler(
            LOG_PATH, backupCount=3, encoding="utf-8"
        )
        handler.doRollover()
        formatter = logging.Formatter(
            "%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    for i in os.getenv("DEBUG", "").split(","):
        if not i:
            continue
        logging.getLogger(i).setLevel(logging.DEBUG)

    if not is_admin():
        LOGGER.error(
            "admin permission is required, otherwise mouse event will be ignored by the game."
        )
        exit(1)
    try:
        main()
    except:
        LOGGER.exception("unexpected exception")
        exit(1)
