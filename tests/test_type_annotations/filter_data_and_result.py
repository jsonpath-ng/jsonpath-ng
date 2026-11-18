"""
Verify ``JSONPath.filter()`` accepts any JSON value as data and returns ``Any``.

This covers ``filter()`` and every override of it,
for both the ``data`` argument and the return value.

The ``data`` argument is typed ``Any`` because it can be any JSON value,
not only a dict or a list.
The return value is typed ``Any`` because no narrower type
is accurate for every JSON value.

Each kind of JSONPath node overrides ``filter()`` with its own signature,
and any one of those signatures can regress independently of the others.
These tests therefore cover:

*   The base class, called through the result of ``parse()``,
    which accepts every kind of JSON value as ``data``.
*   Every node class, which must accept a JSON value and return ``Any``.
*   ``None`` as ``data``, which is a valid JSON value
    and must be accepted by the subclasses, not only the base class.

The ``fn`` argument is covered by ``filter_function.py``.
"""

import typing as t

from jsonpath_ng import Child
from jsonpath_ng import Descendants
from jsonpath_ng import Fields
from jsonpath_ng import Index
from jsonpath_ng import Root
from jsonpath_ng import Slice
from jsonpath_ng import This
from jsonpath_ng import Where
from jsonpath_ng import Wildcard
from jsonpath_ng.ext.filter import Filter
from jsonpath_ng.parser import parse


def keep(value: t.Any) -> bool:
    return True


expression = parse("$.a[*]")

# The data can be a dict or a list...
expression.filter(keep, {"a": [1, 2]})
expression.filter(keep, [1, 2])
# ...or any other JSON value.
expression.filter(keep, "text")
expression.filter(keep, 5)
expression.filter(keep, 1.5)
expression.filter(keep, True)
expression.filter(keep, None)

# Every kind of path accepts any JSON value and returns `Any`.
t.assert_type(expression.filter(keep, 5), t.Any)
t.assert_type(Root().filter(keep, 5), t.Any)
t.assert_type(This().filter(keep, 5), t.Any)
t.assert_type(Child(Root(), Fields("a")).filter(keep, 5), t.Any)
t.assert_type(Where(Fields("a"), Fields("b")).filter(keep, 5), t.Any)
t.assert_type(Descendants(Root(), Fields("a")).filter(keep, 5), t.Any)
t.assert_type(Fields("a").filter(keep, 5), t.Any)
t.assert_type(Wildcard().filter(keep, 5), t.Any)
t.assert_type(Index(0).filter(keep, 5), t.Any)
t.assert_type(Slice(0, 1).filter(keep, 5), t.Any)
t.assert_type(Filter([This()]).filter(keep, 5), t.Any)

# `None` is also a JSON value, and not only for the base class.
t.assert_type(Fields("a").filter(keep, None), t.Any)
t.assert_type(Wildcard().filter(keep, None), t.Any)
t.assert_type(Index(0).filter(keep, None), t.Any)
t.assert_type(Slice(0, 1).filter(keep, None), t.Any)
t.assert_type(Filter([This()]).filter(keep, None), t.Any)
