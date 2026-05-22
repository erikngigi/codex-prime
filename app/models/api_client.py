"""
app/models/api_client.py — Core raw HTTP network request/response serialization engine.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests

import app.config as config

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised whenever remote endpoints respond with non-2xx metadata status bounds."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class UnauthorizedError(APIError):
    """Explicit subclass indicating specialized 401 token revocation exceptions."""

    pass


class APIClient:
    """Core request processing layer wrapping fundamental request payload dispatch calls."""

    @staticmethod
    def request(
        method: str,
        endpoint: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Dispatches formatted synchronous payloads directly down to remote networking layers."""
        try:
            response = requests.request(
                method=method,
                url=endpoint,
                headers=headers,
                params=params,
                json=json_data,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            logger.error(f"Network timeout encountered on endpoint: {endpoint}")
            raise APIError("The remote application connection request timed out.") from exc
        except requests.exceptions.ConnectionError as exc:
            logger.error(f"Network transport fault connectivity drop on: {endpoint}")
            raise APIError("Failed to establish secure network connectivity interfaces.") from exc

        if response.status_code == 401:
            raise UnauthorizedError("Session expired or invalid credentials. Please log in again.", status_code=401)

        # ── EXTRACT DETAILED VALUATION MESSAGES ON NON-SUCCESS RESPONSES ──
        if not response.ok:
            logger.warning(f"Endpoint: {endpoint} returned non-success response code: {response.status_code}")

            try:
                # 1. Read and parse the raw incoming text data into a Python dictionary
                server_error = response.json()

                # 2. Extract the string value from the "detail" key.
                # If "detail" is missing, fall back to a safe fallback dynamic message.
                error_msg = server_error.get("detail", f"Failed to load certificates (HTTP {response.status_code}).")
            except Exception:
                # Fallback safeguard in case the remote server crashes or sends back plain text/HTML instead of JSON
                error_msg = f"Failed to load certificates (HTTP {response.status_code})."

            # 3. Raise the exception containing the clean, user-friendly validation error message
            raise APIError(error_msg, status_code=response.status_code)

        try:
            return response.json()
        except (ValueError, KeyError) as exc:
            raise APIError("Failed to decode application structural data from server payload response.") from exc

    @classmethod
    def get(cls, endpoint: str, headers: Optional[dict[str, str]] = None, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return cls.request("GET", endpoint, headers=headers, params=params)

    @classmethod
    def post(cls, endpoint: str, headers: Optional[dict[str, str]] = None, json_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return cls.request("POST", endpoint, headers=headers, json_data=json_data)
