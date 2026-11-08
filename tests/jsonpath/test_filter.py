import copy

import pytest

import jsonpath_ng.ext
from jsonpath_ng import Child
from jsonpath_ng import Fields
from jsonpath_ng import Root
from jsonpath_ng import This
from jsonpath_ng.ext.filter import Expression
from jsonpath_ng.ext.filter import Filter
from tests.helpers import assert_value_equality


@pytest.mark.parametrize(
    "datum, expected_values",
    [
        pytest.param([1, 2, 3], [2, 3], id="list"),
        pytest.param({"a": 1, "b": 2, "c": 3}, [2, 3], id="dict"),
        pytest.param(2, [], id="int"),
        pytest.param("abc", [], id="str"),
        pytest.param(None, [], id="null"),
    ],
)
def test_filter_returns_lists(datum, expected_values):
    """
    Verify that a Filter follows the find() contract and RFC 9535 behavior.

    RFC 9535 section 2.3.5.2 says filter selectors only work with arrays and objects,
    and "applied to a primitive value, it selects nothing".

    The int case uses a value that would satisfy the filter
    if it were (incorrectly) applied to the datum itself.
    """

    path = jsonpath_ng.ext.parse("$[?@ > 1]")

    results = path.find(datum)

    assert isinstance(results, list)
    assert_value_equality(results, expected_values)


SCORES_ARRAY = [{"score": 90}, {"score": 50}, {"score": 85}]
SCORES_OBJECT = {
    "first": {"score": 90},
    "second": {"score": 50},
    "third": {"score": 85},
}


@pytest.mark.parametrize(
    "path, datum, expected",
    [
        pytest.param(
            "$[?@.score >= 85]",
            SCORES_ARRAY,
            ["X", {"score": 50}, "X"],
            id="array-elements",
        ),
        pytest.param(
            "$[?@.score >= 85]",
            SCORES_OBJECT,
            {"first": "X", "second": {"score": 50}, "third": "X"},
            id="object-members",
        ),
        pytest.param(
            "$.scores[?@.score >= 85]",
            {"scores": SCORES_OBJECT, "other": 1},
            {
                "scores": {"first": "X", "second": {"score": 50}, "third": "X"},
                "other": 1,
            },
            id="object-members-below-child-segment",
        ),
        pytest.param(
            "$[?@.score > 100]", SCORES_ARRAY, SCORES_ARRAY, id="array-no-match"
        ),
        pytest.param(
            "$[?@.score > 100]", SCORES_OBJECT, SCORES_OBJECT, id="object-no-match"
        ),
        pytest.param("$[?@ > 0]", 1, 1, id="int"),
        pytest.param("$[?@ > 0]", "abc", "abc", id="str"),
        pytest.param("$[?@ > 0]", None, None, id="null"),
    ],
)
def test_update_replaces_selected_values(path, datum, expected):
    """
    Verify that update() replaces the values that the filter selects.

    RFC 9535 section 2.3.5.2 says that a filter selector selects
    the elements of an array and the member values of an object
    for which the logical expression is true, and selects nothing from a primitive.
    """

    data = copy.deepcopy(datum)

    result = jsonpath_ng.ext.parse(path).update(data, "X")

    assert result is data
    assert result == expected


@pytest.mark.parametrize(
    "datum, expected_keys",
    [
        pytest.param(SCORES_ARRAY, [0, 2], id="array"),
        pytest.param(SCORES_OBJECT, ["first", "third"], id="object"),
    ],
)
def test_update_callable_receives_value_container_and_key(datum, expected_keys):
    data = copy.deepcopy(datum)
    calls = []

    jsonpath_ng.ext.parse("$[?@.score >= 85]").update(
        data, lambda value, container, key: calls.append((value, container, key))
    )

    assert [key for _, _, key in calls] == expected_keys
    for value, container, key in calls:
        assert container is data
        assert value is data[key]


def test_update_callable_may_add_members_to_an_object():
    def add_copy(value, container, key):
        container[f"{key}-copy"] = value

    data = copy.deepcopy(SCORES_OBJECT)

    jsonpath_ng.ext.parse("$[?@.score >= 85]").update(data, add_copy)

    assert data.keys() == {"first", "second", "third", "first-copy", "third-copy"}


