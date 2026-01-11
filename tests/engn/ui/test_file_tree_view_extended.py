"""Extended unit tests for FileTreeView component."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import flet as ft
import pytest

from engn.ui.file_tree_view import FileTreeView, get_file_icon


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    return page


class TestFileTreeViewExtended:
    """Extended tests for FileTreeView."""

    def test_special_directory_icons_more(self, tmp_path: Path) -> None:
        """Test more special directories get appropriate icons."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        assert str(get_file_icon(git_dir)) == str(ft.Icons.SOURCE)

        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        assert str(get_file_icon(node_modules)) == str(ft.Icons.FOLDER_OFF)

        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        assert str(get_file_icon(pycache)) == str(ft.Icons.FOLDER_OFF)

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        assert str(get_file_icon(config_dir)) == str(ft.Icons.SETTINGS)

    def test_did_mount(self, tmp_path: Path, mock_page) -> None:
        """Test did_mount loads directory."""
        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page  # Manually set page to avoid RuntimeError
        with (
            patch.object(tree, "load_directory") as mock_load,
            patch.object(tree, "render"),
        ):
            tree.did_mount()
            mock_load.assert_called_once_with(tmp_path)

    def test_refresh_call(self, tmp_path: Path, mock_page) -> None:
        """Test refresh calls load_directory."""
        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page
        with patch.object(tree, "load_directory") as mock_load:
            tree.refresh()
            mock_load.assert_called_once_with(tmp_path)

    def test_handle_double_click_folder(self, tmp_path: Path, mock_page) -> None:
        """Test double clicking a folder toggles expansion."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page

        with patch.object(tree, "update"):  # Mock update to avoid Flet internals
            tree.load_directory(tmp_path)

            # Get the subdir node
            subdir_node = tree.roots[0].children[0]
            assert subdir_node.is_expanded is False

            tree._handle_double_click(subdir_node)
            assert subdir_node.is_expanded is True

            tree._handle_double_click(subdir_node)
            assert subdir_node.is_expanded is False

    def test_handle_move_with_callback(self, tmp_path: Path, mock_page) -> None:
        """Test move with callback."""
        on_move = MagicMock(return_value=True)
        tree = FileTreeView(root_path=tmp_path, on_file_move=on_move)
        tree._Control__page = mock_page

        with patch.object(tree, "update"):
            tree.load_directory(tmp_path)

            src = str(tmp_path / "file.txt")
            dest = str(tmp_path / "subdir")

            with (
                patch("engn.ui.file_tree_view.move_node") as mock_move_node,
                patch.object(tree, "_rebuild_node_map"),
            ):
                tree._handle_move(src, dest)
                on_move.assert_called_once()
                mock_move_node.assert_called_once()

    def test_handle_move_no_callback(self, tmp_path: Path, mock_page) -> None:
        """Test move without callback."""
        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page

        with patch.object(tree, "update"):
            tree.load_directory(tmp_path)

            src = str(tmp_path / "file.txt")
            dest = str(tmp_path / "subdir")

            with (
                patch("engn.ui.file_tree_view.move_node") as mock_move_node,
                patch.object(tree, "_rebuild_node_map"),
            ):
                tree._handle_move(src, dest)
                mock_move_node.assert_called_once()

    def test_handle_delete_with_callback(self, tmp_path: Path, mock_page) -> None:
        """Test delete with callback."""
        on_delete = MagicMock(return_value=True)
        tree = FileTreeView(root_path=tmp_path, on_file_delete=on_delete)
        tree._Control__page = mock_page

        with patch.object(tree, "update"):
            tree.load_directory(tmp_path)

            path_str = str(tmp_path / "file.txt")

            with (
                patch("engn.ui.file_tree_view.delete_node") as mock_delete_node,
                patch.object(tree, "_rebuild_node_map"),
            ):
                tree._handle_delete(path_str)
                on_delete.assert_called_once()
                mock_delete_node.assert_called_once()

    def test_handle_delete_no_callback(self, tmp_path: Path, mock_page) -> None:
        """Test delete without callback."""
        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page

        with patch.object(tree, "update"):
            tree.load_directory(tmp_path)

            path_str = str(tmp_path / "file.txt")

            with (
                patch("engn.ui.file_tree_view.delete_node") as mock_delete_node,
                patch.object(tree, "_rebuild_node_map"),
            ):
                tree._handle_delete(path_str)
                mock_delete_node.assert_called_once()

    def test_expand_to_path(self, tmp_path: Path, mock_page) -> None:
        """Test expand_to_path functionality."""
        subdir = tmp_path / "a" / "b"
        subdir.mkdir(parents=True)
        target = subdir / "c.txt"
        target.touch()

        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page

        with patch.object(tree, "update"), patch.object(tree, "select_node"):
            tree.load_directory(tmp_path)
            tree.expand_to_path(target)

            # Check if intermediate nodes are expanded
            node_a = tree._path_to_node.get(str(tmp_path / "a"))
            assert node_a is not None
            assert node_a.is_expanded is True

            node_b = tree._path_to_node.get(str(tmp_path / "a" / "b"))
            assert node_b is not None
            assert node_b.is_expanded is True

            tree.select_node.assert_called_once_with(str(target))

    def test_expand_to_path_no_root(self) -> None:
        """Test expand_to_path when root_path is None."""
        tree = FileTreeView()
        tree.expand_to_path("/some/path")  # Should return early without error

    def test_expand_to_path_outside_root(self, tmp_path: Path, mock_page) -> None:
        """Test expand_to_path for a path outside root."""
        tree = FileTreeView(root_path=tmp_path)
        tree._Control__page = mock_page
        with patch.object(tree, "update"):
            tree.load_directory(tmp_path)
            tree.expand_to_path(
                "/outside/path"
            )  # Should return early via relative_to ValueError
