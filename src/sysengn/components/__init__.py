"""SysEngn UI components."""

from sysengn.components.domain_views import (
    HomeView,
    MBSEView,
    UXView,
)

# Re-export from engn.ui for backward compatibility
from engn.ui import DocsView

__all__ = [
    "HomeView",
    "MBSEView",
    "UXView",
    "DocsView",
]