@pytest.mark.parametrize(
    "path, datum, expected_values",
    [
        pytest.param(
            "$.a[?($.x == 1)]",
            {"x": 1, "a": [1, 2, 3]},
            [1, 2, 3],
            id="comparison-true",
        ),
        pytest.param(
            "$.a[?($.x == 2)]", {"x": 1, "a": [1, 2, 3]}, [], id="comparison-false"
        ),
        pytest.param(
            '$.a[?($.x == "1")]',
            {"x": 1, "a": [1, 2, 3]},
            [],
            id="number-is-not-string",
        ),
        pytest.param("$.a[?$.x]", {"x": 1, "a": [1, 2, 3]}, [1, 2, 3], id="existence"),
        pytest.param("$.a[?$.nope]", {"x": 1, "a": [1, 2, 3]}, [], id="missing"),
        pytest.param(
            "$.a[?!$.x]", {"x": 1, "a": [1, 2, 3]}, [], id="negated-existence"
        ),
        pytest.param(
            "$.a[?!$.nope]", {"x": 1, "a": [1, 2, 3]}, [1, 2, 3], id="negated-missing"
        ),
        pytest.param(
            "$.a[?($ == 2)]",
            {"x": 1, "a": [1, 2, 3]},
            [],
            id="root-is-not-the-element",
        ),
        pytest.param(
            "$.a[?($.x)]",
            {"x": 1, "a": [{"x": 5}, {"y": 1}]},
            [{"x": 5}, {"y": 1}],
            id="element-members-do-not-shadow-root",
        ),
        pytest.param(
            "$.a.b[?($.x == 1)]",
            {"x": 1, "a": {"b": [1, 2]}},
            [1, 2],
            id="nested-path",
        ),
        pytest.param(
            "$[?($.expensive == 10)]",
            {"store": {"bicycle": {"color": "red"}}, "expensive": 10},
            [{"bicycle": {"color": "red"}}, 10],
            id="filter-on-root-object",
        ),
        pytest.param(
            "$.a[?@.b[?($.x == 1)]]",
            {"x": 1, "a": [{"b": [1]}, {"c": 2}]},
            [{"b": [1]}],
            id="nested-filter",
        ),
    ],
)
def test_filter_root_reference_is_document_root(path, datum, expected_values):
    """
    Verify that `$` inside a filter is the root of the query argument.

    RFC 9535 sections 1.4.1 and 2.3.5.1 say that `$` refers to the argument as a whole
    and that absolute queries are allowed in filter expressions.
    Previously `$` was bound to the element being tested, as if it were `@`.
    """

    results = jsonpath_ng.ext.parse(path).find(datum)

    assert_value_equality(results, expected_values)


ROOT_DOC = {"x": 1, "a": [1, 2, 3]}
NESTED_ROOT_DOC = {"k": 1, "o": {"p": [1, 2], "q": [[3]]}}


@pytest.mark.parametrize(
    "path, datum, expected",
    [
        pytest.param(
            "$.a[?($.x == 1)]", ROOT_DOC, {"x": 1, "a": ["X"] * 3}, id="root-true"
        ),
        pytest.param("$.a[?($.x == 2)]", ROOT_DOC, ROOT_DOC, id="root-false"),
        pytest.param(
            "$.a[?($.x == 1)]",
            {"x": 1, "a": {"m": 1, "n": 2}},
            {"x": 1, "a": {"m": "X", "n": "X"}},
            id="object-members",
        ),
        pytest.param("$.a[?!$.x]", ROOT_DOC, ROOT_DOC, id="negated-root"),
        pytest.param(
            "$.o.p[?($.k == 1)]",
            NESTED_ROOT_DOC,
            {**NESTED_ROOT_DOC, "o": {"p": ["X", "X"], "q": [[3]]}},
            id="three-level-child",
        ),
        pytest.param(
            "$.o..[?($.k == 1)]",
            NESTED_ROOT_DOC,
            # `o` is an object, so the filter selects its members `p` and `q`.
            # They are replaced before their own children are visited.
            {"k": 1, "o": {"p": "X", "q": "X"}},
            id="descendants",
        ),
        pytest.param(
            "$.o..[?($.k == 2)]",
            NESTED_ROOT_DOC,
            NESTED_ROOT_DOC,
            id="descendants-false",
        ),
    ],
)
def test_update_root_reference_is_document_root(path, datum, expected):
    result = jsonpath_ng.ext.parse(path).update(copy.deepcopy(datum), "X")
    assert result == expected


def test_update_with_callable_root_reference_is_document_root():
    calls = []
    jsonpath_ng.ext.parse("$.a[?($.x == 1)]").update(
        copy.deepcopy(ROOT_DOC), lambda value, parent, key: calls.append(key)
    )
    assert calls == [0, 1, 2]


