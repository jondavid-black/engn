import json
from pathlib import Path
import re
import pytest
from engn.main import run_check


from typing import Sequence, Any


# Helper to write JSONL content
def write_jsonl(path: Path, items: Sequence[dict[str, Any] | str]):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            if isinstance(item, str):
                f.write(item + "\n")
            else:
                f.write(json.dumps(item) + "\n")


def test_check_no_files(tmp_path, capsys):
    """Test check command when no JSONL files exist."""
    # Run check with no target (uses default paths)
    run_check(None, tmp_path)

    captured = capsys.readouterr()
    assert "No JSONL files found to check." in captured.out


def test_check_valid_files(tmp_path, capsys):
    """Test check command with valid JSONL files."""
    # Create a valid file
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "data.jsonl"

    valid_items = [
        {
            "engn_type": "enum",
            "name": "Status",
            "values": ["open", "closed"],
            "description": "Status enum",
        },
        {
            "engn_type": "type_def",
            "name": "Task",
            "properties": [{"name": "status", "type": "Status"}],
        },
    ]
    write_jsonl(f, valid_items)

    # Run check
    run_check(None, tmp_path)

    captured = capsys.readouterr()
    assert "All checks passed!" in captured.out
    assert "Found" not in captured.out


def test_check_invalid_json(tmp_path, capsys):
    """Test check command with invalid JSON syntax."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "bad.jsonl"

    # Write invalid JSON
    write_jsonl(f, ["{not valid json}"])

    run_check(None, tmp_path)

    captured = capsys.readouterr()
    assert "Found 1 errors" in captured.out
    assert "bad.jsonl at line 1:" in captured.out
    assert (
        "JSON decode error" in captured.out
        or "Expecting property name" in captured.out
        or "json_invalid" in captured.out
    )


def test_check_invalid_schema(tmp_path, capsys):
    """Test check command with valid JSON but invalid schema."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "invalid_schema.jsonl"

    invalid_items = [
        # Missing 'values' for enum
        {"engn_type": "enum", "name": "Status"},
        # Invalid type for 'name' (should be str)
        {"engn_type": "type_def", "name": 123, "properties": []},
    ]
    write_jsonl(f, invalid_items)

    run_check(None, tmp_path)

    captured = capsys.readouterr()
    assert "Found 2 errors" in captured.out
    # Check for specific validation errors
    assert "Field required" in captured.out  # Pydantic error for missing field
    assert (
        "Input should be a valid string" in captured.out
    )  # Pydantic error for wrong type


def test_check_target_file(tmp_path, capsys):
    """Test checking a specific file target."""
    # Create file in a non-standard location
    f = tmp_path / "custom.jsonl"
    valid_items = [{"engn_type": "enum", "name": "Custom", "values": ["A", "B"]}]
    write_jsonl(f, valid_items)

    run_check(f, tmp_path)

    captured = capsys.readouterr()
    assert "All checks passed!" in captured.out


def test_check_target_directory(tmp_path, capsys):
    """Test checking a specific directory target."""
    custom_dir = tmp_path / "custom_dir"
    custom_dir.mkdir()

    f1 = custom_dir / "file1.jsonl"
    write_jsonl(f1, [{"engn_type": "enum", "name": "Enum1", "values": ["1"]}])

    f2 = custom_dir / "subdir" / "file2.jsonl"
    f2.parent.mkdir()
    write_jsonl(f2, [{"engn_type": "enum", "name": "Enum2", "values": ["2"]}])

    run_check(custom_dir, tmp_path)

    captured = capsys.readouterr()
    assert "All checks passed!" in captured.out


def test_check_mixed_validity(tmp_path, capsys):
    """Test mixed valid and invalid files."""
    d = tmp_path / "pm"
    d.mkdir()

    # Valid file
    write_jsonl(
        d / "valid.jsonl", [{"engn_type": "enum", "name": "Valid", "values": ["v"]}]
    )

    # Invalid file
    write_jsonl(
        d / "invalid.jsonl",
        [
            {"engn_type": "unknown_type"}  # Invalid discriminator
        ],
    )

    run_check(None, tmp_path)

    captured = capsys.readouterr()
    assert "Found 1 errors" in captured.out
    assert "invalid.jsonl" in captured.out
    assert (
        "Input tag 'unknown_type' found using 'engn_type' does not match any of the expected tags"
        in captured.out
        or "Input should be a valid dictionary or instance of Enumeration"
        in captured.out
    )


