Fixed
-----

*   Fix ``Filter.update()`` ignoring objects' member values.

    Filters like ``$[?@.score >= 85]`` now update matching member values of objects,
    which matches ``.find()`` and ``.filter()`` behavior.
