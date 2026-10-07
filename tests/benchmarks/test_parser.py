import jsonpath_ng.parser

import pytest


benchmark_group = pytest.mark.benchmark(group="parser")


@benchmark_group
def test_instantiation(benchmark):
    benchmark(jsonpath_ng.parser.JsonPathParser)


@benchmark_group
def test_parse(benchmark):
    instance = jsonpath_ng.parser.JsonPathParser()
    string = "$.a['x'][0] wherenot y | *[1:10:3]"
    benchmark(lambda: instance.parse(string))
