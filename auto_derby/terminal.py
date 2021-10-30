# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import contextlib
from typing import Text

from . import sound, window


class PromptDisabled(PermissionError):
    def __init__(self):
        super().__init__("prompt disabled")


class g:
    pause_sound_path = ""
    prompt_sound_path = ""
    prompt_disabled = False


def pause(message: Text) -> None:
    close_msg = window.info(message)
    try:
        sound.play_file(g.pause_sound_path)
        input("Press enter to continue...")
    finally:
        close_msg()


def prompt(message: Text) -> Text:
    if g.prompt_disabled:
        raise PromptDisabled
    close_msg = window.info("Interaction required in terminal.")
    try:
        sound.play_file(g.pause_sound_path)
        return input(message)
    finally:
        close_msg()


@contextlib.contextmanager
def prompt_disabled(v: bool):
    original = g.prompt_disabled
    g.prompt_disabled = v
    try:
        yield
    finally:
        g.prompt_disabled = original
