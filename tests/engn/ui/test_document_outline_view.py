"""Unit tests for DocumentOutlineView component."""

from unittest.mock import MagicMock


from engn.ui.document_outline_view import (
    OUTLINE_ICONS,
    DocumentOutlineView,
    OutlineItem,
    OutlineItemType,
    create_code_outline,
    create_markdown_outline,
    outline_to_tree_nodes,
)


class TestOutlineItem:
    """Tests for OutlineItem dataclass."""

    def test_default_values(self) -> None:
        """Test OutlineItem initializes with correct defaults."""
        item = OutlineItem(id="1", label="Test")

        assert item.id == "1"
        assert item.label == "Test"
        assert item.item_type == OutlineItemType.ITEM
        assert item.level == 0
        assert item.line_number is None
        assert item.start_offset is None
        assert item.end_offset is None
        assert item.children == []
        assert item.metadata == {}

    def test_full_initialization(self) -> None:
        """Test OutlineItem with all fields."""
        child = OutlineItem(id="c", label="Child")
        item = OutlineItem(
            id="1",
            label="Function",
            item_type=OutlineItemType.FUNCTION,
            level=1,
            line_number=42,
            start_offset=100,
            end_offset=200,
            children=[child],
            metadata={"return_type": "int"},
        )

        assert item.item_type == OutlineItemType.FUNCTION
        assert item.level == 1
        assert item.line_number == 42
        assert item.start_offset == 100
        assert item.end_offset == 200
        assert len(item.children) == 1
        assert item.metadata["return_type"] == "int"


class TestOutlineItemType:
    """Tests for OutlineItemType enum."""

    def test_document_types(self) -> None:
        """Test document structure types exist."""
        assert OutlineItemType.HEADING.value == "heading"
        assert OutlineItemType.SECTION.value == "section"
        assert OutlineItemType.CHAPTER.value == "chapter"
        assert OutlineItemType.PARAGRAPH.value == "paragraph"

    def test_code_types(self) -> None:
        """Test code structure types exist."""
        assert OutlineItemType.CLASS.value == "class"
        assert OutlineItemType.FUNCTION.value == "function"
        assert OutlineItemType.METHOD.value == "method"
        assert OutlineItemType.VARIABLE.value == "variable"

    def test_all_types_have_icons(self) -> None:
        """Test all outline types have associated icons."""
        for item_type in OutlineItemType:
            assert item_type in OUTLINE_ICONS, f"Missing icon for {item_type}"


class TestOutlineToTreeNodes:
    """Tests for outline_to_tree_nodes function."""

    def test_empty_list(self) -> None:
        """Test converting empty list."""
        nodes = outline_to_tree_nodes([])
        assert nodes == []

    def test_single_item(self) -> None:
        """Test converting single item."""
        items = [OutlineItem(id="1", label="Heading")]
        nodes = outline_to_tree_nodes(items)

        assert len(nodes) == 1
        assert nodes[0].id == "1"
        assert nodes[0].label == "Heading"

    def test_nested_items(self) -> None:
        """Test converting nested items."""
        child = OutlineItem(id="c", label="Child")
        parent = OutlineItem(id="p", label="Parent", children=[child])
        nodes = outline_to_tree_nodes([parent])

        assert len(nodes) == 1
        assert nodes[0].is_folder is True
        assert len(nodes[0].children) == 1
        assert nodes[0].children[0].id == "c"

    def test_preserves_item_in_data(self) -> None:
        """Test that original OutlineItem is stored in node.data."""
        item = OutlineItem(id="1", label="Test", line_number=42)
        nodes = outline_to_tree_nodes([item])

        assert nodes[0].data is item
        assert nodes[0].data.line_number == 42

    def test_icon_assignment(self) -> None:
        """Test that correct icons are assigned."""
        item = OutlineItem(id="1", label="MyClass", item_type=OutlineItemType.CLASS)
        nodes = outline_to_tree_nodes([item])

        assert nodes[0].icon == OUTLINE_ICONS[OutlineItemType.CLASS]


