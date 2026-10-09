Deprecated
----------

*   Deprecate the ``jsonpath_ng.__version__`` attribute.

    It will be removed in version 2.0.0.

    Importing modules to check their versions is considered bad practice
    because it executes package code on your system.

    Replace usages with ``importlib.metadata.version("jsonpath-ng")``.
