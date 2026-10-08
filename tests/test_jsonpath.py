import copy
from collections import UserDict
from collections.abc import Callable

import pytest

from jsonpath_ng import JSONPath
from jsonpath_ng.ext.parser import parse as ext_parse
from jsonpath_ng.jsonpath import DatumInContext
from jsonpath_ng.jsonpath import Fields
from jsonpath_ng.jsonpath import Index
from jsonpath_ng.jsonpath import Root
from jsonpath_ng.jsonpath import This
from jsonpath_ng.lexer import JsonPathLexerError
from jsonpath_ng.parser import parse as base_parse

from .helpers import assert_full_path_equality
from .helpers import assert_value_equality


@pytest.mark.parametrize(
    "path_arg, context_arg, expected_path, expected_full_path",
    (
        (None, None, This(), This()),
        (Root(), None, Root(), Root()),
        (Fields("foo"), "unimportant", Fields("foo"), Fields("foo")),
        (
            Fields("foo"),
            DatumInContext("unimportant", path=Fields("baz"), context="unimportant"),
            Fields("foo"),
            Fields("baz").child(Fields("foo")),
        ),
    ),
)
def test_datumincontext_init(path_arg, context_arg, expected_path, expected_full_path):
    datum = DatumInContext(3, path=path_arg, context=context_arg)
    assert datum.path == expected_path
    assert datum.full_path == expected_full_path


def test_datumincontext_in_context():
    d1 = DatumInContext(3, path=Fields("foo"), context=DatumInContext("bar"))
    d2 = DatumInContext(3).in_context(path=Fields("foo"), context=DatumInContext("bar"))
    assert d1 == d2


def test_datumincontext_in_context_nested():
    sequential_calls = (
        DatumInContext(3)
        .in_context(path=Fields("foo"), context="whatever")
        .in_context(path=Fields("baz"), context="whatever")
    )
    nested_calls = DatumInContext(3).in_context(
        path=Fields("foo"),
        context=DatumInContext("whatever").in_context(
            path=Fields("baz"), context="whatever"
        ),
    )
    assert sequential_calls == nested_calls


parsers = pytest.mark.parametrize(
    "parse",
    (
        pytest.param(base_parse, id="parse=jsonpath_ng.parser.parse"),
        pytest.param(ext_parse, id="parse=jsonpath_ng.ext.parser.parse"),
    ),
)


update_test_cases = (
    #
    # Fields
    # ------
    #
    ("foo", {"foo": 1}, 5, {"foo": 5}),
    ("foo", UserDict({"foo": 1}), 5, UserDict({"foo": 5})),
    ("$.*", {"foo": 1, "bar": 2}, 3, {"foo": 3, "bar": 3}),
    #
    # Indexes
    # -------
    #
    ("[0]", ["foo", "bar", "baz"], "test", ["test", "bar", "baz"]),
    ("[0, 1]", ["foo", "bar", "baz"], "test", ["test", "test", "baz"]),
    ("[0, 1]", ["foo", "bar", "baz"], ["test", "test 1"], ["test", "test 1", "baz"]),
    #
    # Slices
    # ------
    #
    ("[0:2]", ["foo", "bar", "baz"], "test", ["test", "test", "baz"]),
    #
    # Root
    # ----
    #
    ("$", "foo", "bar", "bar"),
    #
    # This
    # ----
    #
    ("`this`", "foo", "bar", "bar"),
    #
    # Children
    # --------
    #
    ("$.foo", {"foo": "bar"}, "baz", {"foo": "baz"}),
    ("[-2].foo", [{"foo": 1}, {"foo": 2}], 3, [{"foo": 3}, {"foo": 2}]),
    ("[-3].foo", [{"foo": 1}, {"foo": 2}], 3, [{"foo": 1}, {"foo": 2}]),
    ("foo.bar", {"foo": {"bar": 1}}, "baz", {"foo": {"bar": "baz"}}),
    #
    # Descendants
    # -----------
    #
    ("$..somefield", {"somefield": 1}, 42, {"somefield": 42}),
    (
        "$..nestedfield",
        {"outer": {"nestedfield": 1}},
        42,
        {"outer": {"nestedfield": 42}},
    ),
    (
        "$..bar",
        {"outs": {"bar": 1, "ins": {"bar": 9}}, "outs2": {"bar": 2}},
        42,
        {"outs": {"bar": 42, "ins": {"bar": 42}}, "outs2": {"bar": 42}},
    ),
    #
    # Where
    # -----
    #
    (
        "*.bar where baz",
        {"foo": {"bar": {"baz": 1}}, "bar": {"baz": 2}},
        5,
        {"foo": {"bar": 5}, "bar": {"baz": 2}},
    ),
    (
        "(* where flag) .. bar",
        {"foo": {"bar": 1, "flag": 1}, "baz": {"bar": 2}},
        3,
        {"foo": {"bar": 3, "flag": 1}, "baz": {"bar": 2}},
    ),
    #
    # WhereNot
    # --------
    #
    (
        "(* wherenot flag) .. bar",
        {"foo": {"bar": 1, "flag": 1}, "baz": {"bar": 2}},
        4,
        {"foo": {"bar": 1, "flag": 1}, "baz": {"bar": 4}},
    ),
    #
    # Lambdas
    # -------
    #
    (
        "foo[*].baz",
        {"foo": [{"baz": 1}, {"baz": 2}]},
        lambda x, y, z: x + 1,
        {"foo": [{"baz": 2}, {"baz": 3}]},
    ),
    #
    # Update with Boolean in data
    # ---------------------------
    #
    (
        "$.*.number",
        {"foo": ["abc", "def"], "bar": {"number": 123456}, "boolean": True},
        "98765",
        {"foo": ["abc", "def"], "bar": {"number": "98765"}, "boolean": True},
    ),
)


