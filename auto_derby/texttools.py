# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import itertools
from typing import Dict, Iterable, Iterator, Text

_SIMILARITIES: Dict[Text, Dict[Text, float]] = dict()


def _set_similarity(a: Text, b: Text, v: float) -> None:
    if b < a:
        a, b = b, a
    _SIMILARITIES.setdefault(a, {})[b] = v


_set_similarity("ア", "ァ", 0.95)
_set_similarity("イ", "ィ", 0.95)
_set_similarity("ウ", "ゥ", 0.95)
_set_similarity("エ", "ェ", 0.95)
_set_similarity("オ", "ォ", 0.95)
_set_similarity("カ", "ガ", 0.8)
_set_similarity("キ", "ギ", 0.8)
_set_similarity("ク", "グ", 0.8)
_set_similarity("ケ", "ゲ", 0.8)
_set_similarity("コ", "ゴ", 0.8)
_set_similarity("サ", "ザ", 0.8)
_set_similarity("シ", "ジ", 0.8)
_set_similarity("ス", "ズ", 0.8)
_set_similarity("セ", "ゼ", 0.8)
_set_similarity("ソ", "ゾ", 0.8)
_set_similarity("タ", "ダ", 0.8)
_set_similarity("チ", "ヂ", 0.8)
_set_similarity("ッ", "ツ", 0.8)
_set_similarity("ッ", "ヅ", 0.8)
_set_similarity("ツ", "ヅ", 0.8)
_set_similarity("テ", "デ", 0.8)
_set_similarity("ト", "ド", 0.8)
_set_similarity("ハ", "バ", 0.8)
_set_similarity("ハ", "パ", 0.8)
_set_similarity("バ", "パ", 0.8)
_set_similarity("ヒ", "ビ", 0.8)
_set_similarity("ヒ", "ピ", 0.8)
_set_similarity("ビ", "ピ", 0.8)
_set_similarity("フ", "ブ", 0.8)
_set_similarity("フ", "プ", 0.8)
_set_similarity("プ", "ブ", 0.8)
_set_similarity("ヘ", "ベ", 0.8)
_set_similarity("ヘ", "ペ", 0.8)
_set_similarity("ペ", "ベ", 0.8)
_set_similarity("ホ", "ボ", 0.8)
_set_similarity("ホ", "ポ", 0.8)
_set_similarity("ポ", "ボ", 0.8)
_set_similarity("ャ", "ヤ", 0.95)
_set_similarity("ュ", "ユ", 0.95)
_set_similarity("ョ", "ヨ", 0.95)
_set_similarity("ヮ", "ワ", 0.95)
_set_similarity("ヮ", "ヷ", 0.8)
_set_similarity("ワ", "ヷ", 0.8)


def _compare_char(a: Text, b: Text) -> float:
    if a == b:
        return 1
    if b < a:
        a, b = b, a
    return _SIMILARITIES.get(a, {}).get(b, 0)


def _compare_same_length(a: Text, b: Text) -> float:
    assert len(a) == len(b), (len(a), len(b))
    return sum(_compare_char(i, j) for i, j in zip(a, b)) / len(a)


def _iterate_padding(v: Text, size: int) -> Iterator[Text]:
    if size == len(v):
        yield v
        return
    assert size > len(v)
    for i in range(len(v) + 1):
        yield from _iterate_padding(v[:i] + " " + v[i:], size)


def compare(a: Text, b: Text) -> float:
    if len(b) > len(a):
        a, b = b, a

    size = max(len(a), len(b))
    if size == 0:
        return 1
    return max(
        (
            _compare_same_length(i, j)
            for i, j in itertools.product(
                _iterate_padding(a, size),
                _iterate_padding(b, size),
            )
        ),
        default=0,
    )


def choose(v: Text, options: Iterable[Text], threshold: float = 0.5) -> Text:
    if not options:
        return v
    res, similarity = sorted(
        ((i, compare(v, i)) for i in options),
        key=lambda x: x[1],
        reverse=True,
    )[0]
    if similarity < threshold:
        return v
    return res
