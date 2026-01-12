"""Mock domain views for SysEngn work domains."""

from typing import Any

import flet as ft
from flet.controls.border import Border
from flet.controls.padding import Padding


class HomeView(ft.Container):
    """Home dashboard view."""

    def __init__(self):
        super().__init__()

        # Stats cards
        stats_row = ft.Row(
            controls=[
                self._create_stat_card(
                    "Projects", "3", ft.Icons.FOLDER, ft.Colors.BLUE
                ),
                self._create_stat_card(
                    "Open Issues", "12", ft.Icons.BUG_REPORT, ft.Colors.ORANGE
                ),
                self._create_stat_card(
                    "Completed", "47", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN
                ),
                self._create_stat_card(
                    "Team Members", "5", ft.Icons.PEOPLE, ft.Colors.PURPLE
                ),
            ],
            wrap=True,
            spacing=16,
        )

        # Recent activity
        activity_list = ft.ListView(
            controls=[
                self._create_activity_item(
                    "Updated requirements.md", "2 minutes ago", ft.Icons.EDIT
                ),
                self._create_activity_item(
                    "Closed issue #42", "15 minutes ago", ft.Icons.CHECK
                ),
                self._create_activity_item(
                    "Added system diagram", "1 hour ago", ft.Icons.IMAGE
                ),
                self._create_activity_item(
                    "Created new component", "3 hours ago", ft.Icons.ADD_BOX
                ),
            ],
            spacing=8,
            height=200,
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=24),
                stats_row,
                ft.Container(height=32),
                ft.Text("Recent Activity", size=20, weight=ft.FontWeight.W_500),
                ft.Container(height=12),
                activity_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.padding = 24
        self.expand = True

    def _create_stat_card(
        self, title: str, value: str, icon: Any, color: str
    ) -> ft.Card:
        """Create a statistics card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(icon, color=color, size=32),
                                ft.Container(expand=True),
                            ],
                        ),
                        ft.Text(value, size=36, weight=ft.FontWeight.BOLD),
                        ft.Text(title, color=ft.Colors.GREY_500),
                    ],
                    spacing=8,
                ),
                padding=20,
                width=180,
            ),
        )

    def _create_activity_item(self, text: str, time: str, icon: Any) -> ft.ListTile:
        """Create an activity list item."""
        return ft.ListTile(
            leading=ft.Icon(icon, size=20),
            title=ft.Text(text),
            subtitle=ft.Text(time, size=12, color=ft.Colors.GREY_500),
        )


class MBSEView(ft.Container):
    """Model-Based System Engineering view."""

    def __init__(self):
        super().__init__()

        # Mock system tree
        tree_items = ft.Column(
            controls=[
                self._create_tree_item("System Architecture", ft.Icons.ACCOUNT_TREE, 0),
                self._create_tree_item("Requirements", ft.Icons.LIST_ALT, 1),
                self._create_tree_item("Use Cases", ft.Icons.PEOPLE, 1),
                self._create_tree_item("Components", ft.Icons.WIDGETS, 1),
                self._create_tree_item("Auth Module", ft.Icons.LOCK, 2),
                self._create_tree_item("Data Module", ft.Icons.STORAGE, 2),
                self._create_tree_item("UI Module", ft.Icons.DESIGN_SERVICES, 2),
                self._create_tree_item("Interfaces", ft.Icons.SYNC_ALT, 1),
                self._create_tree_item("Behaviors", ft.Icons.TIMELINE, 1),
            ],
            spacing=4,
        )

        # Left panel - tree
        left_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("System Model", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    tree_items,
                ],
                expand=True,
            ),
            width=280,
            padding=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=8,
        )

        # Right panel - diagram placeholder
        diagram_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "System Block Diagram",
                                size=18,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(icon=ft.Icons.ZOOM_IN, tooltip="Zoom In"),
                            ft.IconButton(icon=ft.Icons.ZOOM_OUT, tooltip="Zoom Out"),
                            ft.IconButton(icon=ft.Icons.FIT_SCREEN, tooltip="Fit"),
                        ],
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.ARCHITECTURE,
                                    size=64,
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "Diagram canvas placeholder",
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "Select a model element to view",
                                    color=ft.Colors.GREY_600,
                                    size=12,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        border=Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                    ),
                ],
                expand=True,
            ),
            expand=True,
            padding=16,
        )

        self.content = ft.Column(
            controls=[
                ft.Text(
                    "Model-Based System Engineering", size=28, weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=[left_panel, diagram_area],
                    expand=True,
                    spacing=16,
                ),
            ],
            expand=True,
        )
        self.padding = 24
        self.expand = True

    def _create_tree_item(self, text: str, icon: Any, indent: int) -> ft.Container:
        """Create a tree item with indentation."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=18),
                    ft.Text(text),
                ],
                spacing=8,
            ),
            padding=Padding.only(left=indent * 20, top=4, bottom=4),
        )


class UXView(ft.Container):
    """UX Design view."""

    def __init__(self):
        super().__init__()

        # Mock screen list
        screen_list = ft.ListView(
            controls=[
                self._create_screen_item("Login Screen", "screens/login.ux"),
                self._create_screen_item("Dashboard", "screens/dashboard.ux"),
                self._create_screen_item("Settings", "screens/settings.ux"),
                self._create_screen_item("Profile", "screens/profile.ux"),
            ],
            spacing=4,
            height=200,
        )

        # Left panel
        left_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Screens", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    screen_list,
                    ft.Divider(),
                    ft.Text("Components", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self._create_component_chip("Button"),
                    self._create_component_chip("TextField"),
                    self._create_component_chip("Card"),
                    self._create_component_chip("Dialog"),
                ],
                expand=True,
            ),
            width=250,
            padding=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=8,
        )

        # Center - preview area
        preview_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Preview", size=18, weight=ft.FontWeight.W_500),
                            ft.Container(expand=True),
                            ft.SegmentedButton(
                                selected=["desktop"],
                                segments=[
                                    ft.Segment(
                                        value="mobile", icon=ft.Icons.PHONE_ANDROID
                                    ),
                                    ft.Segment(value="tablet", icon=ft.Icons.TABLET),
                                    ft.Segment(value="desktop", icon=ft.Icons.COMPUTER),
                                ],
                            ),
                        ],
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.PHONE_ANDROID,
                                    size=64,
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "Screen preview placeholder",
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "Select a screen to preview",
                                    color=ft.Colors.GREY_600,
                                    size=12,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        border=Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                    ),
                ],
                expand=True,
            ),
            expand=True,
            padding=16,
        )

        # Right panel - properties
        properties_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Properties", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        "No element selected", color=ft.Colors.GREY_500, italic=True
                    ),
                ],
            ),
            width=220,
            padding=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=8,
        )

        self.content = ft.Column(
            controls=[
                ft.Text("UX Design", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=16),
                ft.Row(
                    controls=[left_panel, preview_area, properties_panel],
                    expand=True,
                    spacing=16,
                ),
            ],
            expand=True,
        )
        self.padding = 24
        self.expand = True

    def _create_screen_item(self, name: str, path: str) -> ft.ListTile:
        """Create a screen list item."""
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.PHONE_ANDROID, size=20),
            title=ft.Text(name),
            subtitle=ft.Text(path, size=11, color=ft.Colors.GREY_500),
            dense=True,
        )

    def _create_component_chip(self, name: str) -> ft.Chip:
        """Create a draggable component chip."""
        return ft.Chip(
            label=ft.Text(name),
            leading=ft.Icon(ft.Icons.WIDGETS, size=16),
        )
