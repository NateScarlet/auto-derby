# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Text

from . import sound, window


class g:
    pause_sound_path = ""


def pause(message: Text) -> None:
    close_msg = window.info(message)
    try:
        sound.play_file(g.pause_sound_path)
        input("Press enter to continue...")
    finally:
        close_msg()
