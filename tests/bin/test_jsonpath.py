"""
Tests for the CLI.
"""

import io
import pathlib

from jsonpath_ng.bin.jsonpath import main


def test_stdin_mode(monkeypatch, capsys):
    test_file = pathlib.Path(__file__).parent / "test1.json"
    monkeypatch.setattr("sys.stdin", io.StringIO(test_file.read_text()))
    monkeypatch.setattr("sys.argv", ("literally-anything", "$.foo..baz"))

    main()

    stdout, _ = capsys.readouterr()
    assert stdout == "1\n2\n"


def test_filename_mode(monkeypatch, capsys):
    root = pathlib.Path(__file__).parent

    sys_argv = (
        "literally-anything",
        "$.foo..baz",
        str(root / "test1.json"),
        str(root / "test2.json"),
    )
    monkeypatch.setattr("sys.argv", sys_argv)

    main()

    stdout, _ = capsys.readouterr()
    assert stdout == "1\n2\n3\n4\n"
