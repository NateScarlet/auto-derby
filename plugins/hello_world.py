import auto_derby


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        print("hello world")


auto_derby.plugin.register(__name__, Plugin())
