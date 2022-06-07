# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


import sys
from . import running_style_score

import warnings

# spell-checker: disable
warnings.warn("`runing_style_score` is a typo, use `running_style_score` instead.")
sys.modules[__name__] = running_style_score
