# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import itertools
import logging
from typing import Dict, Iterable, Iterator, Text, Tuple

_LOGGER = logging.getLogger(__name__)


_SIMILARITIES: Dict[Tuple[Text, Text], float] = dict()


def _similarity_key(a: Text, b: Text):
    if a == b:
        raise ValueError("should not set similarity for same text: %s" % a)
    if b < a:
        return (b, a)
    return (a, b)


_SIMILARITIES[_similarity_key("ア", "ァ")] = 0.95
_SIMILARITIES[_similarity_key("イ", "ィ")] = 0.95
_SIMILARITIES[_similarity_key("ウ", "ゥ")] = 0.95
_SIMILARITIES[_similarity_key("エ", "ェ")] = 0.95
_SIMILARITIES[_similarity_key("オ", "ォ")] = 0.95
_SIMILARITIES[_similarity_key("カ", "ガ")] = 0.8
_SIMILARITIES[_similarity_key("キ", "ギ")] = 0.8
_SIMILARITIES[_similarity_key("ク", "グ")] = 0.8
_SIMILARITIES[_similarity_key("ケ", "ゲ")] = 0.8
_SIMILARITIES[_similarity_key("コ", "ゴ")] = 0.8
_SIMILARITIES[_similarity_key("サ", "ザ")] = 0.8
_SIMILARITIES[_similarity_key("シ", "ジ")] = 0.8
_SIMILARITIES[_similarity_key("ス", "ズ")] = 0.8
_SIMILARITIES[_similarity_key("セ", "ゼ")] = 0.8
_SIMILARITIES[_similarity_key("ソ", "ゾ")] = 0.8
_SIMILARITIES[_similarity_key("タ", "ダ")] = 0.8
_SIMILARITIES[_similarity_key("チ", "ヂ")] = 0.8
_SIMILARITIES[_similarity_key("ッ", "ツ")] = 0.95
_SIMILARITIES[_similarity_key("ッ", "ヅ")] = 0.8
_SIMILARITIES[_similarity_key("ツ", "ヅ")] = 0.8
_SIMILARITIES[_similarity_key("テ", "デ")] = 0.8
_SIMILARITIES[_similarity_key("ト", "ド")] = 0.8
_SIMILARITIES[_similarity_key("ハ", "バ")] = 0.8
_SIMILARITIES[_similarity_key("ハ", "パ")] = 0.8
_SIMILARITIES[_similarity_key("バ", "パ")] = 0.8
_SIMILARITIES[_similarity_key("ヒ", "ビ")] = 0.8
_SIMILARITIES[_similarity_key("ヒ", "ピ")] = 0.8
_SIMILARITIES[_similarity_key("ビ", "ピ")] = 0.8
_SIMILARITIES[_similarity_key("フ", "ブ")] = 0.8
_SIMILARITIES[_similarity_key("フ", "プ")] = 0.8
_SIMILARITIES[_similarity_key("プ", "ブ")] = 0.8
_SIMILARITIES[_similarity_key("ヘ", "ベ")] = 0.8
_SIMILARITIES[_similarity_key("ヘ", "ペ")] = 0.8
_SIMILARITIES[_similarity_key("ペ", "ベ")] = 0.8
_SIMILARITIES[_similarity_key("ホ", "ボ")] = 0.8
_SIMILARITIES[_similarity_key("ホ", "ポ")] = 0.8
_SIMILARITIES[_similarity_key("ポ", "ボ")] = 0.8
_SIMILARITIES[_similarity_key("ャ", "ヤ")] = 0.95
_SIMILARITIES[_similarity_key("ュ", "ユ")] = 0.95
_SIMILARITIES[_similarity_key("ョ", "ヨ")] = 0.95
_SIMILARITIES[_similarity_key("ヮ", "ワ")] = 0.95
_SIMILARITIES[_similarity_key("ヮ", "ヷ")] = 0.8
_SIMILARITIES[_similarity_key("ワ", "ヷ")] = 0.8
_SIMILARITIES[_similarity_key("→", "ー")] = 0.8
for a, b in itertools.product(range(0, 10), range(0, 10)):
    if a == b:
        continue
    _SIMILARITIES[_similarity_key(str(a), str(b))] = 0.5


def _compare_char(a: Text, b: Text) -> float:
    if a == b:
        return 1
    return _SIMILARITIES.get(_similarity_key(a, b), 0)


def _compare_same_length(a: Text, b: Text) -> float:
    assert len(a) == len(b), (len(a), len(b))
    return sum(_compare_char(i, j) for i, j in zip(a, b)) / len(a)


def fill(
    v: Text,
    size: int,
    *,
    start: int = 0,
    char: Text = " ",
) -> Iterator[Text]:
    """Fill text by given character to reach expected size.

    Args:
        v (Text): text
        size (int): expected size
        start (int, optional): fill start index. Defaults to 0.
        char (Text, optional): character to fill. Defaults to " ".

    Yields:
        Iterator[Text]: All possible fill solutions.
    """
    assert len(char) == 1, char
    if size < len(v):
        return
    if size == len(v):
        yield v
        return
    assert size > len(v)
    for i in range(start, len(v) + 1):
        # skip duplicated result
        if i > 0 and v[i - 1] == char:
            continue
        yield from fill(
            v[:i] + char + v[i:],
            size,
            start=i,
            char=char,
        )


def compare(a: Text, b: Text, *, max_missing_chars: int = 5) -> float:
    size = max(len(a), len(b))
    if size == 0:
        return 1
    if abs(len(a) - len(b)) > max_missing_chars:
        return -1
    return max(
        _compare_same_length(i, j)
        for i, j in itertools.product(
            fill(a, size),
            fill(b, size),
        )
    )


def choose(v: Text, options: Iterable[Text], threshold: float = 0.5) -> Text:
    option_with_similarites = sorted(
        ((i, compare(v, i)) for i in options),
        key=lambda x: x[1],
        reverse=True,
    )
    if not option_with_similarites:
        _LOGGER.warning("choose: empty options")
        return v
    res, similarity = option_with_similarites[0]
    _LOGGER.debug(
        "choose: text='%s' match='%s' similarity=%.3f threshold=%.3f",
        v,
        res,
        similarity,
        threshold,
    )
    if similarity < threshold:
        return v
    return res
