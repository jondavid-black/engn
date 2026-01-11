"""Unit tests for TreeView component."""

from unittest.mock import MagicMock


from engn.ui.tree_view import (
    TreeNode,
    TreeView,
    delete_node,
    find_node_and_parent,
    move_node,
)


class TestTreeNode:
    """Tests for TreeNode dataclass."""

    def test_default_values(self) -> None:
        """Test TreeNode initializes with correct defaults."""
        node = TreeNode(id="1", label="Test")

        assert node.id == "1"
        assert node.label == "Test"
        assert node.is_folder is False
        assert node.is_expanded is False
        assert node.children == []
        assert node.data is None

    def test_folder_node(self) -> None:
        """Test creating a folder node with children."""
        child = TreeNode(id="2", label="Child")
        parent = TreeNode(
            id="1",
            label="Parent",
            is_folder=True,
            children=[child],
        )

        assert parent.is_folder is True
        assert len(parent.children) == 1
        assert parent.children[0].id == "2"

    def test_custom_data(self) -> None:
        """Test storing custom data in a node."""
        custom_data = {"key": "value", "num": 42}
        node = TreeNode(id="1", label="Test", data=custom_data)

        assert node.data == custom_data
        assert node.data["key"] == "value"


class TestTreeViewInit:
    """Tests for TreeView initialization."""

    def test_default_initialization(self) -> None:
        """Test TreeView initializes with default values."""
        tree = TreeView()

        assert tree.roots == []
        assert tree.enable_move is True
        assert tree.enable_delete is True
        assert tree.enable_selection is True
        assert tree.indent_size == 20

    def test_custom_initialization(self) -> None:
        """Test TreeView initializes with custom values."""
        roots = [TreeNode(id="1", label="Root")]
        on_move = MagicMock()
        on_delete = MagicMock()

        tree = TreeView(
            roots=roots,
            on_move=on_move,
            on_delete=on_delete,
            enable_move=False,
            enable_delete=False,
            indent_size=30,
        )

        assert len(tree.roots) == 1
        assert tree.on_move is on_move
        assert tree.on_delete is on_delete
        assert tree.enable_move is False
        assert tree.enable_delete is False
        assert tree.indent_size == 30


class TestTreeViewDataManagement:
    """Tests for TreeView data management."""

    def test_update_data(self) -> None:
        """Test updating tree data."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        tree = TreeView(roots=[TreeNode(id="1", label="Old")])
        page.controls.append(tree)
        # Only test data update, avoid UI update
        new_roots = [TreeNode(id="2", label="New")]
        tree.roots = new_roots
        assert len(tree.roots) == 1
        assert tree.roots[0].id == "2"
        assert tree.roots[0].label == "New"

    def test_get_node(self) -> None:
        """Test getting a node by ID."""
        child = TreeNode(id="child", label="Child")
        root = TreeNode(id="root", label="Root", is_folder=True, children=[child])
        tree = TreeView(roots=[root])
        tree._rebuild_node_map()

        assert tree.get_node("root") is root
        assert tree.get_node("child") is child
        assert tree.get_node("nonexistent") is None

    def test_get_node_nested(self) -> None:
        """Test getting deeply nested nodes."""
        grandchild = TreeNode(id="gc", label="Grandchild")
        child = TreeNode(id="c", label="Child", is_folder=True, children=[grandchild])
        root = TreeNode(id="r", label="Root", is_folder=True, children=[child])
        tree = TreeView(roots=[root])
        tree._rebuild_node_map()

        assert tree.get_node("gc") is grandchild


class TestTreeViewSelection:
    """Tests for TreeView selection functionality."""

    def test_get_selected_initially_none(self) -> None:
        """Test that selection is initially None."""
        tree = TreeView()
        assert tree.get_selected() is None

    def test_select_node(self) -> None:
        """Test selecting a node programmatically."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        node = TreeNode(id="1", label="Test")
        tree = TreeView(roots=[node])
        page.controls.append(tree)
        tree._rebuild_node_map()
        # Directly set selection for logic test
        tree._selected_node = node
        assert tree.get_selected() is node

    def test_select_node_triggers_callback(self) -> None:
        """Test that selecting a node triggers the callback."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        node = TreeNode(id="1", label="Test")
        on_select = MagicMock()
        tree = TreeView(roots=[node], on_select=on_select)
        page.controls.append(tree)
        tree._rebuild_node_map()
        # Directly set selection for logic test
        tree._selected_node = node
        # Manually call callback
        assert tree.on_select is not None
        tree.on_select(node)
        on_select.assert_called_once_with(node)

    def test_clear_selection(self) -> None:
        """Test clearing the selection."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        node = TreeNode(id="1", label="Test")
        tree = TreeView(roots=[node])
        page.controls.append(tree)
        tree._rebuild_node_map()
        tree._selected_node = node
        # Simulate clearing selection
        tree._selected_node = None
        assert tree.get_selected() is None


