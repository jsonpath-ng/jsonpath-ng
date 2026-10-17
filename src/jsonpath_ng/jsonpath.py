from __future__ import annotations

import logging
import re
import typing

from jsonpath_ng.exceptions import JSONPathError

# Get logger name
logger = logging.getLogger(__name__)

# Turn on/off the automatic creation of id attributes
# ... could be a kwarg pervasively but uses are rare and simple today
auto_id_field: str | None = None

NOT_SET = object()
LIST_KEY = object()


Container: typing.TypeAlias = dict[typing.Any, typing.Any] | list[typing.Any]
FilterFunction: typing.TypeAlias = typing.Callable[[Container], bool]


class JSONPath:
    """
    The base class for JSONPath abstract syntax; those
    methods stubbed here are the interface to supported
    JSONPath semantics.
    """

    def find(self, data: typing.Any) -> list[DatumInContext]:
        """
        All `JSONPath` types support `find()`,
        which returns an iterable of `DatumInContext`s.
        They keep track of the path followed to the current location,
        so if the calling code has some opinion about that,
        it can be passed in here as a starting point.
        """
        raise NotImplementedError()

    def find_or_create(self, data: typing.Any) -> list[DatumInContext]:
        return self.find(data)

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        """
        Returns `data` with the specified path replaced by `val`. Only updates
        if the specified path exists.
        """

        raise NotImplementedError()

    def update_or_create(self, data: typing.Any, val: typing.Any) -> typing.Any:
        return self.update(data, val)

    def filter(self, fn: FilterFunction, data: Container) -> Container | None:
        """
        Returns `data` with the specified path filtering nodes according
        the filter evaluation result returned by the filter function.

        Arguments:
            fn (function): unary function that accepts one argument
                and returns bool.
            data (dict|list|tuple): JSON object to filter.
        """

        raise NotImplementedError()

    def child(self, child: JSONPath) -> JSONPath:
        """
        Equivalent to Child(self, next) but with some canonicalization
        """
        if isinstance(self, This) or isinstance(self, Root):
            return child
        elif isinstance(child, This):
            return self
        elif isinstance(child, Root):
            return child
        else:
            return Child(self, child)

    def make_datum(self, value: DatumInContext | typing.Any) -> DatumInContext:
        if isinstance(value, DatumInContext):
            return value
        else:
            return DatumInContext(value, path=Root(), context=None)


class DatumInContext:
    """
    Represents a datum along a path from a context.

    Essentially a zipper but with a structure represented by JsonPath,
    and where the context is more of a parent pointer than a proper
    representation of the context.

    For quick-and-dirty work, this proxies any non-special attributes
    to the underlying datum, but the actual datum can (and usually should)
    be retrieved via the `value` attribute.

    To place `datum` within another, use `datum.in_context(context=..., path=...)`
    which extends the path. If the datum already has a context, it places the entire
    context within that passed in, so an object can be built from the inside
    out.
    """

    @classmethod
    def wrap(cls, data: typing.Any) -> DatumInContext:
        if isinstance(data, cls):
            return data
        else:
            return cls(data)

    def __init__(
        self,
        value: typing.Any,
        path: JSONPath | None = None,
        context: DatumInContext | typing.Any | None = None,
    ) -> None:
        self.__value__ = value
        self.path = path or This()
        # This is a hot path, so avoid the overhead of calling `wrap()`.
        if context is not None and not isinstance(context, DatumInContext):
            context = DatumInContext(context)
        self.context: DatumInContext | None = context

    @property
    def value(self) -> typing.Any:
        return self.__value__

    @value.setter
    def value(self, value: typing.Any) -> None:
        if self.context is not None and self.context.value is not None:
            self.path.update(self.context.value, value)
        self.__value__ = value

    def in_context(self, context: typing.Any, path: JSONPath) -> DatumInContext:
        context = DatumInContext.wrap(context)

        if self.context:
            return DatumInContext(
                value=self.value,
                path=self.path,
                context=context.in_context(path=path, context=context),
            )
        else:
            return DatumInContext(value=self.value, path=path, context=context)

    @property
    def full_path(self) -> JSONPath:
        return (
            self.path
            if self.context is None
            else self.context.full_path.child(self.path)
        )

    @property
    def id_pseudopath(self) -> JSONPath:
        """
        Looks like a path, but with ids stuck in when available
        """
        try:
            pseudopath: JSONPath = Fields(str(self.value[auto_id_field]))
        except (
            TypeError,
            AttributeError,
            KeyError,
        ):  # This may not be all the interesting exceptions
            pseudopath = self.path

        if self.context:
            return self.context.id_pseudopath.child(pseudopath)
        else:
            return pseudopath

    def __repr__(self) -> str:
        return "{}(value={!r}, path={!r}, context={!r})".format(
            self.__class__.__name__, self.value, self.path, self.context
        )

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, DatumInContext)
            and other.value == self.value
            and other.path == self.path
            and self.context == other.context
        )


