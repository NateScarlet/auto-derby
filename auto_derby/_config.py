# -*- coding=UTF-8 -*-
# pyright: strict


import os
import warnings
from typing import Callable, Dict, Text

from auto_derby.constants import TrainingType

from . import ocr, plugin, single_mode, template, terminal, window, data
from .clients import ADBClient, Client
from .single_mode import commands as sc
from .single_mode.training import Training


def _parse_training_levels(spec: Text) -> Dict[TrainingType, int]:
    ret: Dict[TrainingType, int] = {}
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


def _default_on_single_mode_crane_game(ctx: single_mode.Context) -> None:
    pass


def _default_on_single_mode_end(ctx: single_mode.Context) -> None:
    pass


def _getenv_int(key: Text, d: int) -> int:
    try:
        return int(os.getenv(key, ""))
    except:
        return d


def _default_client() -> Client:
    raise NotImplementedError()


class config:
    LOG_PATH = os.getenv("AUTO_DERBY_LOG_PATH", "auto_derby.log")
    PLUGINS = tuple(i for i in os.getenv("AUTO_DERBY_PLUGINS", "").split(",") if i)
    ADB_ADDRESS = os.getenv("AUTO_DERBY_ADB_ADDRESS", "")
    CHECK_UPDATE = os.getenv("AUTO_DERBY_CHECK_UPDATE", "").lower() == "true"

    client = _default_client
    single_mode_race_data_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_RACE_DATA_PATH",
        data.path("single_mode_races.jsonl"),
    )
    single_mode_race_result_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_RACE_RESULT_PATH",
        "data/single_mode_race_results.jsonl",
    )
    single_mode_race_result_max_bytes = _getenv_int(
        "AUTO_DERBY_SINGLE_MODE_RACE_RESULT_MAX_BYTES",
        single_mode.race.g.result_max_bytes,
    )
    ocr_data_path = os.getenv("AUTO_DERBY_OCR_LABEL_PATH", "data/ocr_labels.csv")
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
        "AUTO_DERBY_SINGLE_MODE_CHOICE_PATH", "data/single_mode_choices.csv"
    )
    single_mode_event_prompt_disabled = (
        os.getenv("AUTO_DERBY_SINGLE_MODE_EVENT_PROMPT_DISABLED", "").lower() == "true"
        or os.getenv("AUTO_DERBY_EVENT_PROMPT_DISABLED", "").lower()
        == "true"  # deprecated
    )
    single_mode_item_prompt_disabled = (
        os.getenv("AUTO_DERBY_SINGLE_MODE_ITEM_PROMPT_DISABLED", "").lower() == "true"
    )
    plugin_path = os.getenv("AUTO_DERBY_PLUGIN_PATH", "plugins")
    single_mode_race_class = single_mode.Race
    single_mode_training_class = single_mode.Training
    single_mode_training_partner_class = single_mode.training.Partner
    single_mode_context_class = single_mode.Context
    single_mode_go_out_option_class = single_mode.go_out.Option
    single_mode_go_out_names = single_mode.go_out.g.names
    single_mode_health_care_score = sc.g.health_care_score
    single_mode_rest_score = sc.g.rest_score
    single_mode_summer_rest_score = sc.g.summer_rest_score
    single_mode_ignore_training_commands = sc.g.ignore_training_commands
    single_mode_should_retry_race = sc.g.should_retry_race
    single_mode_item_label_path = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_ITEM_LABEL_PATH", "data/single_mode_item_labels.csv"
    )
    single_mode_item_class = single_mode.item.g.item_class
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
    adb_action_wait = _getenv_int("AUTO_DERBY_ADB_ACTION_WAIT", ADBClient.action_wait)

    on_limited_sale = lambda: terminal.pause(
        "Please handle limited shop manually before confirm in terminal.\n"
        "You can also try `limited_sale_buy_first_3` / `limited_sale_buy_everything` / `limited_sale_close` plugin."
    )

    on_single_mode_live = sc.g.on_winning_live
    on_single_mode_command = sc.g.on_command
    on_single_mode_race_result = sc.g.on_race_result
    on_single_mode_crane_game: Callable[
        [single_mode.Context], None
    ] = _default_on_single_mode_crane_game
    on_single_mode_end: Callable[
        [single_mode.Context], None
    ] = _default_on_single_mode_end

    terminal_pause_sound_path = os.path.expandvars(
        "${WinDir}/Media/Windows Background.wav"
    )
    terminal_prompt_sound_path = terminal_pause_sound_path

    @classmethod
    def apply(cls) -> None:
        ADBClient.key_path = cls.adb_key_path
        ADBClient.action_wait = cls.adb_action_wait
        ocr.g.data_path = cls.ocr_data_path
        ocr.g.image_path = cls.ocr_image_path
        ocr.g.prompt_disabled = cls.ocr_prompt_disabled
        plugin.g.path = cls.plugin_path
        single_mode.event.g.data_path = cls.single_mode_choice_path
        single_mode.event.g.event_image_path = cls.single_mode_event_image_path
        single_mode.event.g.prompt_disabled = cls.single_mode_event_prompt_disabled
        single_mode.context.g.context_class = cls.single_mode_context_class
        single_mode.go_out.g.option_class = cls.single_mode_go_out_option_class
        single_mode.go_out.g.names = cls.single_mode_go_out_names
        single_mode.race.g.data_path = cls.single_mode_race_data_path
        single_mode.race.g.result_path = cls.single_mode_race_result_path
        single_mode.race.g.result_max_bytes = cls.single_mode_race_result_max_bytes
        single_mode.race.g.race_class = cls.single_mode_race_class
        single_mode.training.g.image_path = cls.single_mode_training_image_path
        single_mode.training.g.target_levels = cls.single_mode_target_training_levels
        single_mode.training.g.training_class = cls.single_mode_training_class
        single_mode.training.g.partner_class = cls.single_mode_training_partner_class
        single_mode.item.g.label_path = cls.single_mode_item_label_path
        single_mode.item.g.prompt_disabled = cls.single_mode_item_prompt_disabled
        single_mode.item.g.item_class = cls.single_mode_item_class
        sc.g.rest_score = cls.single_mode_rest_score
        sc.g.summer_rest_score = cls.single_mode_summer_rest_score
        sc.g.health_care_score = cls.single_mode_health_care_score
        sc.g.ignore_training_commands = cls.single_mode_ignore_training_commands
        sc.g.pause_if_race_order_gt = cls.pause_if_race_order_gt
        sc.g.on_winning_live = cls.on_single_mode_live
        sc.g.on_command = cls.on_single_mode_command
        sc.g.on_race_result = cls.on_single_mode_race_result
        sc.g.should_retry_race = cls.single_mode_should_retry_race
        template.g.last_screenshot_save_path = cls.last_screenshot_save_path
        terminal.g.pause_sound_path = cls.terminal_pause_sound_path
        terminal.g.prompt_sound_path = cls.terminal_prompt_sound_path
        window.g.use_legacy_screenshot = cls.use_legacy_screenshot


config.apply()
