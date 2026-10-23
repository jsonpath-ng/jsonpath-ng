from jsonpath_ng.ext import parse as parse_extended
from jsonpath_ng.parser import parse as parse_core


def test_core_parser_applies_mixed_index_and_name_selectors_in_order():
    data = {
        "array": [10, 20, 30],
        "object": {"a": 0, "b": 1},
    }

    assert [match.value for match in parse_core("$.*[1, 'a']").find(data)] == [20, 0]


def test_extended_parser_applies_mixed_index_name_and_filter_selectors_in_order():
    data = {
        "array": [10, 20, 30, 40, 50],
        "object": {"a": 0, "b": 1, "c": 2, "d": 3},
    }

    assert [
        match.value for match in parse_extended("$.*[1, 'a', ?(@ > 45)]").find(data)
    ] == [20, 50, 0]