class AutoIdForDatum(DatumInContext):
    """
    This behaves like a DatumInContext, but the value is
    always the path leading up to it, not including the "id",
    and with any "id" fields along the way replacing the prior
    segment of the path

    For example, it will make "foo.bar.id" return a datum
    that behaves like DatumInContext(value="foo.bar", path="foo.bar.id").

    This is disabled by default; it can be turned on by
    settings the `auto_id_field` global to a value other
    than `None`.
    """

    def __init__(self, datum: DatumInContext, id_field: str | None = None) -> None:
        """
        Invariant is that datum.path is the path from context to datum. The auto id
        will either be the id in the datum (if present) or the id of the context
        followed by the path to the datum.

        The path to this datum is always the path to the context, the path to the
        datum, and then the auto id field.
        """
        self.datum = datum
        self.id_field = id_field or auto_id_field

    @property
    def value(self) -> str:
        return str(self.datum.id_pseudopath)

    @value.setter
    def value(self, value: typing.Any) -> typing.Never:
        raise JSONPathError("The value of an auto ID cannot be set.")

    @property
    def path(self) -> str | None:  # type: ignore[override]
        return self.id_field

    @property
    def context(self) -> DatumInContext:  # type: ignore[override]
        return self.datum

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.datum!r})"

    def in_context(self, context: typing.Any, path: JSONPath) -> AutoIdForDatum:
        return AutoIdForDatum(self.datum.in_context(context=context, path=path))

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, AutoIdForDatum)
            and other.datum == self.datum
            and self.id_field == other.id_field
        )


class Root(JSONPath):
    """
    The JSONPath referring to the "root" object. Concrete syntax is '$'.
    The root is the topmost datum without any context attached.
    """

    def find(self, data: DatumInContext | typing.Any) -> list[DatumInContext]:
        if not isinstance(data, DatumInContext):
            return [DatumInContext(data, path=Root(), context=None)]
        else:
            if data.context is None:
                return [DatumInContext(data.value, context=None, path=Root())]
            else:
                return Root().find(data.context)

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        return val

    def filter(self, fn: FilterFunction, data: Container) -> Container | None:
        return data if fn(data) else None

    def __str__(self) -> str:
        return "$"

    def __repr__(self) -> str:
        return "Root()"

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Root)

    def __hash__(self) -> int:
        return hash("$")


class This(JSONPath):
    """
    The JSONPath referring to the current datum. Concrete syntax is '@'.
    """

    def find(self, datum: typing.Any) -> list[DatumInContext]:
        return [DatumInContext.wrap(datum)]

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        return val

    def filter(self, fn: FilterFunction, data: Container) -> Container | None:
        return data if fn(data) else None

    def __str__(self) -> str:
        return "`this`"

    def __repr__(self) -> str:
        return "This()"

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, This)

    def __hash__(self) -> int:
        return hash("this")


