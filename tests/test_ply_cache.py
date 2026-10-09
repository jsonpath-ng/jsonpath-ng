"""Verify that PLY output is pre-generated and never built or written at runtime."""

import pathlib

import pytest

import jsonpath_ng
import jsonpath_ng._ply.lex as ply_lex
import jsonpath_ng._ply.yacc as ply_yacc
from jsonpath_ng.ext.parser import ExtendedJsonPathParser
from jsonpath_ng.parser import JsonPathParser

parser_classes = (JsonPathParser, ExtendedJsonPathParser)
package_directory = pathlib.Path(jsonpath_ng.__file__).parent


@pytest.fixture(autouse=True)
def forbid_writes(monkeypatch):
    """Fail if PLY attempts to write any generated file."""

    def fail(*args, **kwargs):
        raise AssertionError("PLY attempted to write a file")

    monkeypatch.setattr(ply_yacc.LRTable, "write_table", fail, raising=False)
    monkeypatch.setattr(ply_yacc.LRGeneratedTable, "write_table", fail)
    monkeypatch.setattr(ply_lex.Lexer, "writetab", fail)


@pytest.fixture
def parsetab_names(monkeypatch):
    """Record the name of every parse table module that is read."""

    names = []
    read_table = ply_yacc.LRTable.read_table

    def recording_read_table(self, module):
        names.append(module)
        return read_table(self, module)

    monkeypatch.setattr(ply_yacc.LRTable, "read_table", recording_read_table)
    return names


def test_parsers_use_distinct_parse_tables(parsetab_names):
    """Each parser's grammar differs, so each needs its own table."""

    for parser_class in parser_classes:
        parser_class()

    assert len(parsetab_names) == len(parser_classes)
    assert len(set(parsetab_names)) == len(parser_classes)


@pytest.mark.parametrize("parser_class", parser_classes)
def test_parse_tables_are_pregenerated(parser_class, parsetab_names):
    """The table module must be importable from inside the package."""

    parser_class()

    (name,) = parsetab_names
    module = __import__(name, fromlist=["_lr_action"])
    assert pathlib.Path(module.__file__).is_relative_to(package_directory)


@pytest.mark.parametrize("parser_class", parser_classes)
def test_parser_does_not_build_lalr_tables(parser_class, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("LALR tables were generated at runtime")

    monkeypatch.setattr(ply_yacc.LRGeneratedTable, "__init__", fail)

    parser_class().parse("$.a")


@pytest.mark.parametrize("parser_class", parser_classes)
def test_lexer_does_not_build_regexes(parser_class, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("lexer regexes were built at runtime")

    monkeypatch.setattr(ply_lex, "_form_master_re", fail)

    parser_class().parse("$.a")


@pytest.mark.parametrize("parser_class", parser_classes)
def test_debug_is_deprecated(parser_class):
    with pytest.warns(DeprecationWarning, match="The `debug` parameter is deprecated"):
        parser_class(debug=True)


@pytest.mark.parametrize("parser_class", parser_classes)
def test_parser_out_is_never_written(parser_class, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    existing = (package_directory / "parser.out").exists()

    with pytest.warns(DeprecationWarning):
        parser_class(debug=True).parse("$.a")

    assert not list(tmp_path.glob("parser.out"))
    assert (package_directory / "parser.out").exists() == existing
