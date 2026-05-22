"""
app/views/login_view.py — Login UI view layer card layout configuration.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

import app.config as config

if TYPE_CHECKING:
    from app.controllers.auth_controller import AuthController


class LoginView(tk.Frame):
    """Full-viewport layout grid parsing and hosting input forms."""

    def __init__(self, parent: tk.Misc, controller: AuthController) -> None:
        super().__init__(parent, bg=config.COLOR_BG_DARK)
        self._controller = controller
        self._build_ui()

    def _build_ui(self) -> None:
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = tk.Frame(self, bg=config.COLOR_BG_PANEL, padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="⬡  Fleet Monitor",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ACCENT,
            font=(config.FONT_FAMILY, config.FONT_SIZE_TITLE, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 24), sticky="w")

        self._username_var = tk.StringVar()
        self._password_var = tk.StringVar()

        self._username_entry = self._create_field(card, "Username", self._username_var, row=1)
        self._password_entry = self._create_field(card, "Password", self._password_var, row=3, show="*")

        self._error_var = tk.StringVar()
        self._error_label = tk.Label(
            card,
            textvariable=self._error_var,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
            wraplength=260,
            justify="left",
            anchor="w",
        )
        self._error_label.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="ew")
        self._error_label.grid_remove()

        self._progress = ttk.Progressbar(card, mode="indeterminate", style="Horizontal.TProgressbar")
        self._progress.grid(row=6, column=0, columnspan=2, pady=(16, 0), sticky="ew")
        self._progress.grid_remove()

        self._login_btn = tk.Button(
            card,
            text="SIGN IN",
            bg=config.COLOR_ACCENT,
            fg=config.COLOR_BG_DARK,
            activebackground=config.COLOR_ACCENT,
            activeforeground=config.COLOR_BG_DARK,
            relief="flat",
            cursor="hand2",
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY, "bold"),
            pady=10,
            command=self._on_submit,
        )
        self._login_btn.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        self._close_btn = tk.Button(
            card,
            text="CLOSE APPLICATION",
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_ERROR,
            activebackground=config.COLOR_BG_DARK,
            activeforeground=config.COLOR_ERROR,
            relief="flat",
            cursor="hand2",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            pady=8,
            bd=1,
            highlightbackground=config.COLOR_ERROR,
            command=self._controller.terminate_application,
        )
        self._close_btn.grid(row=8, column=0, columnspan=2, pady=(12, 0), sticky="ew")

        self._username_entry.bind("<Return>", lambda e: self._password_entry.focus_set())
        self._password_entry.bind("<Return>", lambda e: self._on_submit())

    def _create_field(self, parent: tk.Frame, label_text: str, variable: tk.StringVar, row: int, show: str | None = None) -> tk.Entry:
        # Field Header Label
        tk.Label(
            parent,
            text=label_text.upper(),
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_MUTED,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ── INTERACTIVE SUB-GRID FRAME CONTAINER ──
        # This frame groups the entry widget and clear button side-by-side seamlessly
        field_container = tk.Frame(parent, bg=config.COLOR_BG_DARK, bd=1, relief="solid")
        field_container.grid(row=row + 1, column=0, columnspan=2, pady=(0, 16), sticky="ew")
        field_container.columnconfigure(0, weight=1)

        entry = tk.Entry(
            field_container,
            textvariable=variable,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_FG_PRIMARY,
            insertbackground=config.COLOR_ACCENT,
            relief="flat",
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY),
            width=26,
            show=show,
        )
        entry.grid(row=0, column=0, ipady=8, ipadx=6, sticky="ew")

        # ── THE "X" CLEAR ICON BUTTON ──
        # Added visually within login_view.py, executing via the Controller interface callback
        clear_btn = tk.Button(
            field_container,
            text="✕",
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_FG_MUTED,
            activebackground=config.COLOR_BG_DARK,
            activeforeground=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            bd=0,
            cursor="hand2",
            padx=8,
            command=self._controller.clear_credentials,  # Wire to Controller action Hook
        )
        clear_btn.grid(row=0, column=1, sticky="ns")

        return entry

    def show_error(self, message: str) -> None:
        self._error_var.set(message)
        self._error_label.grid()

    def _clear_error(self) -> None:
        self._error_var.set("")
        self._error_label.grid_remove()

    def set_loading(self, loading: bool) -> None:
        if loading:
            self._login_btn.config(state="disabled", text="Signing in…")
            self._progress.grid()
            self._progress.start(12)
            self._clear_error()
        else:
            self._login_btn.config(state="normal", text="SIGN IN")
            self._progress.stop()
            self._progress.grid_remove()

    def show(self) -> None:
        self.clear_fields()
        self.lift()
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._username_entry.focus_set()

    def hide(self) -> None:
        self.place_forget()

    def clear_fields(self) -> None:
        """Resets inputs back to safe empty values."""
        self._clear_error()
        self._username_var.set("")
        self._password_var.set("")
        self._username_entry.focus_set()

    def _on_submit(self) -> None:
        username = self._username_var.get().strip()
        password = self._password_var.get()
        self._controller.attempt_login(username, password)
