"""Unit tests for SysEngn domain views."""

from typing import Any
import flet as ft
from sysengn.components.domain_views import HomeView, MBSEView, UXView
from engn.ui import DocsView


def test_home_view_init():
    """Test HomeView initialization."""
    view = HomeView()
    assert isinstance(view, ft.Container)
    assert view.content is not None
    # Check if dashboard text is present
    content: Any = view.content
    dashboard_text = content.controls[0]
    assert dashboard_text.value == "Dashboard"


def test_mbse_view_init():
    """Test MBSEView initialization."""
    view = MBSEView()
    assert isinstance(view, ft.Container)
    assert view.content is not None
    content: Any = view.content
    mbse_text = content.controls[0]
    assert mbse_text.value == "Model-Based System Engineering"


def test_ux_view_init():
    """Test UXView initialization."""
    view = UXView()
    assert isinstance(view, ft.Container)
    assert view.content is not None
    content: Any = view.content
    ux_text = content.controls[0]
    assert ux_text.value == "UX Design"


def test_docs_view_init():
    """Test DocsView initialization."""
    view = DocsView()
    assert isinstance(view, ft.Container)
    assert view.content is not None
    # DocsView content structure is a bit different
    content: Any = view.content
    row = content.controls[0]
    assert isinstance(row, ft.Row)
    content_area: Any = row.controls[1]
    title_text = content_area.content.controls[2]
    assert title_text.value == "Projects"
