# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../.."))

import logging

import web

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    print(
        web.prompt(
            f"""\
<h1>test</h1>
<a href="/__main__.py">python source file</a>
<form method="POST">
<input name="value" />
<button type="submit" >submit</button>
</form>
""",
            web.Route("/__main__.py", web.StaticFile(__file__, "text/plain")),
            web.middleware.Debug(),
        )
    )
