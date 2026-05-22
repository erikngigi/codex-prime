"""
app/views/root_window.py — Master Tk containment application frame.

Responsibilities: manages display geometry calculation positioning matrices and enforces theme options.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

import app.config as config


class RootWindow(tk.Tk):
    """Primary layout frame workspace boundary wrapper container class."""

    def __init__(self) -> None:
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        self._calculate_screen_centering()
        self._apply_global_theme_defaults()

    def _calculate_screen_centering(self) -> None:
        self.update_idletasks()
        x_coordinate = (self.winfo_screenwidth() - config.WINDOW_WIDTH) // 2
        y_coordinate = (self.winfo_screenheight() - config.WINDOW_HEIGHT) // 2
        self.geometry(f"+{x_coordinate}+{y_coordinate}")

    def _apply_global_theme_defaults(self) -> None:
        self.configure(bg=config.COLOR_BG_DARK)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=config.COLOR_BG_DARK, foreground=config.COLOR_FG_PRIMARY)

        style.configure(
            "Vertical.TScrollbar",
            troughcolor=config.COLOR_BG_PANEL,
            background=config.COLOR_BORDER,
            borderwidth=0,
            arrowsize=12,
        )
        style.configure(
            "Horizontal.TScrollbar",
            troughcolor=config.COLOR_BG_PANEL,
            background=config.COLOR_BORDER,
            borderwidth=0,
            arrowsize=12,
        )
