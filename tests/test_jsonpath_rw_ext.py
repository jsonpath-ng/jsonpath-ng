"""
test_jsonpath_ng_ext
----------------------------------

Tests for `jsonpath_ng_ext` module.
"""

import copy
from types import MappingProxyType

import pytest

from jsonpath_ng.exceptions import JsonPathParserError
from jsonpath_ng.ext import parser
from jsonpath_ng.ext.filter import Filter

from .helpers import assert_value_equality

test_cases = (
    pytest.param(
        "objects.`sorted`",
        {"objects": ["alpha", "gamma", "beta"]},
        [["alpha", "beta", "gamma"]],
        id="sorted_list",
    ),
    pytest.param(
        "objects.`sorted`[1]",
        {"objects": ["alpha", "gamma", "beta"]},
        "beta",
        id="sorted_list_indexed",
    ),
    pytest.param(
        "objects.`sorted`",
        {"objects": {"cow": "moo", "horse": "neigh", "cat": "meow"}},
        [["cat", "cow", "horse"]],
        id="sorted_dict",
    ),
    pytest.param(
        "objects.`sorted`[0]",
        {"objects": {"cow": "moo", "horse": "neigh", "cat": "meow"}},
        "cat",
        id="sorted_dict_indexed",
    ),
    pytest.param(
        "objects.`len`", {"objects": ["alpha", "gamma", "beta"]}, 3, id="len_list"
    ),
    pytest.param(
        "objects.`len`", {"objects": {"cow": "moo", "cat": "neigh"}}, 2, id="len_dict"
    ),
    pytest.param("objects[0].`len`", {"objects": ["alpha", "gamma"]}, 5, id="len_str"),
    pytest.param(
        'objects[?@="alpha"]',
        {"objects": ["alpha", "gamma", "beta"]},
        ["alpha"],
        id="filter_list",
    ),
    pytest.param(
        'objects[?@ =~ "a.+"]',
        {"objects": ["alpha", "gamma", "beta"]},
        ["alpha", "gamma"],
        id="filter_list_2",
    ),
    pytest.param(
        'objects[?@ =~ "a.+"]', {"objects": [1, 2, 3]}, [], id="filter_list_3"
    ),
    pytest.param(
        "objects.`keys`", {"objects": ["alpha", "gamma", "beta"]}, [], id="keys_list"
    ),
    pytest.param(
        "objects.`keys`",
        {"objects": {"cow": "moo", "cat": "neigh"}},
        ["cow", "cat"],
        id="keys_dict",
    ),
    pytest.param(
        "objects.cow.`path`",
        {"objects": {"cow": "moo", "cat": "neigh"}},
        "cow",
        id="path_dict",
    ),
    pytest.param(
        "objects[?cow]",
        {"objects": [{"cow": "moo"}, {"cat": "neigh"}]},
        [{"cow": "moo"}],
        id="filter_exists_syntax1",
    ),
    pytest.param(
        "objects[?@.cow]",
        {"objects": [{"cow": "moo"}, {"cat": "neigh"}]},
        [{"cow": "moo"}],
        id="filter_exists_syntax2",
    ),
    pytest.param(
        "objects[?(@.cow)]",
        {"objects": [{"cow": "moo"}, {"cat": "neigh"}]},
        [{"cow": "moo"}],
        id="filter_exists_syntax3",
    ),
    pytest.param(
        'objects[?(@."cow!?cat")]',
        {"objects": [{"cow!?cat": "moo"}, {"cat": "neigh"}]},
        [{"cow!?cat": "moo"}],
        id="filter_exists_syntax4",
    ),
    pytest.param(
        'objects[?cow="moo"]',
        {"objects": [{"cow": "moo"}, {"cow": "neigh"}, {"cat": "neigh"}]},
        [{"cow": "moo"}],
        id="filter_eq1",
    ),
    pytest.param(
        'objects[?(@.["cow"]="moo")]',
        {"objects": [{"cow": "moo"}, {"cow": "neigh"}, {"cat": "neigh"}]},
        [{"cow": "moo"}],
        id="filter_eq2",
    ),
    pytest.param(
        'objects[?cow=="moo"]',
        {"objects": [{"cow": "moo"}, {"cow": "neigh"}, {"cat": "neigh"}]},
        [{"cow": "moo"}],
        id="filter_eq3",
    ),
    pytest.param(
        'objects[?cow!="moo"]',
        {"objects": [{"cow": "moo"}, {"cow": "neigh"}]},
        [{"cow": "neigh"}],
        id="filter_ne",
    ),
    pytest.param(
        "objects[?cow>5]",
        {"objects": [{"cow": 8}, {"cow": 7}, {"cow": 5}, {"cow": "neigh"}]},
        [{"cow": 8}, {"cow": 7}],
        id="filter_gt",
    ),
    pytest.param(
        "objects[?cow>5&cat=2]",
        {
            "objects": [
                {"cow": 8, "cat": 2},
                {"cow": 7, "cat": 2},
                {"cow": 2, "cat": 2},
                {"cow": 5, "cat": 3},
                {"cow": 8, "cat": 3},
            ]
        },
        [{"cow": 8, "cat": 2}, {"cow": 7, "cat": 2}],
        id="filter_and",
    ),
    pytest.param(
        "objects[?confidence>=0.5].prediction",
        {
            "objects": [
                {"confidence": 0.42, "prediction": "Good"},
                {"confidence": 0.58, "prediction": "Bad"},
            ]
        },
        ["Bad"],
        id="filter_float_gt",
    ),
    pytest.param(
        "objects[/cow]",
        {
            "objects": [
                {"cat": 1, "cow": 2},
                {"cat": 2, "cow": 1},
                {"cat": 3, "cow": 3},
            ]
        },
        [[{"cat": 2, "cow": 1}, {"cat": 1, "cow": 2}, {"cat": 3, "cow": 3}]],
        id="sort1",
    ),
    pytest.param(
        "objects[/cow][0].cat",
        {
            "objects": [
                {"cat": 1, "cow": 2},
                {"cat": 2, "cow": 1},
                {"cat": 3, "cow": 3},
            ]
        },
        2,
        id="sort1_indexed",
    ),
    pytest.param(
        "objects[\\cat]",
        {"objects": [{"cat": 2}, {"cat": 1}, {"cat": 3}]},
        [[{"cat": 3}, {"cat": 2}, {"cat": 1}]],
        id="sort2",
    ),
    pytest.param(
        "objects[\\cat][-1].cat",
        {"objects": [{"cat": 2}, {"cat": 1}, {"cat": 3}]},
        1,
        id="sort2_indexed",
    ),
    pytest.param(
        "objects[/cow,\\cat]",
        {
            "objects": [
                {"cat": 1, "cow": 2},
                {"cat": 2, "cow": 1},
                {"cat": 3, "cow": 1},
                {"cat": 3, "cow": 3},
            ]
        },
        [
            [
                {"cat": 3, "cow": 1},
                {"cat": 2, "cow": 1},
                {"cat": 1, "cow": 2},
                {"cat": 3, "cow": 3},
            ]
        ],
        id="sort3",
    ),
    pytest.param(
        "objects[/cow,\\cat][0].cat",
        {
            "objects": [
                {"cat": 1, "cow": 2},
                {"cat": 2, "cow": 1},
                {"cat": 3, "cow": 1},
                {"cat": 3, "cow": 3},
            ]
        },
        3,
        id="sort3_indexed",
    ),
    pytest.param(
        "objects[/cat.cow]",
        {
            "objects": [
                {"cat": {"dog": 1, "cow": 2}},
                {"cat": {"dog": 2, "cow": 1}},
                {"cat": {"dog": 3, "cow": 3}},
            ]
        },
        [
            [
                {"cat": {"dog": 2, "cow": 1}},
                {"cat": {"dog": 1, "cow": 2}},
                {"cat": {"dog": 3, "cow": 3}},
            ]
        ],
        id="sort4",
    ),
    pytest.param(
        "objects[/cat.cow][0].cat.dog",
        {
            "objects": [
                {"cat": {"dog": 1, "cow": 2}},
                {"cat": {"dog": 2, "cow": 1}},
                {"cat": {"dog": 3, "cow": 3}},
            ]
        },
        2,
        id="sort4_indexed",
    ),
    pytest.param(
        "objects[/cat.(cow,bow)]",
        {
            "objects": [
                {"cat": {"dog": 1, "bow": 3}},
                {"cat": {"dog": 2, "cow": 1}},
                {"cat": {"dog": 2, "bow": 2}},
                {"cat": {"dog": 3, "cow": 2}},
            ]
        },
        [
            [
                {"cat": {"dog": 2, "cow": 1}},
                {"cat": {"dog": 2, "bow": 2}},
                {"cat": {"dog": 3, "cow": 2}},
                {"cat": {"dog": 1, "bow": 3}},
            ]
        ],
        id="sort5_twofields",
    ),
    pytest.param(
        "objects[/cat.(cow,bow)][0].cat.dog",
        {
            "objects": [
                {"cat": {"dog": 1, "bow": 3}},
                {"cat": {"dog": 2, "cow": 1}},
                {"cat": {"dog": 2, "bow": 2}},
                {"cat": {"dog": 3, "cow": 2}},
            ]
        },
        2,
        id="sort5_indexed",
    ),
    pytest.param("3 * 3", {}, [9], id="arithmetic_number_only"),
    pytest.param("$.foo * 10", {"foo": 4}, [40], id="arithmetic_mul1"),
    pytest.param("10 * $.foo", {"foo": 4}, [40], id="arithmetic_mul2"),
    pytest.param("$.foo * 10", {"foo": 4}, [40], id="arithmetic_mul3"),
    pytest.param("$.foo * 3", {"foo": "f"}, ["fff"], id="arithmetic_mul4"),
    pytest.param("foo * 3", {"foo": "f"}, ["foofoofoo"], id="arithmetic_mul5"),
    pytest.param("($.foo * 10 * $.foo) + 2", {"foo": 4}, [162], id="arithmetic_mul6"),
    pytest.param("$.foo * 10 * $.foo + 2", {"foo": 4}, [240], id="arithmetic_mul7"),
    pytest.param(
        "foo + bar", {"foo": "name", "bar": "node"}, ["foobar"], id="arithmetic_str0"
    ),
    pytest.param(
        'foo + "_" + bar',
        {"foo": "name", "bar": "node"},
        ["foo_bar"],
        id="arithmetic_str1",
    ),
    pytest.param(
        '$.foo + "_" + $.bar',
        {"foo": "name", "bar": "node"},
        ["name_node"],
        id="arithmetic_str2",
    ),
    pytest.param(
        "$.foo + $.bar",
        {"foo": "name", "bar": "node"},
        ["namenode"],
        id="arithmetic_str3",
    ),
    pytest.param(
        "foo.cow + bar.cow",
        {"foo": {"cow": "name"}, "bar": {"cow": "node"}},
        ["namenode"],
        id="arithmetic_str4",
    ),
    pytest.param(
        "$.objects[*].cow * 2",
        {"objects": [{"cow": 1}, {"cow": 2}, {"cow": 3}]},
        [2, 4, 6],
        id="arithmetic_list1",
    ),
    pytest.param(
        "$.objects[*].cow * $.objects[*].cow",
        {"objects": [{"cow": 1}, {"cow": 2}, {"cow": 3}]},
        [1, 4, 9],
        id="arithmetic_list2",
    ),
    pytest.param(
        "$.objects[*].cow * $.objects2[*].cow",
        {"objects": [{"cow": 1}, {"cow": 2}, {"cow": 3}], "objects2": [{"cow": 5}]},
        [],
        id="arithmetic_list_err1",
    ),
    pytest.param('$.objects * "foo"', {"objects": []}, [], id="arithmetic_err1"),
    pytest.param('"bar" * "foo"', {}, [], id="arithmetic_err2"),
    pytest.param(
        "payload.metrics[?(@.name='cpu.frequency')].value * 100",
        {
            "payload": {
                "metrics": [
                    {
                        "timestamp": "2013-07-29T06:51:34.472416",
                        "name": "cpu.frequency",
                        "value": 1600,
                        "source": "libvirt.LibvirtDriver",
                    },
                    {
                        "timestamp": "2013-07-29T06:51:34.472416",
                        "name": "cpu.user.time",
                        "value": 17421440000000,
                        "source": "libvirt.LibvirtDriver",
                    },
                ]
            }
        },
        [160000],
        id="real_life_example1",
    ),
    pytest.param(
        "payload.(id|(resource.id))",
        {"payload": {"id": "foobar"}},
        ["foobar"],
        id="real_life_example2",
    ),
    pytest.param(
        "payload.id|(resource.id)",
        {"payload": {"resource": {"id": "foobar"}}},
        ["foobar"],
        id="real_life_example3",
    ),
    pytest.param(
        "payload.id|(resource.id)",
        {"payload": {"id": "yes", "resource": {"id": "foobar"}}},
        ["yes", "foobar"],
        id="real_life_example4",
    ),
    pytest.param(
        "payload.`sub(/(foo\\\\d+)\\\\+(\\\\d+bar)/, \\\\2-\\\\1)`",
        {"payload": "foo5+3bar"},
        ["3bar-foo5"],
        id="sub1",
    ),
    pytest.param(
        "payload.`sub(/foo\\\\+bar/, repl)`",
        {"payload": "foo+bar"},
        ["repl"],
        id="sub2",
    ),
    pytest.param("payload.`str()`", {"payload": 1}, ["1"], id="str1"),
    pytest.param(
        "payload.`split(-, 2, -1)`",
        {"payload": "foo-bar-cat-bow"},
        ["cat"],
        id="split1",
    ),
    pytest.param(
        "payload.`split(-, 2, 2)`",
        {"payload": "foo-bar-cat-bow"},
        ["cat-bow"],
        id="split2",
    ),
    pytest.param(
        "payload.`split(',', 2, -1)`",
        {"payload": "foo,bar,baz"},
        ["baz"],
        id="split3",
    ),
    pytest.param(
        'payload.`split(", ", 2, -1)`',
        {"payload": "foo, bar, baz"},
        ["baz"],
        id="split4",
    ),
    pytest.param(
        'payload.`split(", ", *, -1)`',
        {"payload": "foo, bar, baz"},
        [["foo", "bar", "baz"]],
        id="split5",
    ),
    pytest.param(
        'payload.`split(", ", -1, -1)`',
        {"payload": "foo, bar, baz"},
        ["baz"],
        id="split6",
    ),
    pytest.param(
        "payload.`split(|, -1, 1)`",
        {"payload": "foo|bar|baz"},
        ["bar|baz"],
        id="split7",
    ),
    pytest.param(
        "foo[?(@.baz==1)]",
        {"foo": [{"baz": 1}, {"baz": 2}]},
        [{"baz": 1}],
        id="bug-#2-correct",
    ),
    pytest.param(
        "foo[*][?(@.baz==1)]", {"foo": [{"baz": 1}, {"baz": 2}]}, [], id="bug-#2-wrong"
    ),
    pytest.param(
        "foo[?flag = true].color",
        {
            "foo": [
                {"color": "blue", "flag": True},
                {"color": "green", "flag": False},
            ]
        },
        ["blue"],
        id="boolean-filter-true",
    ),
    pytest.param(
        "foo[?flag = false].color",
        {
            "foo": [
                {"color": "blue", "flag": True},
                {"color": "green", "flag": False},
            ]
        },
        ["green"],
        id="boolean-filter-false",
    ),
    pytest.param(
        "foo[?flag = true].color",
        {
            "foo": [
                {"color": "blue", "flag": True},
                {"color": "green", "flag": 2},
                {"color": "red", "flag": "hi"},
            ]
        },
        ["blue"],
        id="boolean-filter-other-datatypes-involved",
    ),
    pytest.param(
        'foo[?flag = "true"].color',
        {
            "foo": [
                {"color": "blue", "flag": True},
                {"color": "green", "flag": "true"},
            ]
        },
        ["green"],
        id="boolean-filter-string-true-string-literal",
    ),
    pytest.param(
        '$[?!@..["type"]]',
        [
            {
                "name": "foo",
                "data": [{"value": "bar"}]
            },
            {
                "name": "foo",
                "data": [{"value": "bar", "type": "foo"}]
            }
        ],
        [
            {
                "name": "foo",
                "data": [{"value": "bar"}]
            }
        ],
        id="negated_relative_query_existence"
    ),
    pytest.param(
        '$[?!data[*].type]',
        [
            {
                "name": "foo",
                "data": [{"value": "bar"}]
            },
            {
                "name": "foo",
                "data": [{"value": "bar", "type": "foo"}]
            }
        ],
        [
            {
                "name": "foo",
                "data": [{"value": "bar"}]
            }
        ],
        id="negated_relative_query_existence_implicit_this",
    ),
    pytest.param(
        "false_positives",
        {"problems_detected": 4, "false_positives": 2},
        [2],
        id="field-starting-with-false",
    ),
    pytest.param(
        "trueName",
        {"trueName": "value"},
        ["value"],
        id="field-starting-with-true",
    ),
    pytest.param(
        "foo[?flag = true].color",
        {
            "foo": [
                {"color": "blue", "flag": True},
                {"color": "green", "flag": 2},
                {"color": "red", "flag": "hi"},
                {"color": "gray", "flag": None},
            ]
        },
        ["blue"],
        id="boolean-filter-with-null",
    ),
    pytest.param(
        "foo[?(@.v = 0)].k",
        {"foo": [{"k": "A", "v": 0.0}, {"k": "B", "v": 0.6}, {"k": "C", "v": 0}]},
        ["A", "C"],
        id="int-no-float-truncation",
    ),
    pytest.param(
        "foo[?(@.v == 0)].k",
        {"foo": [{"k": "A", "v": 0.0}, {"k": "B", "v": 0.6}, {"k": "C", "v": 0}]},
        ["A", "C"],
        id="int-no-float-truncation-double-equals",
    ),
    pytest.param(
        "foo[?(@.v = 0)].k",
        {"foo": [{"k": "A", "v": None}, {"k": "B", "v": 0}]},
        ["B"],
        id="none-lhs-does-not-crash",
    ),
    pytest.param(
        "foo[?(@.v = -1)].k",
        {"foo": [{"k": "A", "v": -0.9}, {"k": "B", "v": -1}]},
        ["B"],
        id="negative-int-rhs-no-float-truncation",
    ),
)


