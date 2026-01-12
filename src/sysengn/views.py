"""Views module for sysengn application.

This module re-exports views from engn.ui for backward compatibility
and provides sysengn-specific customizations if needed.
"""

# Re-export from engn.ui for backward compatibility
from engn.ui import AdminView, LoginView, UserProfileView

__all__ = ["LoginView", "UserProfileView", "AdminView"]
