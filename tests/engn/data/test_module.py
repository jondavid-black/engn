from engn.data.models import Module, _MODULE_REGISTRY
from engn.main import run_check, run_print


def setup_function():
    """Clear the module registry before each test."""
    _MODULE_REGISTRY.clear()


class TestModuleModel:
    """Tests for the Module model validation."""

    def test_module_creation(self):
        """Test valid module creation."""
        mod = Module(name="Base", files=["base.jsonl", "common.jsonl"])
        assert mod.engn_type == "module"
        assert mod.name == "Base"
        assert mod.files == ["base.jsonl", "common.jsonl"]
        assert _MODULE_REGISTRY["Base"] == mod

    def test_module_json_parsing(self):
        """Test parsing module from JSON."""
        json_str = '{"engn_type": "module", "name": "Core", "files": ["core.jsonl"]}'
        mod = Module.model_validate_json(json_str)
        assert mod.name == "Core"
        assert mod.files == ["core.jsonl"]
        assert _MODULE_REGISTRY["Core"] == mod


class TestModuleInCheck:
    """Tests for module handling in run_check."""

    def test_check_with_module_import(self, tmp_path, capsys):
        """Test that imported modules resolve to their files in check."""
        # Create the file referenced by the module
        base_file = tmp_path / "base.jsonl"
        base_file.write_text(
            '{"engn_type": "enum", "name": "Status", "values": ["open", "closed"]}\n'
        )

        # Create main file that defines a module and imports it
        main_file = tmp_path / "main.jsonl"
        main_file.write_text(
            '{"engn_type": "module", "name": "BaseModule", "files": ["base.jsonl"]}\n'
            '{"engn_type": "import", "modules": ["BaseModule"]}\n'
            '{"engn_type": "type_def", "name": "Task", "properties": [{"name": "status", "type": "Status"}]}\n'
        )

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "All checks passed!" in captured.out

    def test_check_with_missing_module_fails(self, tmp_path, capsys):
        """Test that importing a non-existent module fails."""
        main_file = tmp_path / "main.jsonl"
        main_file.write_text('{"engn_type": "import", "modules": ["NonExistent"]}\n')

        run_check(main_file, tmp_path)
        captured = capsys.readouterr()
        assert "Module not found: NonExistent" in captured.out


class TestModuleInPrint:
    """Tests for module handling in run_print."""

    def test_print_processes_module_imports(self, tmp_path, capsys):
        """Test that print command processes files from imported modules."""
        # Create the file referenced by the module
        base_file = tmp_path / "base.jsonl"
        base_file.write_text(
            '{"engn_type": "enum", "name": "Status", "values": ["open", "closed"]}\n'
        )

        # Create file with module definition
        module_def_file = tmp_path / "mod_def.jsonl"
        module_def_file.write_text(
            '{"engn_type": "module", "name": "MyMod", "files": ["base.jsonl"]}\n'
        )

        # Create main file that imports the module
        main_file = tmp_path / "main.jsonl"
        main_file.write_text('{"engn_type": "import", "modules": ["MyMod"]}\n')

        # We need to make sure mod_def.jsonl is processed so MyMod is registered
        run_print(tmp_path, tmp_path)
        captured = capsys.readouterr()

        assert "[Module] MyMod" in captured.out
        assert "[Enum] Status" in captured.out
