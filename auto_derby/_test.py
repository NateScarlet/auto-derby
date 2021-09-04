import inspect
import json
import os
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Protocol,
    Text,
    Tuple,
    runtime_checkable,
)

import PIL.Image

from . import clients, mathtools, template, config, data


def ignore_user_data():
    config.ocr_data_path = data.path("ocr_labels.csv")
    config.apply()


DATA_PATH = Path(__file__).parent / "test_data"


class ImageClient(clients.Client):
    def __init__(self, img: PIL.Image.Image):
        super().__init__()
        self.image = img

    def width(self) -> int:
        return self.image.width

    def height(self) -> int:
        return self.image.height

    def screenshot(self) -> PIL.Image.Image:
        return self.image

    def tap(self, point: Tuple[int, int]) -> None:
        raise NotImplementedError()

    def swipe(self, point: Tuple[int, int]) -> None:
        raise NotImplementedError()


def use_screenshot(name: Text):
    ignore_user_data()
    img = PIL.Image.open(DATA_PATH / name).convert("RGB")
    # resize old test data
    if img.width == 466:
        img = img.resize((540, 960))
    template.invalidate_screeshot()
    clients.set_current(ImageClient(img))
    template.g.screenshot_width = img.width
    return img, mathtools.ResizeProxy(img.width)


SNAPSHOT_UPDATE = os.getenv("SNAPSHOT_UPDATE", "").lower() == "true"


@runtime_checkable
class SupportsToDict(Protocol):
    def to_dict(self) -> Dict[Text, Any]:
        ...


def _json_transform(v: object) -> object:
    if isinstance(v, SupportsToDict):
        return {k: _json_transform(v) for k, v in v.to_dict().items()}
    if isinstance(v, dict):
        return {str(k): _json_transform(v) for k, v in v.items()}
    if isinstance(v, (list, tuple)):
        return [_json_transform(i) for i in v]
    if isinstance(v, (int, float)):
        return v
    return str(v)


def _default_encode(v: object) -> Tuple[Text, Text]:
    if isinstance(v, (SupportsToDict, list, tuple, int, float, dict)):
        return (
            json.dumps(
                v,
                default=_json_transform,
                indent=2,
                ensure_ascii=False,
            ),
            ".json",
        )

    return str(v), ".txt"


def snapshot_match(
    v: object,
    *,
    name: Text = "",
    encode: Callable[[object], Tuple[Text, Text]] = _default_encode,
    assert_match: Optional[Callable[[Text, Text], None]] = None,
    update: bool = SNAPSHOT_UPDATE,
    skip: int = 0,
):

    actual, ext = encode(v)

    def _assert_match(a: Text, b: Text):
        if assert_match:
            assert_match(a, b)
        elif ext == ".json":
            json_a = json.loads(a)
            json_b = json.loads(b)
            assert json_a == json_b, (json_a, json_b)
        else:
            assert a == b, (a, b)

    _, filename, _, func_name, _, _ = inspect.stack()[skip + 1]
    data_dir = os.path.join(os.path.dirname(filename), "__snapshots__")
    key = func_name
    if name:
        key += "." + name
    save_path = os.path.join(
        data_dir,
        os.path.splitext(os.path.basename(filename))[0],
        key + ext,
    )

    def _update():
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf8") as f:
            f.write(actual)

    if update:
        _update()
        return
    try:
        with open(save_path, "r", encoding="utf8") as f:
            expected = f.read()
        _assert_match(expected, actual)
    except FileNotFoundError:
        _update()
