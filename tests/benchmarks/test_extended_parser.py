import jsonpath_ng.ext.parser

import pytest


benchmark_group = pytest.mark.benchmark(group="extended_parser")


@benchmark_group
def test_extended_parser_instantiation(benchmark):
    benchmark(jsonpath_ng.ext.parser.ExtendedJsonPathParser)


@benchmark_group
def test_extended_parser_parse(benchmark):
    instance = jsonpath_ng.ext.parser.ExtendedJsonPathParser()
    string = "$.a['x'][0] wherenot y | *[1:10:3]"
    benchmark(lambda: instance.parse(string))
