import pytest

import jsonpath_ng.ext.parser as parser


def test_extented_jsonpath_parser_access():
    match = "ExtentedJsonPathParser is a deprecated name"
    with pytest.warns(DeprecationWarning, match=match):
        assert parser.ExtentedJsonPathParser is parser.ExtendedJsonPathParser
