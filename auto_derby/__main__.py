# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """


from auto_derby import templates
import ctypes
from os import name
import time
import webbrowser

import win32con
import win32gui

from . import window, jobs

import logging

LOGGER = logging.getLogger(__name__)

import argparse
def main():
    avaliable_jobs = {
        "team_race": jobs.team_race,
        "daily_race_money": lambda : jobs.daily_race(templates.MOONLIGHT_PRIZE),
        "daily_race_sp": lambda : jobs.daily_race(templates.JUPITER_CUP),
        "create_pos_mask": jobs.create_pos_mask,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("job")
    args = parser.parse_args()
    job = avaliable_jobs.get(args.job)

    if not job:
        LOGGER.error("unknown job: %s\navaliable jobs:\n  %s", args.job, "\n  ".join(avaliable_jobs.keys()))
        exit(1)

    h_wnd = window.get_game()
    if not h_wnd:
        if win32gui.MessageBox(0, "启动DMM赛马娘？", "找不到窗口", win32con.MB_YESNO):
            webbrowser.open('dmmgameplayer://umamusume/cl/general/umamusume')
            while not h_wnd:
                time.sleep(1)
                h_wnd = window.get_game()
        else:
            exit(1)
    # Need fixed height for easy template matching
    window.set_client_height(h_wnd, 720)
    LOGGER.info("game window: %s", h_wnd)
    job()


def is_admin():
    # https://stackoverflow.com/a/41930586
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if not is_admin():
        LOGGER.error("需要用管理员权限运行此脚本，不然无法进行点击")
        exit(1)
    main()