@pytest.mark.parametrize(
    "expression, data, update_value, expected_value",
    update_test_cases,
)
@parsers
def test_update(
    parse: Callable[[str], JSONPath],
    expression: str,
    data,
    update_value,
    expected_value,
):
    data_copy = copy.deepcopy(data)
    update_value_copy = copy.deepcopy(update_value)
    result = parse(expression).update(data_copy, update_value_copy)
    assert result == expected_value

    # inplace update testing
    data_copy2 = copy.deepcopy(data)
    update_value_copy2 = copy.deepcopy(update_value)
    datums = parse(expression).find(data_copy2)
    batch_update = isinstance(update_value, list) and len(datums) == len(update_value)
    for i, datum in enumerate(datums):
        if batch_update:
            datum.value = update_value_copy2[i]
        else:
            datum.value = update_value_copy2
        if isinstance(
            datum.full_path, (Root, This)
        ):  # when the type of `data` is str, int, float etc.
            data_copy2 = datum.value
    assert data_copy2 == expected_value


@pytest.mark.parametrize("data", (["c"], "c", ("c",), 42, 1.5, True, False, None))
@pytest.mark.parametrize("use_callback", (False, True))
@parsers
def test_field_update_ignores_non_mappings(parse, data, use_callback):
    original = copy.deepcopy(data)

    def callback(value, parent, field):
        pytest.fail("The callback must not run when no field matches")

    result = parse("c").update(data, callback if use_callback else 2)

    assert result is data
    assert data == original


@parsers
def test_field_update_in_heterogeneous_data(parse):
    data = {"array": ["c"], "string": "c", "number": 1, "object": {"c": 1}}

    result = parse("$.*.c").update(data, 2)

    assert result is data
    assert data == {"array": ["c"], "string": "c", "number": 1, "object": {"c": 2}}


@parsers
def test_field_update_in_duck_typed_mapping(parse):
    class MappingLike:
        def __init__(self) -> None:
            self.data = {"c": 1}

        def get(self, key, default=None):
            return self.data.get(key, default)

        def __contains__(self, key):
            return key in self.data

        def __setitem__(self, key, value):
            self.data[key] = value

    data = MappingLike()
    assert parse("c").find(data)[0].value == 1
    assert parse("c").update(data, 2) is data
    assert data.data == {"c": 2}


