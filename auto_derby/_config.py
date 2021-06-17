from auto_derby import plugin
from . import single_mode, ocr, template
import os


class config:
    SINGLE_MODE_RACE_DATA_PATH = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_RACE_DATA_PATH", "single_mode_races.json"
    )
    LOG_PATH = os.getenv("AUTO_DERBY_LOG_PATH", "auto_derby.log")
    OCR_DATA_PATH = os.getenv("AUTO_DERBY_OCR_LABEL_PATH", "ocr_labels.json")
    OCR_IMAGE_PATH = os.getenv("AUTO_DERBY_OCR_IMAGE_PATH", "")
    LAST_SCRENSHOT_SAVE_PATH = os.getenv("AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH", "")
    PAUSE_IF_RACE_ORDER_GT = int(os.getenv("AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT", "5"))
    SINGLE_MODE_EVENT_IMAGE_PATH = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH", ""
    )
    SINGLE_MODE_CHOICE_PATH = os.getenv(
        "AUTO_DERBY_SINGLE_MODE_CHOICE_PATH", "single_mode_choices.json"
    )
    PLUGIN_PATH = os.getenv("AUTO_DERBY_PLUGIN_PATH", "plugins")
    PLUGINS = os.getenv("AUTO_DERBY_PLUGINS", "").split(",")
    SINGLE_MODE_RACE_CLASS = single_mode.Race
    SINGLE_MODE_TRAINING_CLASS = single_mode.Training

    @classmethod
    def apply(cls) -> None:
        ocr.g.DATA_PATH = cls.OCR_DATA_PATH
        ocr.g.IMAGE_PATH = cls.OCR_IMAGE_PATH
        plugin.g.PATH = cls.PLUGIN_PATH
        single_mode.choice.g.DATA_PATH = cls.SINGLE_MODE_CHOICE_PATH
        single_mode.choice.g.EVENT_IMAGE_PATH = cls.SINGLE_MODE_EVENT_IMAGE_PATH
        single_mode.race.g.DATA_PATH = cls.SINGLE_MODE_RACE_DATA_PATH
        single_mode.race.g.RACE_CLASS = cls.SINGLE_MODE_RACE_CLASS
        single_mode.training.g.TRAINING_CLASS = cls.SINGLE_MODE_TRAINING_CLASS
        template.g.LAST_SCREENSHOT_SAVE_PATH = cls.LAST_SCRENSHOT_SAVE_PATH

        ocr.reload()
        single_mode.choice.reload()
        single_mode.race.reload()


config.apply()
