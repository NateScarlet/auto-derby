import auto_derby
from auto_derby import window


import logging

_LOGGER = logging.getLogger(__name__)


def _log_process(pid: int):
    try:
        # https://stackoverflow.com/a/42607775
        from win32com.client import GetObject

        wmi = GetObject("winmgmts:")

        # collect all the running processes
        processes = wmi.ExecQuery("Select * from win32_process")
        for p in processes:
            if p.ProcessId == pid:
                _LOGGER.debug(
                    "process %d: name='%s' executable='%s' command='%s'",
                    p.ProcessId,
                    p.Name,
                    p.ExecutablePath,
                    p.CommandLine,
                )
                break
        else:
            _LOGGER.debug("process not found: %d", pid)
    except Exception as ex:
        _LOGGER.error("log process failed: pid=%d error='%s'", pid, ex)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        import win32process
        import win32gui

        _LOGGER.setLevel(logging.DEBUG)
        next_cb = window.g.on_foreground_will_change

        def cb():
            h_wnd = win32gui.GetForegroundWindow()
            text = win32gui.GetWindowText(h_wnd)
            thread_id, process_id = win32process.GetWindowThreadProcessId(h_wnd)
            _LOGGER.debug(
                "foreground window: process_id=%d thread_id=%d text='%s'",
                process_id,
                thread_id,
                text,
            )
            _log_process(process_id)
            next_cb()

        window.g.on_foreground_will_change = cb


auto_derby.plugin.register(__name__, Plugin())
