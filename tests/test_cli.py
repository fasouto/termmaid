"""Tests for the CLI interface."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from termaid.cli import main


class TestCliMain:
    def test_file_input(self, tmp_path: Path):
        mmd = tmp_path / "test.mmd"
        mmd.write_text("graph LR\n  A --> B")
        result = main([str(mmd)])
        assert result == 0

    def test_missing_file(self):
        result = main(["/nonexistent/file.mmd"])
        assert result == 1

    def test_ascii_flag(self, tmp_path: Path):
        mmd = tmp_path / "test.mmd"
        mmd.write_text("graph LR\n  A --> B")
        result = main([str(mmd), "--ascii"])
        assert result == 0

    def test_version_flag(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_empty_file(self, tmp_path: Path):
        mmd = tmp_path / "empty.mmd"
        mmd.write_text("")
        result = main([str(mmd)])
        assert result == 1

    def test_padding_flags(self, tmp_path: Path):
        mmd = tmp_path / "test.mmd"
        mmd.write_text("graph LR\n  A --> B")
        result = main([str(mmd), "--padding-x", "6", "--padding-y", "3"])
        assert result == 0


class TestCliPipe:
    def test_pipe_input(self):
        result = subprocess.run(
            [sys.executable, "-m", "termaid"],
            input="graph LR\n  A --> B",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "A" in result.stdout
        assert "B" in result.stdout

    def test_pipe_ascii(self):
        result = subprocess.run(
            [sys.executable, "-m", "termaid", "--ascii"],
            input="graph LR\n  A --> B",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "+" in result.stdout  # ASCII box char
        assert "┌" not in result.stdout  # No unicode

    def test_pipe_chain(self):
        result = subprocess.run(
            [sys.executable, "-m", "termaid"],
            input="graph LR\n  A --> B --> C --> D",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "A" in result.stdout
        assert "D" in result.stdout
