"""
A quoted ``'*'`` is a member name, and only an unquoted ``*`` is the wildcard.

RFC 9535, section 2.3.1.1: a name selector is a string literal and selects
the member with that name. Section 2.3.2.1: the wildcard selector is the
unquoted ``*``. So ``$['*']`` selects the member named ``*``, never every member.
"""

import copy

import pytest

import jsonpath_ng
import jsonpath_ng.ext

parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)

quoted_star = pytest.mark.parametrize(
    "expression",
    ("$['*']", '$["*"]', "$.'*'", '$."*"'),
)

DATA = {"*": 1, "b": 2, "c": 3}


def values(parse, expression, data):
    return [match.value for match in parse(expression).find(data)]


@parsers
@quoted_star
def test_quoted_star_selects_only_the_member_named_star(parse, expression):
    assert values(parse, expression, DATA) == [1]


@parsers
@quoted_star
def test_quoted_star_selects_nothing_when_no_member_has_that_name(parse, expression):
    assert values(parse, expression, {"b": 2, "c": 3}) == []


@parsers
@quoted_star
def test_quoted_star_selects_nothing_from_arrays(parse, expression):
    assert values(parse, expression, [5, 6]) == []


@parsers
def test_quoted_star_in_a_union_is_a_name(parse):
    assert values(parse, "$['*','b']", DATA) == [1, 2]


@parsers
def test_quoted_star_is_a_name_after_a_descendants_operator(parse):
    data = {"*": 1, "a": {"*": 2, "b": 3}}

    assert values(parse, "$..['*']", data) == [1, 2]


@parsers
def test_unquoted_star_is_still_the_wildcard(parse):
    assert values(parse, "$.*", DATA) == [1, 2, 3]
    assert values(parse, "$[*]", DATA) == [1, 2, 3]


@parsers
def test_full_path_of_a_member_named_star_selects_that_member(parse):
    """A path that is rendered to text must round-trip to the same member."""
    data = {"*": 1, "b": 2}
    match = parse("$.*").find(data)[0]

    assert match.value == 1
    assert values(parse, f"$.{match.full_path}", data) == [1]


@parsers
@quoted_star
def test_update_with_quoted_star_changes_only_the_member_named_star(parse, expression):
    data = copy.deepcopy(DATA)

    parse(expression).update(data, 99)

    assert data == {"*": 99, "b": 2, "c": 3}


@parsers
@quoted_star
def test_update_with_quoted_star_ignores_arrays(parse, expression):
    data = [5, 6]

    parse(expression).update(data, 99)

    assert data == [5, 6]


@parsers
@quoted_star
def test_filter_with_quoted_star_removes_only_the_member_named_star(parse, expression):
    data = copy.deepcopy(DATA)

    parse(expression).filter(lambda value: True, data)

    assert data == {"b": 2, "c": 3}


@parsers
@quoted_star
def test_filter_with_quoted_star_ignores_arrays(parse, expression):
    data = [5, 6]

    parse(expression).filter(lambda value: True, data)

    assert data == [5, 6]


@parsers
def test_update_or_create_with_quoted_star_creates_the_member_named_star(parse):
    data = {"b": 2}

    parse("$['*']").update_or_create(data, 99)

    assert data == {"b": 2, "*": 99}


@parsers
def test_find_or_create_with_quoted_star_creates_the_member_named_star(parse):
    data = {"b": 2}

    parse("$['*']").find_or_create(data)

    assert data == {"b": 2, "*": {}}


@parsers
def test_member_named_star_renders_so_that_it_reparses_as_a_name(parse):
    (match,) = parse("$['*']").find({"*": 1, "b": 2})

    assert str(match.full_path) == "'*'"
    assert [m.value for m in parse(f"$.{match.full_path}").find({"*": 1, "b": 2})] == [
        1
    ]