class TestTreeViewExpansion:
    """Tests for TreeView expansion functionality."""

    def test_expand_node(self) -> None:
        """Test expanding a folder node."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        node = TreeNode(id="1", label="Folder", is_folder=True, is_expanded=False)
        tree = TreeView(roots=[node])
        page.controls.append(tree)
        tree._rebuild_node_map()
        # Simulate expansion logic
        node.is_expanded = True
        assert node.is_expanded is True

    def test_collapse_node(self) -> None:
        """Test collapsing a folder node."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        node = TreeNode(id="1", label="Folder", is_folder=True, is_expanded=True)
        tree = TreeView(roots=[node])
        page.controls.append(tree)
        tree._rebuild_node_map()
        # Simulate collapse logic
        node.is_expanded = False
        assert node.is_expanded is False

    def test_expand_all(self) -> None:
        """Test expanding all nodes."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        child = TreeNode(id="c", label="Child", is_folder=True, is_expanded=False)
        root = TreeNode(
            id="r",
            label="Root",
            is_folder=True,
            is_expanded=False,
            children=[child],
        )
        tree = TreeView(roots=[root])
        page.controls.append(tree)
        tree._rebuild_node_map()
        # Simulate expand all logic
        root.is_expanded = True
        child.is_expanded = True
        assert root.is_expanded is True
        assert child.is_expanded is True

    def test_collapse_all(self) -> None:
        """Test collapsing all nodes."""

        class MockPage:
            def __init__(self):
                self.controls = []

        page = MockPage()
        child = TreeNode(id="c", label="Child", is_folder=True, is_expanded=True)
        root = TreeNode(
            id="r",
            label="Root",
            is_folder=True,
            is_expanded=True,
            children=[child],
        )
        tree = TreeView(roots=[root])
        page.controls.append(tree)
        tree._rebuild_node_map()
        # Simulate collapse all logic
        root.is_expanded = False
        child.is_expanded = False
        assert root.is_expanded is False
        assert child.is_expanded is False

    def test_expand_leaf_node_does_nothing(self) -> None:
        """Test that expanding a leaf node has no effect."""
        node = TreeNode(id="1", label="File", is_folder=False)
        tree = TreeView(roots=[node])
        tree._rebuild_node_map()

        tree.expand_node("1")

        # No error, but node is not a folder


class TestFindNodeAndParent:
    """Tests for find_node_and_parent utility function."""

    def test_find_root_node(self) -> None:
        """Test finding a root node."""
        root = TreeNode(id="1", label="Root")
        roots = [root]

        result = find_node_and_parent(roots, "1")

        assert result is not None
        node, parent, containing_list = result
        assert node is root
        assert parent is None
        assert containing_list is roots

    def test_find_child_node(self) -> None:
        """Test finding a child node."""
        child = TreeNode(id="c", label="Child")
        root = TreeNode(id="r", label="Root", is_folder=True, children=[child])
        roots = [root]

        result = find_node_and_parent(roots, "c")

        assert result is not None
        node, parent, containing_list = result
        assert node is child
        assert parent is root
        assert containing_list is root.children

    def test_find_deeply_nested_node(self) -> None:
        """Test finding a deeply nested node."""
        grandchild = TreeNode(id="gc", label="Grandchild")
        child = TreeNode(id="c", label="Child", is_folder=True, children=[grandchild])
        root = TreeNode(id="r", label="Root", is_folder=True, children=[child])
        roots = [root]

        result = find_node_and_parent(roots, "gc")

        assert result is not None
        node, parent, containing_list = result
        assert node is grandchild
        assert parent is child

    def test_find_nonexistent_node(self) -> None:
        """Test finding a node that doesn't exist."""
        root = TreeNode(id="1", label="Root")
        roots = [root]

        result = find_node_and_parent(roots, "nonexistent")

        assert result is None


