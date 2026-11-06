import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.sorting import ALGORITHMS  # noqa: E402

CASES = [
    [],
    [1.0],
    [3.0, 1.0, 2.0],
    [5.0, 5.0, 5.0, 1.0],          # duplicates
    list(range(50)),               # ascending
    list(range(50, 0, -1)),        # already descending
    [random.uniform(-100, 100) for _ in range(500)],
]


@pytest.mark.parametrize("name", ALGORITHMS)
@pytest.mark.parametrize("values", CASES)
def test_matches_python_sorted(name, values):
    original = list(values)
    assert ALGORITHMS[name](values) == sorted(original, reverse=True)
    assert values == original  # input not modified
