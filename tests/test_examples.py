import pytest

from jsonpath_ng.ext import parse
from jsonpath_ng.ext.filter import Expression, Filter
from jsonpath_ng.jsonpath import Child, Descendants, Fields, Index, Root, Slice, This


@pytest.mark.parametrize(
    "string, parsed",
    [
        # The authors of all books in the store
        (
            "$.store.book[*].author",
            Child(
                Child(Child(Child(Root(), Fields("store")), Fields("book")), Slice()),
                Fields("author"),
            ),
        ),
        #
        # All authors
        ("$..author", Descendants(Root(), Fields("author"))),
        #
        # All things in the store
        ("$.store.*", Child(Child(Root(), Fields("store")), Fields("*"))),
        #
        # The price of everything in the store
        (
            "$.store..price",
            Descendants(Child(Root(), Fields("store")), Fields("price")),
        ),
        #
        # The third book
        ("$..book[2]", Child(Descendants(Root(), Fields("book")), Index(2))),
        #
        # The last book in order
        # "$..book[(@.length-1)]"  # Not implemented
        ("$..book[-1:]", Child(Descendants(Root(), Fields("book")), Slice(start=-1))),
        #
        # The first two books
        ("$..book[0,1]", Child(Descendants(Root(), Fields("book")), Index(0,1))),
        ("$..book[:2]", Child(Descendants(Root(), Fields("book")), Slice(end=2))),
        #
        # Categories and authors of all books
        (
            "$..book[0][category,author]", 
            Child(Child(Descendants(Root(), Fields('book')), Index(0)), Fields('category','author')),
        ),
        #
        # Filter all books with an ISBN
        (
            "$..book[?(@.isbn)]",
            Child(
                Descendants(Root(), Fields("book")),
                Filter([Expression(Child(This(), Fields("isbn")), None, None)]),
            ),
        ),
        #
        # Filter all books cheaper than 10
        (
            "$..book[?(@.price<10)]",
            Child(
                Descendants(Root(), Fields("book")),
                Filter([Expression(Child(This(), Fields("price")), "<", 10)]),
            ),
        ),
        #
        # All members of JSON structure
        ("$..*", Descendants(Root(), Fields("*"))),
    ],
)
def test_goessner_examples(string, parsed):
    """
    Test Stefan Goessner's `examples`_

    .. _examples: https://goessner.net/articles/JsonPath/index.html#e3
    """
    assert parse(string, debug=True) == parsed


def test_attribute_and_dict_syntax():
    """Verify that attribute and dict syntax result in identical parse trees."""

    assert parse("$.store.book[0].title") == parse("$['store']['book'][0]['title']")