def test_check_target_not_found(tmp_path, capsys):
    """Test behavior when target does not exist."""
    # The run_check function calls sys.exit(1) if target not found
    target = tmp_path / "nonexistent"

    with pytest.raises(SystemExit) as e:
        run_check(target, tmp_path)

    assert e.value.code == 1
    captured = capsys.readouterr()
    assert f"Error: Target '{target}' not found." in captured.out


def test_check_error_messages_not_truncated(tmp_path, capsys):
    """Test that error messages are not truncated."""
    f = tmp_path / "data.jsonl"

    # Create a type with many missing required fields to generate a long error
    invalid_item = {
        "engn_type": "type_def",
        "properties": [
            {"name": "prop1"},  # missing 'type'
            {"name": "prop2"},  # missing 'type'
            {"name": "prop3"},  # missing 'type'
        ],
    }
    write_jsonl(f, [invalid_item])

    run_check(f, tmp_path)

    captured = capsys.readouterr()
    assert "Found" in captured.out

    # The Pydantic error URL should appear in full (not truncated)
    # The Pydantic error URL should appear in full (not truncated)
    # This URL is typically at the end of error messages
    error_lines = [line for line in captured.out.split("\n") if "ERROR" in line]
    # Use regex to find the URL to satisfy CodeQL's URL sanitization check
    pydantic_url_pattern = re.compile(r"https://errors\.pydantic\.dev/\S*")
    assert any(pydantic_url_pattern.search(line) for line in error_lines)

    # Error message should not end with "..." (truncation indicator)
    for line in error_lines:
        assert not line.rstrip().endswith("...")


def test_check_errors_sorted_by_file_and_line(tmp_path, capsys):
    """Test that errors are sorted by file name, then line number."""
    # Create files that will have errors at various lines
    # Use names that sort in a specific order: aaa.jsonl < bbb.jsonl
    d = tmp_path / "pm"
    d.mkdir()

    # File bbb.jsonl - errors at lines 1 and 3
    write_jsonl(
        d / "bbb.jsonl",
        [
            {"engn_type": "enum"},  # line 1: missing name and values
            {"engn_type": "enum", "name": "Valid", "values": ["x"]},  # line 2: valid
            {"engn_type": "type_def"},  # line 3: missing name
        ],
    )

    # File aaa.jsonl - errors at lines 2 and 4
    write_jsonl(
        d / "aaa.jsonl",
        [
            {"engn_type": "enum", "name": "E1", "values": ["a"]},  # line 1: valid
            {"engn_type": "enum"},  # line 2: missing name and values
            {"engn_type": "enum", "name": "E2", "values": ["b"]},  # line 3: valid
            {"engn_type": "type_def"},  # line 4: missing name
        ],
    )

    run_check(None, tmp_path)

    captured = capsys.readouterr()
    assert "Found 4 errors" in captured.out

    # Extract error lines and their positions in output
    lines = captured.out.split("\n")
    error_lines = [line for line in lines if "ERROR" in line]

    assert len(error_lines) == 4

    # Errors should be sorted: aaa.jsonl (line 2, line 4), then bbb.jsonl (line 1, line 3)
    assert "aaa.jsonl at line 2:" in error_lines[0]
    assert "aaa.jsonl at line 4:" in error_lines[1]
    assert "bbb.jsonl at line 1:" in error_lines[2]
    assert "bbb.jsonl at line 3:" in error_lines[3]


def test_check_unknown_type_reference(tmp_path, capsys):
    """Test that unknown type references are caught and reported."""
    f = tmp_path / "data.jsonl"

    items = [
        {"engn_type": "enum", "name": "Status", "values": ["open", "closed"]},
        {
            "engn_type": "type_def",
            "name": "Task",
            "properties": [
                {"name": "status", "type": "Status"},  # valid reference
                {"name": "owner", "type": "UnknownType"},  # invalid reference
            ],
        },
    ]
    write_jsonl(f, items)

    run_check(f, tmp_path)

    captured = capsys.readouterr()
    assert "Found 1 errors" in captured.out
    assert "Unknown type 'UnknownType'" in captured.out
    assert "Task.owner" in captured.out