@parsers
def test_update_with_inplace_callback(parse: Callable[[str], JSONPath]):
    """Regression test for #163: update() with an in-place callback that
    returns None should not overwrite the field with None."""

    def lowercase_inplace(orig, data, field):
        data[field] = data[field].lower()
        # intentionally returns None

    data = {
        "Data_cat": {
            "data_entry": [
                {"value": 0, "UPPERCASE": "UPPERCASE_A"},
                {"value": 2, "UPPERCASE": "UPPERCASE_B"},
            ]
        }
    }
    parse("$..UPPERCASE").update(data, lowercase_inplace)
    assert data == {
        "Data_cat": {
            "data_entry": [
                {"value": 0, "UPPERCASE": "uppercase_a"},
                {"value": 2, "UPPERCASE": "uppercase_b"},
            ]
        }
    }


@parsers
def test_update_with_returning_callback(parse: Callable[[str], JSONPath]):
    """Ensure callbacks that return a value still work correctly."""

    def lowercase_return(orig, data, field):
        return orig.lower()

    data = {
        "Data_cat": {
            "data_entry": [
                {"value": 0, "UPPERCASE": "UPPERCASE_A"},
                {"value": 2, "UPPERCASE": "UPPERCASE_B"},
            ]
        }
    }
    parse("$..UPPERCASE").update(data, lowercase_return)
    assert data == {
        "Data_cat": {
            "data_entry": [
                {"value": 0, "UPPERCASE": "uppercase_a"},
                {"value": 2, "UPPERCASE": "uppercase_b"},
            ]
        }
    }


filter_test_cases = (
    # Docs examples
    (
        "foo[*].baz",
        {"foo": [{"baz": 1}, {"baz": 2}]},
        lambda d: True,
        {"foo": [{}, {}]},
    ),
    (
        "foo[*].baz",
        {"foo": [{"baz": 1}, {"baz": 2}]},
        lambda d: d == 2,
        {"foo": [{"baz": 1}, {}]},
    ),
    # Child paths only filter values with an in-range parent index.
    ("[-2].foo", [{"foo": 1}, {"foo": 2}], lambda d: True, [{}, {"foo": 2}]),
    ("[-3].foo", [{"foo": 1}, {"foo": 2}], lambda d: True, [{"foo": 1}, {"foo": 2}]),
    # Wildcard issue fix
    (
        "*.baz",
        {"flag": False, "foo": {"bar": 1, "baz": 2}},
        lambda d: True,
        {"flag": False, "foo": {"bar": 1}},
    ),
)


@pytest.mark.parametrize(
    "expression, data, filter_function, expected_value",
    filter_test_cases,
)
@parsers
def test_filter(
    parse: Callable[[str], JSONPath],
    expression: str,
    data,
    filter_function: Callable,
    expected_value,
):
    data_copy = copy.deepcopy(data)
    parse(expression).filter(filter_function, data_copy)
    assert data_copy == expected_value


