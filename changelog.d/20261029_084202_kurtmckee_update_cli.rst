Changed
-------

*   Relicense the CLI code under the Apache 2.0 license.

    Relicensing is allowed under the terms of the previous license.

*   Make the CLI output matches as valid JSONL.

    Previously the output was simply Python ``repr()`` output,
    so ``{"json": true}`` was output as ``{'json': True}``
    and could not be re-parsed as JSON.

*   Support running the CLI via ``python -m jsonpath_ng``.