class Child(JSONPath):
    """
    JSONPath that first matches the left, then the right.
    Concrete syntax is <left> '.' <right>
    """

    def __init__(self, left: JSONPath, right: JSONPath) -> None:
        self.left = left
        self.right = right

    def find(self, datum: typing.Any) -> list[DatumInContext]:
        """
        Extra special case: auto ids do not have children,
        so cut it off right now rather than auto id the auto id
        """

        return [
            submatch
            for subdata in self.left.find(datum)
            if not isinstance(subdata, AutoIdForDatum)
            for submatch in self.right.find(subdata)
        ]

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        for datum in self.left.find(data):
            self.right.update(datum.value, val)
        return data

    def find_or_create(self, datum: typing.Any) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        submatches = []
        for subdata in self.left.find_or_create(datum):
            if isinstance(subdata, AutoIdForDatum):
                # Extra special case: auto ids do not have children,
                # so cut it off right now rather than auto id the auto id
                continue
            for submatch in self.right.find_or_create(subdata):
                submatches.append(submatch)
        return submatches

    def update_or_create(self, data: typing.Any, val: typing.Any) -> typing.Any:
        for datum in self.left.find_or_create(data):
            self.right.update_or_create(datum.value, val)
        return _clean_list_keys(data)

    def filter(self, fn: FilterFunction, data: Container) -> Container | None:
        for datum in self.left.find(data):
            self.right.filter(fn, datum.value)
        return data

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Child)
            and self.left == other.left
            and self.right == other.right
        )

    def __str__(self) -> str:
        # Special case: If the right side is a `SortedThis` instance,
        # do not inject a period between the left and right sides.
        # Adding a period would corrupt the syntax and prevent re-parsing.
        # Current module design creates circular imports, so imports happen here.
        from .ext.iterable import SortedThis

        if isinstance(self.right, SortedThis):
            return f"{self.left}{self.right}"

        return f"{self.left}.{self.right}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left!r}, {self.right!r})"

    def __hash__(self) -> int:
        return hash((self.left, self.right))


class Parent(JSONPath):
    """
    JSONPath that matches the parent node of the current match.
    Will crash if no such parent exists.
    Available via named operator `parent`.
    """

    def find(self, datum: DatumInContext) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        context = datum.context
        assert context is not None
        return [context]

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Parent)

    def __str__(self) -> str:
        return "`parent`"

    def __repr__(self) -> str:
        return "Parent()"

    def __hash__(self) -> int:
        return hash("parent")


class Where(JSONPath):
    """
    JSONPath that first matches the left, and then
    filters for only those nodes that have
    a match on the right.

    WARNING: Subject to change. May want to have "contains"
    or some other better word for it.
    """

    def __init__(self, left: JSONPath, right: JSONPath) -> None:
        self.left = left
        self.right = right

    def find(self, data: typing.Any) -> list[DatumInContext]:
        return [subdata for subdata in self.left.find(data) if self.right.find(subdata)]

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        for datum in self.find(data):
            datum.path.update(data, val)
        return data

    def filter(self, fn: FilterFunction, data: Container) -> Container | None:
        for datum in self.find(data):
            datum.path.filter(fn, datum.value)
        return data

    def __str__(self) -> str:
        return f"{self.left} where {self.right}"

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Where)
            and other.left == self.left
            and other.right == self.right
        )

    def __hash__(self) -> int:
        return hash((self.left, self.right))


