# -*- coding=UTF-8 -*-
# pyright: strict


from typing import Callable, Dict, Text
from auto_derby.single_mode.training import Training
import os

from auto_derby import plugin

from . import ocr, single_mode, template, window, terminal
from .clients import ADBClient

import warnings


def _parse_training_levels(spec: Text) -> Dict[int, int]:
    ret: Dict[int, int] = {}
    for k, v in zip(
        (
            Training.TYPE_SPEED,
            Training.TYPE_STAMINA,
            Training.TYPE_POWER,
            Training.TYPE_GUTS,
            Training.TYPE_WISDOM,
        ),
        spec.split(","),
    ):
        if not v:
            continue
        ret[k] = int(v)
        if ret[k] > 6:
            warnings.warn(
                "target training level greater than 6 has same effect as 6",
                RuntimeWarning,
            )
    return ret


class config:
    LOG_PATH = os.getenv("AUTO_DERBY_LOG_PATH", "auto_derby.log")
    PLUGINS = tuple(i for i in os.getenv("AUTO_DERBY_PLUGINS", "").split(",") if i)
    ADB_ADDRESS = os.getenv("AUTO_DERBY_ADB_ADDRESS", "")
    CHECK_UPDATE = os.getenv("AUTO_DERBY_CHECK_UPDATE", "").lower() == "true"

    single_mode_race_data_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_RACE_DATA_PATH", "single_mode_races.jsonl"
    )
    ocr_data_path = os.getenv("AUTO_DERBY_OCR_LABEL_PATH", "ocr_labels.json")
    ocr_image_path = os.getenv("AUTO_DERBY_OCR_IMAGE_PATH", "")
    last_screenshot_save_path = os.getenv("AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH", "")
    pause_if_race_order_gt = int(os.getenv("AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT", "5"))
    single_mode_event_image_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH", ""
    )
    single_mode_training_image_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_TRAINING_IMAGE_PATH", ""
    )
    single_mode_choice_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_CHOICE_PATH", "single_mode_choices.json"
    )
    single_mode_event_prompt_disabled = (
        os.getenv("AUTO_DERBY_EVENT_PROMPT_DISABLED", "").lower() == "true"
    )
    plugin_path = os.getenv("AUTO_DERBY_PLUGIN_PATH", "plugins")
    single_mode_race_class = single_mode.Race
    single_mode_training_class = single_mode.Training
    single_mode_context_class = single_mode.Context
    single_mode_go_out_option_class = single_mode.go_out.Option
    single_mode_target_training_levels = _parse_training_levels(
        os.getenv("AUTO_DERBY_SINGLE_MODE_TARGET_TRAINING_LEVELS", "")
    )
    use_legacy_screenshot = (
        os.getenv("AUTO_DERBY_USE_LEGACY_SCREENSHOT", "").lower() == "true"
    )
    ocr_prompt_disabled = (
        os.getenv("AUTO_DERBY_OCR_PROMPT_DISABLED", "").lower() == "true"
    )
    adb_key_path = os.getenv("AUTO_DERBY_ADB_KEY_PATH", ADBClient.key_path)

    on_limited_sale = lambda: terminal.pause(
        "Please handle limited shop manually before confirm in terminal.\n"
        "You can also try `limited_sale_buy_first_3` / `limited_sale_buy_everything` plugin."
    )

    on_single_mode_live: Callable[[single_mode.Context], None] = lambda *_: None
    on_single_mode_crane_game: Callable[[single_mode.Context], None] = lambda *_: None

    terminal_pause_sound_path = os.path.expandvars(
        "${WinDir}/Media/Windows Background.wav"
    )
    terminal_prompt_sound_path = terminal_pause_sound_path

    @classmethod
    def apply(cls) -> None:
        ADBClient.key_path = cls.adb_key_path
        ocr.g.data_path = cls.ocr_data_path
        ocr.g.image_path = cls.ocr_image_path
        ocr.g.prompt_disabled = cls.ocr_prompt_disabled
        plugin.g.path = cls.plugin_path
        single_mode.event.g.data_path = cls.single_mode_choice_path
        single_mode.event.g.event_image_path = cls.single_mode_event_image_path
        single_mode.event.g.prompt_disabled = cls.single_mode_event_prompt_disabled
        single_mode.context.g.context_class = cls.single_mode_context_class
        single_mode.go_out.g.option_class = cls.single_mode_go_out_option_class
        single_mode.race.g.data_path = cls.single_mode_race_data_path
        single_mode.race.g.race_class = cls.single_mode_race_class
        single_mode.training.g.image_path = cls.single_mode_training_image_path
        single_mode.training.g.target_levels = cls.single_mode_target_training_levels
        single_mode.training.g.training_class = cls.single_mode_training_class
        template.g.last_screenshot_save_path = cls.last_screenshot_save_path
        terminal.g.pause_sound_path = cls.terminal_pause_sound_path
        terminal.g.prompt_sound_path = cls.terminal_prompt_sound_path
        window.g.use_legacy_screenshot = cls.use_legacy_screenshot


config.apply()
