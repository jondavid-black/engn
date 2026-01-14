import json
import pytest
from pathlib import Path
from pydantic import ValidationError

from engn.data.models import Import
from engn.main import run_check, run_print


class TestImportModel:
    """Tests for the Import model validation."""

    def test_import_with_files(self):
        """Test valid import with files list."""
        imp = Import(files=["types.jsonl", "enums.jsonl"])
        assert imp.engn_type == "import"
        assert imp.files == ["types.jsonl", "enums.jsonl"]
        assert imp.module is None

    def test_import_with_module(self):
        """Test valid import with module name."""
        imp = Import(module="my_module.types")
        assert imp.engn_type == "import"
        assert imp.files is None
        assert imp.module == "my_module.types"

    def test_import_requires_files_or_module(self):
        """Test that import must have either files or module."""
        with pytest.raises(ValidationError, match="must specify either 'files' or 'module'"):
            Import()

    def test_import_cannot_have_both_files_and_module(self):
        """Test that import cannot have both files and module."""
        with pytest.raises(ValidationError, match="cannot specify both 'files' and 'module'"):
            Import(files=["types.jsonl"], module="my_module")

    def test_import_with_empty_files_list(self):
        """Test that empty files list is invalid."""
        with pytest.raises(ValidationError, match="must specify either 'files' or 'module'"):
            Import(files=[])

    def test_import_json_parsing(self):
        """Test parsing import from JSON."""
        json_str = '{"engn_type": "import", "files": ["base.jsonl"]}'
        imp = Import.model_validate_json(json_str)
        assert imp.files == ["base.jsonl"]

    def test_import_module_json_parsing(self):
        """Test parsing module import from JSON."""
        json_str = '{"engn_type": "import", "module": "engn.schemas.core"}'
        imp = Import.model_validate_json(json_str)
        assert imp.module == "engn.schemas.core"


class TestImportInCheck:
    """Tests for import handling in run_check."""

    def test_check_with_file_import(self, tmp_path, capsys):
        """Test that imported files are included in check."""
        # Create base types file
        base_file = tmp_path / "base.jsonl"
        base_file.write_text('{"engn_type": "enum", "name": "Status", "values": ["open", "closed"]}\n')

        # Create main file that imports base
        main_file = tmp_path / "main.jsonl"
        main_file.write_text(
            '{"engn_type": "import", "files": ["base.jsonl"]}\n'
            '{"engn_type": "type_def", "name": "Task", "properties": [{"name": "status", "type": "Status"}]}\n'
        )

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "All checks passed!" in captured.out

    def test_check_without_import_fails(self, tmp_path, capsys):
        """Test that without import, type reference fails."""
        # Create main file that uses Status without importing it
        main_file = tmp_path / "main.jsonl"
        main_file.write_text(
            '{"engn_type": "type_def", "name": "Task", "properties": [{"name": "status", "type": "Status"}]}\n'
        )

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "Unknown type 'Status'" in captured.out

    def test_check_missing_imported_file(self, tmp_path, capsys):
        """Test error when imported file doesn't exist."""
        main_file = tmp_path / "main.jsonl"
        main_file.write_text('{"engn_type": "import", "files": ["nonexistent.jsonl"]}\n')

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "Imported file not found: nonexistent.jsonl" in captured.out

    def test_check_circular_import(self, tmp_path, capsys):
        """Test that circular imports are handled gracefully."""
        # Create two files that import each other
        file_a = tmp_path / "a.jsonl"
        file_b = tmp_path / "b.jsonl"

        file_a.write_text(
            '{"engn_type": "import", "files": ["b.jsonl"]}\n'
            '{"engn_type": "enum", "name": "EnumA", "values": ["a"]}\n'
        )
        file_b.write_text(
            '{"engn_type": "import", "files": ["a.jsonl"]}\n'
            '{"engn_type": "enum", "name": "EnumB", "values": ["b"]}\n'
        )

        run_check(file_a, tmp_path)
        captured = capsys.readouterr()
        # Should pass - circular imports don't cause infinite loops
        assert "All checks passed!" in captured.out

    def test_check_relative_import_path(self, tmp_path, capsys):
        """Test that relative import paths are resolved from importing file."""
        # Create subdirectory with base types
        subdir = tmp_path / "types"
        subdir.mkdir()
        base_file = subdir / "base.jsonl"
        base_file.write_text('{"engn_type": "enum", "name": "Priority", "values": ["low", "high"]}\n')

        # Create main file in parent dir that imports from subdir
        main_file = tmp_path / "main.jsonl"
        main_file.write_text(
            '{"engn_type": "import", "files": ["types/base.jsonl"]}\n'
            '{"engn_type": "type_def", "name": "Task", "properties": [{"name": "priority", "type": "Priority"}]}\n'
        )

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "All checks passed!" in captured.out

    def test_check_module_import_no_action(self, tmp_path, capsys):
        """Test that module imports don't cause errors (no action taken)."""
        main_file = tmp_path / "main.jsonl"
        main_file.write_text('{"engn_type": "import", "module": "some.module"}\n')

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "All checks passed!" in captured.out


