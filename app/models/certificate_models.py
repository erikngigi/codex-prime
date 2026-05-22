"""
app/models/certificate_models.py — Data structures representing certificate payloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.models.api_client import APIError, UnauthorizedError, config, requests


@dataclass
class Certificate:
    """
    Maps a single certificate record from the live API response payload safely.
    """

    id: int
    certificate_number: str
    client_name: str
    vehicle_registration: str
    vehicle_make_n_type: str
    sacco_name: str
    limiter_serial: str
    service_type: str
    issue_date: str
    expiry_date: str
    inspection_date: str
    verification_code: str
    ntsa_certificate_code: str
    client_id: str
    client_contact: str
    client_postal_address: str
    vehicle_id: int
    vehicle_chassis_number: str
    vehicle_category: str
    sacco_id: str
    simcard_type: str
    simcard_number: str
    kra_pin: str
    member_id: str
    created_by: str
    created_by_sign: str
    approved_by: Optional[str]
    payment_type: str
    comment: str
    fitting_info: str
    approved: int
    printed: int
    status: str
    unit_code: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Certificate:
        """
        Parses a raw single-record JSON dictionary map into a strictly typed Certificate instance.
        """
        return cls(
            id=int(data.get("id", 0)),
            certificate_number=str(data.get("certificate_number", "")),
            client_name=str(data.get("client_name", "")),
            vehicle_registration=str(data.get("vehicle_registration", "")),
            vehicle_make_n_type=str(data.get("vehicle_make_n_type", "")),
            sacco_name=str(data.get("sacco_name", "")),
            limiter_serial=str(data.get("limiter_serial", "")),
            service_type=str(data.get("service_type", "")),
            issue_date=str(data.get("issue_date", "")),
            expiry_date=str(data.get("expiry_date", "")),
            inspection_date=str(data.get("inspection_date", "")),
            verification_code=str(data.get("verification_code", "")),
            ntsa_certificate_code=str(data.get("ntsa_certificate_code", "")),
            client_id=str(data.get("client_id", "")),
            client_contact=str(data.get("client_contact", "")),
            client_postal_address=str(data.get("client_postal_address", "")),
            vehicle_id=int(data.get("vehicle_id", 0)),
            vehicle_chassis_number=str(data.get("vehicle_chassis_number", "")),
            vehicle_category=str(data.get("vehicle_category", "")),
            sacco_id=str(data.get("sacco_id", "")),
            simcard_type=str(data.get("simcard_type", "")),
            simcard_number=str(data.get("simcard_number", "")),
            kra_pin=str(data.get("kra_pin", "")),
            member_id=str(data.get("member_id", "")),
            created_by=str(data.get("created_by", "")),
            created_by_sign=str(data.get("created_by_sign", "")),
            approved_by=data.get("approved_by"),
            payment_type=str(data.get("payment_type", "")),
            comment=str(data.get("comment", "")),
            fitting_info=str(data.get("fitting_info", "")),
            approved=int(data.get("approved", 0)),
            printed=int(data.get("printed", 0)),
            status=str(data.get("status", "valid")),
            unit_code=str(data.get("unit_code", "")),
            created_at=str(data.get("createdAt") or data.get("created_at") or ""),
            updated_at=str(data.get("updatedAt") or data.get("updated_at") or ""),
        )


@dataclass
class CertificatesPage:
    """
    Represents a wrapped page collection framework containing list models metadata.
    """

    total: int
    page: int
    page_size: int
    data: list[Certificate]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CertificatesPage:
        """
        Transforms an entire index collection bundle payload down cleanly.
        """
        raw_items = data.get("data", [])
        parsed_certificates = [Certificate.from_dict(item) for item in raw_items]

        return cls(
            total=int(data.get("total", 0)),
            page=int(data.get("page", 1)),
            page_size=int(data.get("page_size", 20)),
            data=parsed_certificates,
        )

    @staticmethod
    def get_certificates(session: Any, limit: int = 20, search: Optional[str] = None) -> CertificatesPage:
        """
        GET /certificates — Returns parsed CertificatesPage contents.
        Accepts a custom 'limit' for page sizing and an optional registration search string 'search'.
        Raises UnauthorizedError on 401; APIError on network/parsing faults.
        """
        try:
            # Build active URL parameter map payload
            params: dict[str, Any] = {"page_size": limit}

            # If search token exists, intercept query variables context instantly
            if search is not None and search.strip() != "":
                params["search"] = search.strip()

            response = requests.get(
                config.CERTIFICATES_ENDPOINT,
                headers=session.bearer_header,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            raise APIError("Request timed out while fetching certificates.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise APIError("Network error while fetching certificates.") from exc

        if response.status_code == 401:
            raise UnauthorizedError("Session expired. Please log in again.", status_code=401)
        if not response.ok:
            try:
                server_error = response.json()
                error_msg = server_error.get("detail", f"Failed to load certificates (HTTP {response.status_code}).")
            except Exception:
                error_msg = f"Failed to load certificates (HTTP {response.status_code})."

            raise APIError(
                error_msg,
                status_code=response.status_code,
            )
        try:
            return CertificatesPage.from_dict(response.json())
        except (ValueError, KeyError) as exc:
            raise APIError("Could not parse the server response structure.") from exc
