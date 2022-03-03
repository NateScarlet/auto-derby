from .vptree import VPTree
import time


def test_nearest_neighbor():
    class _local:
        call_count = 0

    def _distance(a: int, b: int) -> float:
        _local.call_count += 1
        return abs(a - b)

    tree = VPTree[int](_distance)
    size = 100
    step = 100
    data = range(0, size * step, step)
    tree.set_data(data)
    _local.call_count = 0
    test_count = 0
    start_time = time.perf_counter()
    for i in range(0, size * step):
        test_count += 1
        brute_forced = sorted(((j, abs(j - i)) for j in data), key=lambda x: x[1])
        expected = []
        for p, d in brute_forced:
            if d != brute_forced[0][1]:
                break
            expected.append((d, p))

        assert tree.nearest_neighbor(i) in expected
    elapsed = time.perf_counter() - start_time
    assert _local.call_count < test_count * size * 0.08
    print(
        f"\n\n"
        f"test_nearest_neighbor: finished {size * step} query in {elapsed:.5f}s\n"
        f"    `distance` called {_local.call_count} times "
        f"({_local.call_count / (size * test_count) * 100:.5f}% of brute force method)\n"
    )
