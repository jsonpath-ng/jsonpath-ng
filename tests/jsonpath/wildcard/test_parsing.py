"""
An unquoted ``*`` parses to a ``Wildcard`` node (RFC 9535, section 2.3.2),
and the text form of a wildcard path parses back to the same path.
"""

import pytest

import jsonpath_ng
import jsonpath_ng.ext
from jsonpath_ng.jsonpath import Child
from jsonpath_ng.jsonpath import Descendants
from jsonpath_ng.jsonpath import Fields
from jsonpath_ng.jsonpath import Root
from jsonpath_ng.jsonpath import Slice
from jsonpath_ng.jsonpath import Wildcard

parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)


@parsers
@pytest.mark.parametrize(
    "expression, expected",
    (
        ("$.*", Child(Root(), Wildcard())),
        ("$[*]", Child(Root(), Wildcard())),
        ("$..*", Descendants(Root(), Wildcard())),
        ("$.a.*", Child(Child(Root(), Fields("a")), Wildcard())),
        ("$.a[*].b", Child(Child(Child(Root(), Fields("a")), Wildcard()), Fields("b"))),
        ("*", Wildcard()),
        ("[*]", Wildcard()),
    ),
)
def test_unquoted_star_parses_to_wildcard(parse, expression, expected):
    assert parse(expression) == expected


@parsers
def test_empty_slice_is_not_a_wildcard_node(parse):
    assert parse("$[:]") == Child(Root(), Slice())
    assert parse("$[:]") != parse("$[*]")


@parsers
@pytest.mark.parametrize("expression", ("$.*", "$[*]", "$..*", "$.a.*.b"))
def test_text_form_of_a_wildcard_path_parses_back_to_it(parse, expression):
    path = parse(expression)

    assert parse(str(path)) == path
