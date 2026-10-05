import pytest

from jsonpath_ng.lexer import JsonPathLexer, JsonPathLexerError

token_test_cases = (
    ("$", (("$", "$"),)),
    ('"hello"', (("hello", "ID"),)),
    ("'goodbye'", (("goodbye", "ID"),)),
    ("'doublequote\"'", (('doublequote"', "ID"),)),
    (r'"doublequote\""', (('doublequote"', "ID"),)),
    (r"'singlequote\''", (("singlequote'", "ID"),)),
    ('"singlequote\'"', (("singlequote'", "ID"),)),
    ("fuzz", (("fuzz", "ID"),)),
    ("1", ((1, "NUMBER"),)),
    ("45", ((45, "NUMBER"),)),
    ("-1", ((-1, "NUMBER"),)),
    (" -13 ", ((-13, "NUMBER"),)),
    ('"fuzz.bang"', (("fuzz.bang", "ID"),)),
    ("fuzz.bang", (("fuzz", "ID"), (".", "."), ("bang", "ID"))),
    ("fuzz.*", (("fuzz", "ID"), (".", "."), ("*", "*"))),
    ("fuzz..bang", (("fuzz", "ID"), ("..", "DOUBLEDOT"), ("bang", "ID"))),
    ("&", (("&", "&"),)),
    ("@", (("@", "ID"),)),
    ("`this`", (("this", "NAMED_OPERATOR"),)),
    ("|", (("|", "|"),)),
    ("where", (("where", "WHERE"),)),
    ("wherenot", (("wherenot", "WHERENOT"),)),
)


@pytest.mark.parametrize("string, expected_token_info", token_test_cases)
def test_lexer(string, expected_token_info):
    lexer = JsonPathLexer(debug=True)
    tokens = list(lexer.tokenize(string))
    assert len(tokens) == len(expected_token_info)
    for token, (expected_value, expected_type) in zip(tokens, expected_token_info):
        assert token.type == expected_type
        assert token.value == expected_value


invalid_token_test_cases = (
    "'\"",
    "\"'",
    '`"',
    "`'",
    '"`',
    "'`",
    "?",
    "$.foo.bar.#",
)


@pytest.mark.parametrize("string", invalid_token_test_cases)
def test_lexer_errors(string):
    with pytest.raises(JsonPathLexerError):
        list(JsonPathLexer().tokenize(string))
