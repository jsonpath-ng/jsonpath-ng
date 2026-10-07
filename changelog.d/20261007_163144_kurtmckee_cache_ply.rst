Changed
-------

*   Use pre-generated PLY lex/parse tables. (#121)

    This allows downstream projects to run with Python optimizations enabled.

Deprecated
----------

*   The ``debug`` parameter, given when instantiating lexers and parsers,
    is now deprecated and has no effect. It will be removed in version 2.0.0.
