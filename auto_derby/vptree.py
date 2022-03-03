# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import random
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
        self.left_inner_radius = 0
        self.left_outer_radius = 0
        self.right_inner_radius = 0
        self.right_outer_radius = 0

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
        self.vp = random.choice(points)
        vp = self.vp
        if len(points) == 1:
            return
        assert self.distance(vp, vp) == 0
        pd = sorted(((p, self.distance(vp, p)) for p in points), key=lambda x: x[1])[1:]
        i_median = len(pd) // 2
        _, self.left_inner_radius = pd[0]
        _, self.left_outer_radius = pd[max(0, i_median - 1)]
        _, self.right_inner_radius = pd[i_median]
        _, self.right_outer_radius = pd[-1]
        self.left = self._leaf_for(tuple(p for p, _ in pd[:i_median]))
        self.right = self._leaf_for(tuple(p for p, _ in pd[i_median:]))

    def has_leaf(self) -> bool:
        return not (self.left is None and self.right is None)

    def k_nearest_neighbor(self, point: T, k: int) -> Sequence[Tuple[T, float]]:
        # algorithm from: https://github.com/RickardSjogren/vptree/blob/0621f2b76c34f0cd4869b45158b583ca1364cd5a/vptree.py#L91-L140
        Item = Tuple[T, float]
        buf: List[Item] = []

        def _add(item: Item):
            buf.append(item)
            buf.sort(key=lambda x: x[1])
            while len(buf) > k:
                buf.pop()

        # job include node and best case distance of this node.
        jobs: List[Tuple[Optional[VPTree[T]], float]] = [(self, 0)]
        # limit search radius
        r = float("inf")

        while jobs:
            node, d_best = jobs.pop(0)
            if node is None or node.vp is None:
                continue
            if r < d_best:
                continue

            d = self.distance(point, node.vp)
            _add((node.vp, d))
            if d < r and len(buf) == k:
                r = d

            if not node.has_leaf():
                continue

            if node.left_inner_radius <= d <= node.left_outer_radius:
                jobs.insert(0, (node.left, 0))
            elif node.left_inner_radius - r <= d <= node.left_outer_radius + r:
                jobs.append(
                    (
                        node.left,
                        node.left_inner_radius - d
                        if d < node.left_inner_radius
                        else d - node.left_outer_radius,
                    )
                )

            if node.right_inner_radius <= d <= node.right_outer_radius:
                jobs.insert(0, (node.right, 0))
            elif node.right_inner_radius - r <= d <= node.right_outer_radius + r:
                jobs.append(
                    (
                        node.right,
                        node.right_inner_radius - d
                        if d < node.right_inner_radius
                        else d - node.right_outer_radius,
                    )
                )

        return buf

    def nearest_neighbor(self, point: T) -> Tuple[T, float]:
        if self.vp is None:
            raise ValueError("tree is empty")
        return self.k_nearest_neighbor(point, 1)[0]
