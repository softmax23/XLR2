"""
V8 Optimized XLR API Client

Modern async XLR API client with connection pooling, retries, and performance optimization.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager

from ..models.config import APIConfig


@dataclass
class APIResponse:
    """API response wrapper."""
    status_code: int
    data: Any
    headers: Dict[str, str]
    success: bool

    @property
    def json(self) -> Any:
        """Get JSON data."""
        return self.data


class XLRAPIError(Exception):
    """XLR API error."""
    pass


class AsyncXLRClient:
    """
    Modern async XLR API client.

    Features:
    - Connection pooling
    - Automatic retries with exponential backoff
    - Request/response logging
    - Performance monitoring
    - Batch operations
    """

    def __init__(self, config: APIConfig):
        """
        Initialize XLR client.

        Args:
            config: API configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()

    async def _create_session(self) -> None:
        """Create HTTP session with optimized settings."""
        # Create connector with connection pooling
        self._connector = aiohttp.TCPConnector(
            limit=self.config.connection_pool_size,
            limit_per_host=self.config.connection_pool_size // 2,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )

        # Create session with optimized timeout
        timeout = aiohttp.ClientTimeout(
            total=self.config.timeout,
            connect=self.config.timeout // 3
        )

        # Authentication
        auth = aiohttp.BasicAuth(
            self.config.ops_username_api,
            self.config.ops_password_api
        )

        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout,
            auth=auth,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'XLR-V8-Optimized/1.0'
            }
        )

        self.logger.info("🔗 XLR API session created with connection pooling")

    async def _close_session(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.close()
        if self._connector:
            await self._connector.close()
        self.logger.info("🔌 XLR API session closed")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """
        Make HTTP request with retries.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters

        Returns:
            API response

        Raises:
            XLRAPIError: If request fails
        """
        if not self._session:
            await self._create_session()

        url = f"{self.config.url_api_xlr.rstrip('/')}/{endpoint.lstrip('/')}"

        for attempt in range(self.config.max_retries + 1):
            try:
                self.logger.debug(f"🌐 {method} {url} (attempt {attempt + 1})")

                async with self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    ssl=self.config.verify_ssl
                ) as response:
                    response_data = await response.text()

                    # Try to parse as JSON
                    try:
                        json_data = json.loads(response_data) if response_data else None
                    except json.JSONDecodeError:
                        json_data = response_data

                    api_response = APIResponse(
                        status_code=response.status,
                        data=json_data,
                        headers=dict(response.headers),
                        success=200 <= response.status < 300
                    )

                    if api_response.success:
                        self.logger.debug(f"✅ {method} {url} -> {response.status}")
                        return api_response
                    else:
                        error_msg = f"API request failed: {response.status} - {response_data}"
                        self.logger.warning(error_msg)

                        if attempt < self.config.max_retries and response.status >= 500:
                            # Retry on server errors
                            await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                            continue
                        else:
                            raise XLRAPIError(error_msg)

            except aiohttp.ClientError as e:
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    raise XLRAPIError(f"Request failed after {self.config.max_retries} retries: {e}")

        raise XLRAPIError("Max retries exceeded")

    # Template Management
    async def get_templates(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get templates from XLR."""
        endpoint = "templates"
        if folder_id:
            endpoint += f"?folderId={folder_id}"

        response = await self._make_request("GET", endpoint)
        return response.data if isinstance(response.data, list) else []

    async def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get specific template."""
        response = await self._make_request("GET", f"templates/{template_id}")
        return response.data

    async def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create new template."""
        response = await self._make_request("POST", "templates", data=template_data)
        return response.data.get("id") if isinstance(response.data, dict) else str(response.data)

    async def update_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Update existing template."""
        response = await self._make_request("PUT", f"templates/{template_id}", data=template_data)
        return response.success

    async def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        response = await self._make_request("DELETE", f"templates/{template_id}")
        return response.success

    # Folder Management
    async def get_folders(self, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get folders from XLR."""
        endpoint = "folders"
        if parent_id:
            endpoint += f"?parent={parent_id}"

        response = await self._make_request("GET", endpoint)
        return response.data if isinstance(response.data, list) else []

    async def find_folder_by_path(self, folder_path: str) -> Optional[str]:
        """Find folder ID by path."""
        folders = await self.get_folders()

        # Simple path matching - can be optimized with caching
        for folder in folders:
            if folder.get("title") == folder_path or folder_path in folder.get("title", ""):
                return folder.get("id")

        return None

    # Phase Management
    async def create_phase(self, template_id: str, phase_data: Dict[str, Any]) -> str:
        """Create phase in template."""
        response = await self._make_request(
            "POST",
            f"templates/{template_id}/phases",
            data=phase_data
        )
        return response.data.get("id") if isinstance(response.data, dict) else str(response.data)

    async def get_phases(self, template_id: str) -> List[Dict[str, Any]]:
        """Get phases from template."""
        response = await self._make_request("GET", f"templates/{template_id}/phases")
        return response.data if isinstance(response.data, list) else []

    # Task Management
    async def create_task(self, phase_id: str, task_data: Dict[str, Any]) -> str:
        """Create task in phase."""
        response = await self._make_request(
            "POST",
            f"phases/{phase_id}/tasks",
            data=task_data
        )
        return response.data.get("id") if isinstance(response.data, dict) else str(response.data)

    async def get_tasks(self, phase_id: str) -> List[Dict[str, Any]]:
        """Get tasks from phase."""
        response = await self._make_request("GET", f"phases/{phase_id}/tasks")
        return response.data if isinstance(response.data, list) else []

    # Gate Management
    async def create_gate(self, template_id: str, gate_data: Dict[str, Any]) -> str:
        """Create gate in template."""
        response = await self._make_request(
            "POST",
            f"templates/{template_id}/gates",
            data=gate_data
        )
        return response.data.get("id") if isinstance(response.data, dict) else str(response.data)

    # Variable Management
    async def set_template_variables(self, template_id: str, variables: Dict[str, Any]) -> bool:
        """Set template variables."""
        response = await self._make_request(
            "PUT",
            f"templates/{template_id}/variables",
            data=variables
        )
        return response.success

    # Batch Operations
    async def batch_create_tasks(self, phase_id: str, tasks: List[Dict[str, Any]]) -> List[str]:
        """Create multiple tasks in parallel."""
        task_ids = []

        # Create tasks in batches to avoid overwhelming the server
        batch_size = 5
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_tasks = [
                self.create_task(phase_id, task_data)
                for task_data in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to create task: {result}")
                else:
                    task_ids.append(result)

        return task_ids

    async def batch_create_phases(self, template_id: str, phases: List[Dict[str, Any]]) -> List[str]:
        """Create multiple phases in parallel."""
        phase_tasks = [
            self.create_phase(template_id, phase_data)
            for phase_data in phases
        ]

        results = await asyncio.gather(*phase_tasks, return_exceptions=True)
        phase_ids = []

        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Failed to create phase: {result}")
            else:
                phase_ids.append(result)

        return phase_ids


@asynccontextmanager
async def xlr_client(config: APIConfig):
    """Async context manager for XLR client."""
    async with AsyncXLRClient(config) as client:
        yield client