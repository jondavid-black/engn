"""Reusable domain views for engn applications.

This module provides shared domain views that can be used across
sysengn, projengn, and other engn applications.
"""

from typing import Any

import flet as ft
from flet.controls.padding import Padding


class DocsView(ft.Container):
    """Documentation view.

    A reusable documentation browser with navigation tree, content area,
    and table of contents. Can be customized for different applications.
    """

    def __init__(
        self,
        app_name: str = "Engn",
        initial_content: str | None = None,
    ):
        """Initialize the documentation view.

        Args:
            app_name: Name of the application for documentation context.
            initial_content: Optional initial markdown content to display.
        """
        super().__init__()
        self.app_name = app_name

        default_content = f"""
This section covers how to work with projects in {app_name}.

## Creating a Project

To create a new project, use the project dropdown in the toolbar and select "New Project".

## Project Structure

Each project contains:
- **Requirements** - System requirements and specifications
- **Models** - System models and diagrams
- **Documentation** - Project documentation

## Best Practices

1. Keep models synchronized with requirements
2. Use consistent naming conventions
3. Document all interfaces
        """

        self.markdown_content = initial_content or default_content

        # Mock doc tree
        doc_tree = ft.Column(
            controls=[
                self._create_doc_item("Getting Started", ft.Icons.PLAY_ARROW, True),
                self._create_doc_item("Installation", ft.Icons.DOWNLOAD, False),
                self._create_doc_item("Quick Start", ft.Icons.ROCKET_LAUNCH, False),
                self._create_doc_item("User Guide", ft.Icons.MENU_BOOK, True),
                self._create_doc_item("Projects", ft.Icons.FOLDER, False),
                self._create_doc_item("Workflows", ft.Icons.ACCOUNT_TREE, False),
                self._create_doc_item("API Reference", ft.Icons.CODE, True),
                self._create_doc_item("Configuration", ft.Icons.SETTINGS, False),
            ],
            spacing=2,
        )

        # Left panel - nav
        left_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.TextField(
                        hint_text="Search docs...",
                        prefix_icon=ft.Icons.SEARCH,
                        dense=True,
                    ),
                    ft.Container(height=12),
                    doc_tree,
                ],
                expand=True,
            ),
            width=260,
            padding=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=8,
        )

        # Content area
        content_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.TextButton("Home", icon=ft.Icons.HOME),
                            ft.Text("/", color=ft.Colors.GREY_500),
                            ft.TextButton("User Guide", icon=ft.Icons.MENU_BOOK),
                            ft.Text("/", color=ft.Colors.GREY_500),
                            ft.Text("Projects"),
                        ],
                        spacing=4,
                    ),
                    ft.Container(height=16),
                    ft.Text("Projects", size=32, weight=ft.FontWeight.BOLD),
                    ft.Container(height=12),
                    ft.Markdown(
                        self.markdown_content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
            padding=24,
        )

        # Right panel - table of contents
        toc_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("On this page", weight=ft.FontWeight.BOLD, size=12),
                    ft.Container(height=8),
                    ft.TextButton(
                        "Creating a Project", style=ft.ButtonStyle(padding=4)
                    ),
                    ft.TextButton("Project Structure", style=ft.ButtonStyle(padding=4)),
                    ft.TextButton("Best Practices", style=ft.ButtonStyle(padding=4)),
                ],
            ),
            width=180,
            padding=16,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[left_panel, content_area, toc_panel],
                    expand=True,
                    spacing=0,
                ),
            ],
            expand=True,
        )
        self.expand = True

    def _create_doc_item(self, text: str, icon: Any, is_section: bool) -> ft.Container:
        """Create a documentation tree item."""
        weight = ft.FontWeight.BOLD if is_section else None
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=16),
                    ft.Text(text, weight=weight),
                ],
                spacing=8,
            ),
            padding=Padding.only(left=0 if is_section else 16, top=4, bottom=4),
        )


