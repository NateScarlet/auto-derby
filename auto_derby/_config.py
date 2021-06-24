# -*- coding=UTF-8 -*-
# pyright: strict


from typing import Dict, Text
from auto_derby.single_mode.training import Training
import os

from auto_derby import plugin

from . import ocr, single_mode, template, window
from .clients import ADBClient


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
    return ret


class config:
    LOG_PATH = os.getenv("AUTO_DERBY_LOG_PATH", "auto_derby.log")
    PLUGINS = tuple(i for i in os.getenv("AUTO_DERBY_PLUGINS", "").split(",") if i)
    ADB_ADDRESS = os.getenv("AUTO_DERBY_ADB_ADDRESS", "")

    single_mode_race_data_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_RACE_DATA_PATH", "single_mode_races.json"
    )
    ocr_data_path = os.getenv("AUTO_DERBY_OCR_LABEL_PATH", "ocr_labels.json")
    ocr_image_path = os.getenv("AUTO_DERBY_OCR_IMAGE_PATH", "")
    last_screenshot_save_path = os.getenv("AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH", "")
    pause_if_race_order_gt = int(os.getenv("AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT", "5"))
    single_mode_event_image_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH", ""
    )
    single_mode_choice_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_CHOICE_PATH", "single_mode_choices.json"
    )
    plugin_path = os.getenv("AUTO_DERBY_PLUGIN_PATH", "plugins")
    single_mode_race_class = single_mode.Race
    single_mode_training_class = single_mode.Training
    single_mode_context_class = single_mode.Context
    single_mode_target_training_levels = _parse_training_levels(
        os.getenv("AUTO_DERBY_SINGLE_MODE_TARGET_TRAINING_LEVELS", "")
    )
    use_legacy_screenshot = (
        os.getenv("AUTO_DERBY_USE_LEGACY_SCREENSHOT", "").lower() == "true"
    )
    adb_key_path = os.getenv("AUTO_DERBY_ADB_KEY_PATH", ADBClient.key_path)

    @classmethod
    def apply(cls) -> None:
        ADBClient.key_path = cls.adb_key_path
        ocr.g.data_path = cls.ocr_data_path
        ocr.g.image_path = cls.ocr_image_path
        plugin.g.path = cls.plugin_path
        single_mode.choice.g.data_path = cls.single_mode_choice_path
        single_mode.choice.g.event_image_path = cls.single_mode_event_image_path
        single_mode.context.g.context_class = cls.single_mode_context_class
        single_mode.race.g.data_path = cls.single_mode_race_data_path
        single_mode.race.g.race_class = cls.single_mode_race_class
        single_mode.training.g.training_class = cls.single_mode_training_class
        single_mode.training.g.target_levels = cls.single_mode_target_training_levels
        template.g.last_screenshot_save_path = cls.last_screenshot_save_path
        window.g.use_legacy_screenshot = cls.use_legacy_screenshot

        ocr.reload()
        single_mode.choice.reload()
        single_mode.race.reload()


config.apply()
