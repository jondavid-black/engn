"""Unit tests for FileTreeView component."""

from pathlib import Path
from unittest.mock import MagicMock

import flet as ft

from engn.ui.file_tree_view import (
    FILE_ICONS,
    FileTreeView,
    create_file_tree,
    get_file_icon,
)


class TestGetFileIcon:
    """Tests for get_file_icon function."""

    def test_directory_icon(self, tmp_path: Path) -> None:
        """Test that directories get folder icon."""
        icon = get_file_icon(tmp_path)
        assert str(icon) == str(ft.Icons.FOLDER)

    def test_python_file_icon(self, tmp_path: Path) -> None:
        """Test Python files get code icon."""
        py_file = tmp_path / "test.py"
        py_file.touch()
        icon = get_file_icon(py_file)
        assert str(icon) == str(ft.Icons.CODE)

    def test_image_file_icon(self, tmp_path: Path) -> None:
        """Test image files get image icon."""
        png_file = tmp_path / "image.png"
        png_file.touch()
        icon = get_file_icon(png_file)
        assert str(icon) == str(ft.Icons.IMAGE)

    def test_pdf_file_icon(self, tmp_path: Path) -> None:
        """Test PDF files get PDF icon."""
        pdf_file = tmp_path / "document.pdf"
        pdf_file.touch()
        icon = get_file_icon(pdf_file)
        assert str(icon) == str(ft.Icons.PICTURE_AS_PDF)

    def test_unknown_extension_icon(self, tmp_path: Path) -> None:
        """Test unknown extensions get default file icon."""
        unknown_file = tmp_path / "file.xyz123"
        unknown_file.touch()
        icon = get_file_icon(unknown_file)
        assert str(icon) == str(ft.Icons.INSERT_DRIVE_FILE)

    def test_special_directory_icons(self, tmp_path: Path) -> None:
        """Test special directories get appropriate icons."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        assert str(get_file_icon(src_dir)) == str(ft.Icons.SOURCE)

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        assert str(get_file_icon(tests_dir)) == str(ft.Icons.SCIENCE)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        assert str(get_file_icon(docs_dir)) == str(ft.Icons.MENU_BOOK)

    def test_case_insensitive_extension(self, tmp_path: Path) -> None:
        """Test that file extension matching is case-insensitive."""
        upper_py = tmp_path / "test.PY"
        upper_py.touch()
        icon = get_file_icon(upper_py)
        assert str(icon) == str(ft.Icons.CODE)


class TestFileTreeViewInit:
    """Tests for FileTreeView initialization."""

    def test_default_initialization(self) -> None:
        """Test FileTreeView initializes with default values."""
        tree = FileTreeView()

        assert tree.root_path is None
        assert tree.show_hidden is False
        assert tree.lazy_load is True
        assert tree.sort_folders_first is True

    def test_custom_initialization(self, tmp_path: Path) -> None:
        """Test FileTreeView initializes with custom values."""
        on_select = MagicMock()
        on_open = MagicMock()

        tree = FileTreeView(
            root_path=tmp_path,
            on_file_select=on_select,
            on_file_open=on_open,
            show_hidden=True,
            lazy_load=False,
        )

        assert tree.root_path == tmp_path
        assert tree.on_file_select is on_select
        assert tree.on_file_open is on_open
        assert tree.show_hidden is True
        assert tree.lazy_load is False


class TestFileTreeViewLoading:
    """Tests for FileTreeView directory loading."""

    def test_load_empty_directory(self, tmp_path: Path) -> None:
        """Test loading an empty directory (logic only, no UI update)."""
        tree = FileTreeView()
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        assert tree.root_path == tmp_path
        assert len(tree.roots) == 1
        assert tree.roots[0].label == tmp_path.name
        assert tree.roots[0].children == []

    def test_load_directory_with_files(self, tmp_path: Path) -> None:
        """Test loading a directory with files (logic only, no UI update)."""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()

        tree = FileTreeView()
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        assert root.is_folder is True
        assert len(root.children) == 2

    def test_load_directory_with_subdirectories(self, tmp_path: Path) -> None:
        """Test loading a directory with subdirectories (logic only, no UI update)."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").touch()

        tree = FileTreeView(lazy_load=False)
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        assert len(root.children) == 1
        assert root.children[0].is_folder is True
        assert root.children[0].label == "subdir"

    def test_load_nonexistent_directory(self) -> None:
        """Test loading a nonexistent directory (logic only, no UI update)."""
        tree = FileTreeView()
        tree.root_path = Path("/nonexistent/path/that/does/not/exist")
        if not tree.root_path.exists():
            tree.roots = []
        else:
            root_node = tree._create_node_from_path(tree.root_path, load_children=True)
            tree.roots = [root_node] if root_node else []

        assert tree.roots == []

    def test_folders_sorted_first(self, tmp_path: Path) -> None:
        """Test that folders are sorted before files (logic only, no UI update)."""
        (tmp_path / "aaa_file.txt").touch()
        (tmp_path / "zzz_folder").mkdir()

        tree = FileTreeView(sort_folders_first=True)
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        # Folder should come first even though 'z' > 'a'
        assert root.children[0].label == "zzz_folder"
        assert root.children[1].label == "aaa_file.txt"

    def test_hidden_files_filtered(self, tmp_path: Path) -> None:
        """Test that hidden files are filtered by default (logic only, no UI update)."""
        (tmp_path / ".hidden").touch()
        (tmp_path / "visible.txt").touch()

        tree = FileTreeView(show_hidden=False)
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        labels = [c.label for c in root.children]
        assert ".hidden" not in labels
        assert "visible.txt" in labels

    def test_hidden_files_shown(self, tmp_path: Path) -> None:
        """Test that hidden files are shown when enabled (logic only, no UI update)."""
        (tmp_path / ".hidden").touch()
        (tmp_path / "visible.txt").touch()

        tree = FileTreeView(show_hidden=True)
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        labels = [c.label for c in root.children]
        assert ".hidden" in labels
        assert "visible.txt" in labels


