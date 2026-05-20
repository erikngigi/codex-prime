"""
controllers.py — Application controller.

Owns session state, coordinates background threads, and drives view transitions.
All API calls are dispatched to worker threads so the Tk main loop is never blocked.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Optional

from models import (APIError, APIService, AuthSession, CertificatesPage,
                    UnauthorizedError)

if TYPE_CHECKING:
    from views.dashboard_view import DashboardView
    from views.login_view import LoginView

logger = logging.getLogger(__name__)


class AppController:
    """
    Central controller.  The root Tk window and both views hold a reference to
    this object; they call its methods rather than touching the API directly.
    """

    def __init__(self, root: "tk.Tk") -> None:  # type: ignore[name-defined]
        self._root = root
        self._session: Optional[AuthSession] = None
        self._login_view: Optional["LoginView"] = None
        self._dashboard_view: Optional["DashboardView"] = None

    # ------------------------------------------------------------------
    # View wiring
    # ------------------------------------------------------------------

    def set_login_view(self, view: "LoginView") -> None:
        self._login_view = view

    def set_dashboard_view(self, view: "DashboardView") -> None:
        self._dashboard_view = view

    # ------------------------------------------------------------------
    # Auth actions
    # ------------------------------------------------------------------

    def attempt_login(self, username: str, password: str) -> None:
        """Called by LoginView on submit.  Dispatches to background thread."""
        if not username or not password:
            if self._login_view:
                self._login_view.show_error("Username and password are required.")
            return

        if self._login_view:
            self._login_view.set_loading(True)

        thread = threading.Thread(
            target=self._login_worker,
            args=(username, password),
            daemon=True,
        )
        thread.start()

    def _login_worker(self, username: str, password: str) -> None:
        """Runs on a background thread — never touches Tk widgets directly."""
        try:
            session = APIService.login(username, password)
            self._root.after(0, self._on_login_success, session)
        except APIError as exc:
            self._root.after(0, self._on_login_failure, str(exc))

    def _on_login_success(self, session: AuthSession) -> None:
        """Scheduled back onto the main thread after successful login."""
        self._session = session
        if self._login_view:
            self._login_view.set_loading(False)
            self._login_view.hide()
        if self._dashboard_view:
            self._dashboard_view.show(session)
            self._load_certificates()

    def _on_login_failure(self, message: str) -> None:
        if self._login_view:
            self._login_view.set_loading(False)
            self._login_view.show_error(message)

    def logout(self, message: str = "") -> None:
        """Clear session and return to login screen."""
        self._session = None
        if self._dashboard_view:
            self._dashboard_view.hide()
        if self._login_view:
            self._login_view.show()
            if message:
                self._login_view.show_error(message)

    # ------------------------------------------------------------------
    # Certificate actions
    # ------------------------------------------------------------------

    def refresh_certificates(self) -> None:
        """Called by DashboardView's Refresh button."""
        if not self._session:
            return
        self._load_certificates()

    def _load_certificates(self) -> None:
        if not self._session:
            return
        if self._dashboard_view:
            self._dashboard_view.set_loading(True)

        thread = threading.Thread(
            target=self._certificates_worker,
            args=(self._session,),
            daemon=True,
        )
        thread.start()

    def _certificates_worker(self, session: AuthSession) -> None:
        try:
            page = APIService.get_certificates(session)
            self._root.after(0, self._on_certificates_success, page)
        except UnauthorizedError:
            self._root.after(0, self._on_session_expired)
        except APIError as exc:
            self._root.after(0, self._on_certificates_failure, str(exc))

    def _on_certificates_success(self, page: CertificatesPage) -> None:
        if self._dashboard_view:
            self._dashboard_view.set_loading(False)
            self._dashboard_view.populate(page)

    def _on_certificates_failure(self, message: str) -> None:
        if self._dashboard_view:
            self._dashboard_view.set_loading(False)
            self._dashboard_view.show_status_error(message)

    def _on_session_expired(self) -> None:
        self.logout("Your session has expired. Please log in again.")
