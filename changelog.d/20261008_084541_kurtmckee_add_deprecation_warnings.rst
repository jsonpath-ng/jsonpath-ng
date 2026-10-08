Deprecated
----------

*   Deprecate accessing the extended parser by its old name.

    In v1.8.0, ``ExtentedJsonPathParser`` was renamed to ``ExtendedJsonPathParser``
    but the old name was kept around for backwards compatibility.

    Accessing it using the old name now throws a ``DeprecationWarning``.
    The old name will be removed in version 2.0.0.
