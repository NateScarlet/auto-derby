# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable, Generic, List, Optional, Sequence, Tuple, TypeVar


T = TypeVar("T")


class VPTree(Generic[T]):
    def __init__(
        self, distance: Callable[[T, T], float], points: Sequence[T] = ()
    ) -> None:
        self.vp: Optional[T] = None
        self.left: Optional[VPTree[T]] = None
        self.right: Optional[VPTree[T]] = None
        self.distance = distance
        self.left_min = 0
        self.left_max = 0
        self.right_min = 0
        self.right_max = 0

        self.set_data(points)

    def _leaf_for(self, points: Sequence[T]) -> Optional[VPTree[T]]:
        if not points:
            return None
        v = VPTree[T](self.distance, points)
        return v

    def set_data(self, points: Sequence[T]):
        self.vp = None
        self.left = None
        self.right = None
        if len(points) == 0:
            return
        self.vp = points[0]
        vp = self.vp
        if len(points) == 1:
            return
        assert self.distance(vp, vp) == 0
        pd = sorted(((p, self.distance(vp, p)) for p in points[1:]), key=lambda x: x[1])
        _, self.left_min = pd[0]
        _, self.left_max = pd[len(pd) // 2]
        _, self.right_min = pd[min((len(pd) // 2) + 1, len(pd) - 1)]
        _, self.right_max = pd[-1]
        self.left = self._leaf_for(tuple(p for p, d in pd if d <= self.left_max))
        self.right = self._leaf_for(tuple(p for p, d in pd if d > self.left_max))

    def has_leaf(self) -> bool:
        return not (self.left is None and self.right is None)

    def nearest_n(self, point: T, n: int) -> Sequence[Tuple[T, float]]:
        # algorithm from: https://github.com/RickardSjogren/vptree/blob/0621f2b76c34f0cd4869b45158b583ca1364cd5a/vptree.py#L91-L140
        buf: List[Tuple[T, float]] = []

        def _add_value(v: Tuple[T, float]):
            buf.append(v)
            buf.sort(key=lambda x: x[1])
            while len(buf) > n:
                buf.pop()

        jobs: List[Tuple[Optional[VPTree[T]], float]] = [(self, 0)]
        r = float("inf")

        while len(jobs) > 0:
            node, r_gte = jobs.pop(0)
            if not (node and node.vp is not None and r >= r_gte):
                continue

            d = self.distance(point, node.vp)
            if d < r:
                r = d
                _add_value((node.vp, d))

            if not node.has_leaf():
                continue

            if node.left_min <= d <= node.left_max:
                jobs.insert(0, (node.left, 0))
            elif node.left_min - r <= d <= node.left_max + r:
                jobs.append(
                    (
                        node.left,
                        node.left_min - d if d < node.left_min else d - node.left_max,
                    )
                )

            if node.right_min <= d <= node.right_max:
                jobs.insert(0, (node.right, 0))
            elif node.right_min - r <= d <= node.right_max + r:
                jobs.append(
                    (
                        node.right,
                        node.right_min - d
                        if d < node.right_min
                        else d - node.right_max,
                    )
                )

        return buf

    def nearest(self, point: T) -> Tuple[T, float]:
        if self.vp is None:
            raise ValueError("tree is empty")
        return self.nearest_n(point, 1)[0]
