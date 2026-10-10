import pytest

import jsonpath_ng.ext
from tests.helpers import assert_value_equality


@pytest.mark.parametrize(
    "datum, expected_values",
    [
        pytest.param([1, 2, 3], [2, 3], id="list"),
        pytest.param({"a": 1, "b": 2, "c": 3}, [2, 3], id="dict"),
        pytest.param(2, [], id="int"),
        pytest.param("abc", [], id="str"),
        pytest.param(None, [], id="null"),
    ],
)
def test_filter_returns_lists(datum, expected_values):
    """
    Verify that a Filter follows the find() contract and RFC 9535 behavior.

    RFC 9535 section 2.3.5.2 says filter selectors only work with arrays and objects,
    and "applied to a primitive value, it selects nothing".

    The int case uses a value that would satisfy the filter
    if it were (incorrectly) applied to the datum itself.
    """

    path = jsonpath_ng.ext.parse("$[?@ > 1]")

    results = path.find(datum)

    assert isinstance(results, list)
    assert_value_equality(results, expected_values)
