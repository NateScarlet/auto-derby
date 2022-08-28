# -*- coding=UTF-8 -*-
"""
version info.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

VERSION = "1.28.0"  # x-release-please-version

# deprecated

globals()["RELEASE_DATE"] = datetime.fromtimestamp(0)
globals()["LAST_GIT_COMMIT_DESCRIBE"] = ""
globals()["LAST_GIT_COMMIT_HASH"] = ""
globals()["LAST_GIT_COMMIT_AUTHOR_NAME"] = ""
globals()["LAST_GIT_COMMIT_AUTHOR_DATE"] = datetime.fromtimestamp(0)
globals()["LAST_GIT_COMMIT_SUBJECT"] = ""
globals()["LAST_GIT_COMMIT_BODY"] = ""
