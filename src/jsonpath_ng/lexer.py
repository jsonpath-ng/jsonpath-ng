import logging
import sys
import warnings

import jsonpath_ng._ply.lex
from jsonpath_ng.exceptions import JsonPathLexerError

logger = logging.getLogger(__name__)


class JsonPathLexer:
    """
    A Lexical analyzer for JsonPath.
    """

    # The pre-generated lexer table; see `assets/generate_ply_tables.py`.
    _ply_table_module = "jsonpath_ng._ply_tables.lexer_table"

    def __init__(self, debug=None) -> None:
        if debug is not None:
            msg = (
                "The `debug` parameter is deprecated. "
                "It no longer has any effect and will be removed in version 2.0.0."
            )
            warnings.warn(msg, DeprecationWarning, stacklevel=2)

    def tokenize(self, string):
        """
        Maps a string to an iterator over tokens. In other words: [char] -> [token]
        """

        new_lexer = jsonpath_ng._ply.lex.lex(
            module=self,
            debug=False,
            optimize=True,
            lextab=self._ply_table_module,
            errorlog=logger,
        )
        new_lexer.latest_newline = 0
        new_lexer.string_value = None
        new_lexer.input(string)

        while True:
            t = new_lexer.token()
            if t is None:
                break
            t.col = t.lexpos - new_lexer.latest_newline
            yield t

        if new_lexer.string_value is not None:
            raise JsonPathLexerError("Unexpected EOF in string literal or identifier")

    # ============== PLY Lexer specification ==================
    #
    # This probably should be private but:
    #   - the parser requires access to `tokens` (perhaps they should be defined in a third, shared dependency)
    #   - things like `literals` might be a legitimate part of the public interface.
    #
    # Anyhow, it is pythonic to give some rope to hang oneself with :-)

    literals = ["*", ".", "[", "]", "(", ")", "$", ",", ":", "|", "&", "~"]

    reserved_words = {
        "where": "WHERE",
        "wherenot": "WHERENOT",
    }

    tokens = ["DOUBLEDOT", "NUMBER", "ID", "NAMED_OPERATOR"] + list(
        reserved_words.values()
    )

    states = [
        ("singlequote", "exclusive"),
        ("doublequote", "exclusive"),
        ("backquote", "exclusive"),
    ]

    # Normal lexing, rather easy
    t_DOUBLEDOT = r"\.\."
    t_ignore = " \t"

    def t_ID(self, t):
        # CJK: [\u4E00-\u9FA5]
        # EMOJI: [\U0001F600-\U0001F64F]
        r"([a-zA-Z_@]|[\u4E00-\u9FA5]|[\U0001F600-\U0001F64F])([a-zA-Z0-9_@\-]|[\u4E00-\u9FA5]|[\U0001F600-\U0001F64F])*"
        t.type = self.reserved_words.get(t.value, "ID")
        return t

    def t_NUMBER(self, t):
        r"-?\d+"
        t.value = int(t.value)
        return t

    # Single-quoted strings
    t_singlequote_ignore = ""

    def t_singlequote(self, t):
        r"'"
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("singlequote")

    def t_singlequote_content(self, t):
        r"[^'\\]+"
        t.lexer.string_value += t.value

    def t_singlequote_escape(self, t):
        r"\\."
        t.lexer.string_value += t.value[1]

    def t_singlequote_end(self, t):
        r"'"
        t.value = t.lexer.string_value
        t.type = "ID"
        t.lexer.string_value = None
        t.lexer.pop_state()
        return t

    def t_singlequote_error(self, t):
        raise JsonPathLexerError(
            "Error on line {}, col {} while lexing singlequoted field: Unexpected character: {} ".format(
                t.lexer.lineno, t.lexpos - t.lexer.latest_newline, t.value[0]
            )
        )

    # Double-quoted strings
    t_doublequote_ignore = ""

    def t_doublequote(self, t):
        r'"'
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("doublequote")

    def t_doublequote_content(self, t):
        r'[^"\\]+'
        t.lexer.string_value += t.value

    def t_doublequote_escape(self, t):
        r"\\."
        t.lexer.string_value += t.value[1]

    def t_doublequote_end(self, t):
        r'"'
        t.value = t.lexer.string_value
        t.type = "ID"
        t.lexer.string_value = None
        t.lexer.pop_state()
        return t

    def t_doublequote_error(self, t):
        raise JsonPathLexerError(
            "Error on line {}, col {} while lexing doublequoted field: Unexpected character: {} ".format(
                t.lexer.lineno, t.lexpos - t.lexer.latest_newline, t.value[0]
            )
        )

    # Back-quoted "magic" operators
    t_backquote_ignore = ""

    def t_backquote(self, t):
        r"`"
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("backquote")

    def t_backquote_escape(self, t):
        r"\\."
        t.lexer.string_value += t.value[1]

    def t_backquote_content(self, t):
        r"[^`\\]+"
        t.lexer.string_value += t.value

    def t_backquote_end(self, t):
        r"`"
        t.value = t.lexer.string_value
        t.type = "NAMED_OPERATOR"
        t.lexer.string_value = None
        t.lexer.pop_state()
        return t

    def t_backquote_error(self, t):
        raise JsonPathLexerError(
            "Error on line {}, col {} while lexing backquoted operator: Unexpected character: {} ".format(
                t.lexer.lineno, t.lexpos - t.lexer.latest_newline, t.value[0]
            )
        )

    # Counting lines, handling errors
    def t_newline(self, t):
        r"\n"
        t.lexer.lineno += 1
        t.lexer.latest_newline = t.lexpos

    def t_error(self, t):
        raise JsonPathLexerError(
            "Error on line {}, col {}: Unexpected character: {} ".format(
                t.lexer.lineno, t.lexpos - t.lexer.latest_newline, t.value[0]
            )
        )


if __name__ == "__main__":
    logging.basicConfig()
    lexer = JsonPathLexer()
    for token in lexer.tokenize(sys.stdin.read()):
        print("%-20s%s" % (token.value, token.type))
