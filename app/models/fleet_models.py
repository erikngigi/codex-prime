"""
app/models/fleet_models.py — Aggregated Data Structuring Engine for Unified Fleet Profiles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import requests

import app.config as config
from app.models.api_client import APIError, UnauthorizedError


@dataclass
class FleetAsset:
    """
    Safely captures and casts combined vehicle and certificate parameters
    received from the unified backend tracking endpoint.
    """

    vehicle_registration: str
    vehicle_make_n_type: str
    certificate_number: str
    expiry_date: str
    status: str  # Dynamically calculated below to map onto your UI state layer

    # Newly supplied endpoint parameters mapping onto dashboard UI rows
    chassis_number: str
    owner_name: str
    limiter_serial: str
    limiter_type: str
    issue_date: str
    speed_threshold: str
    fitting_technician_nickname: str
    installation_location: str
    hardcoded_1: str
    hardcoded_2: str
    hardcoded_3: str
    hardcoded_4: str
    official_id: str
    agent_id: str
    company_location: str
    company_email: str
    company_phone_number: str
    company_street_address: str
    telephone1: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FleetAsset:
        """Translates unmarshaled JSON keys directly into structured dataclass properties."""

        # Pull your fresh parameters safely out of the incoming transaction dictionary
        reg_code = str(data.get("vehicle_registration", "")).strip().upper()
        expiry = str(data.get("expiry_date", "")).strip()

        # Dynamic context fallback: Compute status to maintain compliance tracking if not given explicitly
        # This keeps compatibility with your dashboard status strings (e.g., APPROVED / ACTIVE)
        calculated_status = "ACTIVE" if expiry else "UNKNOWN"

        return cls(
            vehicle_registration=reg_code,
            vehicle_make_n_type=str(data.get("vehicle_make_n_type", "—")),
            certificate_number=str(data.get("certificate_number", "—")),
            expiry_date=expiry if expiry else "—",
            status=calculated_status,
            # Map structural field parameters returned natively from the combined tables
            chassis_number=str(data.get("vehicle_chassis_number", "—")),
            owner_name=str(data.get("full_name", "—")),
            limiter_serial=str(data.get("limiter_serial", "—")),
            limiter_type=str(data.get("limiter_type", "—")),
            issue_date=str(data.get("issue_date", "—")),
            speed_threshold=str(data.get("speed_threshold", "—")),
            fitting_technician_nickname=str(data.get("fitting_technician_nickname", "—")),
            installation_location=str(data.get("location_installation", "—")),
            hardcoded_1=str(data.get("hardcoded_1")),
            hardcoded_2=str(data.get("hardcoded_2")),
            hardcoded_3=str(data.get("hardcoded_3")),
            hardcoded_4=str(data.get("hardcoded_4")),
            official_id=str(data.get("official_id")),
            agent_id=str(data.get("agent_id")),
            company_location=str(data.get("company_location")),
            company_email=str(data.get("company_email")),
            company_phone_number=str(data.get("company_phone_number")),
            company_street_address=str(data.get("company_street_address")),
            telephone1=str(data.get("telephone1")),
        )


@dataclass
class FleetPage:
    """Wraps fleet profile asset data lists before delivery to controllers."""

    assets: list[FleetAsset] = field(default_factory=list)

    @classmethod
    def fetch_combined_fleet(cls, session: Any, limit: int = 20, search: Optional[str] = None) -> FleetPage:
        """
        Queries your singular dual-table joint endpoint using the 'search' parameter.
        Handles status interceptions (401 / 422 / 500) natively.
        """
        # Set up parameters utilizing the single available query toggle hook
        params: dict[str, Any] = {"page_size": limit}
        if search and search.strip():
            params["search"] = search.strip()

        try:
            # Executes transaction over the centralized target config endpoint wrapper
            response = requests.get(
                config.FLEET_RESET_ENDPOINT,  # Points directly to your updated unified endpoint route url
                headers=session.bearer_header,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            raise APIError("The remote asset telemetry server connection timed out.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise APIError("Failed to establish secure network connectivity interfaces.") from exc

        # ──EXPLICIT SECURITY CHECK ──
        if response.status_code == 401:
            raise UnauthorizedError("Session expired. Please log in again.", status_code=401)

        # ── EXPLICIT JSON EXTRACTOR BLOCK FOR HTTP 422 VALIDATION CHECKS ──
        if not response.ok:
            try:
                server_error = response.json()
                error_msg = server_error.get("detail", f"Failed to retrieve fleet infrastructure records (HTTP {response.status_code}).")
            except Exception:
                error_msg = f"Failed to retrieve fleet infrastructure records (HTTP {response.status_code})."
            raise APIError(error_msg, status_code=response.status_code)

        # Parse collection payload entries safely
        try:
            json_payload = response.json()

            # Accommodate both an array schema wrapper or a single layout item lookup return signature
            parsed_assets: list[FleetAsset] = []

            if isinstance(json_payload, dict):
                # If the backend returns items wrapped inside a paging envelope array block:
                if "items" in json_payload:
                    for raw_item in json_payload.get("items", []):
                        parsed_assets.append(FleetAsset.from_dict(raw_item))
                # If the backend returned a single flat record object back directly for the lookup match:
                elif "vehicle_registration" in json_payload:
                    parsed_assets.append(FleetAsset.from_dict(json_payload))
            elif isinstance(json_payload, list):
                for raw_item in json_payload:
                    parsed_assets.append(FleetAsset.from_dict(raw_item))

            return cls(assets=parsed_assets)

        except (ValueError, KeyError) as exc:
            raise APIError("Failed to decode application structural data schema from server profile response.") from exc
