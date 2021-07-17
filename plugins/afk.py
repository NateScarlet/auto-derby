import auto_derby


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.pause_if_race_order_gt = 999
        auto_derby.plugin.install("no_ocr_prompt")
        auto_derby.plugin.install("no_event_prompt")
        auto_derby.plugin.install("auto_crane")


auto_derby.plugin.register(__name__, Plugin())
