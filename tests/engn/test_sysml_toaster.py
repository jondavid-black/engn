import json
from pathlib import Path
from engn.main import run_check, run_print, load_standard_modules
from engn.data.models import _MODULE_REGISTRY


def write_jsonl(path: Path, items: list):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def test_sysml_toaster_model(tmp_path, capsys):
    """
    Test defining a SysML v1 model for a toaster and verify it with check and print.
    """
    # 1. Setup: Load standard modules and prepare directory
    _MODULE_REGISTRY.clear()
    load_standard_modules()
    assert "SysML-v1" in _MODULE_REGISTRY

    project_dir = tmp_path / "toaster_project"
    project_dir.mkdir()

    # 2. Define the model
    # We use a single file for the model
    model_file = project_dir / "toaster.jsonl"

    model_items = [
        # Import SysML-v1
        {"engn_type": "import", "modules": ["SysML-v1"]},
        # Requirements
        {
            "engn_type": "Requirement",
            "id": "REQ-001",
            "text": "The toaster shall toast slices of bread to a desired brownness.",
            "kind": "functional",
        },
        {
            "engn_type": "Requirement",
            "id": "REQ-002",
            "text": "The heating element shall reach at least 200 degrees Celsius.",
            "kind": "performance",
            "derived_from": ["REQ-001"],
        },
        # Blocks
        {
            "engn_type": "Block",
            "name": "Toaster",
            "description": "Main toaster block",
            "parts": ["heating_element"],
        },
        {
            "engn_type": "BlockPart",
            "name": "heating_element",
            "block_ref": "HeatingElement",
            "multiplicity": "1",
        },
        {
            "engn_type": "Block",
            "name": "HeatingElement",
            "description": "Component that generates heat",
        },
        # Traceability (Satisfy)
        {
            "engn_type": "Requirement",
            "id": "REQ-001",
            "text": "The toaster shall toast slices of bread to a desired brownness.",
            "kind": "functional",
            "satisfied_by": ["Toaster"],
        },
        {
            "engn_type": "Requirement",
            "id": "REQ-002",
            "text": "The heating element shall reach at least 200 degrees Celsius.",
            "kind": "performance",
            "derived_from": ["REQ-001"],
            "satisfied_by": ["HeatingElement"],
        },
    ]

    # Wait, in SysML-v1 schema, Requirement has properties 'id', 'text', 'kind', etc.
    # The 'engn_type' for these should match the 'name' in the schema's 'type_def'.
    # In sysml_v1_schema.jsonl:
    # {"engn_type": "type_def", "name": "Requirement", ...}
    # So using "engn_type": "Requirement" is correct.

    write_jsonl(model_file, model_items)

    # 3. Run check
    # We need to pass the project_dir as base_path so it finds the imported modules
    # actually run_check(target, base_path)
    capsys.readouterr()  # clear buffer
    run_check(model_file, project_dir)
    captured = capsys.readouterr()
    if "All checks passed!" not in captured.out:
        print(f"Check output:\n{captured.out}")
        with open(model_file, "r") as f:
            print(f"File content:\n{f.read()}")
    assert "All checks passed!" in captured.out

    # 4. Run print
    run_print(model_file, project_dir)
    captured = capsys.readouterr()

    # Verify print output contains key elements
    assert "REQ-001" in captured.out
    assert "The toaster shall toast slices of bread" in captured.out
    assert "Toaster" in captured.out
    assert "HeatingElement" in captured.out
    assert "satisfied_by" in captured.out or "Satisfied By" in captured.out.lower()