find_test_cases = (
    #
    # * (star)
    # --------
    #
    ("*", {"foo": 1, "baz": 2}, {1, 2}, {"foo", "baz"}),
    #
    # Fields
    # ------
    #
    ("foo", {"foo": "baz"}, ["baz"], ["foo"]),
    ("foo,baz", {"foo": 1, "baz": 2}, [1, 2], ["foo", "baz"]),
    ("@foo", {"@foo": 1}, [1], ["@foo"]),
    #
    # Roots
    # -----
    #
    ("$", {"foo": "baz"}, [{"foo": "baz"}], ["$"]),
    ("foo.$", {"foo": "baz"}, [{"foo": "baz"}], ["$"]),
    ("foo.$.foo", {"foo": "baz"}, ["baz"], ["foo"]),
    #
    # This
    # ----
    #
    ("`this`", {"foo": "baz"}, [{"foo": "baz"}], ["`this`"]),
    ("foo.`this`", {"foo": "baz"}, ["baz"], ["foo"]),
    ("foo.`this`.baz", {"foo": {"baz": 3}}, [3], ["foo.baz"]),
    #
    # Indexes
    # -------
    #
    ("[0]", [42], [42], ["[0]"]),
    ("[5]", [42], [], []),
    ("[2]", [34, 65, 29, 59], [29], ["[2]"]),
    ("[0]", None, [], []),
    ("[-1]", None, [], []),
    ("[-1]", [], [], []),
    ("[0]", [], [], []),
    ("[-1]", [42], [42], ["[-1]"]),
    ("[-2]", [42], [], []),
    ("[-3]", [34, 65, 29], [34], ["[-3]"]),
    ("[-4]", [34, 65, 29], [], []),
    ("[3]", [34, 65, 29], [], []),
    (
        "[0,-4,-3,3,-1]",
        [34, 65, 29],
        [34, 34, 29],
        ["[0]", "[-3]", "[-1]"],
    ),
    # Indexing a dict matches nothing rather than raising KeyError (issue #93)
    ("[0]", {"foo": 1}, [], []),
    ("$.*[0].b", {"a": [{"b": 1}], "c": {"d": 2}}, [1], ["a.[0].b"]),
    #
    # Slices
    # ------
    #
    ("[*]", [1, 2, 3], [1, 2, 3], ["[0]", "[1]", "[2]"]),
    ("[*]", range(1, 4), [1, 2, 3], ["[0]", "[1]", "[2]"]),
    ("[1:]", [1, 2, 3, 4], [2, 3, 4], ["[1]", "[2]", "[3]"]),
    ("[1:3]", [1, 2, 3, 4], [2, 3], ["[1]", "[2]"]),
    ("[:2]", [1, 2, 3, 4], [1, 2], ["[0]", "[1]"]),
    ("[:3:2]", [1, 2, 3, 4], [1, 3], ["[0]", "[2]"]),
    ("[1::2]", [1, 2, 3, 4], [2, 4], ["[1]", "[3]"]),
    ("[1:6:3]", range(1, 10), [2, 5], ["[1]", "[4]"]),
    ("[::-2]", [1, 2, 3, 4, 5], [5, 3, 1], ["[4]", "[2]", "[0]"]),
    #
    # Slices (funky hacks)
    # --------------------
    #
    ("[*]", 1, [1], ["[0]"]),
    ("[*]", 1.2, [1.2], ["[0]"]),
    ("[*]", True, [True], ["[0]"]),
    ("[*]", False, [False], ["[0]"]),
    ("[*]", "test", ["test"], ["[0]"]),
    ("[*]", None, [], []),
    ("[0:]", 1, [1], ["[0]"]),
    ("[*]", {"foo": 1}, [{"foo": 1}], ["[0]"]),
    ("[*].foo", {"foo": 1}, [1], ["[0].foo"]),
    #
    # Children
    # --------
    #
    ("foo.baz", {"foo": {"baz": 3}}, [3], ["foo.baz"]),
    ("foo.baz", {"foo": {"baz": [3]}}, [[3]], ["foo.baz"]),
    ("foo.baz.qux", {"foo": {"baz": {"qux": 5}}}, [5], ["foo.baz.qux"]),
    #
    # Descendants
    # -----------
    #
    (
        "foo..baz",
        {"foo": {"baz": 1, "bing": {"baz": 2}}},
        [1, 2],
        ["foo.baz", "foo.bing.baz"],
    ),
    (
        "foo..baz",
        {"foo": [{"baz": 1}, {"baz": 2}]},
        [1, 2],
        ["foo.[0].baz", "foo.[1].baz"],
    ),
    #
    # Parents
    # -------
    #
    ("foo.baz.`parent`", {"foo": {"baz": 3}}, [{"baz": 3}], ["foo"]),
    (
        "foo.`parent`.foo.baz.`parent`.baz.qux",
        {"foo": {"baz": {"qux": 5}}},
        [5],
        ["foo.baz.qux"],
    ),
    #
    # Hyphens
    # -------
    #
    ("foo.bar-baz", {"foo": {"bar-baz": 3}}, [3], ["foo.bar-baz"]),
    (
        "foo.[bar-baz,blah-blah]",
        {"foo": {"bar-baz": 3, "blah-blah": 5}},
        [3, 5],
        ["foo.bar-baz", "foo.blah-blah"],
    ),
    #
    # Literals
    # --------
    #
    ("A.'a.c'", {"A": {"a.c": "d"}}, ["d"], ["A.'a.c'"]),
    #
    # Numeric keys
    # --------
    #
    ("1", {"1": "foo"}, ["foo"], ["'1'"]),
)


@pytest.mark.parametrize(
    "path, data, expected_values, expected_full_paths", find_test_cases
)
@parsers
def test_find(parse, path, data, expected_values, expected_full_paths):
    results = parse(path).find(data)

    # Verify result values and full paths match expectations.
    assert_value_equality(results, expected_values)
    assert_full_path_equality(results, expected_full_paths)


