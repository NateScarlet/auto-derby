import auto_derby
from auto_derby import window, app


import logging


def _log_process(pid: int):
    try:
        # https://stackoverflow.com/a/42607775
        from win32com.client import GetObject

        wmi = GetObject("winmgmts:")

        # collect all the running processes
        processes = wmi.ExecQuery("Select * from win32_process")
        for p in processes:
            if p.ProcessId == pid:
                app.log.text(
                    "process %d: name='%s' executable='%s' command='%s'"
                    % (
                        p.ProcessId,
                        p.Name,
                        p.ExecutablePath,
                        p.CommandLine,
                    ),
                    level=app.DEBUG,
                )
                break
        else:
            app.log.text("process not found: %d" % pid, level=app.DEBUG)
    except Exception as ex:
        app.log.text(
            "log process failed: pid=%d error='%s'" % (pid, ex), level=app.ERROR
        )


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        import win32process
        import win32gui

        next_cb = window.g.on_foreground_will_change

        def cb():
            h_wnd = win32gui.GetForegroundWindow()
            text = win32gui.GetWindowText(h_wnd)
            thread_id, process_id = win32process.GetWindowThreadProcessId(h_wnd)
            app.log.text(
                "foreground window: process_id=%d thread_id=%d text='%s'"
                % (
                    process_id,
                    thread_id,
                    text,
                )
            )
            _log_process(process_id)
            next_cb()

        window.g.on_foreground_will_change = cb


auto_derby.plugin.register(__name__, Plugin())