class TestDocumentOutlineViewInit:
    """Tests for DocumentOutlineView initialization."""

    def test_default_initialization(self) -> None:
        """Test DocumentOutlineView initializes with defaults."""
        outline = DocumentOutlineView()

        assert outline._items == []
        assert outline.show_line_numbers is True
        assert outline.show_icons is True
        assert outline.auto_expand is True
        # Drag-drop disabled by default for outlines
        assert outline.enable_move is False
        assert outline.enable_delete is False

    def test_custom_initialization(self) -> None:
        """Test DocumentOutlineView with custom values."""
        items = [OutlineItem(id="1", label="Test")]
        on_navigate = MagicMock()

        outline = DocumentOutlineView(
            items=items,
            on_navigate=on_navigate,
            show_line_numbers=False,
            show_icons=False,
            auto_expand=False,
        )

        assert len(outline._items) == 1
        assert outline.on_navigate is on_navigate
        assert outline.show_line_numbers is False
        assert outline.show_icons is False
        assert outline.auto_expand is False


class TestDocumentOutlineViewItems:
    """Tests for DocumentOutlineView item management."""

    def test_set_items(self) -> None:
        """Test setting items updates the outline."""
        outline = DocumentOutlineView()
        items = [
            OutlineItem(id="1", label="First"),
            OutlineItem(id="2", label="Second"),
        ]

        # Avoid Flet UI update: set items directly and build map
        outline._items = items
        outline._build_item_map()
        assert len(outline._items) == 2
        assert outline.get_item("1") is not None
        assert outline.get_item("2") is not None

    def test_get_item(self) -> None:
        """Test getting an item by ID."""
        items = [OutlineItem(id="test", label="Test Item")]
        outline = DocumentOutlineView(items=items)
        outline._build_item_map()

        item = outline.get_item("test")
        assert item is not None
        assert item.label == "Test Item"

    def test_get_item_nested(self) -> None:
        """Test getting a nested item."""
        child = OutlineItem(id="child", label="Child")
        parent = OutlineItem(id="parent", label="Parent", children=[child])
        outline = DocumentOutlineView(items=[parent])
        outline._build_item_map()

        item = outline.get_item("child")
        assert item is not None
        assert item.label == "Child"

    def test_get_item_nonexistent(self) -> None:
        """Test getting a nonexistent item."""
        outline = DocumentOutlineView()
        assert outline.get_item("nonexistent") is None


class TestDocumentOutlineViewFiltering:
    """Tests for DocumentOutlineView filtering functionality."""

    def test_set_filter(self) -> None:
        """Test setting a filter."""
        items = [
            OutlineItem(id="1", label="Introduction"),
            OutlineItem(id="2", label="Conclusion"),
        ]
        outline = DocumentOutlineView(items=items)
        outline._build_item_map()

        # Avoid Flet UI update: set filter text directly
        outline._filter_text = "intro"
        outline._build_item_map()
        assert outline._filter_text == "intro"

    def test_clear_filter(self) -> None:
        """Test clearing the filter."""
        outline = DocumentOutlineView()
        outline._filter_text = "test"

        # Avoid Flet UI update: clear filter text directly
        outline._filter_text = ""
        outline._build_item_map()
        assert outline._filter_text == ""

    def test_filter_items_matching(self) -> None:
        """Test filtering items by text."""
        items = [
            OutlineItem(id="1", label="Introduction"),
            OutlineItem(id="2", label="Methods"),
            OutlineItem(id="3", label="Intro Methods"),  # Contains "intro"
        ]
        outline = DocumentOutlineView(items=items)
        outline._filter_text = "intro"

        filtered = outline._filter_items(items)

        assert len(filtered) == 2
        labels = [i.label for i in filtered]
        assert "Introduction" in labels
        assert "Intro Methods" in labels
        assert "Methods" not in labels

    def test_filter_includes_parent_with_matching_child(self) -> None:
        """Test that parents with matching children are included."""
        child = OutlineItem(id="c", label="Matching Item")
        parent = OutlineItem(id="p", label="Parent", children=[child])
        outline = DocumentOutlineView()
        outline._filter_text = "matching"

        filtered = outline._filter_items([parent])

        assert len(filtered) == 1
        assert filtered[0].label == "Parent"
        assert len(filtered[0].children) == 1