class WhereNot(Where):
    """
    Identical to ``Where``, but filters for only those nodes that
    do *not* have a match on the right.

    >>> jsonpath = WhereNot(Fields('spam'), Fields('spam'))
    >>> jsonpath.find({"spam": {"spam": 1}})
    []
    >>> matches = jsonpath.find({"spam": 1})
    >>> matches[0].value
    1

    """

    def find(self, data: typing.Any) -> list[DatumInContext]:
        return [
            subdata for subdata in self.left.find(data) if not self.right.find(subdata)
        ]

    def __str__(self) -> str:
        return f"{self.left} wherenot {self.right}"

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, WhereNot)
            and other.left == self.left
            and other.right == self.right
        )

    def __hash__(self) -> int:
        return hash((self.left, self.right))


class Descendants(JSONPath):
    """
    JSONPath that matches first the left expression then any descendant
    of it which matches the right expression.
    """

    def __init__(self, left: JSONPath, right: JSONPath) -> None:
        self.left = left
        self.right = right

    def find(self, datum: typing.Any) -> list[DatumInContext]:
        # <left> .. <right> ==> <left> . (<right> | *..<right> | [*]..<right>)
        #
        # This walks the data directly instead of delegating to that equivalence.

        # Get all left matches into a list.
        # Some `find()` implementations (e.g. `Filter`, `SortedThis`)
        # return a bare datum instead of a list, so this is typed as `Any`.
        left_matches: typing.Any = self.left.find(datum)

        # TODO: Remove this condition once all `find()` methods return lists.
        if not isinstance(left_matches, list):
            left_matches = [left_matches]

        # Walk the data depth-first and in pre-order using an explicit stack.
        # The next datum to visit is at the end of the list (which is cheap to pop),
        # so children are pushed in reverse to be visited in their natural order.
        right_find = self.right.find
        matches: list[DatumInContext] = []
        stack = left_matches[::-1]
        while stack:
            datum = stack.pop()
            matches.extend(right_find(datum))

            value = datum.value
            if isinstance(value, list):
                children = [
                    DatumInContext(child, context=datum, path=Index(i))
                    for i, child in enumerate(value)
                ]
                children.reverse()
                stack.extend(children)
            elif isinstance(value, dict):
                stack.extend(
                    DatumInContext(child, context=datum, path=Fields(field))
                    for field, child in reversed(value.items())
                )

        return matches

    def is_singular(self) -> typing.Literal[False]:
        return False

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        # Get all left matches into a list.
        # Some `find()` implementations (e.g. `Filter`, `SortedThis`)
        # return a bare datum instead of a list, so this is typed as `Any`.
        left_matches: typing.Any = self.left.find(data)

        # TODO: Remove this condition once all `find()` methods return lists.
        if not isinstance(left_matches, list):
            left_matches = [left_matches]

        # Walk the data depth-first and in pre-order using an explicit stack.
        # Children are pushed in reverse to be visited in their natural order.
        stack = [submatch.value for submatch in reversed(left_matches)]
        while stack:
            node = stack.pop()

            # Update only mutable values corresponding to JSON types.
            if not isinstance(node, (list, dict)):
                continue

            self.right.update(node, val)

            # Manually visit every child and recurse just the right-hand pattern.
            # The children are read after the update, which may have changed them.
            stack.extend(reversed(node if isinstance(node, list) else node.values()))

        return data

    def filter(self, fn: FilterFunction, data: Container) -> Container | None:
        # Get all left matches into a list.
        # Some `find()` implementations (e.g. `Filter`, `SortedThis`)
        # return a bare datum instead of a list, so this is typed as `Any`.
        left_matches: typing.Any = self.left.find(data)

        # TODO: Remove this condition once all `find()` methods return lists.
        if not isinstance(left_matches, list):
            left_matches = [left_matches]

        stack = [submatch.value for submatch in reversed(left_matches)]
        while stack:
            node = stack.pop()

            # Filter only mutable values corresponding to JSON types.
            if not isinstance(node, (list, dict)):
                continue

            self.right.filter(fn, node)

            # The children are read after the filter, which may have removed some.
            stack.extend(reversed(node if isinstance(node, list) else node.values()))

        return data

    def __str__(self) -> str:
        return f"({self.left}..{self.right})"

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Descendants)
            and self.left == other.left
            and self.right == other.right
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left!r}, {self.right!r})"

    def __hash__(self) -> int:
        return hash((self.left, self.right))


