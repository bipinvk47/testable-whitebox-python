"""
test_file_handler.py
====================
Targets:
  - Exception Path Handling (all try/except branches)
  - Loop boundary: 0 / 1 / N iterations
  - Branch coverage: every if/else
  - Statement coverage: 100%
  - Multi-function path tracking (get_config_value → _load_config → read_json_file)
  - Check the flow for the testing.
"""
import json
import os
import tempfile

import pytest
from src.file_handler import (
    compute_checksum,
    find_files_by_extension,
    get_config_value,
    read_json_file,
    safe_read_lines,
    write_output,
)


class TestReadJsonFile:
    def test_valid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"key": "value"}, f)
            path = f.name
        try:
            result = read_json_file(path)
            assert result == {"key": "value"}
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            read_json_file("/nonexistent/path/file.json")

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            result = read_json_file(path)
            assert result == {}
        finally:
            os.unlink(path)

    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{not valid json}")
            path = f.name
        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                read_json_file(path)
        finally:
            os.unlink(path)


class TestFindFilesByExtension:
    def test_no_matches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_files_by_extension(tmpdir, "xyz")
            assert result == []

    def test_single_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.py")
            open(path, "w").close()
            result = find_files_by_extension(tmpdir, "py")
            assert len(result) == 1

    def test_multiple_matches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                open(os.path.join(tmpdir, f"file{i}.py"), "w").close()
            result = find_files_by_extension(tmpdir, "py")
            assert len(result) == 3

    def test_invalid_directory(self):
        result = find_files_by_extension("/no/such/dir", "py")
        assert result == []


class TestSafeReadLines:
    def test_existing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("line1\nline2\n")
            path = f.name
        try:
            lines = safe_read_lines(path)
            assert len(lines) == 2
        finally:
            os.unlink(path)

    def test_missing_file(self):
        result = safe_read_lines("/nonexistent/file.txt")
        assert result == []


class TestWriteOutput:
    def test_new_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "out.txt")
            assert write_output(path, "hello") is True
            assert open(path).read() == "hello"

    def test_overwrite_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "out.txt")
            write_output(path, "first")
            assert write_output(path, "second", overwrite=True) is True

    def test_overwrite_not_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "out.txt")
            write_output(path, "first")
            assert write_output(path, "second", overwrite=False) is False


class TestComputeChecksum:
    def test_empty_bytes(self):
        assert compute_checksum(b"") == 0

    def test_known_bytes(self):
        result = compute_checksum(b"\x01\x02\x03")
        assert result == (1 + 2 + 3) % 256


class TestGetConfigValue:
    def test_existing_key(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"db_host": "localhost"}, f)
            path = f.name
        try:
            val = get_config_value(path, "db_host")
            assert val == "localhost"
        finally:
            os.unlink(path)

    def test_missing_key_returns_default(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({}, f)
            path = f.name
        try:
            val = get_config_value(path, "missing_key", "DEFAULT")
            assert val == "DEFAULT"
        finally:
            os.unlink(path)

    def test_missing_file_returns_default(self):
        val = get_config_value("/no/file.json", "key", "fallback")
        assert val == "fallback"
