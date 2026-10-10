Fixed
-----

*   Fix a ``TypeError`` crash that can occur when filtering scalar values.

    This can only occur when a ``Filter`` has been instantiated without expressions.
    (This usage is now deprecated.)
