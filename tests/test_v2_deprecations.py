import importlib
import re

import pytest

import jsonpath_ng
import jsonpath_ng.ext
import jsonpath_ng.ext.parser as parser
import jsonpath_ng.jsonpath
from jsonpath_ng.ext.filter import Filter
from jsonpath_ng.jsonpath import Child
from jsonpath_ng.jsonpath import Fields
from jsonpath_ng.jsonpath import Root
from tests.helpers import assert_value_equality


def test_extented_jsonpath_parser_access():
    match = "ExtentedJsonPathParser is a deprecated name"
    with pytest.warns(DeprecationWarning, match=match):
        assert parser.ExtentedJsonPathParser is parser.ExtendedJsonPathParser


def test_version_attribute_is_deprecated():
    match = "The `__version__` attribute is deprecated"
    with pytest.warns(DeprecationWarning, match=match):
        assert jsonpath_ng.__version__[0] == "1"


@pytest.mark.parametrize(
    "datum, expected_values",
    [
        pytest.param([1, 2], [1, 2], id="list"),
        pytest.param({"a": 1, "b": 2}, [1, 2], id="dict"),
        pytest.param(2, [], id="int"),
        pytest.param(None, [], id="null"),
    ],
)
def test_filter_without_expressions_is_deprecated(datum, expected_values):
    match = "Creating a Filter with no expressions is deprecated."
    with pytest.warns(DeprecationWarning, match=match):
        selector = Filter([])

    results = Child(Root(), selector).find(datum)
    assert_value_equality(results, expected_values)


PARSERS = pytest.mark.parametrize(
    "parse",
    [
        pytest.param(jsonpath_ng.parse, id="core"),
        pytest.param(jsonpath_ng.ext.parse, id="ext"),
    ],
)
PIPE_MESSAGE = r"The `\|` \(union\) operator is deprecated"
PATH_AMPERSAND_MESSAGE = r"The `&` \(intersection\) operator is deprecated"
FILTER_AMPERSAND_MESSAGE = r"The `&` operator in filters is deprecated"


@PARSERS
def test_pipe_operator_is_deprecated(parse):
    with pytest.warns(DeprecationWarning, match=PIPE_MESSAGE) as record:
        parse("a | b")

    assert len(record) == 1


@PARSERS
def test_pipe_operator_warns_once_per_operator(parse):
    with pytest.warns(DeprecationWarning, match=PIPE_MESSAGE) as record:
        parse("a | b | c")

    assert len(record) == 2


@PARSERS
def test_path_ampersand_operator_is_deprecated(parse):
    with pytest.warns(DeprecationWarning, match=PATH_AMPERSAND_MESSAGE) as record:
        parse("a & b")

    assert len(record) == 1


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("$[?@.a == 1 & @.b == 1]", id="no-parentheses"),
        pytest.param("$[?(@.a == 1) & (@.b == 1)]", id="parentheses"),
    ],
)
def test_filter_ampersand_operator_is_deprecated(query):
    with pytest.warns(DeprecationWarning, match=FILTER_AMPERSAND_MESSAGE) as record:
        jsonpath_ng.ext.parse(query)

    assert len(record) == 1


def test_filter_ampersand_operator_still_works():
    with pytest.warns(DeprecationWarning, match=FILTER_AMPERSAND_MESSAGE):
        query = jsonpath_ng.ext.parse("$[?@.a == 1 & @.b == 1]")

    results = query.find([{"a": 1, "b": 1}, {"a": 1, "b": 2}])
    assert_value_equality(results, [{"a": 1, "b": 1}])


def test_pipe_operator_still_works():
    with pytest.warns(DeprecationWarning, match=PIPE_MESSAGE):
        query = jsonpath_ng.parse("a | b")

    assert_value_equality(query.find({"a": 1, "b": 2}), [1, 2])


def test_path_ampersand_operator_creates_an_intersect():
    with pytest.warns(DeprecationWarning, match=PATH_AMPERSAND_MESSAGE):
        query = jsonpath_ng.parse("a & b")

    assert type(query) is jsonpath_ng.jsonpath._Intersect


def test_parsing_a_pipe_creates_a_union():
    with pytest.warns(DeprecationWarning, match=PIPE_MESSAGE):
        query = jsonpath_ng.parse("a | b")

    assert type(query) is jsonpath_ng.jsonpath._Union


@pytest.mark.parametrize("name", ["Union", "Intersect"])
@pytest.mark.parametrize("module", ["jsonpath_ng", "jsonpath_ng.jsonpath"])
def test_union_and_intersect_access_is_deprecated(module, name):
    module = importlib.import_module(module)
    match = re.escape(f"`{name}` is deprecated")

    with pytest.warns(DeprecationWarning, match=match):
        cls = getattr(module, name)

    assert cls is getattr(jsonpath_ng.jsonpath, f"_{name}")


@pytest.mark.parametrize("name", ["Union", "Intersect"])
def test_union_and_intersect_import_is_deprecated(name):
    with pytest.warns(DeprecationWarning, match=rf"`{name}` is deprecated"):
        namespace = {}
        exec(f"from jsonpath_ng.jsonpath import {name}", namespace)

    assert namespace[name] is getattr(jsonpath_ng.jsonpath, f"_{name}")


@pytest.mark.parametrize("name", ["Union", "Intersect"])
def test_star_import_does_not_export_union_or_intersect(name):
    namespace = {}
    exec("from jsonpath_ng import *", namespace)

    assert name not in namespace


