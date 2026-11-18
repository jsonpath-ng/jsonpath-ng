import warnings

import pytest
from hypothesis import assume
from hypothesis import example
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

import jsonpath_ng
import jsonpath_ng.exceptions
import jsonpath_ng.ext
from jsonpath_ng import Fields

characters = st.characters(min_codepoint=0x20, max_codepoint=0x7E)  # space -> tilde
ascii_text = st.text(characters)

PARSERS = [
    pytest.param(jsonpath_ng.parse, id="core"),
    pytest.param(jsonpath_ng.ext.parse, id="ext"),
]


@given(ascii_text)
@example("10")
@example("';'")
@example('"0@"')
@example('"00"')
@example(r'"\'"')
@example("0..0[0]")
@example("(0..0)[0]")
@example("0..(0[0])")
@example("0..0.[0]")
@settings(max_examples=20)
def test_roundtrip_basic(string: str):
    with warnings.catch_warnings():
        # The random text may contain the deprecated `|` and `&` operators.
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            parsed_original = jsonpath_ng.parse(string)
        except jsonpath_ng.exceptions.JSONPathError:
            assume(False)
            return

        reconstituted = str(parsed_original)
        parsed_reconstituted = jsonpath_ng.parse(reconstituted)
    assert parsed_original == parsed_reconstituted


@given(ascii_text)
@example("0-@")
@example('"@"')
@example("'%'")
@example("''")
@example("A -A")
@example("A -@")
@example("0[/0]")
@settings(max_examples=20)
def test_roundtrip_extended(string: str):
    with warnings.catch_warnings():
        # The random text may contain the deprecated `|` and `&` operators.
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            parsed_original = jsonpath_ng.ext.parse(string)
        except jsonpath_ng.exceptions.JSONPathError:
            assume(False)
            return

        reconstituted = str(parsed_original)
        parsed_reconstituted = jsonpath_ng.ext.parse(reconstituted)
    assert parsed_original == parsed_reconstituted


# Field names that start with `@` can be parsed only when `@` is followed by a
# letter or underscore. Otherwise, the name must be quoted to be re-parsed as a field.
@pytest.mark.parametrize("parse", PARSERS)
@pytest.mark.parametrize("name", ["@", "@@", "@1", "@-", "@@a", "@ a"])
def test_field_names_that_start_with_at_are_quoted(parse, name):
    original = Fields(name)

    assert parse(str(original)) == original


@pytest.mark.parametrize("parse", PARSERS)
@pytest.mark.parametrize("name", ["@a", "@_", "a@", "a@b", "a-b", "_@", "a1"])
def test_field_names_that_do_not_need_quotes_are_not_quoted(parse, name):
    original = Fields(name)

    assert str(original) == name
    assert parse(str(original)) == original


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("$['@']", id="path"),
        pytest.param("$[?@['@'] == 1]", id="filter-target"),
        pytest.param("$[?@['@'] == 1 && @.a == 2]", id="filter-conjunction"),
        pytest.param("$[?@['@@x'] == 1 || @['@1']]", id="filter-disjunction"),
    ],
)
def test_queries_with_at_field_names_roundtrip(query):
    original = jsonpath_ng.ext.parse(query)

    assert jsonpath_ng.ext.parse(str(original)) == original


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("`sorted`", id="sorted-root"),
        pytest.param("$.a.`sorted`", id="sorted-child"),
        pytest.param("$.a.`sorted`.b", id="sorted-then-field"),
        pytest.param("$.a.`sorted`[0]", id="sorted-then-index"),
        pytest.param("$..`sorted`", id="sorted-descendants"),
        pytest.param("$.a[?@.x > 1].`sorted`", id="sorted-after-filter"),
        pytest.param("$.a[/b]", id="sort-expression"),
        pytest.param(r"$[/a, \b]", id="sort-expressions"),
        pytest.param("$.a[/b].c", id="sort-expression-then-field"),
    ],
)
def test_queries_with_sorted_roundtrip(query):
    original = jsonpath_ng.ext.parse(query)

    assert jsonpath_ng.ext.parse(str(original)) == original


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("`sorted`", id="sorted-root"),
        pytest.param("$.a.`sorted`", id="sorted-child"),
        pytest.param("$.a[/b]", id="sort-expression"),
        pytest.param(r"$[/a, \b]", id="sort-expressions"),
    ],
)
def test_sorted_str_matches_the_query(query):
    assert str(jsonpath_ng.ext.parse(query)) == query
