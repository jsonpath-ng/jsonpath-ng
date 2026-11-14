Fixed
-----

*   Fix ``Where.update()`` and ``Where.filter()`` ignoring matches in lists
    and, for ``filter()``, at the top level of the data.

    Expressions like ``foo[*] where baz`` now update and filter the matched nodes,
    which matches ``.find()`` behavior.
