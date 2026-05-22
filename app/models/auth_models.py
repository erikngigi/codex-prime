"""
app/models/auth_models.py — Data object mappings representing authorization boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import app.config as config
from app.models.api_client import APIClient


@dataclass
class AuthSession:
    """Holds active credentials context profiles across application lifetime cycles."""

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthSession:
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data["token_type"],
            user_id=int(data["user_id"]),
            full_name=data["full_name"],
            username=data["username"],
            role=data["role"],
        )

    @staticmethod
    def login(username: str, password: str) -> AuthSession:
        """Executes a synchronous authentication challenge request against the API."""
        payload = {"username": username, "password": password}
        response_data = APIClient.post(config.LOGIN_ENDPOINT, json_data=payload)
        return AuthSession.from_dict(response_data)
