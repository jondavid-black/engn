"""File system tree view component for Flet applications.

This module provides a specialized TreeView for browsing and managing
file system hierarchies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import flet as ft

from engn.ui.tree_view import TreeNode, TreeView, delete_node, move_node
from engn.core.context import get_app_context


# File type to icon mapping
FILE_ICONS: dict[str, str] = {
    # Folders
    ".git": str(ft.Icons.SOURCE),
    # Documents
    ".pdf": str(ft.Icons.PICTURE_AS_PDF),
    ".doc": str(ft.Icons.DESCRIPTION),
    ".docx": str(ft.Icons.DESCRIPTION),
    ".txt": str(ft.Icons.TEXT_SNIPPET),
    ".md": str(ft.Icons.ARTICLE),
    ".rtf": str(ft.Icons.DESCRIPTION),
    # Spreadsheets
    ".xls": str(ft.Icons.TABLE_CHART),
    ".xlsx": str(ft.Icons.TABLE_CHART),
    ".csv": str(ft.Icons.TABLE_CHART),
    # Images
    ".png": str(ft.Icons.IMAGE),
    ".jpg": str(ft.Icons.IMAGE),
    ".jpeg": str(ft.Icons.IMAGE),
    ".gif": str(ft.Icons.IMAGE),
    ".svg": str(ft.Icons.IMAGE),
    ".ico": str(ft.Icons.IMAGE),
    ".webp": str(ft.Icons.IMAGE),
    # Audio/Video
    ".mp3": str(ft.Icons.AUDIO_FILE),
    ".wav": str(ft.Icons.AUDIO_FILE),
    ".mp4": str(ft.Icons.VIDEO_FILE),
    ".mov": str(ft.Icons.VIDEO_FILE),
    ".avi": str(ft.Icons.VIDEO_FILE),
    # Archives
    ".zip": str(ft.Icons.FOLDER_ZIP),
    ".tar": str(ft.Icons.FOLDER_ZIP),
    ".gz": str(ft.Icons.FOLDER_ZIP),
    ".rar": str(ft.Icons.FOLDER_ZIP),
    ".7z": str(ft.Icons.FOLDER_ZIP),
    # Code - Python
    ".py": str(ft.Icons.CODE),
    ".pyw": str(ft.Icons.CODE),
    ".pyi": str(ft.Icons.CODE),
    ".pyc": str(ft.Icons.CODE),
    # Code - Web
    ".html": str(ft.Icons.HTML),
    ".htm": str(ft.Icons.HTML),
    ".css": str(ft.Icons.CSS),
    ".js": str(ft.Icons.JAVASCRIPT),
    ".jsx": str(ft.Icons.JAVASCRIPT),
    ".ts": str(ft.Icons.CODE),
    ".tsx": str(ft.Icons.CODE),
    ".vue": str(ft.Icons.CODE),
    # Code - Other
    ".json": str(ft.Icons.DATA_OBJECT),
    ".xml": str(ft.Icons.CODE),
    ".yaml": str(ft.Icons.SETTINGS),
    ".yml": str(ft.Icons.SETTINGS),
    ".toml": str(ft.Icons.SETTINGS),
    ".ini": str(ft.Icons.SETTINGS),
    ".cfg": str(ft.Icons.SETTINGS),
    ".conf": str(ft.Icons.SETTINGS),
    # Shell/Scripts
    ".sh": str(ft.Icons.TERMINAL),
    ".bash": str(ft.Icons.TERMINAL),
    ".zsh": str(ft.Icons.TERMINAL),
    ".fish": str(ft.Icons.TERMINAL),
    ".bat": str(ft.Icons.TERMINAL),
    ".cmd": str(ft.Icons.TERMINAL),
    ".ps1": str(ft.Icons.TERMINAL),
    # Compiled/Binary
    ".exe": str(ft.Icons.APPS),
    ".dll": str(ft.Icons.EXTENSION),
    ".so": str(ft.Icons.EXTENSION),
    ".dylib": str(ft.Icons.EXTENSION),
    # Data
    ".db": str(ft.Icons.STORAGE),
    ".sqlite": str(ft.Icons.STORAGE),
    ".sql": str(ft.Icons.STORAGE),
    # Git
    ".gitignore": str(ft.Icons.SOURCE),
    ".gitattributes": str(ft.Icons.SOURCE),
}


def get_file_icon(path: Path) -> str:
    """Get the appropriate icon for a file based on its extension.

    Args:
        path: Path to the file.

    Returns:
        Flet icon name.
    """
    if path.is_dir():
        name = path.name.lower()
        if name == ".git":
            return str(ft.Icons.SOURCE)
        if name in ("node_modules", "__pycache__", ".venv", "venv"):
            return str(ft.Icons.FOLDER_OFF)
        if name in ("src", "lib", "pkg"):
            return str(ft.Icons.SOURCE)
        if name in ("test", "tests", "spec", "specs"):
            return str(ft.Icons.SCIENCE)
        if name in ("docs", "doc", "documentation"):
            return str(ft.Icons.MENU_BOOK)
        if name in ("config", "configs", "settings"):
            return str(ft.Icons.SETTINGS)
        return str(ft.Icons.FOLDER)

    suffix = path.suffix.lower()
    return FILE_ICONS.get(suffix, str(ft.Icons.INSERT_DRIVE_FILE))


class FileTreeView(TreeView):
    """A specialized TreeView for browsing file systems.

    This component extends TreeView with file system-specific features:
    - Automatic icon assignment based on file type
    - Lazy loading of directory contents
    - File filtering (show/hide hidden files, specific extensions)
    - File operations (rename, delete, move)
    - Context menu support

    Example:
        ```python
        file_tree = FileTreeView(
            root_path="/home/user/projects",
            on_file_select=lambda path: print(f"Selected: {path}"),
            on_file_open=lambda path: open_file(path),
            show_hidden=False,
        )
        page.add(file_tree)
        ```
    """

    def __init__(
        self,
        root_path: str | Path | None = None,
        on_file_select: Callable[[Path], None] | None = None,
        on_file_open: Callable[[Path], None] | None = None,
        on_file_delete: Callable[[Path], bool] | None = None,
        on_file_move: Callable[[Path, Path], bool] | None = None,
        on_file_rename: Callable[[Path, str], bool] | None = None,
        show_hidden: bool = False,
        file_filter: Callable[[Path], bool] | None = None,
        lazy_load: bool = True,
        sort_folders_first: bool = True,
        **kwargs: Any,
    ):
        """Initialize the FileTreeView.

        Args:
            root_path: Root directory to display. If None, shows nothing.
            on_file_select: Callback when a file/folder is selected.
            on_file_open: Callback when a file is double-clicked/opened.
            on_file_delete: Callback to delete a file. Return True if successful.
            on_file_move: Callback to move a file. Receives (src, dest_dir).
            on_file_rename: Callback to rename a file. Receives (path, new_name).
            show_hidden: Whether to show hidden files (starting with .).
            file_filter: Custom filter function. Return True to include file.
            lazy_load: Load directory contents on demand.
            sort_folders_first: Sort folders before files.
            **kwargs: Additional arguments passed to TreeView.
        """
        super().__init__(
            on_select=self._handle_select,
            on_double_click=self._handle_double_click,
            on_move=self._handle_move,
            on_delete=self._handle_delete,
            **kwargs,
        )

        self.root_path = Path(root_path) if root_path else None
        self.on_file_select = on_file_select
        self.on_file_open = on_file_open
        self.on_file_delete = on_file_delete
        self.on_file_move = on_file_move
        self.on_file_rename = on_file_rename
        self.show_hidden = show_hidden
        self.file_filter = file_filter
        self.lazy_load = lazy_load
        self.sort_folders_first = sort_folders_first

        self._path_to_node: dict[str, TreeNode] = {}

        # Subscribe to context changes if page is available
        self.app_context = None
        if hasattr(kwargs.get("page"), "app_context") or "page" in kwargs:
            # This is a bit tricky since page might not be in kwargs directly
            # and might be passed later or accessed via self.page
            pass

    def did_mount(self) -> None:
        """Load the initial tree when mounted."""
        # Use try-except because self.page raises RuntimeError if not attached
        page = None
        try:
            page = self.page
        except RuntimeError:
            pass

        if page:
            self.app_context = get_app_context(page)
            self.app_context.subscribe(self._on_context_change)

            # If no root path was provided, use the active project from context
            if not self.root_path and self.app_context.active_project_id:
                # We need working directory here, but FileTreeView doesn't have it.
                # Usually it's passed as root_path.
                pass

        if self.root_path:
            self.load_directory(self.root_path)
        super().did_mount()

    def will_unmount(self) -> None:
        """Unsubscribe from context changes."""
        if self.app_context:
            self.app_context.unsubscribe(self._on_context_change)
        super().will_unmount()

    def _on_context_change(self, context):
        """Handle context changes."""
        # For FileTreeView, it usually depends on root_path.
        # If the root_path is supposed to change with the project,
        # the parent component usually handles it.
        # But we can refresh if needed.
        self.refresh()

    def load_directory(self, path: str | Path) -> None:
        """Load a directory as the root of the tree.

        Args:
            path: Path to the directory to load.
        """
        self.root_path = Path(path)
        if not self.root_path.exists():
            self.roots = []
            return

        self._path_to_node.clear()
        root_node = self._create_node_from_path(self.root_path, load_children=True)
        self.roots = [root_node] if root_node else []
        self._rebuild_node_map()
        self.render()

    def refresh(self) -> None:
        """Refresh the tree from the file system."""
        if self.root_path:
            self.load_directory(self.root_path)

    def _create_node_from_path(
        self,
        path: Path,
        load_children: bool = False,
    ) -> TreeNode | None:
        """Create a TreeNode from a file system path.

        Args:
            path: Path to create node from.
            load_children: Whether to load children for directories.

        Returns:
            TreeNode or None if path should be filtered.
        """
        if not self._should_include(path):
            return None

        is_dir = path.is_dir()
        children: list[TreeNode] = []

        if is_dir and load_children:
            children = self._load_children(path)

        node = TreeNode(
            id=str(path),
            label=path.name,
            icon=get_file_icon(path),
            is_folder=is_dir,
            is_expanded=False,
            children=children,
            data=path,
        )

        self._path_to_node[str(path)] = node
        return node

    def _load_children(self, path: Path) -> list[TreeNode]:
        """Load children for a directory node.

        Args:
            path: Path to the directory.

        Returns:
            List of child TreeNode objects.
        """
        try:
            entries = list(path.iterdir())
        except PermissionError:
            return []

        # Sort entries
        if self.sort_folders_first:
            entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        else:
            entries.sort(key=lambda p: p.name.lower())

        children = []
        for entry in entries:
            # For lazy loading, only load one level deep
            load_grandchildren = not self.lazy_load
            node = self._create_node_from_path(entry, load_children=load_grandchildren)
            if node:
                children.append(node)

        return children

    def _should_include(self, path: Path) -> bool:
        """Check if a path should be included in the tree.

        Args:
            path: Path to check.

        Returns:
            True if the path should be included.
        """
        name = path.name

        # Check hidden files
        if not self.show_hidden and name.startswith("."):
            return False

        # Apply custom filter
        if self.file_filter and not self.file_filter(path):
            return False

        return True

    def _handle_select(self, node: TreeNode) -> None:
        """Handle node selection."""
        if node.data and self.on_file_select:
            self.on_file_select(node.data)

        # Lazy load children when selecting a folder
        if self.lazy_load and node.is_folder and not node.children:
            node.children = self._load_children(node.data)
            self._rebuild_node_map()

    def _handle_double_click(self, node: TreeNode) -> None:
        """Handle double-click on a node."""
        if node.data:
            if node.is_folder:
                # Toggle expansion for folders
                node.is_expanded = not node.is_expanded
                self.render()
            elif self.on_file_open:
                self.on_file_open(node.data)

    def _handle_move(self, item_id: str, new_parent_id: str) -> None:
        """Handle move operation."""
        src_path = Path(item_id)
        dest_dir = Path(new_parent_id)

        if self.on_file_move:
            success = self.on_file_move(src_path, dest_dir)
            if success:
                move_node(self.roots, item_id, new_parent_id)
                self._rebuild_node_map()
                self.render()
        else:
            # Default behavior: update the tree model
            move_node(self.roots, item_id, new_parent_id)
            self._rebuild_node_map()
            self.render()

    def _handle_delete(self, item_id: str) -> None:
        """Handle delete operation."""
        path = Path(item_id)

        if self.on_file_delete:
            success = self.on_file_delete(path)
            if success:
                delete_node(self.roots, item_id)
                self._rebuild_node_map()
                self.render()
        else:
            # Default behavior: just remove from tree
            delete_node(self.roots, item_id)
            self._rebuild_node_map()
            self.render()

    def get_path(self, node_id: str) -> Path | None:
        """Get the Path for a node ID.

        Args:
            node_id: The node ID (which is the string path).

        Returns:
            Path object or None.
        """
        node = self.get_node(node_id)
        return node.data if node else None

    def expand_to_path(self, target_path: str | Path) -> None:
        """Expand the tree to reveal a specific path.

        Args:
            target_path: Path to reveal in the tree.
        """
        target = Path(target_path)
        if not self.root_path:
            return

        # Get relative path parts
        try:
            relative = target.relative_to(self.root_path)
        except ValueError:
            return

        # Build up the path and expand each folder
        current = self.root_path
        for part in relative.parts[:-1]:  # Exclude the final item
            current = current / part
            node = self._path_to_node.get(str(current))
            if node and node.is_folder:
                node.is_expanded = True
                if self.lazy_load and not node.children:
                    node.children = self._load_children(current)

        self._rebuild_node_map()
        self.render()

        # Select the target
        self.select_node(str(target))


def create_file_tree(
    root_path: str | Path,
    on_select: Callable[[Path], None] | None = None,
    on_open: Callable[[Path], None] | None = None,
    **kwargs: Any,
) -> FileTreeView:
    """Convenience function to create a file tree view.

    Args:
        root_path: Root directory to display.
        on_select: Callback when a file is selected.
        on_open: Callback when a file is opened (double-clicked).
        **kwargs: Additional arguments passed to FileTreeView.

    Returns:
        Configured FileTreeView instance.
    """
    return FileTreeView(
        root_path=root_path,
        on_file_select=on_select,
        on_file_open=on_open,
        **kwargs,
    )