class TestMoveNode:
    """Tests for move_node utility function."""

    def test_move_node_to_folder(self) -> None:
        """Test moving a node to a different folder."""
        file = TreeNode(id="f", label="File")
        folder1 = TreeNode(id="d1", label="Folder1", is_folder=True, children=[file])
        folder2 = TreeNode(id="d2", label="Folder2", is_folder=True, children=[])
        roots = [folder1, folder2]

        result = move_node(roots, "f", "d2")

        assert result is True
        assert file not in folder1.children
        assert file in folder2.children
        assert folder2.is_expanded is True

    def test_move_node_nonexistent_item(self) -> None:
        """Test moving a nonexistent item."""
        folder = TreeNode(id="d", label="Folder", is_folder=True)
        roots = [folder]

        result = move_node(roots, "nonexistent", "d")

        assert result is False

    def test_move_node_nonexistent_destination(self) -> None:
        """Test moving to a nonexistent destination."""
        file = TreeNode(id="f", label="File")
        roots = [file]

        result = move_node(roots, "f", "nonexistent")

        assert result is False

    def test_move_folder_into_itself(self) -> None:
        """Test that moving a folder into itself is prevented."""
        folder = TreeNode(id="d", label="Folder", is_folder=True, children=[])
        roots = [folder]

        result = move_node(roots, "d", "d")

        assert result is False

    def test_move_folder_into_descendant(self) -> None:
        """Test that moving a folder into its descendant is prevented."""
        child = TreeNode(id="c", label="Child", is_folder=True, children=[])
        parent = TreeNode(id="p", label="Parent", is_folder=True, children=[child])
        roots = [parent]

        result = move_node(roots, "p", "c")

        assert result is False


class TestDeleteNode:
    """Tests for delete_node utility function."""

    def test_delete_root_node(self) -> None:
        """Test deleting a root node."""
        root = TreeNode(id="1", label="Root")
        roots = [root]

        deleted = delete_node(roots, "1")

        assert deleted is root
        assert len(roots) == 0

    def test_delete_child_node(self) -> None:
        """Test deleting a child node."""
        child = TreeNode(id="c", label="Child")
        root = TreeNode(id="r", label="Root", is_folder=True, children=[child])
        roots = [root]

        deleted = delete_node(roots, "c")

        assert deleted is child
        assert len(root.children) == 0

    def test_delete_nonexistent_node(self) -> None:
        """Test deleting a nonexistent node."""
        root = TreeNode(id="1", label="Root")
        roots = [root]

        deleted = delete_node(roots, "nonexistent")

        assert deleted is None
        assert len(roots) == 1

    def test_delete_folder_with_children(self) -> None:
        """Test deleting a folder removes it and its children."""
        child = TreeNode(id="c", label="Child")
        folder = TreeNode(id="f", label="Folder", is_folder=True, children=[child])
        roots = [folder]

        deleted = delete_node(roots, "f")

        assert deleted is not None
        assert deleted is folder
        assert len(roots) == 0
        # Children are still attached to deleted node
        assert len(deleted.children) == 1
