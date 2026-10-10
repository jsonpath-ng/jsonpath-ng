Deprecated
----------

*   Deprecate instantiating ``Filter`` with no expressions.

    It is impossible to encounter this deprecation via a parsed JSONPath string.

    This deprecation helps align programmatic usage with RFC 9535,
    which doesn't syntactically support filters without expressions.

    This usage will raise an exception in version 2.0.0.
