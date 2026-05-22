"""
app/main.py — Application primary launcher bootstrap entry hook file.
"""

from __future__ import annotations

import os
import sys

# --- BOOTSTRAP PATH FIX (LOCAL + PYINSTALLER COMPATIBLE) ---
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Using getattr stops linters from complaining about a missing attribute
    BUNDLE_DIR = getattr(sys, "_MEIPASS")
    if BUNDLE_DIR not in sys.path:
        sys.path.insert(0, BUNDLE_DIR)
else:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)
# -----------------------------------------------------------

import logging

from app.controllers.auth_controller import AuthController
from app.controllers.base_controller import AppCoordinator
from app.controllers.fleet_controller import FleetController
from app.views.dashboard_view import DashboardView
from app.views.login_view import LoginView
from app.views.root_window import RootWindow


def setup_logging() -> None:
    """Configures systemic output presentation patterns."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    )


def main() -> None:
    """Initializes central layout components, pairs dependencies, and boots the main loop."""
    setup_logging()

    # 1. Instantiate master Tk container object window frame
    root = RootWindow()

    # 2. Instantiate runtime supervisor system state coordinators
    coordinator = AppCoordinator(root)

    # 3. Instantiate sub-controllers passing state handles
    auth_controller = AuthController(coordinator)
    fleet_controller = FleetController(coordinator)

    # 4. Build isolated UI layout widgets, injecting sub-controllers
    login_view = LoginView(root, auth_controller)
    dashboard_view = DashboardView(root, fleet_controller)

    # 5. Wire layout pointers backwards onto supervisor coordinators
    coordinator.login_view = login_view
    coordinator.dashboard_view = dashboard_view

    # Launch application presentation window
    login_view.show()

    # Hand off system execution thread context down to Tkinter engine loops
    root.mainloop()


if __name__ == "__main__":
    main()
