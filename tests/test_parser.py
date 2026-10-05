import pytest

from jsonpath_ng.jsonpath import Child, Descendants, Fields, Index, Slice, Where, WhereNot
from jsonpath_ng.lexer import JsonPathLexer
from jsonpath_ng.parser import JsonPathParser

# Format: (string, expected_object)
parser_test_cases = (
    #
    # Atomic
    # ------
    #
    ("😀", Fields("😀")),
    ("你好", Fields("你好")),
    ("foo", Fields("foo")),
    ("*", Fields("*")),
    ("1", Fields("1")),
    ("baz,bizzle", Fields("baz", "bizzle")),
    ("[1]", Index(1)),
    ("[1:]", Slice(start=1)),
    ("[:]", Slice()),
    ("[*]", Slice()),
    ("[:2]", Slice(end=2)),
    ("[1:2]", Slice(start=1, end=2)),
    ("[5:-2]", Slice(start=5, end=-2)),
    #
    # Nested
    # ------
    #
    ("foo.baz", Child(Fields("foo"), Fields("baz"))),
    ("foo.baz,bizzle", Child(Fields("foo"), Fields("baz", "bizzle"))),
    ("foo where baz", Where(Fields("foo"), Fields("baz"))),
    ("foo wherenot baz", WhereNot(Fields("foo"), Fields("baz"))),
    ("foo..baz", Descendants(Fields("foo"), Fields("baz"))),
    ("foo..baz.bing", Descendants(Fields("foo"), Child(Fields("baz"), Fields("bing")))),
)


@pytest.mark.parametrize("string, expected_object", parser_test_cases)
def test_parser(string, expected_object):
    parser = JsonPathParser(lexer_class=lambda: JsonPathLexer())
    assert parser.parse(string) == expected_object
