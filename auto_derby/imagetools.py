# -*- coding=UTF-8 -*-
# pyright: strict
"""tools for image processing.  """

import base64
import csv
import hashlib
import io
import os
import threading
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Literal,
    Optional,
    Set,
    Text,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from typing import cast as cast_type

import cast_unknown as cast
import cv2
import cv2.img_hash
import numpy as np
from PIL.Image import BICUBIC, Image, fromarray

from .vptree import VPTree


class _g:
    window_id = 0


_Resample = Literal[0, 1, 2, 3, 4, 5]


def md5(
    b_img: np.ndarray, *, save_path: Optional[Text] = None, save_mode: Text = "1"
) -> Text:
    _id = hashlib.md5(b_img.tobytes()).hexdigest()

    if save_path:
        dst = Path(save_path) / _id[0] / _id[1:3] / (_id[3:] + ".png")
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            pil_image(b_img).convert(save_mode).save(dst)

    return _id


_HASH_ALGORITHM = cv2.img_hash.BlockMeanHash_create()


def _image_hash(
    cv_img: np.ndarray,
    *,
    divide_x: int = 1,
    divide_y: int = 1,
) -> Text:
    if divide_x > 1:
        h = ""
        for part in np.array_split(cv_img, divide_x, axis=1):
            h += _image_hash(part, divide_y=divide_y)
        return h

    if divide_y > 1:
        h = ""
        for part in np.array_split(cv_img, divide_y, axis=0):
            h += _image_hash(part)
        return h

    return _HASH_ALGORITHM.compute(cv_img).tobytes().hex()


def image_hash(
    img: Image,
    *,
    save_path: Optional[Text] = None,
    divide_x: int = 1,
    divide_y: int = 1,
) -> Text:
    cv_img = np.asarray(img.convert("L"))

    h = _image_hash(cv_img, divide_x=divide_x, divide_y=divide_y)

    if save_path:
        md5_hash = hashlib.md5(img.tobytes()).hexdigest()
        dst = Path(save_path) / h[0] / h[1:3] / h[3:] / (md5_hash + ".png")
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.convert("RGB").save(dst)

    return h


def compare_hash(a: Text, b: Text) -> float:
    if a == b:
        return 1.0
    cv_a = np.array(list(bytes.fromhex(a)), np.uint8)
    cv_b = np.array(list(bytes.fromhex(b)), np.uint8)
    res = _HASH_ALGORITHM.compare(cv_a, cv_b)
    return 1 - (res / (len(a) * 2))


def _hash_distance(a: Text, b: Text) -> float:
    return 1 - compare_hash(a, b)


def _cast_float(v: Any) -> float:
    return float(v)


def cv_image(img: Image) -> np.ndarray:
    if img.mode == "RGB":
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    if img.mode == "L":
        return np.array(img)
    raise ValueError("cv_image: unsupported mode: %s" % img.mode)


def pil_image(img: np.ndarray) -> Image:
    if img.shape[2:] == (3,):
        return fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return fromarray(img)


def pil_image_of(img: Union[np.ndarray, Image]) -> Image:
    if isinstance(img, Image):
        return img
    return pil_image(img)


def compare_color(
    a: Union[Tuple[int, ...], int], b: Union[Tuple[int, ...], int], *, bit_size: int = 8
) -> float:
    max_value = (1 << bit_size) - 1
    t_a = tuple(cast.list_(a, (int,)))
    t_b = tuple(cast.list_(b, (int,)))
    if len(t_a) != len(t_b):
        return 0

    return max(
        1
        - _cast_float(
            np.sqrt(_cast_float(np.sum((np.array(t_a) - np.array(t_b)) ** 2, axis=0)))
        )
        / max_value,
        0,
    )


def level(
    img: np.ndarray, black: np.ndarray, white: np.ndarray, *, bit_size: int = 8
) -> np.ndarray:
    max_value = (1 << bit_size) - 1
    return np.clip((img - black) / (white - black) * max_value, 0, max_value).astype(
        img.dtype
    )


