"""
Verify that the tracked PLY tables match what the code would generate now.

The tables are regenerated entirely in memory and compared with the files on
disk, so this runs locally (and in CI) without writing anything.
"""

import functools
import importlib.util
import pathlib

import pytest

import jsonpath_ng

repository_root = pathlib.Path(__file__).parent.parent
generator_path = repository_root / "assets" / "generate_ply_tables.py"
package_directory = pathlib.Path(jsonpath_ng.__file__).parent
tables_directory = package_directory / "_ply_tables"

pytestmark = pytest.mark.skipif(
    not generator_path.exists(), reason="the table generator is not distributed"
)


@functools.cache
def generate():
    spec = importlib.util.spec_from_file_location("generate_ply_tables", generator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_tables()


def test_tables_are_generated_for_each_parser_and_lexer():
    filenames = generate()

    assert set(filenames) == {
        "lexer_table.py",
        "parser_table.py",
        "ext_lexer_table.py",
        "ext_parser_table.py",
    }


def test_tracked_tables_are_current():
    for filename, expected in generate().items():
        path = tables_directory / filename
        assert path.is_file(), f"{filename} is missing; regenerate the tables"
        stale_message = f"{filename} is stale; regenerate the tables"
        assert path.read_text() == expected, stale_message


def test_no_orphaned_tables():
    expected = set(generate())
    on_disk = {
        path.name
        for path in package_directory.rglob("_ply_tables/*_table.py")
    }

    assert on_disk == expected


def test_generation_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = sorted(package_directory.rglob("*"))

    generate.cache_clear()
    generate()

    assert sorted(package_directory.rglob("*")) == before
    assert not list(tmp_path.iterdir())
