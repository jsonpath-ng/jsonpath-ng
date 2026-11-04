Fixed
-----

*   Fix empty slices acting like wildcards by selecting member values of objects.

    RFC 9535 says that a slice selects nothing from a value that is not an array.
    Given ``{"x": 1, "y": 2}``, ``parse("$[:]").find(data)`` now correctly returns ``[]``.
    The same applies to updating and filtering.

    Use ``[*]`` to select the members of an object.

    This may break code that relied on ``[:]`` or ``[::]`` selecting object members.

Deprecated
----------

*   Deprecate interpreting ``Slice()`` with no parameters as a wildcard.

    ``Slice()`` will continue to incorrectly select member values of an object,
    but in version 2.0.0 it will select nothing from an object.

    Replace usages with ``Wildcard()``.
