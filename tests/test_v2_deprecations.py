import pytest

import jsonpath_ng
import jsonpath_ng.ext.parser as parser
from jsonpath_ng.ext.filter import Filter
from jsonpath_ng.jsonpath import Child
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
