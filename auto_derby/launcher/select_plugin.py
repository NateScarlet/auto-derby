# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../../.."))


from auto_derby import plugin, web, config
import uuid


def main():
    plugin.reload()
    plugins = [
        {"name": name, "doc": (p.__doc__ or "").strip()}
        for name, p in plugin.g.plugins.items()
        if not plugin.is_deprecated(name)
    ]
    token = uuid.uuid4().hex
    form_data = web.prompt(
        web.page.render(
            {
                "type": "PLUGIN_SELECT",
                "submitURL": "?token=" + token,
                "plugins": plugins,
                "defaultValue": config.PLUGINS,
            }
        ),
        web.page.ASSETS,
        web.middleware.Debug(),
        web.middleware.TokenAuth(token, ("POST",)),
    )
    value = form_data["value"]
    print(f"\nAUTO_DERBY_PLUGINS={','.join(value)}\n")


if __name__ == "__main__":
    main()
