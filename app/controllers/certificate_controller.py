"""
app/controllers/certificate_controller.py — Certificate Data Sub-Controller.

Coordinates backend payload transformations and handles live network text-matching
queries using parameter 'search' across asynchronous execution contexts.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.models.api_client import APIError, UnauthorizedError
from app.models.certificate_models import CertificatesPage

if TYPE_CHECKING:
    from app.controllers.base_controller import AppCoordinator

logger = logging.getLogger(__name__)


class CertificateController:
    """Manages tracking adjustments, parsing parameters, and async payload transformations."""

    def __init__(self, coordinator: AppCoordinator) -> None:
        self.coordinator = coordinator
        self.page_size: int = 20

    def set_page_size(self, size: int) -> None:
        """Alters target page limits dynamically and immediately updates data tables."""
        logger.debug(f"Mutating runtime database result offset window sizes to index count: {size}")
        self.page_size = size
        self.refresh_certificates()

    def refresh_certificates(self) -> None:
        """Dispatches automated or manual requests targeting remote storage metrics."""
        if not self.coordinator.session:
            return

        if self.coordinator.dashboard_view:
            # Check if there is an active text string inside our custom registration search box
            active_search = ""
            if hasattr(self.coordinator.dashboard_view, "_search_var"):
                active_search = self.coordinator.dashboard_view._search_var.get().strip()

            if active_search:
                self.search_by_registration(active_search)
                return

            self.coordinator.dashboard_view.set_loading(True)

        self.coordinator.execute_async(worker_func=self._fetch_all_worker, worker_args=(self.coordinator.session,), name="CertificateFetchPipeline")

    def search_by_registration(self, registration_query: str) -> None:
        """Dispatches an explicit background thread request targeting a specific registration code."""
        if not self.coordinator.session:
            return

        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(True)

        self.coordinator.execute_async(
            worker_func=self._certificates_worker, worker_args=(self.coordinator.session, registration_query), name="CertificateSearchPipeline"
        )

    def _fetch_all_worker(self, session) -> None:
        """Standard sync tracking target routine mapping basic list requests onto display tables."""
        try:
            page = CertificatesPage.get_certificates(session, limit=self.page_size)
            self.coordinator.root_window.after(0, self._on_certificates_success, page)
        except UnauthorizedError:
            self.coordinator.root_window.after(0, self._on_session_expired)
        except APIError as exc:
            self.coordinator.root_window.after(0, self._on_certificates_failure, str(exc))

    def _certificates_worker(self, session, registration_query: str) -> None:
        """Executes the specialized registration search by passing registration values as keyword inputs."""
        try:
            # We try to pass 'search' as an explicit keyword arg to your static model endpoint.
            # If your models.py code hasn't been updated yet to include `search=None` inside its method arguments signature,
            # we fall back to a safe try/except fallback block or a direct data pass configuration.
            try:
                page = CertificatesPage.get_certificates(session, limit=1, search=registration_query)  # type: ignore
            except TypeError:
                # Fallback implementation signature handler: If models.py has a fixed structural signature,
                # we notify the client space or log it clearly so that the signature can be aligned.
                logger.warning("Method signature error caught. Ensure get_certificates receives optional search parameter.")
                raise APIError("Model layer method signature must be updated to accept optional parameter 'search'.")

            target_record_dict: dict | None = None

            if hasattr(page, "data") and page.data:
                # Pluck out the primary verified asset from the data list array
                item = page.data[0]
                if hasattr(item, "__dict__"):
                    target_record_dict = item.__dict__
                elif isinstance(item, dict):
                    target_record_dict = item

            if target_record_dict:
                self.coordinator.root_window.after(0, self._on_match_success, target_record_dict)
            else:
                self.coordinator.root_window.after(
                    0, self._on_certificates_failure, f"No records found corresponding to registration code '{registration_query.upper()}'."
                )

        except UnauthorizedError:
            self.coordinator.root_window.after(0, self._on_session_expired)
        except APIError as exc:
            self.coordinator.root_window.after(0, self._on_certificates_failure, str(exc))

    def _on_certificates_success(self, page: CertificatesPage) -> None:
        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(False)
            # Standard treeview layout population fallback logic
            if hasattr(self.coordinator.dashboard_view, "populate"):
                self.coordinator.dashboard_view.populate(page)

    def _on_match_success(self, matched_payload: dict) -> None:
        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(False)
            if hasattr(self.coordinator.dashboard_view, "populate_profile"):
                self.coordinator.dashboard_view.populate_profile(matched_payload)

    def _on_certificates_failure(self, message: str) -> None:
        if self.coordinator.dashboard_view:
            if hasattr(self.coordinator.dashboard_view, "clear_fields"):
                self.coordinator.dashboard_view.clear_fields()
            self.coordinator.dashboard_view.set_loading(False)
            self.coordinator.dashboard_view.show_status_error(message)

    def _on_session_expired(self) -> None:
        self.coordinator.force_logout("Active connection token scope expired. Please access authorization spaces again.")
