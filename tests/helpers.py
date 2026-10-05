def assert_value_equality(results, expected_values):
    """Assert equality between two objects.

    *results* must be a list of results as returned by `.find()` methods.

    If *expected_values* is a list, then value equality and ordering will be checked.
    If *expected_values* is a set, value equality and container length will be checked.
    Otherwise, the value of the results will be compared to the expected values.
    """

    left_values = [result.value for result in results]
    if isinstance(expected_values, list):
        assert left_values == expected_values, f"{left_values!r} != {expected_values!r}"
    elif isinstance(expected_values, set):
        assert len(left_values) == len(expected_values)
        assert set(left_values) == expected_values, f"{left_values!r} != {expected_values!r}"
    else:
        assert results[0].value == expected_values


def assert_full_path_equality(results, expected_full_paths):
    """Assert equality between two objects.

    *results* must be a list or set of results as returned by `.find()` methods.

    If *expected_full_paths* is a list, then path equality and ordering will be checked.
    If *expected_full_paths* is a set, then path equality and length will be checked.
    """

    full_paths = [str(result.full_path) for result in results]
    if isinstance(expected_full_paths, list):
        assert full_paths == expected_full_paths, full_paths
    else:  # isinstance(expected_full_paths, set):
        assert len(full_paths) == len(expected_full_paths)
        assert set(full_paths) == expected_full_paths
