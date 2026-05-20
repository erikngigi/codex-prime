"""
models.py — Data models and the API service layer.

All network I/O lives here; the rest of the application never imports `requests`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import config
import requests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass
class AuthSession:
    """Holds the authenticated session state."""

    access_token: str
    refresh_token: str
    token_type: str
    user_id: int
    full_name: str
    username: str
    role: str

    @property
    def bearer_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}


@dataclass
class Certificate:
    """Maps a single certificate record from the API payload."""

    id: int
    vehicle_registration: str
    vehicle_make_n_type: str
    vehicle_category: str
    vehicle_chassis_number: str
    limiter_type: str
    limiter_serial: str
    limiter_imei: str
    status: str
    client_id: str
    fitting_date: Optional[str]
    agent_id: str
    speed_threshold: str
    location_installation: str
    fitting_technician_nickname: str
    simcard_type: str
    simcard_number: str
    limiter_configuration: str
    needs_repair: int
    repair_comment: str
    created_by: str
    signed_by: str
    comment: str
    createdAt: str
    updatedAt: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Certificate":
        return cls(
            id=data.get("id", 0),
            vehicle_registration=data.get("vehicle_registration", ""),
            vehicle_make_n_type=data.get("vehicle_make_n_type", ""),
            vehicle_category=data.get("vehicle_category", ""),
            vehicle_chassis_number=data.get("vehicle_chassis_number", ""),
            limiter_type=data.get("limiter_type", ""),
            limiter_serial=data.get("limiter_serial", ""),
            limiter_imei=data.get("limiter_imei", ""),
            status=data.get("status", ""),
            client_id=data.get("client_id", ""),
            fitting_date=data.get("fitting_date"),
            agent_id=data.get("agent_id", ""),
            speed_threshold=data.get("speed_threshold", ""),
            location_installation=data.get("location_installation", ""),
            fitting_technician_nickname=data.get("fitting_technician_nickname", ""),
            simcard_type=data.get("simcard_type", ""),
            simcard_number=data.get("simcard_number", ""),
            limiter_configuration=data.get("limiter_configuration", ""),
            needs_repair=data.get("needs_repair", 0),
            repair_comment=data.get("repair_comment", ""),
            created_by=data.get("created_by", ""),
            signed_by=data.get("signed_by", ""),
            comment=data.get("comment", ""),
            createdAt=data.get("createdAt", ""),
            updatedAt=data.get("updatedAt", ""),
        )


@dataclass
class CertificatesPage:
    """Paginated response wrapper."""

    total: int
    page: int
    page_size: int
    data: list[Certificate] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CertificatesPage":
        return cls(
            total=raw.get("total", 0),
            page=raw.get("page", 1),
            page_size=raw.get("page_size", 100),
            data=[Certificate.from_dict(item) for item in raw.get("data", [])],
        )


# ---------------------------------------------------------------------------
# API exceptions
# ---------------------------------------------------------------------------


class APIError(Exception):
    """Raised for all handled API-layer failures."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class UnauthorizedError(APIError):
    """Raised specifically on 401 responses so the controller can log out."""


# ---------------------------------------------------------------------------
# API service
# ---------------------------------------------------------------------------


class APIService:
    """
    Stateless API service.  Instantiate once; pass a session for authenticated calls.
    """

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    @staticmethod
    def login(username: str, password: str) -> AuthSession:
        """
        POST /auth/login — returns an AuthSession on success.
        Raises APIError on any failure.
        """
        payload = {"username": username, "password": password}
        try:
            response = requests.post(
                config.LOGIN_ENDPOINT,
                json=payload,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            raise APIError("Connection timed out. Please try again.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise APIError("Could not reach the server. Check your network.") from exc

        if response.status_code == 401:
            raise APIError("Invalid username or password.", status_code=401)
        if response.status_code == 400:
            raise APIError("Bad request — check your credentials.", status_code=400)
        if not response.ok:
            raise APIError(
                f"Login failed (HTTP {response.status_code}).",
                status_code=response.status_code,
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise APIError("Server returned an unexpected response.") from exc

        return AuthSession(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
            user_id=data["user_id"],
            full_name=data["full_name"],
            username=data["username"],
            role=data["role"],
        )

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    @staticmethod
    def get_certificates(session: AuthSession) -> CertificatesPage:
        """
        GET /certificates — returns a CertificatesPage on success.
        Raises UnauthorizedError on 401; APIError on all other failures.
        """
        try:
            response = requests.get(
                config.CERTIFICATES_ENDPOINT,
                headers=session.bearer_header,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            raise APIError("Request timed out while fetching certificates.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise APIError("Network error while fetching certificates.") from exc

        if response.status_code == 401:
            raise UnauthorizedError("Session expired. Please log in again.", status_code=401)
        if not response.ok:
            raise APIError(
                f"Failed to load certificates (HTTP {response.status_code}).",
                status_code=response.status_code,
            )

        try:
            return CertificatesPage.from_dict(response.json())
        except (ValueError, KeyError) as exc:
            raise APIError("Could not parse the server response.") from exc