class BaselineView(ft.Container):
    """Program Baseline view for projengn.

    Displays baseline configuration including cost, schedule,
    and scope baselines for program management.
    """

    def __init__(self):
        super().__init__()

        # Baseline summary cards
        baseline_cards = ft.Row(
            controls=[
                self._create_baseline_card(
                    "Cost Baseline",
                    "$2.4M",
                    "Budget allocated",
                    ft.Icons.ATTACH_MONEY,
                    ft.Colors.GREEN,
                ),
                self._create_baseline_card(
                    "Schedule Baseline",
                    "18 months",
                    "Program duration",
                    ft.Icons.CALENDAR_MONTH,
                    ft.Colors.BLUE,
                ),
                self._create_baseline_card(
                    "Scope Baseline",
                    "42 deliverables",
                    "Work packages defined",
                    ft.Icons.CHECKLIST,
                    ft.Colors.PURPLE,
                ),
            ],
            wrap=True,
            spacing=16,
        )

        # Work Breakdown Structure preview
        wbs_items = ft.Column(
            controls=[
                self._create_wbs_item("1.0 Program Management", 0, "$240K"),
                self._create_wbs_item("1.1 Planning", 1, "$80K"),
                self._create_wbs_item("1.2 Oversight", 1, "$160K"),
                self._create_wbs_item("2.0 Systems Engineering", 0, "$480K"),
                self._create_wbs_item("2.1 Requirements", 1, "$120K"),
                self._create_wbs_item("2.2 Design", 1, "$200K"),
                self._create_wbs_item("2.3 Integration", 1, "$160K"),
                self._create_wbs_item("3.0 Development", 0, "$1.2M"),
                self._create_wbs_item("4.0 Test & Evaluation", 0, "$480K"),
            ],
            spacing=4,
        )

        wbs_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Work Breakdown Structure",
                                size=18,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(icon=ft.Icons.ADD, tooltip="Add WBS Element"),
                            ft.IconButton(icon=ft.Icons.EDIT, tooltip="Edit"),
                        ],
                    ),
                    ft.Divider(),
                    wbs_items,
                ],
                expand=True,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
            expand=True,
        )

        # Milestone timeline
        milestones = ft.Column(
            controls=[
                self._create_milestone("Program Kickoff", "2024-01-15", "Completed"),
                self._create_milestone("SRR", "2024-03-01", "Completed"),
                self._create_milestone("PDR", "2024-06-15", "In Progress"),
                self._create_milestone("CDR", "2024-09-30", "Planned"),
                self._create_milestone("TRR", "2025-03-15", "Planned"),
                self._create_milestone("FCA/PCA", "2025-06-30", "Planned"),
            ],
            spacing=8,
        )

        milestone_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Key Milestones", size=18, weight=ft.FontWeight.W_500),
                    ft.Divider(),
                    milestones,
                ],
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
            width=350,
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Program Baseline", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=16),
                baseline_cards,
                ft.Container(height=24),
                ft.Row(
                    controls=[wbs_panel, milestone_panel],
                    spacing=16,
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.padding = 24
        self.expand = True

    def _create_baseline_card(
        self, title: str, value: str, subtitle: str, icon: Any, color: str
    ) -> ft.Card:
        """Create a baseline summary card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(icon, color=color, size=28),
                                ft.Container(expand=True),
                            ],
                        ),
                        ft.Text(value, size=28, weight=ft.FontWeight.BOLD),
                        ft.Text(title, size=14),
                        ft.Text(subtitle, size=12, color=ft.Colors.GREY_500),
                    ],
                    spacing=4,
                ),
                padding=20,
                width=200,
            ),
        )

    def _create_wbs_item(self, text: str, indent: int, budget: str) -> ft.Container:
        """Create a WBS tree item."""
        weight = ft.FontWeight.BOLD if indent == 0 else None
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(text, weight=weight, expand=True),
                    ft.Text(budget, color=ft.Colors.GREY_500),
                ],
            ),
            padding=Padding.only(left=indent * 24, top=4, bottom=4),
        )

    def _create_milestone(self, name: str, date: str, status: str) -> ft.Container:
        """Create a milestone item."""
        status_color = {
            "Completed": ft.Colors.GREEN,
            "In Progress": ft.Colors.ORANGE,
            "Planned": ft.Colors.GREY_500,
        }.get(status, ft.Colors.GREY_500)

        status_icon = {
            "Completed": ft.Icons.CHECK_CIRCLE,
            "In Progress": ft.Icons.PENDING,
            "Planned": ft.Icons.CIRCLE_OUTLINED,
        }.get(status, ft.Icons.CIRCLE_OUTLINED)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(status_icon, color=status_color, size=20),
                    ft.Column(
                        controls=[
                            ft.Text(name, weight=ft.FontWeight.W_500),
                            ft.Text(date, size=12, color=ft.Colors.GREY_500),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Chip(
                        label=ft.Text(status, size=10),
                        bgcolor=status_color,
                    ),
                ],
                spacing=12,
            ),
            padding=4,
        )


class ActualView(ft.Container):
    """Program Actuals view for projengn.

    Displays actual performance data including cost actuals,
    schedule progress, and earned value metrics.
    """

    def __init__(self):
        super().__init__()

        # Performance summary cards
        performance_cards = ft.Row(
            controls=[
                self._create_metric_card(
                    "Actual Cost",
                    "$1.1M",
                    "+2.3% vs plan",
                    ft.Icons.ATTACH_MONEY,
                    ft.Colors.AMBER,
                ),
                self._create_metric_card(
                    "Schedule Progress",
                    "45%",
                    "On Track",
                    ft.Icons.TIMELINE,
                    ft.Colors.GREEN,
                ),
                self._create_metric_card(
                    "Earned Value",
                    "$980K",
                    "BCWP",
                    ft.Icons.TRENDING_UP,
                    ft.Colors.BLUE,
                ),
                self._create_metric_card(
                    "Variance",
                    "-$120K",
                    "Cost Variance",
                    ft.Icons.SHOW_CHART,
                    ft.Colors.RED,
                ),
            ],
            wrap=True,
            spacing=16,
        )

        # Earned Value chart placeholder
        ev_chart = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Earned Value Performance",
                        size=18,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.SHOW_CHART,
                                    size=64,
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "EV Chart Placeholder",
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Text("BCWS", size=12),
                                            bgcolor=ft.Colors.BLUE_100,
                                            padding=8,
                                            border_radius=4,
                                        ),
                                        ft.Container(
                                            content=ft.Text("BCWP", size=12),
                                            bgcolor=ft.Colors.GREEN_100,
                                            padding=8,
                                            border_radius=4,
                                        ),
                                        ft.Container(
                                            content=ft.Text("ACWP", size=12),
                                            bgcolor=ft.Colors.RED_100,
                                            padding=8,
                                            border_radius=4,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=16,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        ),
                        expand=True,
                        height=250,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
                expand=True,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
            expand=True,
        )

        # Recent actuals table
        actuals_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("WBS")),
                ft.DataColumn(label=ft.Text("Description")),
                ft.DataColumn(label=ft.Text("Planned"), numeric=True),
                ft.DataColumn(label=ft.Text("Actual"), numeric=True),
                ft.DataColumn(label=ft.Text("Variance"), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("1.1")),
                        ft.DataCell(ft.Text("Planning")),
                        ft.DataCell(ft.Text("$80K")),
                        ft.DataCell(ft.Text("$75K")),
                        ft.DataCell(ft.Text("+$5K", color=ft.Colors.GREEN)),
                    ]
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("2.1")),
                        ft.DataCell(ft.Text("Requirements")),
                        ft.DataCell(ft.Text("$120K")),
                        ft.DataCell(ft.Text("$135K")),
                        ft.DataCell(ft.Text("-$15K", color=ft.Colors.RED)),
                    ]
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("2.2")),
                        ft.DataCell(ft.Text("Design")),
                        ft.DataCell(ft.Text("$200K")),
                        ft.DataCell(ft.Text("$180K")),
                        ft.DataCell(ft.Text("+$20K", color=ft.Colors.GREEN)),
                    ]
                ),
            ],
        )

        actuals_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Cost Actuals by WBS",
                                size=18,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(icon=ft.Icons.DOWNLOAD, tooltip="Export"),
                            ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refresh"),
                        ],
                    ),
                    ft.Divider(),
                    actuals_table,
                ],
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Program Actuals", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=16),
                performance_cards,
                ft.Container(height=24),
                ev_chart,
                ft.Container(height=24),
                actuals_panel,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.padding = 24
        self.expand = True

    def _create_metric_card(
        self, title: str, value: str, subtitle: str, icon: Any, color: str
    ) -> ft.Card:
        """Create a performance metric card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(icon, color=color, size=28),
                                ft.Container(expand=True),
                            ],
                        ),
                        ft.Text(value, size=28, weight=ft.FontWeight.BOLD),
                        ft.Text(title, size=14),
                        ft.Text(subtitle, size=12, color=ft.Colors.GREY_500),
                    ],
                    spacing=4,
                ),
                padding=20,
                width=180,
            ),
        )


