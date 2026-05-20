"""
views/login_view.py — Login screen.

Responsibilities: render credentials form, delegate submission to the controller,
display inline error messages without alert popups.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

import config

if TYPE_CHECKING:
    from controllers import AppController


class LoginView(tk.Frame):
    """Full-window login frame placed over the root window."""

    def __init__(self, parent: tk.Misc, controller: "AppController") -> None:
        super().__init__(parent, bg=config.COLOR_BG_DARK)
        self._controller = controller
        self._build_ui()
        controller.set_login_view(self)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ── centre card ──────────────────────────────────────────────
        card = tk.Frame(self, bg=config.COLOR_BG_PANEL, padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / title
        tk.Label(
            card,
            text="⬡  Fleet Monitor",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ACCENT,
            font=(config.FONT_FAMILY, config.FONT_SIZE_TITLE, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 6))

        tk.Label(
            card,
            text="Sign in to your account",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_MUTED,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
        ).grid(row=1, column=0, columnspan=2, pady=(0, 24))

        # Username
        self._make_field_label(card, "USERNAME", row=2)
        self._username_var = tk.StringVar()
        username_entry = self._make_entry(card, self._username_var, row=3)
        username_entry.focus_set()

        # Password
        self._make_field_label(card, "PASSWORD", row=4)
        self._password_var = tk.StringVar()
        self._make_entry(card, self._password_var, row=5, show="•")

        # Error label (hidden initially)
        self._error_var = tk.StringVar()
        self._error_label = tk.Label(
            card,
            textvariable=self._error_var,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
            wraplength=300,
        )
        self._error_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        self._error_label.grid_remove()

        # Submit button
        self._login_btn = tk.Button(
            card,
            text="SIGN IN",
            bg=config.COLOR_ACCENT,
            fg=config.COLOR_BG_DARK,
            activebackground=config.COLOR_ACCENT,
            activeforeground=config.COLOR_BG_DARK,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._on_submit,
        )
        self._login_btn.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        # Loading progress bar (hidden initially)
        self._progress = ttk.Progressbar(card, mode="indeterminate", length=300)
        self._progress.grid(row=8, column=0, columnspan=2, pady=(12, 0))
        self._progress.grid_remove()

        # Bind Enter key to submit
        self.bind_all("<Return>", lambda _event: self._on_submit())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_field_label(self, parent: tk.Frame, text: str, row: int) -> None:
        tk.Label(
            parent,
            text=text,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_MUTED,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            anchor="w",
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 2))

    def _make_entry(
        self,
        parent: tk.Frame,
        var: tk.StringVar,
        row: int,
        show: str = "",
    ) -> tk.Entry:
        entry = tk.Entry(
            parent,
            textvariable=var,
            show=show,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_FG_PRIMARY,
            insertbackground=config.COLOR_ACCENT,
            relief="flat",
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY),
            width=34,
            highlightthickness=1,
            highlightbackground=config.COLOR_BORDER,
            highlightcolor=config.COLOR_ACCENT,
        )
        entry.grid(row=row, column=0, columnspan=2, ipady=6, sticky="ew")
        return entry

    # ------------------------------------------------------------------
    # Public interface (called by controller via main thread)
    # ------------------------------------------------------------------

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
        self._clear_error()
        self._username_var.set("")
        self._password_var.set("")
        self.lift()
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide(self) -> None:
        self.place_forget()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_submit(self) -> None:
        username = self._username_var.get().strip()
        password = self._password_var.get()
        self._controller.attempt_login(username, password)
