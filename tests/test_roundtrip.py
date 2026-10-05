from hypothesis import example, given, settings, strategies as st, assume

import jsonpath_ng
import jsonpath_ng.exceptions
import jsonpath_ng.ext

characters = st.characters(min_codepoint=0x20, max_codepoint=0x7e)  # space -> tilde
ascii_text = st.text(characters)

@given(ascii_text)
@example("10")
@example("0&0")
@example("';'")
@example('"0@"')
@example('"00"')
@example(r'"\'"')
@example("0..0[0]")
@example("(0..0)[0]")
@example("0..(0[0])")
@example("0..0.[0]")
@settings(max_examples=20)
def test_roundtrip_basic(string: str):
    try:
        parsed_original = jsonpath_ng.parse(string)
    except jsonpath_ng.exceptions.JSONPathError:
        assume(False)
        return

    reconstituted = str(parsed_original)
    parsed_reconstituted = jsonpath_ng.parse(reconstituted)
    assert parsed_original == parsed_reconstituted


@given(ascii_text)
@example("0-@")
@example("0|0")
@example("'%'")
@example("''")
@example("A -A")
@example("A -@")
@example("0[/0]")
@settings(max_examples=20)
def test_roundtrip_extended(string: str):
    try:
        parsed_original = jsonpath_ng.ext.parse(string)
    except jsonpath_ng.exceptions.JSONPathError:
        assume(False)
        return

    reconstituted = str(parsed_original)
    parsed_reconstituted = jsonpath_ng.ext.parse(reconstituted)
    assert parsed_original == parsed_reconstituted
