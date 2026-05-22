"""
app/controllers/auth_controller.py — Session initialization sub-controller interfaces.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.models.api_client import APIError, UnauthorizedError
from app.models.auth_models import AuthSession

if TYPE_CHECKING:
    from app.controllers.base_controller import AppCoordinator

logger = logging.getLogger(__name__)


class AuthController:
    """Translates submission inputs into structured interaction routines targeting API clients."""

    def __init__(self, coordinator: AppCoordinator) -> None:
        self.coordinator = coordinator

    def clear_credentials(self) -> None:
        """Flushes active state entries inside the view layer credentials forms"""
        if self.coordinator.login_view:
            self.coordinator.login_view.clear_fields()

    def attempt_login(self, username: str, password: str) -> None:
        """Orchestrates authorization requests using async execution hooks."""
        if not username or not password:
            if self.coordinator.login_view:
                self.coordinator.login_view.show_error("Please supply entries across both input fields.")
            return

        if self.coordinator.login_view:
            self.coordinator.login_view.set_loading(True)

        self.coordinator.execute_async(worker_func=self._login_worker, worker_args=(username, password), name="AuthWorkerPipeline")

    def _login_worker(self, username: str, password: str) -> None:
        """Target execution thread method running structural network interactions."""
        try:
            session = AuthSession.login(username, password)
            self.coordinator.root_window.after(0, self._on_login_success, session)
        except (UnauthorizedError, APIError) as exc:
            self.coordinator.root_window.after(0, self._on_login_failure, str(exc))

    def _on_login_success(self, session: AuthSession) -> None:
        if self.coordinator.login_view:
            self.coordinator.login_view.set_loading(False)
        self.coordinator.switch_to_dashboard(session)

    def _on_login_failure(self, error_message: str) -> None:
        if self.coordinator.login_view:
            self.coordinator.login_view.set_loading(False)
            self.coordinator.login_view.show_error(error_message)

    def terminate_application(self) -> None:
        """Gracefully shutdown all background works and kills the active process."""
        self.coordinator.force_quit()
