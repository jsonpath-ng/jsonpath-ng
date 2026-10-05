import pytest

import jsonpath_ng.ext


parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)


@pytest.mark.parametrize(
    "data, expected_serialization",
    (
        ("a..b", "(a..b)"),  # Not ideal
        # This is not an ideal serialization,
        # nor is it consistent with the precedence rules of 'a..b[c]', below.
        ("a..b.c", "(a..b.c)"),
        ("a..b[c]", "(a..b).c"),
    ),
)
@parsers
def test_serialization(parse, data, expected_serialization):
    """Test serialization of Descendant instances.

    Regardless of what the test inputs claim,
    the expected serialization must still parse to the same JSONPath
    that the original data parsed to.
    """

    parsed = parse(data)
    reserialized = str(parsed)

    assert reserialized == expected_serialization

    # Now that the test has succeeded, do an additional sanity check.
    assert parsed == parse(reserialized)


def test_find_recursive_wildcard():
    data = {"a": ["foo", "bar"]}

    matches = jsonpath_ng.parse("$..[*]").find(data)

    assert [(str(match.full_path), match.value) for match in matches] == [
        ("a.[0]", "foo"),
        ("a.[1]", "bar"),
    ]
    for match in matches:
        assert jsonpath_ng.parse(str(match.full_path)).find(data)[0].value == match.value
