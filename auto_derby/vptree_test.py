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
    elapsed = 0
    for i in range(0, size * step):
        test_count += 1
        brute_forced = sorted(((abs(j - i), j) for j in data))
        expected = []
        for d, p in brute_forced:
            if d != brute_forced[0][0]:
                break
            expected.append((d, p))

        start_time = time.perf_counter()
        assert tree.nearest_neighbor(i) in expected
        elapsed += time.perf_counter() - start_time
    brute_force_call_count = test_count * size
    assert _local.call_count < brute_force_call_count * 0.08
    print(
        f"\n\n"
        f"test_nearest_neighbor: finished {test_count} query in {elapsed:.5f}s\n"
        f"    `distance` called {_local.call_count} times "
        f"({_local.call_count / brute_force_call_count * 100:.5f}% of brute force method)\n"
    )