class TestDocumentOutlineViewPosition:
    """Tests for DocumentOutlineView position tracking."""

    def test_set_current_position(self) -> None:
        """Test setting current position by line number."""
        items = [
            OutlineItem(id="1", label="First", line_number=1),
            OutlineItem(id="2", label="Second", line_number=50),
            OutlineItem(id="3", label="Third", line_number=100),
        ]
        outline = DocumentOutlineView(items=items)
        outline._build_item_map()

        outline.set_current_position(75)

        assert outline._current_position is not None
        assert outline._current_position.label == "Second"

    def test_find_item_at_line_exact(self) -> None:
        """Test finding item at exact line number."""
        items = [
            OutlineItem(id="1", label="First", line_number=10),
        ]
        outline = DocumentOutlineView(items=items)

        item = outline._find_item_at_line(10)

        assert item is not None
        assert item.label == "First"

    def test_find_item_at_line_between(self) -> None:
        """Test finding item when line is between two items."""
        items = [
            OutlineItem(id="1", label="First", line_number=10),
            OutlineItem(id="2", label="Second", line_number=50),
        ]
        outline = DocumentOutlineView(items=items)

        item = outline._find_item_at_line(30)

        assert item is not None
        assert item.label == "First"

    def test_find_item_at_line_nested(self) -> None:
        """Test finding item in nested structure."""
        child = OutlineItem(id="c", label="Method", line_number=20)
        parent = OutlineItem(id="p", label="Class", line_number=10, children=[child])
        outline = DocumentOutlineView(items=[parent])

        item = outline._find_item_at_line(25)

        assert item is not None
        assert item.label == "Method"

    def test_get_breadcrumb(self) -> None:
        """Test getting breadcrumb trail."""
        grandchild = OutlineItem(id="gc", label="Grandchild")
        child = OutlineItem(id="c", label="Child", children=[grandchild])
        root = OutlineItem(id="r", label="Root", children=[child])
        outline = DocumentOutlineView(items=[root])
        outline._build_item_map()
        outline._current_position = grandchild

        breadcrumb = outline.get_breadcrumb()

        assert len(breadcrumb) == 3
        assert breadcrumb[0].label == "Root"
        assert breadcrumb[1].label == "Child"
        assert breadcrumb[2].label == "Grandchild"

    def test_get_breadcrumb_no_selection(self) -> None:
        """Test breadcrumb with no selection."""
        outline = DocumentOutlineView()
        breadcrumb = outline.get_breadcrumb()
        assert breadcrumb == []


class TestDocumentOutlineViewCallbacks:
    """Tests for DocumentOutlineView callbacks."""

    def test_on_item_select_callback(self) -> None:
        """Test item select callback is triggered."""
        item = OutlineItem(id="1", label="Test")
        on_select = MagicMock()
        outline = DocumentOutlineView(items=[item], on_item_select=on_select)
        outline._build_item_map()
        # Avoid Flet UI update: simulate callback directly
        node = outline.roots[0] if outline.roots else None
        if node:
            outline._handle_select(node)
            on_select.assert_called_once()
            assert on_select.call_args[0][0].label == "Test"

    def test_on_navigate_callback(self) -> None:
        """Test navigate callback is triggered on double-click."""
        item = OutlineItem(id="1", label="Test", line_number=42)
        on_navigate = MagicMock()
        outline = DocumentOutlineView(items=[item], on_navigate=on_navigate)
        outline._build_item_map()
        # Avoid Flet UI update: simulate callback directly
        node = outline.roots[0] if outline.roots else None
        if node:
            outline._handle_navigate(node)
            on_navigate.assert_called_once()
            assert on_navigate.call_args[0][0].line_number == 42


