"""
XL Release API Client - Enhanced version with best practices
===========================================================

This module provides a robust API client for XL Release following the official
REST API documentation best practices.

Features:
- Multiple authentication methods (Basic Auth, Personal Access Tokens, OAuth2)
- Proper error handling and retry logic
- Pagination support
- Search capabilities
- Full identifier support
- Comprehensive logging
"""

import json
import logging
import time
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin, quote

import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AuthType(Enum):
    """Authentication types supported by XL Release."""
    BASIC = "basic"
    TOKEN = "token"
    OAUTH2 = "oauth2"


class XLRAPIException(Exception):
    """Custom exception for XL Release API errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class XLRAPIClient:
    """
    Enhanced XL Release API Client with best practices implementation.

    This client provides:
    - Robust authentication handling
    - Automatic retry with exponential backoff
    - Comprehensive error handling
    - Pagination support
    - Search capabilities
    - Full REST API coverage
    """

    # Standard API endpoints following XL Release 22.2.x documentation
    ENDPOINTS = {
        'templates': '/api/v1/templates',
        'releases': '/api/v1/releases',
        'phases': '/api/v1/phases',
        'tasks': '/api/v1/tasks',
        'search': '/api/v1/search',
        'folders': '/api/v1/folders',
        'variables': '/api/v1/variables'
    }

    def __init__(self,
                 base_url: str,
                 auth_type: AuthType = AuthType.BASIC,
                 username: str = None,
                 password: str = None,
                 token: str = None,
                 verify_ssl: bool = False,
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        Initialize the XL Release API client.

        Args:
            base_url: XL Release server URL (e.g., 'https://xlr.company.com')
            auth_type: Authentication method to use
            username: Username for basic auth
            password: Password for basic auth
            token: Personal access token or OAuth2 token
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.auth_type = auth_type
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize session with retry strategy
        self.session = self._create_session(max_retries)

        # Setup authentication
        self._setup_authentication(username, password, token)

        # Default headers
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'XLR-Python-Client/1.0'
        }

    def _create_session(self, max_retries: int) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1  # Exponential backoff
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _setup_authentication(self, username: str, password: str, token: str) -> None:
        """Setup authentication based on the specified method."""
        if self.auth_type == AuthType.BASIC:
            if not username or not password:
                raise ValueError("Username and password required for basic authentication")
            self.session.auth = HTTPBasicAuth(username, password)

        elif self.auth_type == AuthType.TOKEN:
            if not token:
                raise ValueError("Token required for token authentication")
            self.headers['Authorization'] = f'Bearer {token}'

        elif self.auth_type == AuthType.OAUTH2:
            if not token:
                raise ValueError("OAuth2 token required for OAuth2 authentication")
            self.headers['Authorization'] = f'Bearer {token}'

        else:
            raise ValueError(f"Unsupported authentication type: {self.auth_type}")

    def _build_url(self, endpoint: str, resource_id: str = None) -> str:
        """Build full URL for API endpoint."""
        url = urljoin(self.base_url, endpoint)
        if resource_id:
            url = urljoin(url + '/', quote(resource_id, safe=''))
        return url

    def _make_request(self,
                     method: str,
                     endpoint: str,
                     resource_id: str = None,
                     data: dict = None,
                     params: dict = None) -> dict:
        """
        Make HTTP request with proper error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            resource_id: Optional resource identifier
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            XLRAPIException: For API errors
        """
        url = self._build_url(endpoint, resource_id)

        # Prepare request arguments
        request_kwargs = {
            'url': url,
            'headers': self.headers,
            'timeout': self.timeout,
            'verify': self.verify_ssl,
            'params': params
        }

        if data:
            request_kwargs['json'] = data

        # Log request
        self.logger.debug(f"{method} {url}")
        if data:
            self.logger.debug(f"Request data: {json.dumps(data, indent=2)}")

        try:
            response = self.session.request(method, **request_kwargs)

            # Log response
            self.logger.debug(f"Response status: {response.status_code}")

            # Handle different response codes
            if response.status_code == 204:  # No Content
                return {}

            if response.status_code >= 400:
                self._handle_error_response(response)

            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'content': response.text}

        except requests.exceptions.RequestException as e:
            raise XLRAPIException(f"Request failed: {str(e)}")

    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle HTTP error responses with detailed information."""
        try:
            error_data = response.json()
            error_message = error_data.get('message', response.text)
        except json.JSONDecodeError:
            error_message = response.text or f"HTTP {response.status_code} error"

        # Map common HTTP status codes to meaningful messages
        status_messages = {
            400: "Bad Request - Invalid request parameters",
            401: "Unauthorized - Check authentication credentials",
            403: "Forbidden - Insufficient permissions",
            404: "Not Found - Resource does not exist",
            409: "Conflict - Resource already exists or in invalid state",
            422: "Unprocessable Entity - Validation errors",
            429: "Rate Limited - Too many requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }

        status_msg = status_messages.get(response.status_code, "Unknown error")
        full_message = f"{status_msg}: {error_message}"

        raise XLRAPIException(
            full_message,
            status_code=response.status_code,
            response=error_data if 'error_data' in locals() else None
        )

    # Template Operations
    def create_template(self, template_data: dict) -> dict:
        """Create a new template."""
        return self._make_request('POST', self.ENDPOINTS['templates'], data=template_data)

    def get_template(self, template_id: str) -> dict:
        """Get template by ID."""
        return self._make_request('GET', self.ENDPOINTS['templates'], template_id)

    def update_template(self, template_id: str, template_data: dict) -> dict:
        """Update existing template."""
        return self._make_request('PUT', self.ENDPOINTS['templates'], template_id, data=template_data)

    def delete_template(self, template_id: str) -> dict:
        """Delete template by ID."""
        return self._make_request('DELETE', self.ENDPOINTS['templates'], template_id)

    def list_templates(self, page: int = 0, results_per_page: int = 100) -> dict:
        """List templates with pagination."""
        params = {
            'page': page,
            'resultsPerPage': results_per_page
        }
        return self._make_request('GET', self.ENDPOINTS['templates'], params=params)

    # Release Operations
    def create_release(self, release_data: dict) -> dict:
        """Create a new release."""
        return self._make_request('POST', self.ENDPOINTS['releases'], data=release_data)

    def get_release(self, release_id: str) -> dict:
        """Get release by ID."""
        return self._make_request('GET', self.ENDPOINTS['releases'], release_id)

    def update_release(self, release_id: str, release_data: dict) -> dict:
        """Update existing release."""
        return self._make_request('PUT', self.ENDPOINTS['releases'], release_id, data=release_data)

    def delete_release(self, release_id: str) -> dict:
        """Delete release by ID."""
        return self._make_request('DELETE', self.ENDPOINTS['releases'], release_id)

    # Phase Operations
    def create_phase(self, release_id: str, phase_data: dict) -> dict:
        """Create a new phase in a release."""
        endpoint = f"{self.ENDPOINTS['releases']}/{quote(release_id, safe='')}/phases"
        return self._make_request('POST', endpoint, data=phase_data)

    def get_phase(self, phase_id: str) -> dict:
        """Get phase by ID."""
        return self._make_request('GET', self.ENDPOINTS['phases'], phase_id)

    def update_phase(self, phase_id: str, phase_data: dict) -> dict:
        """Update existing phase."""
        return self._make_request('PUT', self.ENDPOINTS['phases'], phase_id, data=phase_data)

    def delete_phase(self, phase_id: str) -> dict:
        """Delete phase by ID."""
        return self._make_request('DELETE', self.ENDPOINTS['phases'], phase_id)

    # Task Operations
    def create_task(self, phase_id: str, task_data: dict) -> dict:
        """Create a new task in a phase."""
        endpoint = f"{self.ENDPOINTS['phases']}/{quote(phase_id, safe='')}/tasks"
        return self._make_request('POST', endpoint, data=task_data)

    def get_task(self, task_id: str) -> dict:
        """Get task by ID."""
        return self._make_request('GET', self.ENDPOINTS['tasks'], task_id)

    def update_task(self, task_id: str, task_data: dict) -> dict:
        """Update existing task."""
        return self._make_request('PUT', self.ENDPOINTS['tasks'], task_id, data=task_data)

    def delete_task(self, task_id: str) -> dict:
        """Delete task by ID."""
        return self._make_request('DELETE', self.ENDPOINTS['tasks'], task_id)

    # Search Operations
    def search(self,
               query: str,
               entity_type: str = None,
               page: int = 0,
               results_per_page: int = 100) -> dict:
        """
        Search for entities using XL Release search API.

        Args:
            query: Search query string
            entity_type: Entity type to search for (template, release, etc.)
            page: Page number for pagination
            results_per_page: Number of results per page

        Returns:
            Search results with pagination info
        """
        params = {
            'q': query,
            'page': page,
            'resultsPerPage': results_per_page
        }

        if entity_type:
            params['entityType'] = entity_type

        return self._make_request('GET', self.ENDPOINTS['search'], params=params)

    def find_templates_by_title(self, title: str) -> List[dict]:
        """Find templates by title using search API."""
        search_results = self.search(f'title:"{title}"', entity_type='template')
        return search_results.get('entities', [])

    def find_releases_by_title(self, title: str) -> List[dict]:
        """Find releases by title using search API."""
        search_results = self.search(f'title:"{title}"', entity_type='release')
        return search_results.get('entities', [])

    # Folder Operations
    def get_folder(self, folder_id: str) -> dict:
        """Get folder by ID."""
        return self._make_request('GET', self.ENDPOINTS['folders'], folder_id)

    def find_folder_by_path(self, path: str) -> Optional[dict]:
        """Find folder by path."""
        search_results = self.search(f'path:"{path}"', entity_type='folder')
        folders = search_results.get('entities', [])
        return folders[0] if folders else None

    # Variable Operations
    def create_variable(self, release_id: str, variable_data: dict) -> dict:
        """Create a variable in a release."""
        endpoint = f"{self.ENDPOINTS['releases']}/{quote(release_id, safe='')}/variables"
        return self._make_request('POST', endpoint, data=variable_data)

    def get_variables(self, release_id: str) -> List[dict]:
        """Get all variables for a release."""
        endpoint = f"{self.ENDPOINTS['releases']}/{quote(release_id, safe='')}/variables"
        return self._make_request('GET', endpoint)

    def update_variable(self, variable_id: str, variable_data: dict) -> dict:
        """Update a variable."""
        return self._make_request('PUT', self.ENDPOINTS['variables'], variable_id, data=variable_data)

    def delete_variable(self, variable_id: str) -> dict:
        """Delete a variable."""
        return self._make_request('DELETE', self.ENDPOINTS['variables'], variable_id)

    # Utility methods
    def get_full_identifier(self, entity_type: str, entity_id: str) -> str:
        """
        Get full identifier for an entity following XL Release conventions.

        Args:
            entity_type: Type of entity (Applications, Releases, etc.)
            entity_id: Entity ID

        Returns:
            Full identifier string
        """
        return f"{entity_type}/{entity_id}"

    def health_check(self) -> bool:
        """
        Perform a health check on the XL Release server.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Try to access a simple endpoint
            self._make_request('GET', '/api/v1/health')
            return True
        except XLRAPIException:
            return False

    def get_server_info(self) -> dict:
        """Get XL Release server information."""
        return self._make_request('GET', '/api/v1/server/info')

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience factory functions
def create_basic_auth_client(base_url: str, username: str, password: str, **kwargs) -> XLRAPIClient:
    """Create XLR API client with basic authentication."""
    return XLRAPIClient(
        base_url=base_url,
        auth_type=AuthType.BASIC,
        username=username,
        password=password,
        **kwargs
    )


def create_token_auth_client(base_url: str, token: str, **kwargs) -> XLRAPIClient:
    """Create XLR API client with token authentication."""
    return XLRAPIClient(
        base_url=base_url,
        auth_type=AuthType.TOKEN,
        token=token,
        **kwargs
    )


def create_oauth2_client(base_url: str, oauth_token: str, **kwargs) -> XLRAPIClient:
    """Create XLR API client with OAuth2 authentication."""
    return XLRAPIClient(
        base_url=base_url,
        auth_type=AuthType.OAUTH2,
        token=oauth_token,
        **kwargs
    )