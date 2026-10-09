import pytest

import jsonpath_ng
import jsonpath_ng.ext.parser as parser


def test_extented_jsonpath_parser_access():
    match = "ExtentedJsonPathParser is a deprecated name"
    with pytest.warns(DeprecationWarning, match=match):
        assert parser.ExtentedJsonPathParser is parser.ExtendedJsonPathParser


def test_version_attribute_is_deprecated():
    match = "The `__version__` attribute is deprecated"
    with pytest.warns(DeprecationWarning, match=match):
        assert jsonpath_ng.__version__[0] == "1"