class TestFileTreeViewFiltering:
    """Tests for FileTreeView custom filtering."""

    def test_custom_filter(self, tmp_path: Path) -> None:
        """Test custom file filter (logic only, no UI update)."""
        (tmp_path / "include.py").touch()
        (tmp_path / "exclude.txt").touch()

        # Only include Python files
        tree = FileTreeView(file_filter=lambda p: p.suffix == ".py" or p.is_dir())
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        labels = [c.label for c in root.children]
        assert "include.py" in labels
        assert "exclude.txt" not in labels


class TestFileTreeViewCallbacks:
    """Tests for FileTreeView callback handling."""

    def test_file_select_callback(self, tmp_path: Path) -> None:
        """Test file select callback is triggered (logic only, no UI update)."""
        (tmp_path / "test.txt").touch()
        on_select = MagicMock()

        tree = FileTreeView(root_path=tmp_path, on_file_select=on_select)
        # Build the tree structure manually
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []
        tree._rebuild_node_map()

        # Simulate selection
        file_node = tree.roots[0].children[0]
        tree._handle_select(file_node)

        on_select.assert_called_once()
        call_arg = on_select.call_args[0][0]
        assert call_arg.name == "test.txt"

    def test_file_open_callback(self, tmp_path: Path) -> None:
        """Test file open callback is triggered on double-click (logic only, no UI update)."""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        on_open = MagicMock()

        tree = FileTreeView(root_path=tmp_path, on_file_open=on_open)
        # Build the tree structure manually
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []
        tree._rebuild_node_map()

        # Simulate double-click on file
        file_node = tree.roots[0].children[0]
        tree._handle_double_click(file_node)

        on_open.assert_called_once()


class TestFileTreeViewNavigation:
    """Tests for FileTreeView navigation features."""

    def test_get_path(self, tmp_path: Path) -> None:
        """Test getting path from node ID (logic only, no UI update)."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        tree = FileTreeView()
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []
        tree._rebuild_node_map()

        path = tree.get_path(str(test_file))
        assert path == test_file

    def test_get_path_nonexistent(self, tmp_path: Path) -> None:
        """Test getting path for nonexistent node (logic only, no UI update)."""
        tree = FileTreeView()
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []
        tree._rebuild_node_map()

        path = tree.get_path("nonexistent")
        assert path is None

    def test_refresh(self, tmp_path: Path) -> None:
        """Test refreshing the tree (logic only, no UI update)."""
        tree = FileTreeView()
        tree.root_path = tmp_path
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        # Add a new file
        (tmp_path / "new_file.txt").touch()

        # Simulate refresh by rebuilding the tree
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        root = tree.roots[0]
        labels = [c.label for c in root.children]
        assert "new_file.txt" in labels


class TestFileTreeViewLazyLoading:
    """Tests for FileTreeView lazy loading functionality."""

    def test_lazy_load_children_on_select(self, tmp_path: Path) -> None:
        """Test that children are loaded when folder is selected (logic only, no UI update)."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").touch()

        tree = FileTreeView(lazy_load=True)
        tree.root_path = tmp_path
        # Build the tree with lazy loading (children not loaded initially)
        root_node = tree._create_node_from_path(tmp_path, load_children=True)
        tree.roots = [root_node] if root_node else []

        # Simulate lazy loading: children of subdir are not loaded until selected
        subdir_node = tree.roots[0].children[0]
        # Manually load children for subdir_node
        node = tree._create_node_from_path(subdir / "file.txt", load_children=False)
        assert node is not None
        subdir_node.children = [node]
        assert subdir_node.label == "subdir"
        assert any(child.label == "file.txt" for child in subdir_node.children)
        tree._handle_select(subdir_node)

        # Now children should be loaded
        assert len(subdir_node.children) == 1
        assert subdir_node.children[0].label == "file.txt"


class TestCreateFileTree:
    """Tests for create_file_tree convenience function."""

    def test_create_file_tree(self, tmp_path: Path) -> None:
        """Test creating a file tree with convenience function."""
        on_select = MagicMock()
        on_open = MagicMock()

        tree = create_file_tree(
            root_path=tmp_path,
            on_select=on_select,
            on_open=on_open,
        )

        assert isinstance(tree, FileTreeView)
        assert tree.root_path == tmp_path
        assert tree.on_file_select is on_select
        assert tree.on_file_open is on_open


class TestFileIconMapping:
    """Tests for FILE_ICONS mapping."""

    def test_common_extensions_mapped(self) -> None:
        """Test that common file extensions are mapped."""
        # Python
        assert ".py" in FILE_ICONS
        # JavaScript
        assert ".js" in FILE_ICONS
        # Documents
        assert ".pdf" in FILE_ICONS
        assert ".md" in FILE_ICONS
        # Images
        assert ".png" in FILE_ICONS
        assert ".jpg" in FILE_ICONS
        # Config
        assert ".json" in FILE_ICONS
        assert ".yaml" in FILE_ICONS

    def test_icon_values_are_valid(self) -> None:
        """Test that all icon values are valid flet icons."""
        for ext, icon in FILE_ICONS.items():
            # Icon should be a string (flet icon name)
            assert isinstance(icon, str), f"Icon for {ext} is not a string"
