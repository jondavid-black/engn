"""Document outline tree view component for Flet applications.

This module provides a specialized TreeView for displaying document
structure outlines, such as headings in a markdown file, sections in
a code file, or chapters in a document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import flet as ft

from engn.ui.tree_view import TreeNode, TreeView


class OutlineItemType(Enum):
    """Types of outline items."""

    # Document structure
    HEADING = "heading"
    SECTION = "section"
    CHAPTER = "chapter"
    PARAGRAPH = "paragraph"

    # Code structure
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    MODULE = "module"
    NAMESPACE = "namespace"
    INTERFACE = "interface"
    ENUM = "enum"
    TYPE = "type"

    # Generic
    ITEM = "item"
    GROUP = "group"
    BOOKMARK = "bookmark"
    ANNOTATION = "annotation"


# Icon mapping for outline item types
OUTLINE_ICONS: dict[OutlineItemType, str] = {
    # Document structure
    OutlineItemType.HEADING: str(ft.Icons.TITLE),
    OutlineItemType.SECTION: str(ft.Icons.SEGMENT),
    OutlineItemType.CHAPTER: str(ft.Icons.BOOK),
    OutlineItemType.PARAGRAPH: str(ft.Icons.NOTES),
    # Code structure
    OutlineItemType.CLASS: str(ft.Icons.CLASS_),
    OutlineItemType.FUNCTION: str(ft.Icons.FUNCTIONS),
    OutlineItemType.METHOD: str(ft.Icons.FUNCTIONS),
    OutlineItemType.PROPERTY: str(ft.Icons.LABEL),
    OutlineItemType.VARIABLE: str(ft.Icons.DATA_OBJECT),
    OutlineItemType.CONSTANT: str(ft.Icons.LOCK),
    OutlineItemType.IMPORT: str(ft.Icons.INPUT),
    OutlineItemType.MODULE: str(ft.Icons.INVENTORY_2),
    OutlineItemType.NAMESPACE: str(ft.Icons.FOLDER_SPECIAL),
    OutlineItemType.INTERFACE: str(ft.Icons.INTEGRATION_INSTRUCTIONS),
    OutlineItemType.ENUM: str(ft.Icons.FORMAT_LIST_NUMBERED),
    OutlineItemType.TYPE: str(ft.Icons.TEXT_FIELDS),
    # Generic
    OutlineItemType.ITEM: str(ft.Icons.CIRCLE),
    OutlineItemType.GROUP: str(ft.Icons.FOLDER),
    OutlineItemType.BOOKMARK: str(ft.Icons.BOOKMARK),
    OutlineItemType.ANNOTATION: str(ft.Icons.COMMENT),
}


@dataclass
class OutlineItem:
    """Represents an item in a document outline.

    Attributes:
        id: Unique identifier for the item.
        label: Display text for the item.
        item_type: Type of outline item (affects icon and styling).
        level: Nesting level (0 = top level, 1 = first indent, etc.).
        line_number: Optional line number in the source document.
        start_offset: Optional character offset where this item starts.
        end_offset: Optional character offset where this item ends.
        children: Child outline items.
        metadata: Additional metadata (e.g., return type, parameters).
    """

    id: str
    label: str
    item_type: OutlineItemType = OutlineItemType.ITEM
    level: int = 0
    line_number: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    children: list[OutlineItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def outline_to_tree_nodes(items: list[OutlineItem]) -> list[TreeNode]:
    """Convert a list of OutlineItems to TreeNodes.

    Args:
        items: List of OutlineItem objects.

    Returns:
        List of TreeNode objects.
    """
    nodes = []
    for item in items:
        node = TreeNode(
            id=item.id,
            label=item.label,
            icon=OUTLINE_ICONS.get(item.item_type, str(ft.Icons.CIRCLE)),
            is_folder=bool(item.children),
            is_expanded=True,  # Outlines are usually expanded by default
            children=outline_to_tree_nodes(item.children),
            data=item,
        )
        nodes.append(node)
    return nodes


class DocumentOutlineView(TreeView):
    """A specialized TreeView for displaying document outlines.

    This component extends TreeView with document outline-specific features:
    - Support for different item types (headings, functions, classes, etc.)
    - Line number display
    - Jump-to-location callbacks
    - Symbol search/filter
    - Breadcrumb trail for current position

    Example:
        ```python
        outline = DocumentOutlineView(
            items=[
                OutlineItem(
                    id="h1",
                    label="Introduction",
                    item_type=OutlineItemType.HEADING,
                def on_click(event) -> None:
                ),
                OutlineItem(
                    id="fn1",
                    label="main()",
                    item_type=OutlineItemType.FUNCTION,
                def on_double_click_handler(event) -> None:
                    children=[
                        OutlineItem(
                            id="var1",
                            label="result",
                            item_type=OutlineItemType.VARIABLE,
                            line_number=12,
                        ),
                    ],
                ),
            ],
            on_navigate=lambda item: go_to_line(item.line_number),
        )
        page.add(outline)
        ```
    """

    def __init__(
        self,
        items: list[OutlineItem] | None = None,
        on_navigate: Callable[[OutlineItem], None] | None = None,
        on_item_select: Callable[[OutlineItem], None] | None = None,
        show_line_numbers: bool = True,
        show_icons: bool = True,
        auto_expand: bool = True,
        filter_text: str = "",
        **kwargs: Any,
    ):
        """Initialize the DocumentOutlineView.

        Args:
            items: List of OutlineItem objects to display.
            on_navigate: Callback when user wants to navigate to an item.
            on_item_select: Callback when an item is selected.
            show_line_numbers: Display line numbers next to items.
            show_icons: Display type icons next to items.
            auto_expand: Automatically expand all nodes.
            filter_text: Initial filter text for searching.
            **kwargs: Additional arguments passed to TreeView.
        """
        # Disable drag-drop and delete by default for outlines
        kwargs.setdefault("enable_move", False)
        kwargs.setdefault("enable_delete", False)

        super().__init__(
            on_select=self._handle_select,
            on_double_click=self._handle_navigate,
            **kwargs,
        )

        self.on_navigate = on_navigate
        self.on_item_select = on_item_select
        self.show_line_numbers = show_line_numbers
        self.show_icons = show_icons
        self.auto_expand = auto_expand
        self._items = items or []
        self._filter_text = filter_text
        self._current_position: OutlineItem | None = None

        self._item_map: dict[str, OutlineItem] = {}

    def did_mount(self) -> None:
        """Initialize the outline when mounted."""
        self._build_item_map()
        self._update_tree()
        super().did_mount()

    def set_items(self, items: list[OutlineItem]) -> None:
        """Update the outline items.

        Args:
            items: New list of OutlineItem objects.
        """
        self._items = items
        self._build_item_map()
        self._update_tree()

    def _build_item_map(self) -> None:
        """Build internal item lookup map."""
        self._item_map.clear()
        self._add_items_to_map(self._items)

    def _add_items_to_map(self, items: list[OutlineItem]) -> None:
        """Recursively add items to the lookup map."""
        for item in items:
            self._item_map[item.id] = item
            if item.children:
                self._add_items_to_map(item.children)

    def _update_tree(self) -> None:
        """Update the tree nodes from current items."""
        if self._filter_text:
            filtered = self._filter_items(self._items)
            self.roots = outline_to_tree_nodes(filtered)
        else:
            self.roots = outline_to_tree_nodes(self._items)

        if self.auto_expand:
            self._set_all_expanded(self.roots, True)

        self._rebuild_node_map()
        if self.page:
            self.render()

    def _filter_items(self, items: list[OutlineItem]) -> list[OutlineItem]:
        """Filter items based on current filter text.

        Args:
            items: Items to filter.

        Returns:
            Filtered list of items.
        """
        result = []
        for item in items:
            # Check if this item matches
            matches = self._filter_text in item.label.lower()

            # Recursively filter children
            filtered_children = self._filter_items(item.children)

            # Include item if it matches or has matching children
            if matches or filtered_children:
                # Create a copy with filtered children
                filtered_item = OutlineItem(
                    id=item.id,
                    label=item.label,
                    item_type=item.item_type,
                    level=item.level,
                    line_number=item.line_number,
                    start_offset=item.start_offset,
                    end_offset=item.end_offset,
                    children=filtered_children,
                    metadata=item.metadata,
                )
                result.append(filtered_item)

        return result

    def set_filter(self, text: str) -> None:
        """Set the filter text for searching.

        Args:
            text: Filter text (case-insensitive).
        """
        self._filter_text = text.lower()
        self._update_tree()

    def clear_filter(self) -> None:
        """Clear the current filter."""
        self._filter_text = ""
        self._update_tree()

    def get_item(self, item_id: str) -> OutlineItem | None:
        """Get an outline item by its ID.

        Args:
            item_id: The ID of the item.

        Returns:
            OutlineItem or None if not found.
        """
        return self._item_map.get(item_id)

    def set_current_position(self, line_number: int) -> None:
        """Set the current position in the document.

        This highlights the item that contains the given line number.

        Args:
            line_number: Current line number in the document.
        """
        item = self._find_item_at_line(line_number)
        if item:
            self._current_position = item
            self.select_node(item.id)

    def _find_item_at_line(
        self,
        line_number: int,
        items: list[OutlineItem] | None = None,
    ) -> OutlineItem | None:
        """Find the deepest item containing the given line number.

        Args:
            line_number: Line number to find.
            items: Items to search (defaults to root items).

        Returns:
            OutlineItem or None.
        """
        if items is None:
            items = self._items

        result = None
        for item in items:
            if item.line_number is not None and item.line_number <= line_number:
                result = item
                # Check children for a more specific match
                child_match = self._find_item_at_line(line_number, item.children)
                if child_match:
                    result = child_match

        return result

    def get_breadcrumb(self) -> list[OutlineItem]:
        """Get the breadcrumb trail to the current position.

        Returns:
            List of OutlineItem from root to current position.
        """
        if not self._current_position:
            return []

        return self._find_path_to_item(self._current_position.id)

    def _find_path_to_item(
        self,
        target_id: str,
        items: list[OutlineItem] | None = None,
        path: list[OutlineItem] | None = None,
    ) -> list[OutlineItem]:
        """Find the path from root to a specific item.

        Args:
            target_id: ID of the target item.
            items: Items to search.
            path: Current path (used recursively).

        Returns:
            List of items from root to target.
        """
        if items is None:
            items = self._items
        if path is None:
            path = []

        for item in items:
            current_path = path + [item]
            if item.id == target_id:
                return current_path
            if item.children:
                result = self._find_path_to_item(target_id, item.children, current_path)
                if result:
                    return result

        return []

    def _handle_select(self, node: TreeNode) -> None:
        """Handle node selection."""
        item = node.data
        if item and isinstance(item, OutlineItem):
            self._current_position = item
            if self.on_item_select:
                self.on_item_select(item)

    def _handle_navigate(self, node: TreeNode) -> None:
        """Handle navigation (double-click)."""
        item = node.data
        if item and isinstance(item, OutlineItem) and self.on_navigate:
            self.on_navigate(item)

    def _build_leaf_tile(
        self,
        node: TreeNode,
        trailing: ft.Control | None,
        is_selected: bool,
        depth: int,
    ) -> ft.ListTile:
        """Override to add line numbers to leaf tiles."""
        item = node.data

        # Build title with optional line number
        title_controls: list[ft.Control] = [
            ft.Text(
                node.label,
                weight=ft.FontWeight.W_500 if is_selected else None,
            ),
        ]

        if (
            self.show_line_numbers
            and isinstance(item, OutlineItem)
            and item.line_number
        ):
            title_controls.append(
                ft.Text(
                    f":{item.line_number}",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            )

        title = ft.Row(
            controls=title_controls,
            spacing=4,
        )

        def on_click(e: Any) -> None:
            if self.enable_selection:
                self._selected_node = node
                self._handle_select(node)
                self.render()

        def on_double_click_handler(e: Any) -> None:
            self._handle_navigate(node)

        return ft.ListTile(
            title=title,
            leading=ft.Icon(
                getattr(ft.Icons, node.icon, ft.Icons.CIRCLE)
                if isinstance(node.icon, str)
                else node.icon,
                color=ft.Colors.PRIMARY if is_selected else None,
            )
            if self.show_icons
            else None,
            trailing=trailing,
            on_click=on_click,
            on_long_press=on_double_click_handler,
            content_padding=ft.padding.only(left=depth * self.indent_size + 16),
            bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else None,
        )

    def _build_folder_tile(
        self,
        node: TreeNode,
        trailing: ft.Control | None,
        is_selected: bool,
        depth: int,
    ) -> ft.ExpansionTile:
        """Override to add line numbers to folder tiles."""
        item = node.data

        # Build title with optional line number
        title_controls: list[ft.Control] = [
            ft.Text(
                node.label,
                weight=ft.FontWeight.W_500 if is_selected else None,
            ),
        ]

        if (
            self.show_line_numbers
            and isinstance(item, OutlineItem)
            and item.line_number
        ):
            title_controls.append(
                ft.Text(
                    f":{item.line_number}",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            )

        def on_click(e: Any) -> None:
            if self.enable_selection:
                self._selected_node = node
                self._handle_select(node)
                self.render()

        def on_double_click_handler(e: Any) -> None:
            self._handle_navigate(node)

        def on_expansion_change(e: Any) -> None:
            node.is_expanded = e.data == "true"

        title_row = ft.Row(
            controls=title_controls,
            spacing=4,
        )

        return ft.ExpansionTile(
            title=ft.GestureDetector(
                content=title_row,
                on_tap=on_click,
                on_double_tap=on_double_click_handler,
            ),
            leading=ft.Icon(
                getattr(ft.Icons, node.icon, ft.Icons.FOLDER)
                if isinstance(node.icon, str)
                else node.icon,
                color=ft.Colors.PRIMARY if is_selected else None,
            )
            if self.show_icons
            else None,
            trailing=trailing,
            expanded=node.is_expanded,
            controls=[self._build_node(child, depth + 1) for child in node.children],
            on_change=on_expansion_change,
            tile_padding=ft.padding.only(left=depth * self.indent_size),
            bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else None,
        )


def create_markdown_outline(content: str) -> list[OutlineItem]:
    """Parse markdown content and create an outline from headings.

    Args:
        content: Markdown text content.

    Returns:
        List of OutlineItem objects representing the heading structure.
    """
    items: list[OutlineItem] = []
    stack: list[tuple[int, OutlineItem]] = []  # (level, item) stack for nesting

    lines = content.split("\n")
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue

        # Count heading level
        level = 0
        for char in stripped:
            if char == "#":
                level += 1
            else:
                break

        if level == 0 or level > 6:
            continue

        # Extract heading text
        heading_text = stripped[level:].strip()
        if not heading_text:
            continue

        item = OutlineItem(
            id=f"heading-{line_num}",
            label=heading_text,
            item_type=OutlineItemType.HEADING,
            level=level - 1,
            line_number=line_num,
        )

        # Find the appropriate parent
        while stack and stack[-1][0] >= level:
            stack.pop()

        if stack:
            # Add as child of the last item with a lower level
            stack[-1][1].children.append(item)
        else:
            # Top-level item
            items.append(item)

        stack.append((level, item))

    return items


def create_code_outline(
    symbols: list[dict[str, Any]],
) -> list[OutlineItem]:
    """Create an outline from a list of code symbols.

    This is a utility function to convert LSP-style symbol information
    into OutlineItem objects.

    Args:
        symbols: List of symbol dictionaries with keys:
            - name: Symbol name
            - kind: Symbol kind (e.g., "class", "function", "variable")
            - line: Line number
            - children: Optional list of child symbols

    Returns:
        List of OutlineItem objects.
    """
    kind_map = {
        "class": OutlineItemType.CLASS,
        "function": OutlineItemType.FUNCTION,
        "method": OutlineItemType.METHOD,
        "property": OutlineItemType.PROPERTY,
        "variable": OutlineItemType.VARIABLE,
        "constant": OutlineItemType.CONSTANT,
        "import": OutlineItemType.IMPORT,
        "module": OutlineItemType.MODULE,
        "namespace": OutlineItemType.NAMESPACE,
        "interface": OutlineItemType.INTERFACE,
        "enum": OutlineItemType.ENUM,
        "type": OutlineItemType.TYPE,
    }

    items = []
    for idx, symbol in enumerate(symbols):
        kind = symbol.get("kind", "item").lower()
        item_type = kind_map.get(kind, OutlineItemType.ITEM)

        children = []
        if "children" in symbol:
            children = create_code_outline(symbol["children"])

        item = OutlineItem(
            id=f"symbol-{idx}-{symbol.get('name', 'unknown')}",
            label=symbol.get("name", "Unknown"),
            item_type=item_type,
            line_number=symbol.get("line"),
            children=children,
            metadata=symbol.get("metadata", {}),
        )
        items.append(item)

    return items