def color_key(
    img: np.ndarray, color: np.ndarray, threshold: float = 0.8, bit_size: int = 8
) -> np.ndarray:
    max_value = (1 << bit_size) - 1
    assert img.shape == color.shape, (img.shape, color.shape)

    if len(img.shape) == 2:
        img = img[..., np.newaxis]
        color = color[..., np.newaxis]

    # do this is somehow faster than
    # `numpy.linalg.norm(img.astype(int) - color.astype(int), axis=2,).clip(0, 255).astype(np.uint8)`
    diff_img = (
        np.asarray(
            np.sqrt(
                np.asarray(np.sum((img.astype(int) - color.astype(int)) ** 2, axis=2))
            )
        )
        .clip(0, 255)
        .astype(img.dtype)
    )

    ret = max_value - diff_img
    if threshold > 0:
        mask_img = (ret > (max_value * threshold)).astype(img.dtype)
        ret *= mask_img
    ret = ret.clip(0, 255)
    ret = ret.astype(img.dtype)
    return ret


def constant_color_key(
    img: np.ndarray, *colors: Tuple[int, ...], threshold: float = 0.8, bit_size: int = 8
) -> np.ndarray:
    ret = np.zeros(img.shape[:2], dtype=img.dtype)

    for color in colors:
        match_img = color_key(
            img, np.full_like(img, color), threshold=threshold, bit_size=bit_size
        )
        ret = np.array(np.maximum(ret, match_img))

    return ret


def compare_color_near(
    img: np.ndarray,
    pos: Tuple[int, int],
    color: Tuple[int, ...],
    radius: int = 2,
) -> float:
    x, y = pos
    bbox = (
        x - radius,
        y - radius,
        x + radius,
        y + radius,
    )
    mask = constant_color_key(
        img[
            bbox[1] : bbox[3],
            bbox[0] : bbox[2],
        ],
        color,
    )
    mask_max = np.uint8(np.amax(mask))
    return int(mask_max) / 255


def sharpen(img: np.ndarray, size: int = 1, *, bit_size: int = 8) -> np.ndarray:
    return cv2.filter2D(
        img, bit_size, np.array(((-1, -1, -1), (-1, 9, -1), (-1, -1, -1))) * size
    )


def mix(a: np.ndarray, b: np.ndarray, a_mix: float) -> np.ndarray:
    total_ratio = 10000
    a_ratio = int(a_mix * total_ratio)
    b_ratio = total_ratio - a_ratio
    return ((a.astype(int) * a_ratio + b.astype(int) * b_ratio) / total_ratio).astype(
        a.dtype
    )


def border_flood_fill(
    cv_img: np.ndarray, color: Tuple[int, ...] = (255,)
) -> np.ndarray:
    h, w = cv_img.shape[:2]

    border_points = (
        *((0, i) for i in range(h)),
        *((i, 0) for i in range(w)),
        *((w - 1, i) for i in range(h)),
        *((i, h - 1) for i in range(w)),
    )

    fill_mask_img = cv2.copyMakeBorder(cv_img, 1, 1, 1, 1, cv2.BORDER_CONSTANT)
    bg_mask_img = np.zeros_like(cv_img)
    for i in border_points:
        x, y = i
        if cv_img[y, x] != 0:
            continue
        cv2.floodFill(bg_mask_img, fill_mask_img, (x, y), color, 0, 0)

    return bg_mask_img


def bg_mask_by_outline(outline_img: np.ndarray) -> np.ndarray:
    return border_flood_fill(outline_img)


def inside_outline(img: np.ndarray, outline_img: np.ndarray) -> np.ndarray:
    _, outline_img = cv2.threshold(outline_img, 0, 255, cv2.THRESH_BINARY)
    bg_mask = border_flood_fill(outline_img) + outline_img
    fg_mask = 255 - bg_mask
    return cv2.copyTo(img, fg_mask)


def resize(
    img: Image,
    *,
    height: Optional[int] = None,
    width: Optional[int] = None,
    resample: _Resample = BICUBIC,
) -> Image:
    if height and width:
        return img.resize((width, height), resample=resample)
    w, h = img.width, img.height
    if height:
        w = round(height * (w / h))
        h = height
    elif width:
        h = round(width * (h / w))
        w = width
    return img.resize((w, h), resample=resample)