@pytest.mark.parametrize("path, data, expected_values", test_cases)
def test_values(path, data, expected_values):
    results = parser.parse(path).find(data)
    assert_value_equality(results, expected_values)


def test_filter_find_does_not_mutate_mapping():
    source = {
        "objects": {
            "first": {"score": 90},
            "second": {"score": 50},
        }
    }
    original = copy.deepcopy(source)

    matches = parser.parse("$.objects[?(@.score >= 85)]").find(source)

    assert [match.value for match in matches] == [{"score": 90}]
    assert [str(match.full_path) for match in matches] == ["objects.first"]
    assert source == original

    matches[0].value = {"score": 95}
    assert source["objects"] == {
        "first": {"score": 95},
        "second": {"score": 50},
    }


def test_filter_find_accepts_read_only_mapping():
    source = MappingProxyType(
        {
            "objects": {
                "first": {"score": 90},
                "second": {"score": 50},
            }
        }
    )

    matches = parser.parse("$.objects[?(@.score >= 85)]").find(source)

    assert [match.value for match in matches] == [{"score": 90}]


def test_filter_removes_matching_mapping_entries():
    source = {
        "first": {"score": 90},
        "second": {"score": 50},
    }

    parser.parse("$[?(@.score >= 85)]").filter(lambda _: True, source)

    assert source == {"second": {"score": 50}}


def test_filter_stops_evaluating_after_first_failed_expression():
    calls = []

    class MatchesSecondValue:
        def find(self, value):
            calls.append(("first", value))
            return [value] if value == 2 else []

    class RecordsLaterExpression:
        def find(self, value):
            calls.append(("second", value))
            return [value]

    matches = Filter([MatchesSecondValue(), RecordsLaterExpression()]).find([1, 2, 3])

    assert [match.value for match in matches] == [2]
    assert calls == [("first", 1), ("first", 2), ("second", 2), ("first", 3)]


def test_invalid_hyphenation_in_key():
    # This test is almost copied-and-pasted directly from `test_jsonpath.py`.
    # However, the parsers generate different exceptions for this syntax error.
    # This discrepancy needs to be resolved.
    with pytest.raises(JsonPathParserError):
        parser.parse("foo.-baz")
