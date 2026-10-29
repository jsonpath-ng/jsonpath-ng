"""
Test how the `sub` and `split` extensions parse their definitions.

The definitions are matched with regular expressions that must not backtrack
quadratically when a definition is malformed, and that must keep the greedy
choices that let `/`, `,`, and `)` appear inside arguments.
"""

import timeit

import pytest

from jsonpath_ng.ext import parse
from jsonpath_ng.ext.string import DefintionInvalid
from jsonpath_ng.ext.string import Split
from jsonpath_ng.ext.string import Sub


@pytest.mark.parametrize(
    "definition, expr, repl",
    (
        pytest.param("sub(/a/, b)", "a", "b", id="simple"),
        pytest.param("sub(/a/,   b)", "a", "b", id="extra whitespace"),
        pytest.param("sub(/ a /, b)", "a", "b", id="arguments are stripped"),
        pytest.param("sub(//, b)", "", "b", id="empty regex"),
        pytest.param("sub(/a/, )", "a", "", id="empty replacement"),
        pytest.param("sub(/x/y/, Z)", "x/y", "Z", id="slash in regex"),
        pytest.param("sub(/x/,  y/, Z)", "x/,  y", "Z", id="last separator wins"),
        pytest.param("sub(/x/, a, b)", "x", "a, b", id="comma in replacement"),
        pytest.param("sub(/x/, (b))", "x", "(b)", id="parentheses in replacement"),
        pytest.param("sub(/(a)/, \\1)", "(a)", "\\1", id="paren in regex"),
        pytest.param("sub(/a/, b))", "a", "b)", id="last paren wins"),
        pytest.param("sub(/a/, b) trailing", "a", "b", id="trailing text ignored"),
    ),
)
def test_sub_definition(definition, expr, repl):
    sub = Sub(definition)

    assert sub.expr == expr
    assert sub.repl == repl


@pytest.mark.parametrize(
    "definition",
    (
        "sub(/a/b)",
        "sub(/a/,b)",
        "sub(/a/, b",
        "sub(a/, b)",
        "sub(/" + "/,  " * 10,
        " sub(/a/, b)",
        "sub",
    ),
)
def test_sub_definition_invalid(definition):
    with pytest.raises(DefintionInvalid):
        Sub(definition)


@pytest.mark.parametrize(
    "definition, chars, segment, max_split",
    (
        pytest.param("split(-, 2, -1)", "-", "2", -1, id="simple"),
        pytest.param("split(-, *, 3)", "-", "*", 3, id="wildcard segment"),
        pytest.param("split(-,-2,-1)", "-", "-2", -1, id="negative segment"),
        pytest.param("split (-, 2, 2)", "-", "2", 2, id="space before paren"),
        pytest.param("split( -, 2, 2 )", "-", "2", 2, id="space inside parens"),
        pytest.param("split(\t-\t,\t2\t,\t2\t)", "-\t", "2", 2, id="tabs"),
        pytest.param("split(',', *, -1)", ",", "*", -1, id="single-quoted comma"),
        pytest.param('split(",", *, -1)', ",", "*", -1, id="double-quoted comma"),
        pytest.param("split(' ', -1, -1)", " ", "-1", -1, id="quoted space"),
        pytest.param("split(,, *, -1)", ",", "*", -1, id="unquoted comma"),
        pytest.param("split(/, *, -1)", "/", "*", -1, id="slash"),
        pytest.param("split(ab, 1, 2)", "ab", "1", 2, id="multi-character"),
        pytest.param("split(a , 1, 2)", "a ", "1", 2, id="trailing space kept"),
        pytest.param("split( , *, 1)", " ", "*", 1, id="space is a separator"),
        pytest.param("split(a, 1, 2), 3, 4)", "a, 1, 2)", "3", 4, id="last tail wins"),
        pytest.param("split('a, *, 1)", "'a", "*", 1, id="unclosed quote"),
        pytest.param("split(a, 1, 2) trailing", "a", "1", 2, id="trailing text"),
    ),
)
def test_split_definition(definition, chars, segment, max_split):
    split = Split(definition)

    assert split.chars == chars
    assert split.segment == segment
    assert split.max_split == max_split


@pytest.mark.parametrize(
    "definition",
    (
        "split(, 1, 2)",
        "split(a, x, 2)",
        "split(a, 1, *)",
        "split(a, 1, 2",
        "split(a, 1)",
        "split(a 1, 2)",
        "split(a" + " " * 20 + ",",
        "split" + " " * 20 + "(a",
        " split(a, 1, 2)",
        "split",
    ),
)
def test_split_definition_invalid(definition):
    with pytest.raises(DefintionInvalid):
        Split(definition)


@pytest.mark.parametrize(
    "query, data, expected",
    (
        pytest.param("a.`sub(/x/y/, Z)`", {"a": "x/y"}, ["Z"], id="sub slash"),
        pytest.param("a.`sub(/x\\/y/, Z)`", {"a": "x/y"}, ["Z"], id="sub escaped"),
        pytest.param("a.`sub(/x/, a, b)`", {"a": "x"}, ["a, b"], id="sub comma"),
        pytest.param(
            "a.`sub(/foo\\\\+(.*)/, \\\\1)`",
            {"a": "foo+bar"},
            ["bar"],
            id="sub README example",
        ),
        pytest.param("a.`split(,, *, -1)`", {"a": "1,2,3"}, [["1", "2", "3"]], id="1"),
        pytest.param(
            "a.`split(\\,, 1, -1)`", {"a": "1,2,3"}, ["2"], id="split escaped"
        ),
        pytest.param("a.`split(/, 1, -1)`", {"a": "1/2/3"}, ["2"], id="split slash"),
    ),
)
def test_queries(query, data, expected):
    assert [match.value for match in parse(query).find(data)] == expected


SMALL = 1000
LARGE = SMALL * 4


def best_time(function, definition_for_size, size):
    definition = definition_for_size(size)

    def attempt():
        with pytest.raises(DefintionInvalid):
            function(definition)

    return min(timeit.repeat(attempt, number=3, repeat=7))


@pytest.mark.parametrize(
    "function, definition_for_size",
    (
        pytest.param(Sub, lambda n: "sub(/" + "/,  " * n, id="sub separators"),
        pytest.param(Sub, lambda n: "sub(/)" + "/,  " * n, id="sub early paren"),
        pytest.param(Sub, lambda n: "sub(/a/," + " " * n, id="sub whitespace"),
        pytest.param(Split, lambda n: "split(a" + " " * n + ",", id="split before"),
        pytest.param(Split, lambda n: "split(" + " " * n + "a", id="split after"),
        pytest.param(Split, lambda n: "split(" + "a," * n + "x", id="split commas"),
        pytest.param(Split, lambda n: "split(a, 1," + " 1," * n, id="split tails"),
    ),
)
def test_definition_failure_time_is_linear_to_length(function, definition_for_size):
    ratio = best_time(function, definition_for_size, LARGE) / best_time(
        function, definition_for_size, SMALL
    )

    # Linear growth gives ~4 and quadratic growth gives ~16;
    # 8 leaves margin for timing noise on both sides.
    assert ratio < 8, f"{LARGE / SMALL:.0f}x the text took {ratio:.1f}x as long"