class TestImportInPrint:
    """Tests for import handling in run_print."""

    def test_print_processes_imported_files(self, tmp_path, capsys):
        """Test that print command processes imported files."""
        # Create base types file
        base_file = tmp_path / "base.jsonl"
        base_file.write_text('{"engn_type": "enum", "name": "Status", "values": ["open", "closed"]}\n')

        # Create import file (separate from type definitions)
        import_file = tmp_path / "imports.jsonl"
        import_file.write_text('{"engn_type": "import", "files": ["base.jsonl"]}\n')

        # Create types file with TypeDef
        types_file = tmp_path / "types.jsonl"
        types_file.write_text('{"engn_type": "type_def", "name": "Task", "properties": [{"name": "status", "type": "Status"}]}\n')

        # Process the imports file first (which will pull in base.jsonl)
        # Then process the types file
        run_print(tmp_path, tmp_path)
        captured = capsys.readouterr()
        # Content from imported and direct files should be shown
        assert "[Enum] Status" in captured.out
        assert "[Type] Task" in captured.out

    def test_print_resolves_types_across_imports(self, tmp_path, capsys):
        """Test that types from imported files are available for resolution."""
        # Create base types file with enum
        base_file = tmp_path / "base.jsonl"
        base_file.write_text('{"engn_type": "enum", "name": "Priority", "values": ["low", "medium", "high"]}\n')

        # Create import file
        import_file = tmp_path / "imports.jsonl"
        import_file.write_text('{"engn_type": "import", "files": ["base.jsonl"]}\n')

        # Create types file that uses imported type
        types_file = tmp_path / "types.jsonl"
        types_file.write_text('{"engn_type": "type_def", "name": "Task", "properties": [{"name": "priority", "type": "Priority"}]}\n')

        run_print(tmp_path, tmp_path)
        captured = capsys.readouterr()
        # Type should be properly displayed with imported enum type
        assert "[Enum] Priority" in captured.out
        assert "[Type] Task" in captured.out
        assert "priority: Priority" in captured.out

    def test_print_chained_imports(self, tmp_path, capsys):
        """Test that chained imports (A imports B, B imports C) work."""
        # Create base file
        file_c = tmp_path / "c.jsonl"
        file_c.write_text('{"engn_type": "enum", "name": "Level", "values": ["1", "2", "3"]}\n')

        # Create intermediate file that imports base (only import directive)
        file_b = tmp_path / "b.jsonl"
        file_b.write_text('{"engn_type": "import", "files": ["c.jsonl"]}\n')

        # Create another file with enum
        file_d = tmp_path / "d.jsonl"
        file_d.write_text('{"engn_type": "enum", "name": "Category", "values": ["a", "b"]}\n')

        # Create main file that imports intermediate
        file_a = tmp_path / "a.jsonl"
        file_a.write_text('{"engn_type": "import", "files": ["b.jsonl", "d.jsonl"]}\n')

        run_print(file_a, tmp_path)
        captured = capsys.readouterr()
        # All files in chain should be processed
        assert "[Enum] Level" in captured.out
        assert "[Enum] Category" in captured.out