find_test_cases_with_auto_id = (
    #
    # * (star)
    # --------
    #
    ("*", {"foo": 1, "baz": 2}, {1, 2, "`this`"}),
    #
    # Fields
    # ------
    #
    ("foo.id", {"foo": "baz"}, ["foo"]),
    ("foo.id", {"foo": {"id": "baz"}}, ["baz"]),
    ("foo,baz.id", {"foo": 1, "baz": 2}, ["foo", "baz"]),
    ("*.id", {"foo": {"id": 1}, "baz": 2}, {"'1'", "baz"}),
    #
    # Roots
    # -----
    #
    ("$.id", {"foo": "baz"}, ["$"]),
    ("foo.$.id", {"foo": "baz", "id": "bizzle"}, ["bizzle"]),
    ("foo.$.baz.id", {"foo": 4, "baz": 3}, ["baz"]),
    #
    # This
    # ----
    #
    ("id", {"foo": "baz"}, ["`this`"]),
    ("foo.`this`.id", {"foo": "baz"}, ["foo"]),
    ("foo.`this`.baz.id", {"foo": {"baz": 3}}, ["foo.baz"]),
    #
    # Indexes
    # -------
    #
    ("[0].id", [42], ["[0]"]),
    ("[2].id", [34, 65, 29, 59], ["[2]"]),
    #
    # Slices
    # ------
    #
    ("[*].id", [1, 2, 3], ["[0]", "[1]", "[2]"]),
    ("[1:].id", [1, 2, 3, 4], ["[1]", "[2]", "[3]"]),
    #
    # Children
    # --------
    #
    ("foo.baz.id", {"foo": {"baz": 3}}, ["foo.baz"]),
    ("foo.baz.id", {"foo": {"baz": [3]}}, ["foo.baz"]),
    ("foo.baz.id", {"foo": {"id": "bizzle", "baz": 3}}, ["bizzle.baz"]),
    ("foo.baz.id", {"foo": {"baz": {"id": "hi"}}}, ["foo.hi"]),
    ("foo.baz.bizzle.id", {"foo": {"baz": {"bizzle": 5}}}, ["foo.baz.bizzle"]),
    #
    # Descendants
    # -----------
    #
    (
        "foo..baz.id",
        {"foo": {"baz": 1, "bing": {"baz": 2}}},
        ["foo.baz", "foo.bing.baz"],
    ),
)


@pytest.mark.parametrize("path, data, expected_values", find_test_cases_with_auto_id)
@parsers
def test_find_values_auto_id(auto_id_field, parse, path, data, expected_values):
    result = parse(path).find(data)
    assert_value_equality(result, expected_values)


@parsers
def test_find_full_paths_auto_id(auto_id_field, parse):
    results = parse("*").find({"foo": 1, "baz": 2})
    assert_full_path_equality(results, {"foo", "baz", "id"})


@pytest.mark.parametrize(
    "string, target",
    (
        ("m.[1].id", ["'1'.m.a2id"]),
        ("m.[1].$.b.id", ["'1'.bid"]),
        ("m.[0].id", ["'1'.m.[0]"]),
    ),
)
@parsers
def test_nested_index_auto_id(auto_id_field, parse, string, target):
    data = {
        "id": 1,
        "b": {"id": "bid", "name": "bob"},
        "m": [{"a": "a1"}, {"a": "a2", "id": "a2id"}],
    }
    result = parse(string).find(data)
    assert_value_equality(result, target)


def test_invalid_hyphenation_in_key():
    with pytest.raises(JsonPathLexerError):
        base_parse("foo.-baz")


def test_index_hashable():
    idx = Index(0)
    assert hash(idx) == hash((0,))
    assert {idx: "value"}[idx] == "value"


def test_index_multi_indices_hashable():
    idx = Index(0, 1, 2)
    assert hash(idx) == hash((0, 1, 2))
    assert {idx: "value"}[idx] == "value"


@pytest.mark.parametrize(
    "path, data, expected_values",
    (
        ("[-1]", [], []),
        ("[-1]", [42], [42]),
        ("[-2]", [42], []),
    ),
)
@parsers
def test_find_or_create_negative_index(parse, path, data, expected_values):
    original = copy.deepcopy(data)
    results = parse(path).find_or_create(data)
    assert_value_equality(results, expected_values)
    assert data == original
