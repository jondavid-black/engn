import json
from pathlib import Path
from engn.main import run_check, load_standard_modules
from engn.data.models import _MODULE_REGISTRY


def write_jsonl(path: Path, items: list):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def test_block_with_properties(tmp_path, capsys):
    """Verify that a Block can have a 'properties' field containing Property definitions."""
    _MODULE_REGISTRY.clear()
    load_standard_modules()

    project_dir = tmp_path / "prop_project"
    project_dir.mkdir()

    model_file = project_dir / "model.jsonl"
    model_items = [
        {"engn_type": "import", "modules": ["SysML-v1"]},
        {
            "engn_type": "Block",
            "name": "PropBlock",
            "properties": [
                {
                    "name": "mass",
                    "type": "mass",
                    "description": "Object mass",
                    "presence": "required",
                    "default": "1 kg",
                }
            ],
        },
    ]

    write_jsonl(model_file, model_items)

    # Run check
    run_check(model_file, project_dir)
    captured = capsys.readouterr()

    assert "All checks passed!" in captured.out
