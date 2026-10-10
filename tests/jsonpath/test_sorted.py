import pytest

from jsonpath_ng import DatumInContext
from jsonpath_ng.ext import parse


@pytest.mark.parametrize(
    ("value", "expected"),
    [([3, 1, 2], [1, 2, 3]), ({"b": 1, "a": 2}, ["a", "b"]), (4, 4)],
)
@pytest.mark.parametrize("wrapped", [False, True])
def test_sorted_accepts_raw_and_wrapped_values(value, expected, wrapped):
    datum = DatumInContext.wrap(value) if wrapped else value
    matches = parse("`sorted`").find(datum)
    assert isinstance(matches, list)
    assert [match.value for match in matches] == [expected]


@pytest.mark.parametrize("value", [None, False, 4, "value"])
def test_sorted_scalar_in_child_expression(value):
    matches = parse("objects.`sorted`").find({"objects": value})
    assert [match.value for match in matches] == [value]
    assert str(matches[0].full_path) == "objects"


def test_field_sort_leaves_dictionary_unchanged():
    value = {"name": "item"}
    matches = parse("$[/name]").find(value)
    assert isinstance(matches, list)
    assert matches[0].value is value
