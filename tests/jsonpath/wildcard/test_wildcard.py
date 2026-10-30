"""
The ``Wildcard`` node selects every child of an object or array.

RFC 9535, section 2.3.2: a wildcard selects every member of an object
and every element of an array, and selects nothing from a scalar.
"""

import pytest

import jsonpath_ng
import jsonpath_ng.ext
from jsonpath_ng.jsonpath import Fields
from jsonpath_ng.jsonpath import Slice
from jsonpath_ng.jsonpath import Wildcard

parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)


@parsers
def test_wildcard_selects_object_members(parse):
    found = [
        (str(match.full_path), match.value)
        for match in parse("$.*").find({"a": 1, "b": [2]})
    ]

    assert found == [("a", 1), ("b", [2])]


@parsers
def test_wildcard_selects_array_elements(parse):
    found = [
        (str(match.full_path), match.value) for match in parse("$[*]").find([1, 2, 3])
    ]

    assert found == [("[0]", 1), ("[1]", 2), ("[2]", 3)]


@parsers
@pytest.mark.parametrize("data", (5, 1.5, True, None, "text"))
def test_wildcard_selects_nothing_from_scalars(parse, data):
    assert parse("$.*").find(data) == []
    assert parse("$[*]").find(data) == []


def test_wildcard_node_selects_children_directly():
    assert [match.value for match in Wildcard().find({"a": 1, "b": 2})] == [1, 2]
    assert [match.value for match in Wildcard().find([3, 4])] == [3, 4]
    assert Wildcard().find(7) == []


def test_wildcard_finds_the_member_named_star_by_name_only_once():
    assert [m.value for m in Wildcard().find({"*": 1, "b": 2})] == [1, 2]


@parsers
def test_descendant_wildcard_selects_every_descendant(parse):
    data = {"a": [1, {"b": 2}]}

    assert [match.value for match in parse("$..*").find(data)] == [
        [1, {"b": 2}],
        1,
        {"b": 2},
        2,
    ]


def test_update_with_wildcard_replaces_every_member():
    data = {"a": 1, "b": 2}

    assert Wildcard().update(data, 0) == {"a": 0, "b": 0}


def test_update_with_wildcard_replaces_every_element():
    assert Wildcard().update([1, 2, 3], 0) == [0, 0, 0]


def test_update_with_wildcard_calls_a_callable_with_value_data_and_key():
    data = {"a": 1}

    Wildcard().update(data, lambda value, container, key: f"{key}{value}")

    assert data == {"a": "a1"}


@pytest.mark.parametrize("data", (5, None, "text", True))
def test_update_with_wildcard_ignores_scalars(data):
    assert Wildcard().update(data, 0) == data


def test_update_or_create_with_wildcard_replaces_every_member():
    data = {"a": 1, "b": 2}

    assert Wildcard().update_or_create(data, 0) == {"a": 0, "b": 0}


def test_find_or_create_with_wildcard_creates_nothing():
    data = {"a": 1}

    assert [m.value for m in Wildcard().find_or_create(data)] == [1]
    assert data == {"a": 1}


def test_filter_with_wildcard_removes_matching_members():
    data = {"a": 1, "b": 2, "c": 3}

    assert Wildcard().filter(lambda value: value > 1, data) == {"a": 1}


def test_filter_with_wildcard_removes_matching_elements():
    assert Wildcard().filter(lambda value: value != 2, [1, 2, 3]) == [2]


def test_filter_with_wildcard_ignores_scalars():
    assert Wildcard().filter(lambda value: True, 5) == 5


def test_wildcard_text_form_and_equality():
    assert str(Wildcard()) == "*"
    assert repr(Wildcard()) == "Wildcard()"
    assert Wildcard() == Wildcard()
    assert hash(Wildcard()) == hash(Wildcard())
    assert Wildcard() != Slice()
    assert Wildcard() != Fields("a")
