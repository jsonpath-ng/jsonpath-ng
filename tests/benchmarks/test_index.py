import pytest

import jsonpath_ng.parser

benchmark_group = pytest.mark.benchmark(group="index")

# Some list operations can be expensive (like removing from the front of a list),
# so lists must be long enough for performance issues in `Index.filter()` to surface.
SIZE = 20_000


def index_query(count):
    """Build a query that selects the first *count* array elements by index.

    For example:

        index_query(3) == "$[0,1,2]"

    """

    return "$[" + ",".join(str(i) for i in range(count)) + "]"


def filter_each_round(benchmark, query, predicate):
    """Benchmark `.filter()`, giving each round a fresh list to remove from.

    `.filter()` mutates its data, so the data can't be reused between rounds.
    Building it in `setup` keeps that work out of the measurement.
    """

    path = jsonpath_ng.parser.JsonPathParser().parse(query)
    return benchmark.pedantic(
        lambda data: path.filter(predicate, data),
        setup=lambda: ((list(range(SIZE)),), {}),
    )


@benchmark_group
def test_index_filter_remove_one(benchmark):
    """Benchmark removing a single element from the front of a list by index."""

    result = filter_each_round(benchmark, index_query(1), lambda value: True)

    assert result == list(range(1, SIZE))


@benchmark_group
def test_index_filter_remove_few(benchmark):
    """Benchmark removing a few elements from the front of a list by index."""

    result = filter_each_round(benchmark, index_query(5), lambda value: True)

    assert result == list(range(5, SIZE))


@benchmark_group
def test_index_filter_remove_first_half(benchmark):
    """Benchmark filtering out the first half of a list by index."""

    result = filter_each_round(benchmark, index_query(SIZE // 2), lambda value: True)

    assert result == list(range(SIZE // 2, SIZE))


@benchmark_group
def test_index_filter_remove_all(benchmark):
    """Benchmark filtering out all elements in a list by index."""

    result = filter_each_round(benchmark, index_query(SIZE), lambda value: True)

    assert result == []


@benchmark_group
def test_index_filter_remove_none(benchmark):
    """Benchmark removing no elements from a list (though all must be evaluated)."""

    result = filter_each_round(benchmark, index_query(SIZE // 2), lambda value: False)

    assert result == list(range(SIZE))
