import flet as ft


class RightDrawer(ft.Container):
    """A horizontally resizable right-side drawer component."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.width = 350
        self.visible = False
        self.bgcolor = ft.Colors.SURFACE
        self.border = ft.Border(left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT))
        self.content = self._build_ui()

    def _build_ui(self):
        # Header with title and close button
        self.title_text = ft.Text(
            "", weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.ON_SURFACE_VARIANT
        )
        header = ft.Container(
            content=ft.Row(
                [
                    self.title_text,
                    ft.IconButton(
                        ft.Icons.CLOSE,
                        icon_size=20,
                        on_click=lambda _: self.hide(),
                        tooltip="Close Drawer",
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(left=15, right=5, top=5, bottom=5),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
        )

        # Content area for dynamic content
        self.content_container = ft.Container(
            expand=True,
            padding=15,
        )

        # Resize handle on the left edge
        self.resize_handle = ft.GestureDetector(
            content=ft.Container(
                width=10,
                bgcolor=ft.Colors.WHITE_10,  # Slight visible background for better hit detection
            ),
            on_pan_update=self._handle_resize,
            on_hover=self._handle_resize_hover,
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
        )

        return ft.Row(
            [
                self.resize_handle,
                ft.Column(
                    [
                        header,
                        ft.Divider(
                            height=1, thickness=1, color=ft.Colors.OUTLINE_VARIANT
                        ),
                        self.content_container,
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def _handle_resize_hover(self, e: ft.HoverEvent):
        """Highlight the resize handle on hover."""
        if isinstance(self.resize_handle.content, ft.Container):
            self.resize_handle.content.bgcolor = (
                ft.Colors.BLUE_400 if e.data == "true" else ft.Colors.WHITE_10
            )
            self.safe_update()

    def safe_update(self):
        """Safely update the control only if it is attached to a page."""
        try:
            if self.page:
                self.update()
        except Exception:
            pass

    def _handle_resize(self, e: ft.DragUpdateEvent):
        # delta_x is positive when moving right, which should decrease width
        dx = getattr(e, "delta_x", 0)
        if dx is None or dx == 0:
            # Fallback for some environments
            dx = getattr(e, "dx", 0)

        if dx is None:
            dx = 0

        w = self.width
        if w is None:
            w = 350

        new_width = w - dx
        if 150 <= new_width <= 1200:  # Increased max width
            self.width = new_width
            self.safe_update()

    def show(self, title: str, content: ft.Control):
        """Show the drawer with specified title and content."""
        self.title_text.value = title
        self.content_container.content = content
        self.visible = True
        self.safe_update()

    def hide(self):
        """Hide the drawer."""
        self.visible = False
        self.safe_update()

    def set_content(self, title: str, content: ft.Control):
        """Update drawer content without changing visibility."""
        self.title_text.value = title
        self.content_container.content = content
        self.safe_update()

    def toggle(self, title: str, content: ft.Control):
        """Toggle drawer visibility or update content if already visible with different title."""
        if self.visible and self.title_text.value == title:
            self.hide()
        else:
            self.show(title, content)