class Union(JSONPath):
    """
    JSONPath that returns the union of the results of each match.
    This is pretty shoddily implemented for now. The nicest semantics
    in case of mismatched bits (list vs atomic) is to put
    them all in a list, but I haven't done that yet.

    WARNING: Any appearance of this being the _concatenation_ is
    coincidence. It may even be a bug! (or laziness)
    """

    def __init__(self, left: JSONPath, right: JSONPath) -> None:
        self.left = left
        self.right = right

    def is_singular(self) -> typing.Literal[False]:
        return False

    def find(self, data: typing.Any) -> list[DatumInContext]:
        return self.left.find(data) + self.right.find(data)

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Union)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self) -> int:
        return hash((self.left, self.right))

    def __repr__(self) -> str:
        return f"Union({self.left} | {self.right})"

    def __str__(self) -> str:
        return f"{self.left} | {self.right}"


class Intersect(JSONPath):
    """
    JSONPath for bits that match *both* patterns.

    This can be accomplished a couple of ways. The most
    efficient is to actually build the intersected
    AST as in building a state machine for matching the
    intersection of regular languages. The next
    idea is to build a filtered data and match against
    that.
    """

    def __init__(self, left: JSONPath, right: JSONPath) -> None:
        self.left = left
        self.right = right

    def is_singular(self) -> typing.Literal[False]:
        return False

    def find(self, data: typing.Any) -> list[DatumInContext]:
        raise NotImplementedError()

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Intersect)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self) -> int:
        return hash((self.left, self.right))

    def __repr__(self) -> str:
        return f"Intersect({self.left} & {self.right})"

    def __str__(self) -> str:
        return f"{self.left} & {self.right}"


class Fields(JSONPath):
    """
    JSONPath referring to some field of the current object.
    Concrete syntax ix comma-separated field names.

    WARNING: If '*' is any of the field names, then they will
    all be returned.
    The wildcard also selects all of the elements of an array.
    """

    def __init__(self, *fields: str) -> None:
        self.fields = fields

    def _is_wildcard_on_array(self, value: typing.Any) -> bool:
        return "*" in self.fields and isinstance(value, (list, tuple))

    @staticmethod
    def get_field_datum(
        datum: DatumInContext, field: str, create: bool
    ) -> DatumInContext | None:
        if field == auto_id_field:
            return AutoIdForDatum(datum)
        try:
            field_value = datum.value.get(field, NOT_SET)
            if field_value is NOT_SET:
                if create:
                    datum.value[field] = field_value = {}
                else:
                    return None
            return DatumInContext(field_value, path=Fields(field), context=datum)
        except (TypeError, AttributeError):
            return None

    def reified_fields(self, datum: DatumInContext) -> tuple[str, ...]:
        if "*" not in self.fields:
            return self.fields
        else:
            try:
                fields = tuple(datum.value.keys())
                return fields if auto_id_field is None else fields + (auto_id_field,)
            except AttributeError:
                return ()

    def find(self, datum: typing.Any) -> list[DatumInContext]:
        return self._find_base(datum, create=False)

    def find_or_create(self, datum: typing.Any) -> list[DatumInContext]:
        return self._find_base(datum, create=True)

    def _find_base(self, datum: typing.Any, create: bool) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        if self._is_wildcard_on_array(datum.value):
            return Slice().find(datum)
        field_data = [
            self.get_field_datum(datum, field, create)
            for field in self.reified_fields(datum)
        ]
        return [fd for fd in field_data if fd is not None]

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        if "*" in self.fields and isinstance(data, list):
            return Slice().update(data, val)
        if not hasattr(data, "get"):
            return data
        return self._update_base(data, val, create=False)

    def update_or_create(self, data: typing.Any, val: typing.Any) -> typing.Any:
        return self._update_base(data, val, create=True)

    def _update_base(
        self, data: typing.Any, val: typing.Any, create: bool
    ) -> typing.Any:
        if data is not None:
            for field in self.reified_fields(DatumInContext.wrap(data)):
                if create and field not in data:
                    data[field] = {}
                if type(data) is not bool and field in data:
                    if callable(val):
                        val_result = val(data[field], data, field)
                        if val_result is not None:
                            data[field] = val_result
                    else:
                        data[field] = val
        return data

    def filter(self, fn: FilterFunction, data: Container) -> Container:
        if "*" in self.fields and isinstance(data, list):
            return Slice().filter(fn, data)
        if data is not None and isinstance(data, dict):
            for field in self.reified_fields(DatumInContext.wrap(data)):
                if field in data:
                    if fn(data[field]):
                        data.pop(field)
        return data

    def __str__(self) -> str:
        # Enclose fields in quotes as needed.
        # This is a conservative check, and is biased toward quoting fields.
        rendered_fields: list[str] = []
        for field in self.fields:
            if re.match(r"^[A-Za-z_@][A-Za-z0-9_@-]*$", field):
                rendered_fields.append(field)
            else:
                rendered_fields.append(f"{field!r}")
        return ",".join(rendered_fields)

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__, ",".join(map(repr, self.fields))
        )

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Fields) and tuple(self.fields) == tuple(other.fields)

    def __hash__(self) -> int:
        return hash(tuple(self.fields))


