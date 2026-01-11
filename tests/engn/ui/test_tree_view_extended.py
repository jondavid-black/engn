"""Extended unit tests for TreeView component."""

from unittest.mock import MagicMock, patch, PropertyMock

import flet as ft
import pytest

from engn.ui.tree_view import TreeNode, TreeView, move_node, delete_node


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    return page


class TestTreeViewExtended:
    """Extended tests for TreeView."""

    def test_update_data(self, mock_page) -> None:
        """Test update_data refreshes roots and map."""
        tree = TreeView()
        setattr(
            tree, "_Control__page", mock_page
        )  # Manually set page to avoid RuntimeError
        new_roots = [TreeNode(id="1", label="New Root")]

        with patch.object(tree, "render") as mock_render:
            tree.update_data(new_roots)
            assert tree.roots == new_roots
            assert tree.get_node("1") is not None
            mock_render.assert_called_once()

    def test_selection_methods(self, mock_page) -> None:
        """Test select_node and clear_selection."""
        node = TreeNode(id="1", label="Node")
        tree = TreeView(roots=[node])
        setattr(tree, "_Control__page", mock_page)
        tree._rebuild_node_map()

        on_select = MagicMock()
        tree.on_select = on_select

        with patch.object(tree, "render"):
            tree.select_node("1")
            assert tree.get_selected() == node
            on_select.assert_called_once_with(node)

            tree.clear_selection()
            assert tree.get_selected() is None

    def test_expand_collapse_node(self, mock_page) -> None:
        """Test expand_node and collapse_node."""
        node = TreeNode(id="1", label="Folder", is_folder=True)
        tree = TreeView(roots=[node])
        setattr(tree, "_Control__page", mock_page)
        tree._rebuild_node_map()

        with patch.object(tree, "render"):
            tree.expand_node("1")
            assert node.is_expanded is True

            tree.collapse_node("1")
            assert node.is_expanded is False

    def test_expand_collapse_all(self, mock_page) -> None:
        """Test expand_all and collapse_all."""
        nodes = [
            TreeNode(
                id="1",
                label="F1",
                is_folder=True,
                children=[TreeNode(id="2", label="F2", is_folder=True)],
            )
        ]
        tree = TreeView(roots=nodes)
        setattr(tree, "_Control__page", mock_page)
        tree._rebuild_node_map()

        with patch.object(tree, "render"):
            tree.expand_all()
            assert nodes[0].is_expanded is True
            assert nodes[0].children[0].is_expanded is True

            tree.collapse_all()
            assert nodes[0].is_expanded is False
            assert nodes[0].children[0].is_expanded is False

    def test_build_trailing_no_delete(self) -> None:
        """Test _build_trailing returns None when delete is disabled."""
        tree = TreeView(enable_delete=False)
        assert tree._build_trailing(TreeNode(id="1", label="L")) is None

    def test_handle_drop_self_prevented(self, mock_page) -> None:
        """Test that dropping a node on itself is prevented."""
        node = TreeNode(id="1", label="F", is_folder=True)
        tree = TreeView(roots=[node])

        with patch.object(
            TreeView, "page", new_callable=PropertyMock
        ) as mock_tree_page:
            mock_tree_page.return_value = mock_page

            e = MagicMock()
            e.src_id = "src"
            mock_page.get_control.return_value = MagicMock(data="1")  # Same ID

            on_move = MagicMock()
            tree.on_move = on_move

            tree._handle_drop(e, node)
            on_move.assert_not_called()

    def test_move_node_failures(self) -> None:
        """Test move_node failure cases."""
        roots = [TreeNode(id="1", label="F")]
        # Item not found
        assert move_node(roots, "nonexistent", "1") is False
        # Destination not found
        assert move_node(roots, "1", "nonexistent") is False
        # Ancestor check (prevent moving folder into itself)
        assert move_node(roots, "1", "1") is False

    def test_delete_node_not_found(self) -> None:
        """Test delete_node when ID not found."""
        assert delete_node([], "any") is None

    def test_handle_will_accept_visual_feedback(self) -> None:
        """Test visual feedback during drag."""
        tree = TreeView()
        e = MagicMock()
        e.data = "true"
        # Mocking the complex nested structure of e.control.content.content
        e.control.content.content = MagicMock()

        tree._handle_will_accept(e)
        assert e.control.content.content.bgcolor == ft.Colors.BLUE_200
        e.control.update.assert_called_once()

        e.data = "false"
        tree._handle_will_accept(e)
        assert e.control.content.content.bgcolor == ft.Colors.RED_200

    def test_handle_leave_visual_feedback(self) -> None:
        """Test visual feedback reset on leave."""
        tree = TreeView()
        e = MagicMock()
        e.control.content.content = MagicMock()
        e.control.content.content.bgcolor = ft.Colors.BLUE_200

        tree._handle_leave(e)
        assert e.control.content.content.bgcolor is None
        e.control.update.assert_called_once()
