import json
from pathlib import Path
from typing import Sequence, Any

from engn.main import run_print


def write_jsonl(path: Path, items: Sequence[dict[str, Any] | str]):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            if isinstance(item, str):
                f.write(item + "\n")
            else:
                f.write(json.dumps(item) + "\n")


def test_print_no_files(tmp_path, capsys):
    """Test print command when no JSONL files exist."""
    run_print(None, tmp_path)

    captured = capsys.readouterr()
    assert "No JSONL files found to print." in captured.out


def test_print_enum(tmp_path, capsys):
    """Test print command displays enums correctly."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "data.jsonl"

    enum_item = {
        "engn_type": "enum",
        "name": "Status",
        "description": "Task status values",
        "values": ["open", "in_progress", "closed"],
    }
    write_jsonl(f, [enum_item])

    run_print(None, tmp_path)

    captured = capsys.readouterr()
    assert "[Enum] Status" in captured.out
    assert "Description: Task status values" in captured.out
    assert "Values: open, in_progress, closed" in captured.out


def test_print_type_def(tmp_path, capsys):
    """Test print command displays type definitions correctly."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "data.jsonl"

    items = [
        {"engn_type": "enum", "name": "Priority", "values": ["low", "medium", "high"]},
        {
            "engn_type": "type_def",
            "name": "Task",
            "description": "A task item",
            "properties": [
                {"name": "title", "type": "str", "presence": "required"},
                {"name": "priority", "type": "Priority", "presence": "optional", "default": "medium"},
            ],
        },
    ]
    write_jsonl(f, items)

    run_print(None, tmp_path)

    captured = capsys.readouterr()
    assert "[Type] Task" in captured.out
    assert "Description: A task item" in captured.out
    assert "Properties:" in captured.out
    assert "- title: str (required)" in captured.out
    assert "- priority: Priority (optional, default: medium)" in captured.out


def test_print_type_def_with_extends(tmp_path, capsys):
    """Test print command displays type definitions with extends."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "data.jsonl"

    items = [
        {
            "engn_type": "type_def",
            "name": "BaseItem",
            "properties": [{"name": "id", "type": "str", "presence": "required"}],
        },
        {
            "engn_type": "type_def",
            "name": "Task",
            "extends": "BaseItem",
            "properties": [{"name": "title", "type": "str"}],
        },
    ]
    write_jsonl(f, items)

    run_print(None, tmp_path)

    captured = capsys.readouterr()
    assert "[Type] Task" in captured.out
    assert "Extends: BaseItem" in captured.out


def test_print_target_file(tmp_path, capsys):
    """Test print command with specific file target."""
    f = tmp_path / "custom.jsonl"
    write_jsonl(f, [{"engn_type": "enum", "name": "Custom", "values": ["A", "B"]}])

    run_print(f, tmp_path)

    captured = capsys.readouterr()
    assert "custom.jsonl" in captured.out
    assert "[Enum] Custom" in captured.out


def test_print_target_directory(tmp_path, capsys):
    """Test print command with directory target."""
    custom_dir = tmp_path / "custom_dir"
    custom_dir.mkdir()

    f1 = custom_dir / "file1.jsonl"
    write_jsonl(f1, [{"engn_type": "enum", "name": "Enum1", "values": ["1"]}])

    f2 = custom_dir / "subdir" / "file2.jsonl"
    f2.parent.mkdir()
    write_jsonl(f2, [{"engn_type": "enum", "name": "Enum2", "values": ["2"]}])

    run_print(custom_dir, tmp_path)

    captured = capsys.readouterr()
    assert "[Enum] Enum1" in captured.out
    assert "[Enum] Enum2" in captured.out


def test_print_empty_file(tmp_path, capsys):
    """Test print command with empty JSONL file."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "empty.jsonl"
    f.write_text("")

    run_print(None, tmp_path)

    captured = capsys.readouterr()
    assert "No data items found." in captured.out


def test_print_enum_without_description(tmp_path, capsys):
    """Test print command handles enums without description."""
    d = tmp_path / "pm"
    d.mkdir()
    f = d / "data.jsonl"

    write_jsonl(f, [{"engn_type": "enum", "name": "Simple", "values": ["x", "y"]}])

    run_print(None, tmp_path)

    captured = capsys.readouterr()
    assert "[Enum] Simple" in captured.out
    assert "Values: x, y" in captured.out
    # Should not have "Description:" line
    lines = captured.out.split("\n")
    enum_section = False
    for line in lines:
        if "[Enum] Simple" in line:
            enum_section = True
        elif enum_section and line.startswith("["):
            break
        elif enum_section and "Description:" in line:
            assert False, "Should not have Description line for enum without description"
