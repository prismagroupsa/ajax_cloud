"""API Client for Ajax Cloud Backend."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientSession, ClientTimeout

_LOGGER = logging.getLogger(__name__)

TIMEOUT = ClientTimeout(total=30)


class AjaxCloudClient:
    """Client to communicate with Ajax Cloud backend."""

    def __init__(self, session: ClientSession, backend_url: str, token: str) -> None:
        """Initialize the client."""
        self._session = session
        self._backend_url = backend_url.rstrip("/")
        self._token = token

    async def _request(
        self, method: str, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a request to the backend."""
        url = f"{self._backend_url}/api/v1{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        try:
            async with self._session.request(
                method, url, json=data, headers=headers, timeout=TIMEOUT
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with backend: %s", err)
            raise
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout communicating with backend")
            raise

    async def async_authenticate(self, email: str) -> dict[str, Any]:
        """Request authentication/registration."""
        return await self._request("POST", "/auth/register", {"email": email})

    async def async_check_status(self) -> dict[str, Any]:
        """Check connection status and approval."""
        return await self._request("GET", "/auth/status")

    async def async_get_devices(self) -> dict[str, Any]:
        """Get all devices and their states."""
        return await self._request("GET", "/devices")

    async def async_get_device_state(self, device_id: str) -> dict[str, Any]:
        """Get specific device state."""
        return await self._request("GET", f"/devices/{device_id}")

    async def async_arm_alarm(self, hub_id: str, mode: str) -> dict[str, Any]:
        """Arm the alarm system."""
        return await self._request(
            "POST", f"/hubs/{hub_id}/arm", {"mode": mode}
        )

    async def async_disarm_alarm(self, hub_id: str) -> dict[str, Any]:
        """Disarm the alarm system."""
        return await self._request("POST", f"/hubs/{hub_id}/disarm")
