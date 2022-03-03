# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import bisect
import random
from typing import Callable, Generic, List, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


class VPTree(Generic[T]):
    def __init__(
        self, distance: Callable[[T, T], float], points: Sequence[T] = ()
    ) -> None:
        self._vp: Optional[T] = None
        self._left: Optional[VPTree[T]] = None
        self._right: Optional[VPTree[T]] = None

        # single `r` means `radius`
        self._r_left_inner = 0
        self._r_left_outer = 0
        self._r_right_inner = 0
        self._r_right_outer = 0

        self.distance = distance

        self.set_data(points)

    def _leaf_for(self, points: Sequence[T]) -> Optional[VPTree[T]]:
        if not points:
            return None
        return VPTree[T](self.distance, points)

    def set_data(self, points: Sequence[T]):
        self._vp = None
        self._left = None
        self._right = None
        if len(points) == 0:
            return
        self._vp = random.choice(points)
        vp = self._vp
        assert self.distance(vp, vp) == 0
        if len(points) == 1:
            return
        pd = sorted(((self.distance(vp, p), p) for p in points))[1:]
        i_median = len(pd) // 2
        self._r_left_inner, _ = pd[0]
        self._r_left_outer, _ = pd[max(0, i_median - 1)]
        self._r_right_inner, _ = pd[i_median]
        self._r_right_outer, _ = pd[-1]
        self._left = self._leaf_for(tuple(p for _, p in pd[:i_median]))
        self._right = self._leaf_for(tuple(p for _, p in pd[i_median:]))

    def is_empty(self) -> bool:
        return self._vp is None

    def has_leaf(self) -> bool:
        return self._left is not None or self._right is not None

    def k_nearest_neighbor(self, point: T, k: int) -> Sequence[Tuple[float, T]]:
        # algorithm from: https://github.com/RickardSjogren/vptree/blob/0621f2b76c34f0cd4869b45158b583ca1364cd5a/vptree.py#L91-L140
        Item = Tuple[float, T]
        buf: List[Item] = []

        def _add(item: Item):
            index = bisect.bisect(buf, item)
            buf.insert(index, item)
            while len(buf) > k:
                buf.pop()

        # job include node and best case distance of this node.
        jobs: List[Tuple[Optional[VPTree[T]], float]] = [(self, 0)]
        # limit search radius
        r = float("inf")

        while jobs:
            node, d_best = jobs.pop(0)
            if node is None or node._vp is None:
                continue
            if r < d_best:
                continue

            d = self.distance(point, node._vp)
            _add((d, node._vp))
            if len(buf) == k:
                r = buf[-1][0]

            if not node.has_leaf():
                continue

            if node._r_left_inner <= d <= node._r_left_outer:
                jobs.insert(0, (node._left, 0))
            elif node._r_left_inner - r <= d <= node._r_left_outer + r:
                jobs.append(
                    (
                        node._left,
                        node._r_left_inner - d
                        if d < node._r_left_inner
                        else d - node._r_left_outer,
                    )
                )

            if node._r_right_inner <= d <= node._r_right_outer:
                jobs.insert(0, (node._right, 0))
            elif node._r_right_inner - r <= d <= node._r_right_outer + r:
                jobs.append(
                    (
                        node._right,
                        node._r_right_inner - d
                        if d < node._r_right_inner
                        else d - node._r_right_outer,
                    )
                )

        return buf

    def nearest_neighbor(self, point: T) -> Tuple[float, T]:
        if self.is_empty():
            raise ValueError("tree is empty")
        return self.k_nearest_neighbor(point, 1)[0]