class Index(JSONPath):
    """
    JSONPath that matches indices of the current datum, or none if not large enough.
    Concrete syntax is brackets.

    WARNING: If the datum is None or not long enough,
    it will not crash but will not match anything.
    NOTE: For the concrete syntax of `[*]`,
    the abstract syntax is a Slice() with no parameters (equiv to `[:]`).
    """

    def __init__(self, *indices: int) -> None:
        self.indices = indices

    def find(self, datum: typing.Any) -> list[DatumInContext]:
        return self._find_base(datum, create=False)

    def find_or_create(self, datum: typing.Any) -> list[DatumInContext]:
        return self._find_base(datum, create=True)

    def _find_base(self, datum: typing.Any, create: bool) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)
        if create:
            if datum.value == {}:
                datum.value = _create_list_key(datum.value)
            self._pad_value(datum.value)
        rv: list[DatumInContext] = []
        if not isinstance(datum.value, (list, tuple)):
            # Integer indices only apply to arrays.
            return rv
        for index in self.indices:
            # invalid indices do not crash, return [] instead
            if datum.value and -len(datum.value) <= index < len(datum.value):
                rv += [
                    DatumInContext(datum.value[index], path=Index(index), context=datum)
                ]
        return rv

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        return self._update_base(data, val, create=False)

    def update_or_create(self, data: typing.Any, val: typing.Any) -> typing.Any:
        return self._update_base(data, val, create=True)

    def _update_base(
        self, data: typing.Any, val: typing.Any, create: bool
    ) -> typing.Any:
        if create:
            if data == {}:
                data = _create_list_key(data)
            self._pad_value(data)
        if callable(val):
            for index in self.indices:
                val_result = val(data[index], data, index)
                if val_result is not None:
                    data[index] = val_result
        else:
            for index in self.indices:
                if len(data) > index:
                    try:
                        if isinstance(val, list):
                            # allows somelist[5,1,2] = [
                            #   some_value, another_value, third_value
                            # ]
                            data[index] = val.pop(0)
                        else:
                            data[index] = val
                    except Exception as e:
                        raise e
        return data

    def filter(self, fn: FilterFunction, data: Container) -> Container:
        for index in self.indices:
            if fn(data[index]):
                data.pop(index)  # relies on mutation :(
        return data

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Index) and sorted(self.indices) == sorted(
            other.indices
        )

    def __str__(self) -> str:
        return "[%s]" % ",".join(str(index) for index in self.indices)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(indices={self.indices!r})"

    def _pad_value(self, value: typing.Any) -> None:
        _max = max(self.indices)
        if len(value) <= _max:
            pad = _max - len(value) + 1
            value += [{} for __ in range(pad)]

    def __hash__(self) -> int:
        return hash(self.indices)


