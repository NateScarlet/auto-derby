# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """


import ctypes
import time
import webbrowser

import win32con
import win32gui

from . import window, jobs

import logging

LOGGER = logging.getLogger(__name__)


def main():
    h_wnd = window.get_game()
    if not h_wnd:
        if win32gui.MessageBox(0, "启动DMM赛马娘？", "找不到窗口", win32con.MB_YESNO):
            webbrowser.open('dmmgameplayer://umamusume/cl/general/umamusume')
            while not h_wnd:
                time.sleep(1)
                h_wnd = window.get_game()
        else:
            exit(1)
    LOGGER.info("game window: %s", h_wnd)
    jobs.team_race()


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
