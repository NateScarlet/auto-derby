# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import auto_derby


from auto_derby import limited_sale


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.on_limited_sale = lambda: limited_sale.ignore()


auto_derby.plugin.register(__name__, Plugin())

# Deprecated: remove at next major version
auto_derby.plugin.register("limited_sale_close", Plugin())
