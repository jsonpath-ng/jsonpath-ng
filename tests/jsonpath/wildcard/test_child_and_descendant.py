"""
The ``*`` wildcard must follow RFC 9535, sections 2.3.2.2, 2.5.1.1, and 2.5.2.1.

``.*`` is shorthand for ``[*]``, and ``..*`` is shorthand for ``..[*]``.
A wildcard selects the children of an object or array and nothing from a scalar.
"""

import pytest

import jsonpath_ng
import jsonpath_ng.ext

parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)


def paths_and_values(parse, expression, data):
    return [
        (str(match.full_path), match.value) for match in parse(expression).find(data)
    ]


@parsers
def test_child_wildcard_selects_array_elements(parse):
    found = paths_and_values(parse, "$.*", [1, 2, 3])

    assert found == [("[0]", 1), ("[1]", 2), ("[2]", 3)]


@parsers
def test_child_wildcard_selects_nested_array_elements(parse):
    found = paths_and_values(parse, "$.a.*", {"a": ["x", "y"]})

    assert found == [("a.[0]", "x"), ("a.[1]", "y")]


@parsers
def test_child_wildcard_still_selects_object_members(parse):
    found = paths_and_values(parse, "$.*", {"a": 1, "b": [2]})

    assert found == [("a", 1), ("b", [2])]


@pytest.mark.parametrize("data", (5, 1.5, True, None, "text"))
@parsers
def test_child_wildcard_selects_nothing_from_scalars(parse, data):
    assert parse("$.*").find(data) == []


@parsers
def test_descendant_wildcard_selects_array_elements(parse):
    """The reporter's example in #11."""
    found = paths_and_values(parse, "$..*", [1, 2, 3])

    assert found == [("[0]", 1), ("[1]", 2), ("[2]", 3)]


@parsers
def test_descendant_wildcard_selects_nested_array_elements(parse):
    found = paths_and_values(parse, "$..*", [[1, 2], [3]])

    assert found == [
        ("[0]", [1, 2]),
        ("[1]", [3]),
        ("[0].[0]", 1),
        ("[0].[1]", 2),
        ("[1].[0]", 3),
    ]


@parsers
def test_descendant_wildcard_selects_all_nodes_below_an_object(parse):
    """The example in #164."""
    data = {"list": [{"prop1": "val1"}, {"prop2": "val2"}]}

    found = paths_and_values(parse, "$..*", data)

    assert sorted(path for path, _ in found) == [
        "list",
        "list.[0]",
        "list.[0].prop1",
        "list.[1]",
        "list.[1].prop2",
    ]


@parsers
def test_descendant_wildcard_rfc_table_16(parse):
    """RFC 9535 section 2.5.2.3, Table 16: the nodes selected by ``$..*``.

    The RFC guarantees only a partial ordering of the results,
    which is asserted separately below.
    """
    data = {"o": {"j": 1, "k": 2}, "a": [5, 3, [{"j": 4}, {"k": 6}]]}

    found = paths_and_values(parse, "$..*", data)

    assert sorted(found, key=lambda item: item[0]) == [
        ("a", [5, 3, [{"j": 4}, {"k": 6}]]),
        ("a.[0]", 5),
        ("a.[1]", 3),
        ("a.[2]", [{"j": 4}, {"k": 6}]),
        ("a.[2].[0]", {"j": 4}),
        ("a.[2].[0].j", 4),
        ("a.[2].[1]", {"k": 6}),
        ("a.[2].[1].k", 6),
        ("o", {"j": 1, "k": 2}),
        ("o.j", 1),
        ("o.k", 2),
    ]
    assert found == paths_and_values(parse, "$..[*]", data), "RFC 2.5.2.1 shorthand"


@parsers
def test_descendant_wildcard_rfc_table_16_ordering(parse):
    """The ordering constraints in the note below Table 16 (RFC 9535 2.5.2.3)."""
    data = {"o": {"j": 1, "k": 2}, "a": [5, 3, [{"j": 4}, {"k": 6}]]}

    order = [path for path, _ in paths_and_values(parse, "$..*", data)]

    # Each tuple must appear in this order, though not necessarily adjacently.
    for chain in (
        ("o", "o.j"),
        ("o", "o.k"),
        ("a", "a.[0]", "a.[1]", "a.[2]"),
        ("a.[1]", "a.[2].[0]", "a.[2].[0].j"),
        ("a.[1]", "a.[2].[1]", "a.[2].[1].k"),
        ("a.[2]", "a.[2].[0]", "a.[2].[1]", "a.[2].[0].j", "a.[2].[1].k"),
    ):
        positions = [order.index(path) for path in chain]
        assert positions == sorted(positions), chain


@parsers
def test_wildcard_full_paths_round_trip(parse):
    """The full path of a match identifies exactly that node (RFC 9535 section 2.7)."""
    data = {"a": [{"b": 1}, [2]]}

    for match in parse("$..*").find(data):
        found = parse(str(match.full_path)).find(data)
        assert [m.value for m in found] == [match.value], str(match.full_path)


@parsers
def test_update_wildcard_sets_array_elements(parse):
    assert parse("$.*").update([1, 2, 3], 0) == [0, 0, 0]
    assert parse("$..*").update([1, 2, 3], 0) == [0, 0, 0]


@parsers
def test_filter_wildcard_removes_array_elements(parse):
    assert parse("$.*").filter(lambda value: value > 1, [1, 2, 3]) == [1]


@parsers
def test_update_and_filter_leave_tuples_unchanged(parse):
    """Tuples are immutable, so update and filter must not try to change them."""
    assert parse("$.*").update((1, 2), 0) == (1, 2)
    assert parse("$.*").filter(lambda value: value > 1, (1, 2)) == (1, 2)


@parsers
def test_find_selects_tuple_elements(parse):
    assert [match.value for match in parse("$.*").find((1, 2))] == [1, 2]