@pytest.mark.parametrize(
    "path, datum, expected",
    [
        pytest.param("$.a[?($.x == 1)]", ROOT_DOC, {"x": 1, "a": []}, id="root-true"),
        pytest.param("$.a[?($.x == 2)]", ROOT_DOC, ROOT_DOC, id="root-false"),
        pytest.param(
            "$.o.p[?($.k == 1)]",
            NESTED_ROOT_DOC,
            {"k": 1, "o": {"p": [], "q": [[3]]}},
            id="three-level-child",
        ),
        pytest.param(
            "$.o..[?($.k == 1)]",
            NESTED_ROOT_DOC,
            {"k": 1, "o": {}},
            id="descendants",
        ),
        pytest.param(
            "$.o..[?($.k == 2)]",
            NESTED_ROOT_DOC,
            NESTED_ROOT_DOC,
            id="descendants-false",
        ),
    ],
)
def test_filter_method_root_reference_is_document_root(path, datum, expected):
    result = jsonpath_ng.ext.parse(path).filter(
        lambda value: True, copy.deepcopy(datum)
    )
    assert result == expected


MUTATION_DOC = {"k": "thing", "a": [{"y": ["thing"]}, {"y": ["other"]}]}


def _root_comparison():
    """Create the expression `$.k == "thing"`, which is true for MUTATION_DOC."""

    return Expression(Child(Root(), Fields("k")), "==", "thing")


def _find_filters(path):
    """Return the outer filter of `$.a[?@.y]...` and the filter nested inside it."""

    outer = path
    while not isinstance(outer, Filter):
        outer = outer.right
    inner = outer.expressions[0].target.right
    assert isinstance(inner, Filter)
    return outer, inner


def test_filter_notices_root_reference_added_to_nested_filter_by_assignment():
    """
    Verify that replacing the expressions of a nested filter is noticed.

    The outer filter must evaluate `$` against the document root
    when any filter nested within it references `$`,
    even if that reference was added after the outer filter was created.
    """

    path = jsonpath_ng.ext.parse('$.a[?@.y[?@ == "thing"]]')
    outer, inner = _find_filters(path)
    assert_value_equality(path.find(MUTATION_DOC), [{"y": ["thing"]}])

    inner.expressions = [_root_comparison()]

    # `$.k == "thing"` is true for every candidate, so every element now matches.
    assert_value_equality(path.find(MUTATION_DOC), [{"y": ["thing"]}, {"y": ["other"]}])


def test_filter_notices_root_reference_added_to_nested_filter_in_place():
    """Verify that appending to the expressions of a nested filter is noticed."""

    path = jsonpath_ng.ext.parse('$.a[?@.y[?@ == "thing"]]')
    outer, inner = _find_filters(path)

    inner.expressions.append(_root_comparison())

    # The new expression is true, so only the original `@ == "thing"` decides.
    assert_value_equality(path.find(MUTATION_DOC), [{"y": ["thing"]}])


def test_filter_notices_root_reference_appended_to_its_own_expressions():
    """Verify that appending to the expressions of a filter is noticed."""

    path = jsonpath_ng.ext.parse("$.a[?@.y]")
    outer = path.right
    assert isinstance(outer, Filter)

    outer.expressions.append(_root_comparison())

    assert_value_equality(path.find(MUTATION_DOC), [{"y": ["thing"]}, {"y": ["other"]}])


def test_update_notices_root_reference_appended_to_expressions():
    """Verify that update() notices a root reference added after creation."""

    path = jsonpath_ng.ext.parse("$.a[?@.y]")
    outer = path.right
    assert isinstance(outer, Filter)

    outer.expressions.append(_root_comparison())

    result = path.update(copy.deepcopy(MUTATION_DOC), "X")
    assert result == {"k": "thing", "a": ["X", "X"]}


def test_filter_is_unaffected_by_later_changes_to_the_list_it_was_created_with():
    """Verify that a filter keeps its own copy of the expressions."""

    expressions = [Expression(Child(Root(), Fields("k")), "==", "nope")]
    flt = Filter(expressions)

    expressions.clear()

    assert len(flt.expressions) == 1
    assert flt.find([1, 2]) == []


def test_filter_accepts_expressions_assigned_as_a_tuple():
    """Verify that find() does not assume that the expressions are a list."""

    flt = Filter([Expression(Child(Root(), Fields("k")), "==", "nope")])
    flt.expressions = (Expression(Child(This(), Fields("y")), None, None),)

    assert_value_equality(flt.find(MUTATION_DOC["a"]), MUTATION_DOC["a"])
