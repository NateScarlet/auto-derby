# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable, Generic, Optional, Sequence, Tuple, TypeVar


T = TypeVar("T")


class VPTree(Generic[T]):
    def __init__(
        self, distance: Callable[[T, T], float], points: Sequence[T] = ()
    ) -> None:
        self.vp: Optional[T] = None
        self.closer: Optional[VPTree[T]] = None
        self.further: Optional[VPTree[T]] = None
        self.distance = distance
        self.mean_distance = 0
        self.min_distance = 0
        self.max_distance = 0

        self.set_data(points)

    def _leaf_for(self, points: Sequence[T]) -> Optional[VPTree[T]]:
        if not points:
            return None
        v = VPTree[T](self.distance, points)
        return v

    def set_data(self, points: Sequence[T]):
        self.vp = None
        self.closer = None
        self.further = None
        if len(points) == 0:
            return
        self.vp = points[0]
        vp = self.vp
        if len(points) == 1:
            return
        assert self.distance(vp, vp) == 0
        pd = sorted(((p, self.distance(vp, p)) for p in points[1:]), key=lambda x: x[1])
        _, self.min_distance = pd[0]
        _, self.mean_distance = pd[len(pd) // 2]
        _, self.max_distance = pd[-1]
        self.closer = self._leaf_for(tuple(p for p, d in pd if d <= self.mean_distance))
        self.further = self._leaf_for(tuple(p for p, d in pd if d > self.mean_distance))

    def has_leaf(self) -> bool:
        return not (self.closer is None and self.further is None)

    def nearest(self, point: T) -> Tuple[T, float]:
        if self.vp is None:
            raise ValueError("tree is empty")
        p, d = self.vp, self.distance(self.vp, point)
        d0 = d
        r = d

        def _find_in_leaf(leaf: Optional[VPTree[T]]) -> Tuple[T, float, float]:
            if leaf is None:
                return p, d, r
            p2, d2 = leaf.nearest(point)
            if d2 < r:
                return p2, d2, d2
            return p, d, r

        if d0 <= self.mean_distance + r:
            p, d, r = _find_in_leaf(self.closer)

        if d0 >= self.mean_distance - r:
            p, d, r = _find_in_leaf(self.further)
        return p, d