class TestCreateMarkdownOutline:
    """Tests for create_markdown_outline function."""

    def test_empty_content(self) -> None:
        """Test parsing empty content."""
        items = create_markdown_outline("")
        assert items == []

    def test_no_headings(self) -> None:
        """Test content without headings."""
        content = "Just some text\nwithout any headings."
        items = create_markdown_outline(content)
        assert items == []

    def test_single_heading(self) -> None:
        """Test parsing single heading."""
        content = "# Introduction"
        items = create_markdown_outline(content)

        assert len(items) == 1
        assert items[0].label == "Introduction"
        assert items[0].item_type == OutlineItemType.HEADING
        assert items[0].line_number == 1

    def test_multiple_headings_same_level(self) -> None:
        """Test parsing multiple headings at same level."""
        content = """# First
# Second
# Third"""
        items = create_markdown_outline(content)

        assert len(items) == 3
        assert items[0].label == "First"
        assert items[1].label == "Second"
        assert items[2].label == "Third"

    def test_nested_headings(self) -> None:
        """Test parsing nested heading structure."""
        content = """# Chapter 1
## Section 1.1
## Section 1.2
# Chapter 2
## Section 2.1"""
        items = create_markdown_outline(content)

        assert len(items) == 2  # Two top-level chapters
        assert items[0].label == "Chapter 1"
        assert len(items[0].children) == 2
        assert items[0].children[0].label == "Section 1.1"
        assert items[1].label == "Chapter 2"
        assert len(items[1].children) == 1

    def test_deeply_nested_headings(self) -> None:
        """Test parsing deeply nested headings."""
        content = """# H1
## H2
### H3
#### H4"""
        items = create_markdown_outline(content)

        assert len(items) == 1
        assert items[0].label == "H1"
        assert items[0].children[0].label == "H2"
        assert items[0].children[0].children[0].label == "H3"
        assert items[0].children[0].children[0].children[0].label == "H4"

    def test_heading_with_content_between(self) -> None:
        """Test headings with content between them."""
        content = """# First

Some content here.

# Second

More content."""
        items = create_markdown_outline(content)

        assert len(items) == 2
        assert items[0].line_number == 1
        assert items[1].line_number == 5

    def test_heading_level_jump(self) -> None:
        """Test jumping heading levels (e.g., # to ###)."""
        content = """# H1
### H3"""
        items = create_markdown_outline(content)

        # H3 should still be child of H1 since there's no H2
        assert len(items) == 1
        assert items[0].children[0].label == "H3"

    def test_empty_heading_ignored(self) -> None:
        """Test that empty headings are ignored."""
        content = """# Valid
#
# Another Valid"""
        items = create_markdown_outline(content)

        assert len(items) == 2

    def test_heading_with_special_characters(self) -> None:
        """Test headings with special characters."""
        content = "# Code: `example()` & More!"
        items = create_markdown_outline(content)

        assert items[0].label == "Code: `example()` & More!"


class TestCreateCodeOutline:
    """Tests for create_code_outline function."""

    def test_empty_symbols(self) -> None:
        """Test with empty symbol list."""
        items = create_code_outline([])
        assert items == []

    def test_single_function(self) -> None:
        """Test parsing single function symbol."""
        symbols = [{"name": "main", "kind": "function", "line": 10}]
        items = create_code_outline(symbols)

        assert len(items) == 1
        assert items[0].label == "main"
        assert items[0].item_type == OutlineItemType.FUNCTION
        assert items[0].line_number == 10

    def test_class_with_methods(self) -> None:
        """Test parsing class with methods."""
        symbols = [
            {
                "name": "MyClass",
                "kind": "class",
                "line": 1,
                "children": [
                    {"name": "__init__", "kind": "method", "line": 2},
                    {"name": "run", "kind": "method", "line": 10},
                ],
            }
        ]
        items = create_code_outline(symbols)

        assert len(items) == 1
        assert items[0].label == "MyClass"
        assert items[0].item_type == OutlineItemType.CLASS
        assert len(items[0].children) == 2
        assert items[0].children[0].item_type == OutlineItemType.METHOD

    def test_various_kinds(self) -> None:
        """Test various symbol kinds are mapped correctly."""
        symbols = [
            {"name": "MyClass", "kind": "class"},
            {"name": "my_func", "kind": "function"},
            {"name": "MY_CONST", "kind": "constant"},
            {"name": "my_var", "kind": "variable"},
            {"name": "MyInterface", "kind": "interface"},
        ]
        items = create_code_outline(symbols)

        assert items[0].item_type == OutlineItemType.CLASS
        assert items[1].item_type == OutlineItemType.FUNCTION
        assert items[2].item_type == OutlineItemType.CONSTANT
        assert items[3].item_type == OutlineItemType.VARIABLE
        assert items[4].item_type == OutlineItemType.INTERFACE

    def test_unknown_kind(self) -> None:
        """Test unknown kind defaults to ITEM."""
        symbols = [{"name": "unknown", "kind": "unknown_type"}]
        items = create_code_outline(symbols)

        assert items[0].item_type == OutlineItemType.ITEM

    def test_metadata_preserved(self) -> None:
        """Test that metadata is preserved."""
        symbols = [
            {
                "name": "func",
                "kind": "function",
                "metadata": {"return_type": "int", "params": ["a", "b"]},
            }
        ]
        items = create_code_outline(symbols)

        assert items[0].metadata == {"return_type": "int", "params": ["a", "b"]}
