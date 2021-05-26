# -*- coding=UTF-8 -*-
# pyright: strict
"""tools for image processing.  """


import hashlib
import os
from pathlib import Path
from typing import Optional, Text

import numpy as np
from PIL.Image import fromarray


SKIP_SAVE = os.getenv("AUTO_DERBY_IMAGE_SKIP_SAVE", "").lower() == "true"

def md5(b_img: np.ndarray, *, save_path: Optional[Text] = None) -> Text:
    _id = hashlib.md5(b_img.tobytes()).hexdigest()

    if save_path and not SKIP_SAVE:
        dst = Path(save_path) / _id[0] / _id[1:3] / (_id[3:] + ".png")
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            fromarray(b_img).convert("1").save(dst)

    return _id
