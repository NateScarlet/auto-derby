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

    @classmethod
    def apply(cls) -> None:
        single_mode.race.g.DATA_PATH = cls.SINGLE_MODE_RACE_DATA_PATH
        single_mode.race.load()
        ocr.g.DATA_PATH = cls.OCR_DATA_PATH
        ocr.g.IMAGE_PATH = cls.OCR_IMAGE_PATH
        ocr.load()
        template.g.LAST_SCREENSHOT_SAVE_PATH = cls.LAST_SCRENSHOT_SAVE_PATH
        single_mode.choice.g.EVENT_IMAGE_PATH = cls.SINGLE_MODE_EVENT_IMAGE_PATH
        single_mode.choice.g.DATA_PATH = cls.SINGLE_MODE_CHOICE_PATH


config.apply()
