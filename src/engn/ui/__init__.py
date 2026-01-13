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
from engn.ui.domain_views import (
    ActualView,
    AnalyzeView,
    BaselineView,
    DocsView,
)
from engn.ui.file_tree_view import FileTreeView, create_file_tree, get_file_icon
from engn.ui.home_page import HomeDomainPage
from engn.ui.terminal_emulator import TerminalEmulator
from engn.ui.toolbar import Toolbar
from engn.ui.drawer import RightDrawer
from engn.ui.tree_view import (
    TreeNode,
    TreeView,
    delete_node,
    find_node_and_parent,
    move_node,
)
from engn.ui.views import AdminView, LoginView, UserProfileView

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
    # Toolbar
    "Toolbar",
    # Drawer
    "RightDrawer",
    # Views
    "LoginView",
    "UserProfileView",
    "AdminView",
    # Home Page
    "HomeDomainPage",
    # Domain Views
    "DocsView",
    "BaselineView",
    "ActualView",
    "AnalyzeView",
]
