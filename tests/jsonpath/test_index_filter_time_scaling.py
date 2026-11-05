"""
Test that `Index.filter()` takes time that is linear to the number of removals.

This test compares how the time grows when the data is quadrupled.
Removing a block of elements from the front of a list
by deleting them one at a time would be quadratic.
"""

import timeit

import jsonpath_ng.ext

# Large lists are required to demonstrate or disprove linear vs quadratic time.
SMALL = 10_000
LARGE = SMALL * 4


def best_time(size):
    # Remove the first half of the elements; the indices come from the query.
    path_string = "$[%s]" % ",".join(str(index) for index in range(size // 2))
    path = jsonpath_ng.ext.parse(path_string)

    def remove_first_half():
        path.filter(lambda value: True, list(range(size)))

    return min(timeit.repeat(remove_first_half, number=1, repeat=5))


def test_index_filter_time_is_linear_to_data_size():
    ratio = best_time(LARGE) / best_time(SMALL)

    # Linear growth gives ~4 and quadratic growth gives ~16;
    # 8 leaves margin for timing noise on both sides.
    assert ratio < 8, f"{LARGE / SMALL:.0f}x the data took {ratio:.1f}x as long"
