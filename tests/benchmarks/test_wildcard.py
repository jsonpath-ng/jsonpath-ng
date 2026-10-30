import pytest

import jsonpath_ng.parser

benchmark_group = pytest.mark.benchmark(group="wildcard")

SIZE = 1000


@benchmark_group
@pytest.mark.parametrize("query", ("$[*]", "$.*"))
def test_wildcard_find_object_members(benchmark, query):
    path = jsonpath_ng.parser.JsonPathParser().parse(query)
    data = {str(i): i for i in range(SIZE)}

    result = benchmark(path.find, data)

    assert len(result) == SIZE


@benchmark_group
@pytest.mark.parametrize("query", ("$[*]", "$.*"))
def test_wildcard_find_array_elements(benchmark, query):
    path = jsonpath_ng.parser.JsonPathParser().parse(query)
    data = list(range(SIZE))

    result = benchmark(path.find, data)

    assert len(result) == SIZE