def fill_area(
    img: np.ndarray,
    color: Tuple[int, ...],
    *,
    mode: int = cv2.RETR_EXTERNAL,
    size_lt: int,
):
    contours, _ = cv2.findContours(
        (img * 255).astype(np.uint8), mode, cv2.CHAIN_APPROX_NONE
    )
    for i in contours:
        size = cv2.contourArea(i)
        if size < size_lt:
            cv2.drawContours(img, [i], -1, color, cv2.FILLED)


def show(img: Image, title: Text = "") -> Callable[[], None]:

    stop_event = threading.Event()
    _g.window_id += 1
    title = f"{title} - {_g.window_id}"

    def _run():
        cv_img = cv_image(img)
        try:
            cv2.imshow(title, cv_img)
            while not stop_event.is_set() and cv2.getWindowProperty(title, 0) >= 0:
                if cv2.pollKey() == "q":
                    break
        finally:
            cv2.destroyWindow(title)

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    def _close():
        stop_event.set()
        t.join()

    return _close


T = TypeVar("T")


class ImageHashMapQueryResult(Generic[T]):
    def __init__(self, hash: Text, value: T, similarity: float) -> None:
        self.hash = hash
        self.value = value
        self.similarity = similarity

    def __str__(self):
        return (
            f"IHMQueryResult<{self.similarity*100:.1f}%,{self.value},{self.hash[:8]}>"
        )


class ImageHashMap(Generic[T]):
    def __init__(self) -> None:
        self._labels: Dict[Text, T] = {}
        self._tree = VPTree[Text](_hash_distance)
        self._tree_key = 0

    def _prepare_tree(self) -> VPTree[Text]:
        key = len(self._labels)
        if self._tree_key != key:
            self._tree.set_data(tuple(self._labels.keys()))
            self._tree_key = key
        return self._tree

    def is_empty(self) -> bool:
        return not self._labels

    def query(self, h: Text) -> ImageHashMapQueryResult[T]:
        if not self._labels:
            raise ValueError("no data")
        tree = self._prepare_tree()
        distance, hash = tree.nearest_neighbor(h)
        return ImageHashMapQueryResult(
            hash,
            self._labels[hash],
            1 - distance,
        )

    def label(self, h: Text, value: T) -> None:
        self._labels[h] = value

    def clear(self) -> None:
        self._labels.clear()


class CSVImageHashMap(ImageHashMap[T]):
    def __init__(
        self,
        type: Type[T],
    ):
        super().__init__()
        self.type = type
        self.save_path = ""

        self._loaded_paths: Set[Text] = set()

    def _value_from_text(self, v: Text) -> T:
        if self.type is str:
            return cast_type(T, v)
        if self.type is int:
            return cast_type(T, int(v))
        raise NotImplementedError("not supported type", self.type)

    def _value_to_text(self, v: T) -> Text:
        return str(v)

    def load(self, path: Text) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for k, v in csv.reader(f):
                    self._labels[k] = self._value_from_text(v)
        except FileNotFoundError:
            return False
        self._loaded_paths.add(path)
        return True

    def load_once(self, path: Text) -> bool:
        if path in self._loaded_paths:
            return False
        return self.load(path)

    def label(self, h: Text, value: T) -> None:
        super().label(h, value)
        path = self.save_path
        if not path:
            raise ValueError("label save path is empty")

        def _do():
            with open(path, "a", encoding="utf-8", newline="") as f:
                csv.writer(f).writerow((h, self._value_to_text(value)))

        try:
            _do()
        except FileNotFoundError:
            os.makedirs(os.path.dirname(path))
            _do()

    def clear(self) -> None:
        super().clear()
        self._loaded_paths.clear()


def bbox_from_rect(rect: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    x, y, w, h = rect
    l, t, r, b = x, y, x + w, y + h
    return l, t, r, b


def rect_from_bbox(bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    l, t, r, b = bbox
    x, y, w, h = l, b, r - l, b - t
    return x, y, w, h


def auto_crop(cv_img: np.ndarray) -> np.ndarray:
    l, t, r, b = bbox_from_rect(
        cv2.boundingRect(
            cv2.findNonZero(cv_img),
        )
    )
    return cv_img[t:b, l:r]


def data_url(img: Image) -> Text:
    b = io.BytesIO()
    img.save(b, "PNG")
    data = base64.b64encode(b.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{data}"