@pytest.mark.parametrize("module", [jsonpath_ng, jsonpath_ng.jsonpath])
def test_unknown_attributes_still_raise_attribute_error(module):
    with pytest.raises(AttributeError, match="NoSuchName"):
        module.NoSuchName


BARE_WORD_MESSAGE = r"An unquoted word as a comparison operand is deprecated"


@pytest.mark.parametrize("operator", ["==", "!=", "<", "<=", ">", ">=", "=~"])
def test_bare_word_comparison_operand_is_deprecated(operator):
    with pytest.warns(DeprecationWarning, match=BARE_WORD_MESSAGE) as record:
        jsonpath_ng.ext.parse(f"$[?@.a {operator} foo]")

    assert len(record) == 1


def test_bare_word_deprecation_suggests_the_quoted_string():
    with pytest.warns(DeprecationWarning, match=r"Write `'foo'` instead") as record:
        jsonpath_ng.ext.parse("$[?@.a == foo]")

    assert len(record) == 1


def test_bare_word_deprecation_warns_once_per_bare_word():
    with pytest.warns(DeprecationWarning, match=BARE_WORD_MESSAGE) as record:
        jsonpath_ng.ext.parse("$[?@.a == foo && @.b == bar || @.c == 'baz']")

    assert len(record) == 2


def test_bare_word_deprecation_is_attributed_to_the_caller():
    with pytest.warns(DeprecationWarning, match=BARE_WORD_MESSAGE) as record:
        jsonpath_ng.ext.parse("$[?@.a == foo]")

    assert record[0].filename == __file__


def test_bare_word_comparison_operand_still_means_a_string():
    with pytest.warns(DeprecationWarning, match=BARE_WORD_MESSAGE):
        query = jsonpath_ng.ext.parse("$[?@.a == foo]")

    results = query.find([{"a": "foo"}, {"a": "bar"}, {"a": 1}])
    assert_value_equality(results, [{"a": "foo"}])


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("$[?@.a == 'foo']", id="single-quoted"),
        pytest.param('$[?@.a == "foo"]', id="double-quoted"),
        pytest.param("$[?@.a =~ 'f.*']", id="quoted-pattern"),
        pytest.param("$[?@.a == 1]", id="integer"),
        pytest.param("$[?@.a == 1.5]", id="float"),
        pytest.param("$[?@.a == true]", id="true"),
        pytest.param("$[?@.a == false]", id="false"),
        pytest.param("$[?@.a == null]", id="null"),
        pytest.param("$[?@.a == @.b]", id="current-node-query"),
        pytest.param("$[?@.a == $.b]", id="root-query"),
    ],
)
def test_comparison_operands_that_are_not_bare_words_do_not_warn(query):
    # `pytest` turns every warning into an error.
    jsonpath_ng.ext.parse(query)


def test_building_fields_star_is_deprecated():
    with pytest.warns(DeprecationWarning, match=r"Fields\('\*'\).*Wildcard\(\)"):
        Fields("*")


def test_building_fields_that_include_star_is_deprecated():
    with pytest.warns(DeprecationWarning, match=r"Wildcard\(\)"):
        Fields("a", "*")


def test_building_fields_without_star_is_not_deprecated(recwarn):
    Fields("a", "b")

    assert not recwarn.list


def test_deprecated_fields_star_still_selects_object_members():
    with pytest.warns(DeprecationWarning):
        path = Fields("*")

    assert [m.value for m in path.find({"a": 1, "b": 2})] == [1, 2]


def test_deprecated_fields_star_still_selects_array_elements():
    with pytest.warns(DeprecationWarning):
        path = Fields("*")

    assert [m.value for m in path.find([1, 2])] == [1, 2]


def test_deprecated_fields_star_still_updates_and_filters():
    with pytest.warns(DeprecationWarning):
        path = Fields("*")

    assert path.update({"a": 1, "b": 2}, 0) == {"a": 0, "b": 0}
    assert path.update([1, 2], 0) == [0, 0]
    assert path.filter(lambda value: value > 1, {"a": 1, "b": 2}) == {"a": 1}


def test_deprecated_fields_star_text_form_still_means_wildcard():
    with pytest.warns(DeprecationWarning):
        path = Fields("*")

    assert str(path) == "*"


def test_parsing_never_triggers_the_fields_star_deprecation(recwarn):
    for expression in ("$.*", "$[*]", "$..*", "$['*']", "$.'*'", "$['*','b']"):
        jsonpath_ng.parse(expression).find({"*": 1, "b": 2})
        jsonpath_ng.ext.parse(expression).find({"*": 1, "b": 2})

    assert not recwarn.list


def test_a_data_key_named_star_never_triggers_the_deprecation(recwarn):
    data = {"*": 1, "a": {"*": 2}}

    jsonpath_ng.parse("$..*").find(data)
    jsonpath_ng.ext.parse("$[?@.*]").find({"x": {"*": 1}})
    jsonpath_ng.ext.parse("$[?@ > 0]").find(data)
    jsonpath_ng.parse("$..a").find(data)

    assert not recwarn.list


@pytest.mark.xfail(strict=True, reason="These attributes should be deleted in v2")
@pytest.mark.parametrize(
    "attribute",
    ("_compliant_constructor", "_deprecated_wildcard_use"),
)
def test_fields_attributes(attribute):
    assert not hasattr(Fields("x"), attribute)
