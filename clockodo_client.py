"""
Clockodo API Client for time tracking integration.
Provides async HTTP client for Clockodo REST API with authentication.
"""

import os
import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ClockodoAPIError(Exception):
    """Custom exception for Clockodo API errors."""
    pass


logger = logging.getLogger(__name__)


class ClockodoClient:
    """Async HTTP client for Clockodo API."""

    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize Clockodo client with credentials."""
        self.email = email or os.getenv("CLOCKODO_EMAIL")
        self.api_key = api_key or os.getenv("CLOCKODO_API_KEY")
        self.base_url = "https://my.clockodo.com/api/v2"

        if not self.email or not self.api_key:
            raise ValueError("Clockodo email and API key must be provided")

        self.headers = {
            "X-ClockodoApiUser": self.email,
            "X-ClockodoApiKey": self.api_key,
            "X-Clockodo-External-Application": "claude-mcp-server contact@example.com",
            "Content-Type": "application/json"
        }

        logger.info("ClockodoClient initialized", extra={"clockodo_email": self.email})

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Clockodo API."""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                logger.debug(
                    "Sending request to Clockodo",
                    extra={
                        "method": method,
                        "endpoint": endpoint,
                        "has_params": "params" in kwargs,
                        "has_json": "json" in kwargs
                    }
                )
                response = await client.request(
                    method, url, headers=self.headers, **kwargs
                )
                logger.debug(
                    "Received response from Clockodo",
                    extra={
                        "status_code": response.status_code,
                        "method": method,
                        "endpoint": endpoint
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("message", str(e))
                except:
                    error_detail = str(e)
                logger.error(
                    "Clockodo API returned error",
                    extra={
                        "status_code": e.response.status_code,
                        "method": method,
                        "endpoint": endpoint,
                        "error_detail": error_detail
                    }
                )
                raise ClockodoAPIError(f"API Error {e.response.status_code}: {error_detail}")
            except Exception as e:
                logger.exception(
                    "Unexpected error while calling Clockodo",
                    extra={
                        "method": method,
                        "endpoint": endpoint
                    }
                )
                raise ClockodoAPIError(f"Request failed: {str(e)}")

    # Clock/Timer operations
    async def start_clock(self, customers_id: int, projects_id: Optional[int] = None,
                         services_id: Optional[int] = None, billable: bool = True,
                         text: Optional[str] = None) -> Dict[str, Any]:
        """Start time tracking."""
        params = {
            "customers_id": customers_id,
            "billable": billable
        }
        if projects_id:
            params["projects_id"] = projects_id
        if services_id:
            params["services_id"] = services_id
        if text:
            params["text"] = text

        return await self._request("POST", "/clock", params=params)

    async def stop_clock(self) -> Dict[str, Any]:
        """Stop current time tracking."""
        return await self._request("DELETE", "/clock")

    async def get_clock(self) -> Optional[Dict[str, Any]]:
        """Get current running clock entry."""
        try:
            result = await self._request("GET", "/clock")
            return result.get("running_entry")
        except ClockodoAPIError:
            return None

    # Entry operations
    async def get_entries(self, time_since: str, time_until: str,
                         customers_id: Optional[int] = None,
                         projects_id: Optional[int] = None,
                         billable: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get time entries for a period."""
        params = {
            "time_since": time_since,
            "time_until": time_until
        }
        if customers_id:
            params["customers_id"] = customers_id
        if projects_id:
            params["projects_id"] = projects_id
        if billable is not None:
            params["billable"] = billable

        result = await self._request("GET", "/entries", params=params)
        return result.get("entries", [])

    async def create_entry(self, customers_id: int, time_since: str, time_until: str,
                          projects_id: Optional[int] = None, services_id: Optional[int] = None,
                          billable: bool = True, text: Optional[str] = None) -> Dict[str, Any]:
        """Create a new time entry."""
        data = {
            "customers_id": customers_id,
            "time_since": time_since,
            "time_until": time_until,
            "billable": billable
        }
        if projects_id:
            data["projects_id"] = projects_id
        if services_id:
            data["services_id"] = services_id
        if text:
            data["text"] = text

        return await self._request("POST", "/entries", json=data)

    async def update_entry(self, entry_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing time entry."""
        return await self._request("PUT", f"/entries/{entry_id}", json=kwargs)

    async def delete_entry(self, entry_id: int) -> bool:
        """Delete a time entry."""
        try:
            await self._request("DELETE", f"/entries/{entry_id}")
            return True
        except ClockodoAPIError:
            return False

    # Resource operations
    async def get_customers(self) -> List[Dict[str, Any]]:
        """Get all customers."""
        result = await self._request("GET", "/customers")
        return result.get("customers", [])

    async def get_projects(self, customers_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get projects, optionally filtered by customer."""
        params = {}
        if customers_id:
            params["customers_id"] = customers_id

        result = await self._request("GET", "/projects", params=params)
        return result.get("projects", [])

    async def get_services(self) -> List[Dict[str, Any]]:
        """Get all services."""
        result = await self._request("GET", "/services")
        return result.get("services", [])

    async def get_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        result = await self._request("GET", "/users")
        return result.get("users", [])

    async def get_current_user_id(self) -> int:
        """Get current user ID by email."""
        users = await self.get_users()
        current_user = next((user for user in users if user["email"] == self.email), None)
        if not current_user:
            logger.error("Current Clockodo user not found", extra={"clockodo_email": self.email})
            raise ValueError(f"User with email {self.email} not found")
        return current_user["id"]

    # Utility methods
    def format_datetime(self, dt: datetime) -> str:
        """Format datetime for Clockodo API."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def format_date(self, d: date) -> str:
        """Format date for Clockodo API v2."""
        return d.strftime("%Y-%m-%dT00:00:00Z")

    def format_date_end(self, d: date) -> str:
        """Format end date for Clockodo API v2."""
        return d.strftime("%Y-%m-%dT23:59:59Z")

    async def get_week_entries(self, year: int, week: int) -> List[Dict[str, Any]]:
        """Get entries for a specific week."""
        from datetime import timedelta

        # Calculate week start and end
        jan_1 = date(year, 1, 1)
        week_start = jan_1 + timedelta(weeks=week-1, days=-jan_1.weekday())
        week_end = week_start + timedelta(days=6)

        return await self.get_entries(
            self.format_date(week_start),
            self.format_date(week_end)
        )
