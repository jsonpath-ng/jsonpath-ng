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
        ("a.b", "a.b"),
        ("a[b]", "a.b"),
        ("a.b.c", "a.b.c"),
        ("'a.b'.c", "'a.b'.c"),
        ("a.'b.c'", "a.'b.c'"),
        ("a..b[c]", "(a..b).c"),
        ("(a..b)[c]", "(a..b).c"),
        ("(a..b).c", "(a..b).c"),
    ),
)
@parsers
def test_serialization(parse, data, expected_serialization):
    """Test serialization of Child instances.

    Regardless of what the test inputs claim,
    the expected serialization must still parse to the same JSONPath
    that the original data parsed to.
    """

    parsed = parse(data)
    reserialized = str(parsed)

    assert reserialized == expected_serialization

    # Now that the test has succeeded, do an additional sanity check.
    assert parsed == parse(reserialized)
