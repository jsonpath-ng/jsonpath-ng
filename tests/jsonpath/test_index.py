import pytest

import jsonpath_ng
import jsonpath_ng.ext
from jsonpath_ng.jsonpath import Index


parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)


@pytest.mark.parametrize(
    "indices, expected",
    (
        ((0,), "[0]"),
        ((-1,), "[-1]"),
        ((0, 1), "[0,1]"),
        ((0, 1, 2), "[0,1,2]"),
        ((0, -1), "[0,-1]"),
    ),
)
def test_str(indices, expected):
    assert str(Index(*indices)) == expected


@pytest.mark.parametrize(
    "expression",
    (
        "[0]",
        "[0,1]",
        "[0,1,2]",
    ),
)
@parsers
def test_str_roundtrip(parse, expression):
    parsed = parse(expression)
    reserialized = str(parsed)

    assert reserialized == expression
    assert parsed == parse(reserialized)