class AnalyzeView(ft.Container):
    """Program Analysis view for projengn.

    Provides analysis tools for program health, risk assessment,
    and performance forecasting.
    """

    def __init__(self):
        super().__init__()

        # Health indicators
        health_row = ft.Row(
            controls=[
                self._create_health_indicator("Cost", "Yellow", 0.85),
                self._create_health_indicator("Schedule", "Green", 0.92),
                self._create_health_indicator("Technical", "Green", 0.88),
                self._create_health_indicator("Risk", "Yellow", 0.75),
            ],
            spacing=24,
            wrap=True,
        )

        # Risk matrix
        risk_matrix = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Risk Matrix", size=18, weight=ft.FontWeight.W_500),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.GRID_4X4,
                                    size=64,
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "Risk Matrix Placeholder",
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "5x5 probability/impact matrix",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        height=200,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
            expand=True,
        )

        # Top risks list
        risks_list = ft.Column(
            controls=[
                self._create_risk_item(
                    "R-001",
                    "Supply chain delays",
                    "High",
                    "Cost/Schedule",
                ),
                self._create_risk_item(
                    "R-002",
                    "Technical complexity",
                    "Medium",
                    "Technical",
                ),
                self._create_risk_item(
                    "R-003",
                    "Resource availability",
                    "Medium",
                    "Schedule",
                ),
                self._create_risk_item(
                    "R-004",
                    "Requirements volatility",
                    "Low",
                    "Scope",
                ),
            ],
            spacing=8,
        )

        risks_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Top Risks", size=18, weight=ft.FontWeight.W_500),
                            ft.Container(expand=True),
                            ft.IconButton(icon=ft.Icons.ADD, tooltip="Add Risk"),
                        ],
                    ),
                    ft.Divider(),
                    risks_list,
                ],
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
            width=400,
        )

        # Forecast panel
        forecast_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Forecast", size=18, weight=ft.FontWeight.W_500),
                    ft.Divider(),
                    ft.Row(
                        controls=[
                            ft.Text("EAC:", weight=ft.FontWeight.BOLD),
                            ft.Text("$2.52M"),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("VAC:", weight=ft.FontWeight.BOLD),
                            ft.Text("-$120K", color=ft.Colors.RED),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("TCPI:", weight=ft.FontWeight.BOLD),
                            ft.Text("1.08"),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "Estimated completion: 2025-08-15",
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        "Confidence: 75%",
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                ],
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=16,
            border_radius=8,
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Program Analysis", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=16),
                ft.Text("Program Health", size=20, weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                health_row,
                ft.Container(height=24),
                ft.Row(
                    controls=[risk_matrix, risks_panel],
                    spacing=16,
                    expand=True,
                ),
                ft.Container(height=16),
                forecast_panel,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.padding = 24
        self.expand = True

    def _create_health_indicator(
        self, name: str, status: str, score: float
    ) -> ft.Container:
        """Create a health indicator."""
        color_map = {
            "Green": ft.Colors.GREEN,
            "Yellow": ft.Colors.AMBER,
            "Red": ft.Colors.RED,
        }
        color = color_map.get(status, ft.Colors.GREY_500)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(name, weight=ft.FontWeight.W_500),
                    ft.ProgressRing(
                        value=score,
                        stroke_width=8,
                        color=color,
                        width=60,
                        height=60,
                    ),
                    ft.Text(f"{int(score * 100)}%", size=12),
                    ft.Chip(
                        label=ft.Text(status, size=10),
                        bgcolor=color,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
        )

    def _create_risk_item(
        self, risk_id: str, description: str, level: str, category: str
    ) -> ft.Container:
        """Create a risk list item."""
        level_color = {
            "High": ft.Colors.RED,
            "Medium": ft.Colors.AMBER,
            "Low": ft.Colors.GREEN,
        }.get(level, ft.Colors.GREY_500)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(risk_id, size=12),
                        bgcolor=ft.Colors.GREY_800,
                        padding=6,
                        border_radius=4,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(description),
                            ft.Text(category, size=11, color=ft.Colors.GREY_500),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Chip(
                        label=ft.Text(level, size=10),
                        bgcolor=level_color,
                    ),
                ],
                spacing=12,
            ),
            padding=8,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=4,
        )
