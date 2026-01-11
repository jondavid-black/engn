"""Reusable UI components for Flet applications.

This module provides shared UI components that can be used across
sysengn, projengn, and other engn applications.
"""

from engn.ui.document_outline_view import (
    DocumentOutlineView,
    OutlineItem,
    OutlineItemType,
    create_code_outline,
    create_markdown_outline,
)
from engn.ui.file_tree_view import FileTreeView, create_file_tree, get_file_icon
from engn.ui.terminal_emulator import TerminalEmulator
from engn.ui.tree_view import (
    TreeNode,
    TreeView,
    delete_node,
    find_node_and_parent,
    move_node,
)

__all__ = [
    # Base TreeView
    "TreeNode",
    "TreeView",
    "find_node_and_parent",
    "move_node",
    "delete_node",
    # FileTreeView
    "FileTreeView",
    "create_file_tree",
    "get_file_icon",
    # DocumentOutlineView
    "DocumentOutlineView",
    "OutlineItem",
    "OutlineItemType",
    "create_markdown_outline",
    "create_code_outline",
    # TerminalEmulator
    "TerminalEmulator",
]
