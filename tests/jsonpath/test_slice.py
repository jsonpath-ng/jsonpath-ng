import pytest

import jsonpath_ng
import jsonpath_ng.ext


parsers = pytest.mark.parametrize(
    "parse",
    (jsonpath_ng.parse, jsonpath_ng.ext.parse),
    ids=lambda function: function.__module__,
)


@pytest.mark.parametrize(
    "data, expected_start, expected_end, expected_step",
    (
        # Special case
        pytest.param("[*]", None, None, None, id="wildcard"),
        # Individual elements
        pytest.param("[0:]", 0, None, None, id="start-false-y"),
        pytest.param("[1:]", 1, None, None, id="start-1"),
        pytest.param("[:0]", None, 0, None, id="end-false-y"),
        pytest.param("[:1]", None, 1, None, id="end-1"),
        pytest.param("[::0]", None, None, 0, id="step-nonsense"),
        pytest.param("[::1]", None, None, 1, id="step-default"),
        pytest.param("[::2]", None, None, 2, id="step-2"),
        # Paired elements
        pytest.param("[1:2]", 1, 2, None, id="start-and-end"),
        pytest.param("[:1:2]", None, 1, 2, id="end-and-step"),
        pytest.param("[1::2]", 1, None, 2, id="start-and-step"),
        # All elements
        pytest.param("[1:2:3]", 1, 2, 3, id="all-elements"),
    )
)
@parsers
def test_slice(parse, data, expected_start, expected_end, expected_step):
    instance = parse(data)

    assert isinstance(instance, jsonpath_ng.Slice)
    assert instance.start == expected_start
    assert instance.end == expected_end
    assert instance.step == expected_step

    assert str(instance) == data
