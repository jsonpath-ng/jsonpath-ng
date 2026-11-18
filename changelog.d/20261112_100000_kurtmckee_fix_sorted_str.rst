Fixed
-----

*   Fix ``str()`` raising ``TypeError`` for queries that use the ``sorted`` operator.

    Queries like ``$.a.`sorted``` can now be converted to strings and re-parsed.
