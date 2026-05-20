"""
views/dashboard_view.py — Main data dashboard.

Responsibilities: display session info, render the certificates Treeview,
expose loading/error states, and provide a Refresh action.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING, Optional

import config
from models import AuthSession, Certificate, CertificatesPage

if TYPE_CHECKING:
    from controllers import AppController


# Treeview column definitions: (column_id, display_header, width, anchor)
_COLUMNS: list[tuple[str, str, int, str]] = [
    ("id", "ID", 55, "center"),
    ("registration", "Registration", 100, "w"),
    ("make_n_type", "Make & Type", 160, "w"),
    ("category", "Category", 180, "w"),
    ("status", "Status", 80, "center"),
    ("client_id", "Client ID", 100, "center"),
    ("fitting_date", "Fitted", 130, "w"),
    ("speed_threshold", "Speed Limit", 80, "center"),
    ("technician", "Technician", 140, "w"),
    ("location", "Install Location", 160, "w"),
]


class DashboardView(tk.Frame):
    """Full-window dashboard frame."""

    def __init__(self, parent: tk.Misc, controller: "AppController") -> None:
        super().__init__(parent, bg=config.COLOR_BG_DARK)
        self._controller = controller
        self._root = parent
        self._session: Optional[AuthSession] = None
        self._build_styles()
        self._build_ui()
        controller.set_dashboard_view(self)

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Dashboard.Treeview",
            background=config.COLOR_BG_DARK,
            foreground=config.COLOR_FG_PRIMARY,
            rowheight=28,
            fieldbackground=config.COLOR_BG_DARK,
            borderwidth=0,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
        )
        style.configure(
            "Dashboard.Treeview.Heading",
            background=config.COLOR_BG_PANEL,
            foreground=config.COLOR_ACCENT,
            relief="flat",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
        )
        style.map(
            "Dashboard.Treeview",
            background=[("selected", config.COLOR_ACCENT)],
            foreground=[("selected", config.COLOR_BG_DARK)],
        )
        style.configure(
            "Accent.TButton",
            background=config.COLOR_ACCENT,
            foreground=config.COLOR_BG_DARK,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            borderwidth=0,
            padding=(14, 6),
        )
        style.configure(
            "Loading.Horizontal.TProgressbar",
            troughcolor=config.COLOR_BG_PANEL,
            background=config.COLOR_ACCENT,
            borderwidth=0,
        )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ── Top navigation bar ─────────────────────────────────────────
        nav = tk.Frame(self, bg=config.COLOR_BG_PANEL, height=56)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        tk.Label(
            nav,
            text="Fleet Monitor",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ACCENT,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SUBTITLE, "bold"),
        ).pack(side="left", padx=20)

        # Quit button
        tk.Button(
            nav,
            text="Quit",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ERROR,
            activebackground=config.COLOR_BG_PANEL,
            activeforeground=config.COLOR_ERROR,
            relief="flat",
            cursor="hand2",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
            command=self._root.destroy,
        ).pack(side="right", padx=(0, 8))

        # Logout button
        tk.Button(
            nav,
            text="Logout",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_MUTED,
            activebackground=config.COLOR_BG_PANEL,
            activeforeground=config.COLOR_FG_PRIMARY,
            relief="flat",
            cursor="hand2",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
            command=self._on_logout,
        ).pack(side="right", padx=20)

        # Session info
        self._session_label_var = tk.StringVar()
        tk.Label(
            nav,
            textvariable=self._session_label_var,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_MUTED,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
        ).pack(side="right", padx=4)

        # ── Toolbar ────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=config.COLOR_BG_DARK, pady=10)
        toolbar.pack(fill="x", padx=20)

        tk.Label(
            toolbar,
            text="Certificates",
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_FG_PRIMARY,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SUBTITLE, "bold"),
        ).pack(side="left")

        self._total_label = tk.Label(
            toolbar,
            text="",
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_FG_MUTED,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
        )
        self._total_label.pack(side="left", padx=(10, 0))

        self._refresh_btn = ttk.Button(
            toolbar,
            text="Refresh",
            style="Accent.TButton",
            command=self._on_refresh,
        )
        self._refresh_btn.pack(side="right")

        # ── Status / error bar ─────────────────────────────────────────
        self._status_var = tk.StringVar()
        self._status_bar = tk.Label(
            self,
            textvariable=self._status_var,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
            anchor="w",
        )
        self._status_bar.pack(fill="x", padx=20)

        # ── Loading bar ────────────────────────────────────────────────
        self._progress = ttk.Progressbar(
            self,
            mode="indeterminate",
            style="Loading.Horizontal.TProgressbar",
        )
        self._progress.pack(fill="x", padx=20, pady=(0, 6))
        self._progress.pack_forget()

        # ── Treeview + scrollbars ──────────────────────────────────────
        tree_frame = tk.Frame(self, bg=config.COLOR_BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        col_ids = [c[0] for c in _COLUMNS]
        self._tree = ttk.Treeview(
            tree_frame,
            columns=col_ids,
            show="headings",
            style="Dashboard.Treeview",
            selectmode="browse",
        )

        for col_id, header, width, anchor in _COLUMNS:
            self._tree.heading(col_id, text=header)
            self._tree.column(col_id, width=width, anchor=anchor, minwidth=50, stretch=False)

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        self._tree.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Alternating row tags
        self._tree.tag_configure("odd", background=config.COLOR_BG_DARK)
        self._tree.tag_configure("even", background=config.COLOR_BG_ROW_ALT)
        self._tree.tag_configure("active", foreground=config.COLOR_SUCCESS)
        self._tree.tag_configure("repair", foreground=config.COLOR_ERROR)

    # ------------------------------------------------------------------
    # Public interface (called by controller via main thread)
    # ------------------------------------------------------------------

    def show(self, session: AuthSession) -> None:
        self._session = session
        self._session_label_var.set(f"Signed in as  {session.full_name}  ({session.role.upper()})")
        self.lift()
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide(self) -> None:
        self.place_forget()

    def set_loading(self, loading: bool) -> None:
        if loading:
            self._refresh_btn.state(["disabled"])
            self._status_var.set("")
            self._progress.pack(fill="x", padx=20, pady=(0, 6))
            self._progress.start(10)
        else:
            self._progress.stop()
            self._progress.pack_forget()
            self._refresh_btn.state(["!disabled"])

    def populate(self, page: CertificatesPage) -> None:
        """Clear and refill the Treeview with certificate data."""
        self._tree.delete(*self._tree.get_children())
        self._total_label.config(text=f"{page.total} record{'s' if page.total != 1 else ''}  —  " f"page {page.page}")
        self._status_var.set("")

        for idx, cert in enumerate(page.data):
            tags: list[str] = ["even" if idx % 2 == 0 else "odd"]
            if cert.status.lower() == "active":
                tags.append("active")
            if cert.needs_repair:
                tags.append("repair")

            self._tree.insert(
                "",
                "end",
                iid=str(cert.id),
                values=(
                    cert.id,
                    cert.vehicle_registration,
                    cert.vehicle_make_n_type,
                    cert.vehicle_category,
                    cert.status.upper(),
                    cert.client_id,
                    (cert.fitting_date or "")[:19],
                    f"{cert.speed_threshold} km/h",
                    cert.fitting_technician_nickname,
                    cert.location_installation,
                ),
                tags=tags,
            )

    def show_status_error(self, message: str) -> None:
        self._status_var.set(f"!  {message}")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_refresh(self) -> None:
        self._controller.refresh_certificates()

    def _on_logout(self) -> None:
        self._controller.logout()
