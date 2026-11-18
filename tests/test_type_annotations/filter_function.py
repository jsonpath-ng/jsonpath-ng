"""
Verify ``JSONPath.filter()`` accepts filter functions with a specific value type.

This file covers the ``fn`` argument of ``filter()``
and the ``FilterFunction`` alias that annotates it.

A filter function can receive any JSON value, not only a dict or a list,
so it must be able to declare the type that it expects.
These tests therefore cover:

*   Functions that declare a specific type, ``object``, or ``Any``,
    which are accepted.
*   An unannotated lambda, which is accepted
    and is not given a restrictive parameter type.
*   Using ``FilterFunction`` to annotate a variable.
*   Callables that are not filter functions, which are rejected:
    those that do not return a bool, do not accept exactly one argument,
    or are not callable.

The ``data`` argument and the return value of ``filter()``
are covered by ``filter_data_and_result.py``.
"""

import typing as t

from jsonpath_ng.jsonpath import FilterFunction
from jsonpath_ng.parser import parse

data = {"a": [1, 2, 3, 4]}
expression = parse("$.a[*]")


def is_even(value: int) -> bool:
    return value % 2 == 0


def is_short(value: str) -> bool:
    return len(value) < 3


def is_anything(value: object) -> bool:
    return True


def takes_any(value: t.Any) -> bool:
    return bool(value)


# A filter function that declares the type of value it expects is accepted.
expression.filter(is_even, data)
expression.filter(is_short, data)
expression.filter(is_anything, data)
expression.filter(takes_any, data)

# An unannotated lambda is not given a restrictive parameter type.
# (`value % 2` would be an error if `value` were a dict or a list.)
expression.filter(lambda value: value % 2 == 0, data)

# The alias is usable for annotating a filter function.
fn: FilterFunction = is_even
fn = is_short
fn = is_anything
fn = takes_any


# These are not filter functions.
def returns_str(value: int) -> str:
    return "yes"


def takes_two_arguments(left: int, right: int) -> bool:
    return left < right


def takes_no_arguments() -> bool:
    return True


# The function must return a bool, accept exactly one argument, and be callable.
expression.filter(returns_str, data)  # type: ignore[arg-type]
expression.filter(takes_two_arguments, data)  # type: ignore[arg-type]
expression.filter(takes_no_arguments, data)  # type: ignore[arg-type]
expression.filter(None, data)  # type: ignore[arg-type]
expression.filter("is_even", data)  # type: ignore[arg-type]
bad: FilterFunction = returns_str  # type: ignore[assignment]
bad = takes_two_arguments  # type: ignore[assignment]
