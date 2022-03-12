import auto_derby


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_item_prompt_disabled = True


auto_derby.plugin.register(__name__, Plugin())
