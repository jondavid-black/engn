"""Reusable TreeView component for Flet applications.

This module provides a flexible, extensible TreeView component that can be
used as a base for file browsers, document outlines, and other hierarchical
data displays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, cast

import flet as ft


@dataclass
class TreeNode:
    """Represents a node in the tree hierarchy.

    Attributes:
        id: Unique identifier for the node.
        label: Display text for the node.
        icon: Flet icon to display. Defaults to a file icon.
        is_expanded: Whether the node is expanded (for folders).
        children: List of child TreeNode objects.
        is_folder: Whether this node can contain children.
        data: Optional arbitrary data associated with this node.
    """

    id: str
    label: str
    icon: str = str(ft.Icons.INSERT_DRIVE_FILE)
    is_expanded: bool = False
    children: list[TreeNode] = field(default_factory=list)
    is_folder: bool = False
    data: Any = None


class TreeView(ft.Column):
    """A reusable tree view component with drag-and-drop support.

    This component displays hierarchical data using nested ExpansionTile
    controls. It supports:
    - Recursive tree structure visualization
    - Drag and drop for reorganizing items
    - Delete operations
    - Selection callbacks
    - Customizable appearance

    Example:
        ```python
        tree = TreeView(
            roots=[
                TreeNode(id="1", label="Folder", is_folder=True, children=[
                    TreeNode(id="2", label="File.txt"),
                ]),
            ],
            on_select=lambda node: print(f"Selected: {node.label}"),
        )
        page.add(tree)
        ```
    """

    def __init__(
        self,
        roots: list[TreeNode] | None = None,
        on_move: Callable[[str, str], None] | None = None,
        on_delete: Callable[[str], None] | None = None,
        on_select: Callable[[TreeNode], None] | None = None,
        on_double_click: Callable[[TreeNode], None] | None = None,
        enable_move: bool = True,
        enable_delete: bool = True,
        enable_selection: bool = True,
        indent_size: int = 20,
        show_root_lines: bool = False,
        **kwargs: Any,
    ):
        """Initialize the TreeView.

        Args:
            roots: List of root TreeNode objects to display.
            on_move: Callback when an item is moved. Receives (item_id, new_parent_id).
            on_delete: Callback when an item is deleted. Receives item_id.
            on_select: Callback when an item is selected. Receives the TreeNode.
            on_double_click: Callback when an item is double-clicked. Receives the TreeNode.
            enable_move: Enable drag-and-drop moving of items.
            enable_delete: Show delete buttons on items.
            enable_selection: Enable item selection.
            indent_size: Pixels to indent each level.
            show_root_lines: Show connecting lines between nodes.
            **kwargs: Additional arguments passed to ft.Column.
        """
        super().__init__(**kwargs)
        self.roots = roots or []
        self.on_move = on_move
        self.on_delete = on_delete
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.enable_move = enable_move
        self.enable_delete = enable_delete
        self.enable_selection = enable_selection
        self.indent_size = indent_size
        self.show_root_lines = show_root_lines

        self._selected_node: TreeNode | None = None
        self._node_map: dict[str, TreeNode] = {}

        self.scroll = ft.ScrollMode.AUTO
        self.expand = kwargs.get("expand", True)

    def did_mount(self) -> None:
        """Called when the control is added to the page."""
        self._rebuild_node_map()
        self.render()

    def update_data(self, new_roots: list[TreeNode]) -> None:
        """Update the tree data and refresh the UI.

        Args:
            new_roots: New list of root TreeNode objects.
        """
        self.roots = new_roots
        self._rebuild_node_map()
        self.render()

    def _rebuild_node_map(self) -> None:
        """Rebuild the internal node lookup map."""
        self._node_map.clear()
        self._build_node_map(self.roots)

    def _build_node_map(self, nodes: list[TreeNode]) -> None:
        """Recursively build the node map."""
        for node in nodes:
            self._node_map[node.id] = node
            if node.children:
                self._build_node_map(node.children)

    def get_node(self, node_id: str) -> TreeNode | None:
        """Get a node by its ID.

        Args:
            node_id: The ID of the node to find.

        Returns:
            The TreeNode if found, None otherwise.
        """
        return self._node_map.get(node_id)

    def get_selected(self) -> TreeNode | None:
        """Get the currently selected node.

        Returns:
            The selected TreeNode or None if nothing is selected.
        """
        return self._selected_node

    def select_node(self, node_id: str) -> None:
        """Programmatically select a node.

        Args:
            node_id: The ID of the node to select.
        """
        node = self.get_node(node_id)
        if node:
            self._selected_node = node
            if self.on_select:
                self.on_select(node)
            self.render()

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._selected_node = None
        self.render()

    def expand_node(self, node_id: str) -> None:
        """Expand a folder node.

        Args:
            node_id: The ID of the node to expand.
        """
        node = self.get_node(node_id)
        if node and node.is_folder:
            node.is_expanded = True
            self.render()

    def collapse_node(self, node_id: str) -> None:
        """Collapse a folder node.

        Args:
            node_id: The ID of the node to collapse.
        """
        node = self.get_node(node_id)
        if node and node.is_folder:
            node.is_expanded = False
            self.render()

    def expand_all(self) -> None:
        """Expand all folder nodes."""
        self._set_all_expanded(self.roots, True)
        self.render()

    def collapse_all(self) -> None:
        """Collapse all folder nodes."""
        self._set_all_expanded(self.roots, False)
        self.render()

    def _set_all_expanded(self, nodes: list[TreeNode], expanded: bool) -> None:
        """Recursively set expansion state for all nodes."""
        for node in nodes:
            if node.is_folder:
                node.is_expanded = expanded
                self._set_all_expanded(node.children, expanded)

    def render(self) -> None:
        """Rebuild the visual tree based on current data."""
        self.controls = [self._build_node(node, depth=0) for node in self.roots]
        self.update()

    def _build_node(self, node: TreeNode, depth: int) -> ft.Control:
        """Recursively build the visual representation of a node.

        Args:
            node: The TreeNode to build.
            depth: Current nesting depth for indentation.

        Returns:
            A Flet Control representing the node.
        """
        is_selected = bool(self._selected_node and self._selected_node.id == node.id)

        # Build trailing controls (e.g., delete button)
        trailing = self._build_trailing(node)

        # Build the core tile
        if node.is_folder:
            tile = self._build_folder_tile(node, trailing, is_selected, depth)
        else:
            tile = self._build_leaf_tile(node, trailing, is_selected, depth)

        # Wrap in drag-and-drop if enabled
        if not self.enable_move:
            return tile

        return self._wrap_with_drag_drop(node, tile)

    def _build_trailing(self, node: TreeNode) -> ft.Control | None:
        """Build trailing controls for a node."""
        if not self.enable_delete:
            return None

        def on_delete_click(e: Any) -> None:
            if self.on_delete:
                self.on_delete(node.id)

        return ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.ERROR,
            icon_size=18,
            tooltip="Delete",
            on_click=on_delete_click,
        )

    def _build_folder_tile(
        self,
        node: TreeNode,
        trailing: ft.Control | None,
        is_selected: bool,
        depth: int,
    ) -> ft.ExpansionTile:
        """Build an ExpansionTile for a folder node."""

        def on_click(e: Any) -> None:
            if self.enable_selection:
                self._selected_node = node
                if self.on_select:
                    self.on_select(node)
                self.render()

        def on_expansion_change(e: Any) -> None:
            node.is_expanded = e.data == "true"

        def on_long_press(e: Any) -> None:
            if self.on_double_click:
                self.on_double_click(node)

        title_row = ft.Row(
            controls=[
                ft.Text(
                    node.label,
                    weight=ft.FontWeight.W_500 if is_selected else None,
                ),
            ],
            spacing=0,
        )

        return ft.ExpansionTile(
            title=ft.GestureDetector(
                content=title_row,
                on_tap=on_click,
                on_double_tap=on_long_press,
            ),
            leading=ft.Icon(
                icon=cast(Any, node.icon or ft.Icons.FOLDER),
                color=ft.Colors.PRIMARY if is_selected else None,
            ),
            trailing=trailing,
            expanded=node.is_expanded,
            controls=[self._build_node(child, depth + 1) for child in node.children],
            on_change=on_expansion_change,
            tile_padding=ft.padding.only(left=depth * self.indent_size),
            bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else None,
        )

    def _build_leaf_tile(
        self,
        node: TreeNode,
        trailing: ft.Control | None,
        is_selected: bool,
        depth: int,
    ) -> ft.ListTile:
        """Build a ListTile for a leaf node."""

        def on_click(e: Any) -> None:
            if self.enable_selection:
                self._selected_node = node
                if self.on_select:
                    self.on_select(node)
                self.render()

        def on_double_click_handler(e: Any) -> None:
            if self.on_double_click:
                self.on_double_click(node)

        return ft.ListTile(
            title=ft.Text(
                node.label,
                weight=ft.FontWeight.W_500 if is_selected else None,
            ),
            leading=ft.Icon(
                icon=cast(Any, node.icon),
                color=ft.Colors.PRIMARY if is_selected else None,
            ),
            trailing=trailing,
            on_click=on_click,
            on_long_press=on_double_click_handler,
            content_padding=ft.padding.only(left=depth * self.indent_size + 16),
            bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else None,
        )

    def _wrap_with_drag_drop(self, node: TreeNode, tile: ft.Control) -> ft.Control:
        """Wrap a tile with drag-and-drop functionality."""
        # Create the draggable wrapper
        draggable = ft.Draggable(
            group="tree_item",
            content=tile,
            content_when_dragging=ft.Container(
                content=ft.Text(node.label, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_GREY_400,
                padding=5,
                border_radius=5,
                opacity=0.5,
            ),
        )
        draggable.data = node.id

        # If this is a folder, make it a drop target
        if node.is_folder:
            return ft.DragTarget(
                group="tree_item",
                content=draggable,
                on_accept=lambda e: self._handle_drop(e, target_node=node),
                on_will_accept=self._handle_will_accept,
                on_leave=self._handle_leave,
            )

        return draggable

    def _handle_drop(self, e: Any, target_node: TreeNode) -> None:
        """Handle a drop event on a folder node."""
        if not self.page:
            return

        src_control: Any = cast(Any, self.page).get_control(e.src_id)
        if not src_control:
            return

        moved_item_id = src_control.data

        # Reset visual feedback
        if hasattr(e.control, "content") and hasattr(e.control.content, "content"):
            e.control.content.content.bgcolor = None
            e.control.update()

        # Prevent self-drop
        if moved_item_id != target_node.id and self.on_move:
            self.on_move(moved_item_id, target_node.id)

    def _handle_will_accept(self, e: Any) -> None:
        """Visual feedback when hovering over a valid drop target."""
        if hasattr(e.control, "content") and hasattr(e.control.content, "content"):
            e.control.content.content.bgcolor = (
                ft.Colors.BLUE_200 if e.data == "true" else ft.Colors.RED_200
            )
            e.control.update()

    def _handle_leave(self, e: Any) -> None:
        """Reset visual feedback when leaving a drop target."""
        if hasattr(e.control, "content") and hasattr(e.control.content, "content"):
            e.control.content.content.bgcolor = None
            e.control.update()


# Utility functions for tree manipulation


def find_node_and_parent(
    roots: list[TreeNode],
    target_id: str,
    parent: TreeNode | None = None,
) -> tuple[TreeNode, TreeNode | None, list[TreeNode]] | None:
    """Find a node and its parent in a tree.

    Args:
        roots: List of root nodes to search.
        target_id: ID of the node to find.
        parent: Current parent node (used internally).

    Returns:
        Tuple of (node, parent_node, containing_list) or None if not found.
    """
    for node in roots:
        if node.id == target_id:
            return (node, parent, roots)
        if node.children:
            result = find_node_and_parent(node.children, target_id, node)
            if result:
                return result
    return None


def move_node(
    roots: list[TreeNode],
    item_id: str,
    new_parent_id: str,
    **kwargs: Any,
) -> bool:
    """Move a node to a new parent.

    Args:
        roots: List of root nodes.
        item_id: ID of the node to move.
        new_parent_id: ID of the new parent node.

    Returns:
        True if the move was successful, False otherwise.
    """
    # Find the item to move
    item_result = find_node_and_parent(roots, item_id)
    if not item_result:
        return False
    item, _old_parent, old_list = item_result

    # Find the new parent
    dest_result = find_node_and_parent(roots, new_parent_id)
    if not dest_result:
        return False
    new_parent, _, _ = dest_result

    # Prevent moving a folder into itself or its descendants
    if _is_ancestor(item, new_parent_id):
        return False

    # Execute the move
    old_list.remove(item)
    new_parent.children.append(item)
    new_parent.is_expanded = True

    return True


def _is_ancestor(node: TreeNode, descendant_id: str) -> bool:
    """Check if a node is an ancestor of another node."""
    if node.id == descendant_id:
        return True
    for child in node.children:
        if _is_ancestor(child, descendant_id):
            return True
    return False


def delete_node(roots: list[TreeNode], item_id: str) -> TreeNode | None:
    """Delete a node from the tree.

    Args:
        roots: List of root nodes.
        item_id: ID of the node to delete.

    Returns:
        The deleted TreeNode or None if not found.
    """
    result = find_node_and_parent(roots, item_id)
    if result:
        item, _, parent_list = result
        parent_list.remove(item)
        return item
    return None
