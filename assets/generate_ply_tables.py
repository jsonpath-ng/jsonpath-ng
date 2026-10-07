"""
Generate the PLY lexer and parser tables that jsonpath-ng loads at runtime.

PLY can pre-compute its LALR parse tables and lexer regexes and store them as
Python modules. jsonpath-ng ships these tracked files and never generates or
writes anything at runtime.

Run this script to (re)write the tables in ``src/jsonpath_ng/_ply_tables/``.
The tables are generated entirely in memory by ``generate_tables()``,
which the test suite also uses to check that the tracked files are current.
"""

import contextlib
import io
import os
import pathlib
import sys
from unittest import mock

root = pathlib.Path(__file__).resolve().parent.parent
tables_directory = root / "src/jsonpath_ng/_ply_tables"
sys.path.insert(0, str(root / "src"))

import jsonpath_ng._ply.lex as ply_lex  # noqa: E402
import jsonpath_ng._ply.yacc as ply_yacc  # noqa: E402
from jsonpath_ng.ext.parser import (  # noqa: E402
    ExtendedJsonPathLexer,
    ExtendedJsonPathParser,
)
from jsonpath_ng.lexer import JsonPathLexer  # noqa: E402
from jsonpath_ng.parser import JsonPathParser  # noqa: E402

lexer_classes = (JsonPathLexer, ExtendedJsonPathLexer)
parser_classes = (JsonPathParser, ExtendedJsonPathParser)


def _dedent_docstring(doc: str) -> str:
    """Strip common indentation as the compiler does on Python 3.13+."""

    lines = doc.expandtabs().split("\n")
    margins = [len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()]
    margin = min(margins, default=0)
    return "\n".join([lines[0]] + [line[margin:] for line in lines[1:]])


@contextlib.contextmanager
def _canonical_docstrings():
    """Make grammar docstrings identical on every supported Python version.

    PLY embeds the grammar docstrings in each parse table's signature.
    Python 3.13 began stripping their indentation at compile time,
    so the tables can differ depending on the interpreter version.
    """

    if sys.version_info >= (3, 13):
        yield
        return

    original = {}
    for parser_class in parser_classes:
        for name in dir(parser_class):
            function = getattr(parser_class, name)
            if name.startswith("p_") and function.__doc__:
                original[function] = function.__doc__
    try:
        for function, doc in original.items():
            function.__doc__ = _dedent_docstring(doc)
        yield
    finally:
        for function, doc in original.items():
            function.__doc__ = doc


class _Capture(io.StringIO):
    """A file-like object whose contents survive ``close()``."""

    def close(self):
        pass


@contextlib.contextmanager
def _in_memory_tables(module_names):
    """Redirect PLY's table files to memory, and force PLY to regenerate them."""

    captured = {}

    def capturing_open(filename, mode="r", *args, **kwargs):
        assert mode == "w", f"unexpected PLY file access: {filename!r} ({mode!r})"
        return captured.setdefault(os.path.basename(filename), _Capture())

    with (
        mock.patch.dict(sys.modules, dict.fromkeys(module_names)),
        mock.patch.object(ply_yacc, "open", capturing_open, create=True),
        mock.patch.object(ply_lex, "open", capturing_open, create=True),
    ):
        yield captured


def _strip_trailing_whitespace(text: str) -> str:
    """Strip trailing whitespace from every line."""

    return "".join(line.rstrip() + "\n" for line in text.splitlines())


def generate_tables() -> dict[str, str]:
    """Return ``{filename: contents}`` for every table, without writing files."""

    module_names = [c._ply_table_module for c in parser_classes]
    module_names += [c._ply_table_module for c in lexer_classes]

    with _canonical_docstrings(), _in_memory_tables(module_names) as captured:
        for lexer_class in lexer_classes:
            ply_lex.lex(
                module=lexer_class(),
                optimize=True,
                lextab=lexer_class._ply_table_module,
                outputdir="",
                errorlog=ply_yacc.NullLogger(),
            )
        for parser_class in parser_classes:
            # Bypass `__init__`, which would load the table that doesn't exist yet.
            ply_yacc.yacc(
                module=parser_class.__new__(parser_class),
                debug=False,
                tabmodule=parser_class._ply_table_module,
                outputdir="",
                write_tables=True,
                start="jsonpath",
                errorlog=ply_yacc.NullLogger(),
            )

    return {
        filename: _strip_trailing_whitespace(file.getvalue())
        for filename, file in sorted(captured.items())
    }


def main():
    for filename, contents in generate_tables().items():
        path = tables_directory / filename
        if not path.exists() or path.read_text() != contents:
            path.write_text(contents)
            print(f"wrote {path.relative_to(root)}")


if __name__ == "__main__":
    main()
