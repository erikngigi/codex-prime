"""
main.py — Application entry point.

Creates the root Tk window, wires up the controller and views, then starts
the main event loop.
"""

from __future__ import annotations

import logging
import tkinter as tk
import tkinter.ttk as ttk

import config
from controllers import AppController
from views.dashboard_view import DashboardView
from views.login_view import LoginView


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    )


def apply_global_theme(root: tk.Tk) -> None:
    """Configure root window and global ttk theme defaults."""
    root.configure(bg=config.COLOR_BG_DARK)
    style = ttk.Style(root)
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


def main() -> None:
    setup_logging()

    root = tk.Tk()
    root.title(config.APP_TITLE)
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

    # Centre window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - config.WINDOW_WIDTH) // 2
    y = (root.winfo_screenheight() - config.WINDOW_HEIGHT) // 2
    root.geometry(f"+{x}+{y}")

    apply_global_theme(root)

    # Dependency injection: controller owns state; views hold a reference back
    controller = AppController(root)
    LoginView(root, controller)
    dashboard = DashboardView(root, controller)
    dashboard.hide()  # ensure app always starts on the login screen

    root.mainloop()


if __name__ == "__main__":
    main()
