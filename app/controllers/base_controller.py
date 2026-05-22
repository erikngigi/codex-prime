"""
app/controllers/base_controller.py — Application lifecycle orchestration supervisor.

Abstracts multi-threaded background routines and coordinates top-level frame mapping routes.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any, Callable, Optional

from app.models.auth_models import AuthSession

if TYPE_CHECKING:
    from app.views.dashboard_view import DashboardView
    from app.views.login_view import LoginView
    from app.views.root_window import RootWindow

logger = logging.getLogger(__name__)


class AppCoordinator:
    """Central structural mediator tracking frame profiles and active credentials."""

    def __init__(self, root_window: RootWindow) -> None:
        self.root_window = root_window
        self.session: Optional[AuthSession] = None

        # Post-initialization view bindings
        self.login_view: Optional[LoginView] = None
        self.dashboard_view: Optional[DashboardView] = None

    def execute_async(self, worker_func: Callable[..., Any], worker_args: tuple[Any, ...], name: str) -> None:
        """Spawns an isolated daemon worker thread to handle heavy networking I/O safely."""
        logger.debug(f"Spawning asynchronous lifecycle process execution pipeline thread: [{name}]")
        thread = threading.Thread(target=worker_func, args=worker_args, daemon=True, name=name)
        thread.start()

    def switch_to_dashboard(self, session: AuthSession) -> None:
        """Caches valid access credentials globally and focuses onto primary data spaces."""
        self.session = session
        logger.info(f"Pivoting window focus target spaces for authenticated user footprint: {session.username}")

        if self.login_view:
            self.login_view.hide()
        if self.dashboard_view:
            self.dashboard_view.show(session)

    def force_logout(self, message: Optional[str] = None) -> None:
        """Purges cached memory token instances and maps view contexts retroactively."""
        logger.warning(f"Evicting active session state frame profile. Target Reason: {message or 'Manual Logout'}")
        self.session = None

        if self.dashboard_view:
            self.dashboard_view.hide()
        if self.login_view:
            self.login_view.show()
            if message:
                self.login_view.show_error(message)

    def force_quit(self) -> None:
        """Purges session state and terminates the application process entirely."""
        logger.warning(f"Force quit triggered - destroyinh root window and exiting process.")
        self.session = None
        self.root_window.destroy()
