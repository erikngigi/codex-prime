"""
app/controllers/fleet_controller.py — Unified Fleet Operational Sub-Controller.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.models.api_client import APIError, UnauthorizedError
from app.models.fleet_models import FleetPage

if TYPE_CHECKING:
    from app.controllers.base_controller import AppCoordinator

logger = logging.getLogger(__name__)


class FleetController:
    """Coordinates business operations for multi-endpoint aggregated fleet profiles."""

    def __init__(self, coordinator: AppCoordinator) -> None:
        self.coordinator = coordinator
        self.page_size: int = 20

    def set_page_size(self, size: int) -> None:
        """Alters target listing dimensions and refreshes active datasets."""
        logger.debug(f"Mutating runtime result offset window sizes to index count: {size}")
        self.page_size = size
        self.refresh_fleet_registry()

    def refresh_fleet_registry(self) -> None:
        """Dispatches automated or manual requests targeting remote storage metrics."""
        if not self.coordinator.session:
            return

        active_search = ""
        if self.coordinator.dashboard_view and hasattr(self.coordinator.dashboard_view, "_search_var"):
            active_search = self.coordinator.dashboard_view._search_var.get().strip()

        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(True)

        self.coordinator.execute_async(
            worker_func=self._fleet_worker, worker_args=(self.coordinator.session, active_search), name="FleetDataAggregatorPipeline"
        )

    def search_by_registration(self, registration_code: str) -> None:
        """Executes targeted lookup matching filters on backend datastores."""
        if not self.coordinator.session or not registration_code.strip():
            return

        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(True)

        self.coordinator.execute_async(
            worker_func=self._fleet_worker, worker_args=(self.coordinator.session, registration_code.strip()), name="FleetQueryTargetPipeline"
        )

    def _fleet_worker(self, session: Any, query: str) -> None:
        """Background thread target worker executing data fetch routines safely."""
        try:
            fleet_page = FleetPage.fetch_combined_fleet(session, limit=self.page_size, search=query)

            if query:
                normalized_query = query.upper().strip()
                # Isolate the exact matching asset out of the parsed return page list
                matched_asset = None
                for asset in fleet_page.assets:
                    if asset.vehicle_registration == normalized_query or asset.limiter_serial == normalized_query:
                        matched_asset = asset
                        break

                if matched_asset:
                    self.coordinator.root_window.after(0, self._on_match_success, matched_asset)
                else:
                    raise APIError(f"No records found matching tracking registration profile '{query}'.", status_code=404)
            else:
                self.coordinator.root_window.after(0, self._on_fleet_success, fleet_page)

        except UnauthorizedError:
            self.coordinator.root_window.after(0, self._on_session_expired)
        except APIError as exc:
            self.coordinator.root_window.after(0, self._on_fleet_failure, str(exc))

    def _on_fleet_success(self, page: FleetPage) -> None:
        """Runs on the main GUI thread when a bulk listing query succeeds."""
        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(False)
            if hasattr(self.coordinator.dashboard_view, "populate"):
                self.coordinator.dashboard_view.populate(page)

    def _log_vehicle_search(self, asset: Any) -> None:
        """Appends a timestamped search record to the audit log at the project root."""
        log_path = Path(__file__).resolve().parents[2] / "vehicle_search.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}]\n")
            log_file.write(f"vehicle_registration : {asset.vehicle_registration}\n")
            log_file.write(f"certificate_number   : {asset.certificate_number}\n")
            log_file.write(f"issue_date           : {asset.issue_date}\n")
            log_file.write(f"expiry_date          : {asset.expiry_date}\n")
            log_file.write("-" * 40 + "\n")
        logger.debug(f"Vehicle search logged to {log_path}")

    def _on_match_success(self, asset: Any) -> None:
        """Runs on the main GUI thread when a single specific record matches successfully."""
        if self.coordinator.dashboard_view:
            self.coordinator.dashboard_view.set_loading(False)
            self._log_vehicle_search(asset)

            clipboard_payload = {
                "limiter_serial": asset.limiter_serial,
                "hardcoded_1": asset.hardcoded_1,
                "hardcoded_2": asset.hardcoded_2,
                "hardcoded_3": asset.hardcoded_3,
                "hardcoded_4": asset.hardcoded_4,
                "owner_name": "",  # Empty
                "official_id": "",  # Empty
                "telephone1": "",  # Empty
                "vehicle_registration": "",  # Empty
                "chassis_number": "",  # Empty
                "vehicle_make_n_type": "",  # Empty
                "certificate_number": asset.certificate_number,
                "limiter_type": "",  # Empty
                "empty_placeholder_field": "",  # Empty slot after limiter type
                "issue_date": asset.issue_date,
                "installation_location": asset.installation_location,
                "agent_id": asset.agent_id,
                "company_location": "",  # Empty
                "company_email": "",  # Empty
                "company_phone_number": "",  # Empty
                "company_street_address": "",  # Empty
                "expiry_date": asset.expiry_date,
                "speed_threshold": asset.speed_threshold,
                "fitting_technician_nickname": asset.fitting_technician_nickname,
            }

            raw_string_values = [str(val).strip() for val in clipboard_payload.values()]
            formatted_parenthesis_string = f"({','.join(raw_string_values)})"

            self.coordinator.dashboard_view.set_parenthesis_payload(formatted_parenthesis_string)

            ui_payload = {
                "limiter_serial": asset.limiter_serial,
                "hardcoded_1": asset.hardcoded_1,
                "hardcoded_2": asset.hardcoded_2,
                "hardcoded_3": asset.hardcoded_3,
                "hardcoded_4": asset.hardcoded_4,
                "owner_name": asset.owner_name,
                "official_id": asset.official_id,
                "telephone1": asset.telephone1,
                "vehicle_registration": asset.vehicle_registration,
                "chassis_number": asset.chassis_number,
                "vehicle_make_n_type": asset.vehicle_make_n_type,
                "certificate_number": asset.certificate_number,
                "limiter_type": asset.limiter_type,
                "issue_date": asset.issue_date,
                "installation_location": asset.installation_location,
                "agent_id": asset.agent_id,
                "company_location": asset.company_location,
                "company_email": asset.company_email,
                "company_phone_number": asset.company_phone_number,
                "company_street_address": asset.company_street_address,
                "expiry_date": asset.expiry_date,
                "speed_threshold": asset.speed_threshold,
                "fitting_technician_nickname": asset.fitting_technician_nickname,
            }

            if hasattr(self.coordinator.dashboard_view, "populate_profile"):
                self.coordinator.dashboard_view.populate_profile(ui_payload)

    def _on_fleet_failure(self, message: str) -> None:
        """Handles background process failures safely on the main UI execution loop."""
        if self.coordinator.dashboard_view:
            if hasattr(self.coordinator.dashboard_view, "clear_fields"):
                self.coordinator.dashboard_view.clear_fields()
            self.coordinator.dashboard_view.set_loading(False)
            self.coordinator.dashboard_view.show_status_error(message)

    def _on_session_expired(self) -> None:
        """Evicts active views if the authentication security scope token drops."""
        self.coordinator.force_logout("Active connection token scope expired. Please access authorization spaces again.")
