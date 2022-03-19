import auto_derby
from auto_derby.single_mode import item


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        item.g.explain_effect_summary = True


auto_derby.plugin.register(__name__, Plugin())