class Slice(JSONPath):
    """
    JSONPath matching a slice of an array.

    The wildcard ``[*]`` (a slice with no parameters) matches all the elements
    of an array and all the member values of an object.
    Slices match nothing when applied to a value that is not an array,
    and the wildcard matches nothing when applied to a scalar value.
    """

    def __init__(
        self, start: int | None = None, end: int | None = None, step: int | None = None
    ) -> None:
        self.start = start
        self.end = end
        self.step = step

    def find(self, datum: typing.Any) -> list[DatumInContext]:
        datum = DatumInContext.wrap(datum)

        is_wildcard = self.start is None and self.end is None and self.step is None

        if is_wildcard and isinstance(datum.value, dict):
            return [
                DatumInContext(value, path=Fields(field), context=datum)
                for field, value in datum.value.items()
            ]

        if not isinstance(datum.value, (list, tuple)):
            return []

        if is_wildcard:
            return [
                DatumInContext(child, path=Index(i), context=datum)
                for i, child in enumerate(datum.value)
            ]

        return [
            DatumInContext(datum.value[i], path=Index(i), context=datum)
            for i in range(0, len(datum.value))[self.start : self.end : self.step]
        ]

    def update(self, data: typing.Any, val: typing.Any) -> typing.Any:
        for datum in self.find(data):
            datum.path.update(data, val)
        return data

    def filter(self, fn: FilterFunction, data: Container) -> Container:
        while True:
            length = len(data)
            for datum in self.find(data):
                data = typing.cast(Container, datum.path.filter(fn, data))
                if len(data) < length:
                    break

            if length == len(data):
                break
        return data

    def __str__(self) -> str:
        elements: list[str] = []

        for i, element in enumerate((self.start, self.end, self.step)):
            if element is None:
                continue
            # Ensure that `elements` contains `i` elements, then append `element`.
            elements.extend([""] * (i - len(elements)))
            elements.append(str(element))

        # If only `start` is present, add a blank element to ensure a trailing ':'.
        if len(elements) == 1:
            elements.append("")

        return f"[{':'.join(elements) or '*'}]"

    def __repr__(self) -> str:
        return "{}(start={!r},end={!r},step={!r})".format(
            self.__class__.__name__, self.start, self.end, self.step
        )

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Slice)
            and other.start == self.start
            and self.end == other.end
            and other.step == self.step
        )

    def __hash__(self) -> int:
        return hash((self.start, self.end, self.step))


def _create_list_key(
    dict_: dict[typing.Any, typing.Any],
) -> list[dict[str, typing.Any]]:
    """
    Adds a list to a dictionary by reference and returns the list.

    See `_clean_list_keys()`
    """
    new_list: list[dict[str, typing.Any]] = [{}]
    dict_[LIST_KEY] = new_list
    return new_list


def _clean_list_keys(struct_: Container) -> Container:
    """
    Replace {LIST_KEY: ['foo', 'bar']} with ['foo', 'bar'].

    >>> _clean_list_keys({LIST_KEY: ['foo', 'bar']})
    ['foo', 'bar']

    """
    if isinstance(struct_, list):
        for ind, value in enumerate(struct_):
            struct_[ind] = _clean_list_keys(value)
    elif isinstance(struct_, dict):
        if LIST_KEY in struct_:
            return _clean_list_keys(struct_[LIST_KEY])
        else:
            for key, value in struct_.items():
                struct_[key] = _clean_list_keys(value)
    return struct_
