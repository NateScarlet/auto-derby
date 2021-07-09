# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Text

from . import sound, window


class g:
    pause_sound_path = ""
    prompt_sound_path = ""


def pause(message: Text) -> None:
    close_msg = window.info(message)
    try:
        sound.play_file(g.pause_sound_path)
        input("Press enter to continue...")
    finally:
        close_msg()


def prompt(message: Text) -> Text:
    close_msg = window.info("Interaction required in terminal.")
    try:
        sound.play_file(g.pause_sound_path)
        return input(message)
    finally:
        close_msg()
