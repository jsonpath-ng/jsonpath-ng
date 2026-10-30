Breaking changes
----------------

*   Parse an unquoted ``*`` to the new ``Wildcard()`` node.

    ``$.*``, ``$[*]``, and ``$..*`` used to parse to ``Fields('*')`` or ``Slice()``.
    Code that compares or inspects these parsed expressions must be updated.
    The results of finding, updating, and filtering are unchanged.

    This change can only affect code that first parses a JSONPath string
    containing an unquoted wildcard character (``*``)
    and then interacts with the resulting AST.

Added
-----

*   Add a ``Wildcard`` node that selects every child of an object or array.

Fixed
-----

*   Treat a quoted ``*`` as a field name, not as a wildcard.

    Given an object like ``{"*": "multiply", "/": "divide"}``,
    ``parse("$['*']").find(data)`` will now correctly return only ``["multiply"]``.

Deprecated
----------

*   Deprecate interpreting ``Fields('*')`` as a wildcard.

    ``Fields('*')`` still selects every child, but in version 2.0.0
    it will select only the field named ``*``.

    Replace usages with ``Wildcard()``.
