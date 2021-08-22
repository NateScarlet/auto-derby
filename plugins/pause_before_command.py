from auto_derby.single_mode.commands.command import Command
from auto_derby.single_mode.context import Context
import auto_derby
from auto_derby import terminal


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next = auto_derby.config.on_single_mode_command

        def _on_command(ctx: Context, command: Command):
            terminal.pause(f"pause before command: {command.name()}")
            _next(ctx, command)

        auto_derby.config.on_single_mode_command = _on_command


auto_derby.plugin.register(__name__, Plugin())
