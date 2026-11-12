#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools
import typing as t

from .. import DatumInContext
from .. import JSONPath
from .. import This


class SortedThis(This):
    """The JSONPath referring to the sorted version of the current object.

    Concrete syntax is '`sorted`' or [\\field,/field].
    """

    def __init__(self, expressions: list[tuple[JSONPath, bool]] | None = None) -> None:
        self.expressions = expressions

    def _compare(self, left: t.Any, right: t.Any) -> int:
        left = DatumInContext.wrap(left)
        right = DatumInContext.wrap(right)

        # `_compare()` is only used as a sort key when `expressions` is truthy.
        for expr in self.expressions:  # type: ignore[union-attr]
            field, reverse = expr
            l_datum = field.find(left)
            r_datum = field.find(right)
            if (
                not l_datum
                or not r_datum
                or len(l_datum) > 1
                or len(r_datum) > 1
                or l_datum[0].value == r_datum[0].value
            ):
                # NOTE(sileht): should we do something if the expression
                # match multiple fields, for now ignore them
                continue
            elif l_datum[0].value < r_datum[0].value:
                return 1 if reverse else -1
            else:
                return -1 if reverse else 1
        return 0

    # NOTE: This returns a bare datum, not a list, when nothing is sorted;
    # that contradicts `JSONPath.find()`, hence the `override` suppression.
    def find(  # type: ignore[override]
        self, datum: DatumInContext
    ) -> list[DatumInContext] | DatumInContext:
        """Return sorted value of This if list or dict."""
        if isinstance(datum.value, dict) and self.expressions:
            return datum

        if isinstance(datum.value, dict) or isinstance(datum.value, list):
            key = functools.cmp_to_key(self._compare) if self.expressions else None
            return [
                DatumInContext.wrap([value for value in sorted(datum.value, key=key)])
            ]
        return datum

    def __eq__(self, other: t.Any) -> bool:
        return isinstance(other, SortedThis) and self.expressions == other.expressions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expressions!r})"

    def __str__(self) -> str:
        if not self.expressions:
            return "`sorted`"

        expressions: list[str] = []
        for field, reverse in self.expressions:
            prefix = "\\" if reverse else "/"
            expressions.append(f"{prefix}{field}")
        return f"[{', '.join(expressions)}]"


class Len(JSONPath):
    """The JSONPath referring to the len of the current object.

    Concrete syntax is '`len`'.
    """

    def find(self, datum: t.Any) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        try:
            value = len(datum.value)
        except TypeError:
            return []
        else:
            return [DatumInContext(value, context=None, path=Len())]

    def __eq__(self, other: t.Any) -> bool:
        return isinstance(other, Len)

    def __str__(self) -> str:
        return "`len`"

    def __repr__(self) -> str:
        return "Len()"


class Keys(JSONPath):
    """The JSONPath referring to the keys of the current object.
    Concrete syntax is '`keys`'.
    """

    def find(self, datum: t.Any) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        try:
            value = list(datum.value.keys())
        except Exception:
            return []
        else:
            return [
                DatumInContext(value[i], context=None, path=Keys())
                for i in range(0, len(datum.value))
            ]

    def __eq__(self, other: t.Any) -> bool:
        return isinstance(other, Keys)

    def __str__(self) -> str:
        return "`keys`"

    def __repr__(self) -> str:
        return "Keys()"


class Path(JSONPath):
    """The JSONPath referring to the path of the current object.
    Concrete syntax is 'path`'.
    """

    def find(self, datum: t.Any) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        try:
            value = str(datum.path)
        except Exception:
            return []
        else:
            return [DatumInContext(value, context=datum, path=Path())]

    def __eq__(self, other: t.Any) -> bool:
        return isinstance(other, Path)

    def __str__(self) -> str:
        return "`path`"

    def __repr__(self) -> str:
        return "Path()"
