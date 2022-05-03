# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """


import argparse
import logging
import logging.handlers
import os
import time
import warnings
import webbrowser

import win32con
import win32gui

from . import __version__, clients, config, jobs, plugin, templates, version, app
from .infrastructure.logging_log_service import LoggingLogService
from .infrastructure.multi_log_service import MultiLogService
from .infrastructure.web_log_service import WebLogService

LOGGER = logging.getLogger(__name__)


def main():
    LOGGER.info(f"auto_derby: {__version__.VERSION} ({__version__.RELEASE_DATE})")
    if config.CHECK_UPDATE:
        version.check_update()
    avaliable_jobs = {
        "team_race": jobs.team_race,
        "champions_meeting": jobs.champions_meeting,
        "legend_race": jobs.legend_race,
        "nurturing": jobs.nurturing,
        "daily_race_money": lambda: jobs.daily_race(templates.MOONLIGHT_PRIZE),
        "daily_race_sp": lambda: jobs.daily_race(templates.JUPITER_CUP),
        "roulette_derby": jobs.roulette_derby,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("job")
    parser.add_argument(
        "-p",
        "--plugin",
        nargs="+",
        default=config.PLUGINS,
        help="plugin names to enable",
    )
    parser.add_argument(
        "--adb",
        help="adb connect address like `127.0.0.1:5037`",
        default=config.ADB_ADDRESS,
    )
    args = parser.parse_args()
    job = avaliable_jobs.get(args.job)
    config.ADB_ADDRESS = args.adb

    def _client() -> clients.Client:
        if config.ADB_ADDRESS:
            return clients.ADBClient(config.ADB_ADDRESS)
        else:
            c = clients.DMMClient.find()
            if not c:
                if (
                    win32gui.MessageBox(
                        0,
                        "Launch DMM umamusume?",
                        "Can not found window",
                        win32con.MB_YESNO,
                    )
                    == 6
                ):
                    webbrowser.open("dmmgameplayer://umamusume/cl/general/umamusume")
                    while not c:
                        time.sleep(1)
                        LOGGER.info("waiting game launch")
                        c = clients.DMMClient.find()
                    LOGGER.info("game window: %s", c.h_wnd)
                else:
                    exit(1)
            return c

    plugin.reload()
    config.client = _client
    plugins = args.plugin
    for i in plugins:
        plugin.install(i)
    config.apply()

    with app.cleanup as cleanup:
        if not config.web_log_disabled:
            app.log = MultiLogService(
                app.log,
                WebLogService(cleanup),
            )
            time.sleep(1)  # wait browser

        if not job:
            LOGGER.error(
                "unknown job: %s\navaliable jobs:\n  %s",
                args.job,
                "\n  ".join(avaliable_jobs.keys()),
            )
            exit(1)

        c = config.client()
        c.setup()
        clients.set_current(c)
        job()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    app.log = LoggingLogService()

    LOG_PATH = config.LOG_PATH
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

    warnings.filterwarnings("once", module="auto_derby(\\..*)?")
    try:
        main()
    except SystemExit:
        raise
    except:
        LOGGER.exception("unexpected exception")
        exit(1)
