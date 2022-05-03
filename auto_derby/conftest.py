# -*- coding=UTF-8 -*-
"""pytest configuration file, should not been imported"""

import os
import time
import pytest

from . import app
from .infrastructure.web_log_service import WebLogService


@pytest.fixture(autouse=True, scope="session", name="app")
def _app():
    with app.cleanup:
        if not os.getenv("CI"):
            app.log = WebLogService(
                app.cleanup,
            )
            time.sleep(1)  # wait browser
        yield app
