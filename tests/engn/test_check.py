import json
from pathlib import Path
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
    assert "bad.jsonl:1:" in captured.out
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
