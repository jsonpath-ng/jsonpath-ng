Type annotation tests
=====================

These tests verify the correctness of type annotations.

*   Positive tests have no ``type: ignore`` comments.
*   Negative tests must have a ``# type: ignore[error-code]`` comment.
    If the line stops being an error, the ignore becomes unused,
    and mypy catches this because ``warn_unused_ignores`` is enabled
    (via ``strict`` mode).
*   ``typing.assert_type()`` confirms the type that mypy infers.

Examples:

..  code-block:: python

    import typing as t

    from jsonpath_ng import JSONPath
    from jsonpath_ng.parser import parse

    # A positive test for the *string* parameter.
    parse("string")

    # A negative test for the *string* parameter.
    parse({"wrong": "type"})  # type: ignore[arg-type]

    # Confirm the return type.
    t.assert_type(parse("string"), JSONPath)
