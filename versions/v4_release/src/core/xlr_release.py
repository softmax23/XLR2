"""
XLR Release module for managing XLR releases.

This module provides the XLRRelease class which handles release creation,
management, and execution in XLR (XebiaLabs Release).
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import requests
import urllib3

from .xlr_generic import XLRGeneric, XLRGenericError

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRReleaseError(Exception):
    """Custom exception for XLRRelease operations."""
    pass


class XLRRelease:
    """
    XLR Release class for handling release creation and management.

    This class provides methods for creating releases from templates,
    managing release lifecycle, and handling release-specific operations.
    """

    def __init__(self):
        """Initialize XLRRelease with required dependencies."""
        self.xlr_generic = XLRGeneric()
        self.logger_cr = logging.getLogger('xlr.release.create')
        self.logger_error = logging.getLogger('xlr.release.error')

        # XLR API attributes
        self.url_api_xlr = None
        self.header = {'Content-Type': 'application/json'}
        self.ops_username_api = None
        self.ops_password_api = None

        # Release specific attributes
        self.release_id = None
        self.release_title = None
        self.template_id = None

    def create_release_from_template(
        self,
        template_id: str,
        release_title: str,
        release_variables: Dict[str, Any] = None,
        scheduled_start_date: Optional[str] = None,
        folder_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new release from an existing template.

        Args:
            template_id: ID of the template to use
            release_title: Title for the new release
            release_variables: Variables to set in the release
            scheduled_start_date: When to schedule the release (ISO format)
            folder_id: Folder where to create the release

        Returns:
            Release ID if successful, None otherwise
        """
        try:
            if not all([template_id, release_title]):
                raise XLRReleaseError("Template ID and release title are required")

            url = f"{self.url_api_xlr}releases"

            # Default scheduled start date to now + 1 hour
            if not scheduled_start_date:
                start_time = datetime.now() + timedelta(hours=1)
                scheduled_start_date = start_time.isoformat() + "Z"

            release_data = {
                "releaseTitle": release_title,
                "templateId": template_id,
                "scheduledStartDate": scheduled_start_date,
                "releaseVariables": release_variables or {},
                "autoStart": False
            }

            if folder_id:
                release_data["folderId"] = folder_id

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=release_data,
                verify=False
            )
            response.raise_for_status()

            release_info = response.json()
            self.release_id = release_info.get('id')
            self.release_title = release_title
            self.template_id = template_id

            self.logger_cr.info(f"Created release '{release_title}' from template {template_id}")
            self.logger_cr.info(f"Release ID: {self.release_id}")

            return self.release_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create release from template: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating release: {e}")
            return None

    def create_release_direct(
        self,
        release_title: str,
        phases_config: List[Dict[str, Any]],
        release_variables: Dict[str, Any] = None,
        scheduled_start_date: Optional[str] = None,
        folder_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a release directly without using a template.

        Args:
            release_title: Title for the new release
            phases_config: Configuration for release phases
            release_variables: Variables to set in the release
            scheduled_start_date: When to schedule the release (ISO format)
            folder_id: Folder where to create the release

        Returns:
            Release ID if successful, None otherwise
        """
        try:
            if not all([release_title, phases_config]):
                raise XLRReleaseError("Release title and phases configuration are required")

            url = f"{self.url_api_xlr}releases"

            # Default scheduled start date to now + 1 hour
            if not scheduled_start_date:
                start_time = datetime.now() + timedelta(hours=1)
                scheduled_start_date = start_time.isoformat() + "Z"

            release_data = {
                "id": None,
                "type": "xlrelease.Release",
                "title": release_title,
                "scheduledStartDate": scheduled_start_date,
                "variables": [],
                "phases": []
            }

            if folder_id:
                release_data["folderId"] = folder_id

            # Add release variables
            if release_variables:
                for key, value in release_variables.items():
                    var_data = {
                        "key": key,
                        "type": "xlrelease.StringVariable",
                        "value": str(value)
                    }
                    release_data["variables"].append(var_data)

            # Add phases
            for phase_config in phases_config:
                phase_data = {
                    "id": None,
                    "type": "xlrelease.Phase",
                    "title": phase_config.get("title", "Unnamed Phase"),
                    "tasks": phase_config.get("tasks", [])
                }
                release_data["phases"].append(phase_data)

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=release_data,
                verify=False
            )
            response.raise_for_status()

            release_info = response.json()
            self.release_id = release_info.get('id')
            self.release_title = release_title

            self.logger_cr.info(f"Created release '{release_title}' directly")
            self.logger_cr.info(f"Release ID: {self.release_id}")

            return self.release_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create release directly: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating release: {e}")
            return None

    def start_release(self, release_id: Optional[str] = None) -> bool:
        """
        Start a release.

        Args:
            release_id: ID of the release to start (uses self.release_id if not provided)

        Returns:
            True if successful, False otherwise
        """
        try:
            target_release_id = release_id or self.release_id
            if not target_release_id:
                raise XLRReleaseError("No release ID provided or available")

            url = f"{self.url_api_xlr}releases/{target_release_id}/start"

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Started release: {target_release_id}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to start release: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error starting release: {e}")
            return False

    def get_release_status(self, release_id: Optional[str] = None) -> Optional[str]:
        """
        Get the status of a release.

        Args:
            release_id: ID of the release (uses self.release_id if not provided)

        Returns:
            Release status if successful, None otherwise
        """
        try:
            target_release_id = release_id or self.release_id
            if not target_release_id:
                raise XLRReleaseError("No release ID provided or available")

            url = f"{self.url_api_xlr}releases/{target_release_id}"

            response = requests.get(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )
            response.raise_for_status()

            release_info = response.json()
            status = release_info.get('status', 'UNKNOWN')

            self.logger_cr.info(f"Release {target_release_id} status: {status}")
            return status

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to get release status: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error getting release status: {e}")
            return None

    def update_release_variables(
        self,
        variables: Dict[str, Any],
        release_id: Optional[str] = None
    ) -> bool:
        """
        Update variables in a release.

        Args:
            variables: Dictionary of variables to update
            release_id: ID of the release (uses self.release_id if not provided)

        Returns:
            True if successful, False otherwise
        """
        try:
            target_release_id = release_id or self.release_id
            if not target_release_id:
                raise XLRReleaseError("No release ID provided or available")

            for key, value in variables.items():
                url = f"{self.url_api_xlr}releases/{target_release_id}/variables/{key}"

                variable_data = {
                    "key": key,
                    "value": str(value)
                }

                response = requests.put(
                    url,
                    headers=self.header,
                    auth=(self.ops_username_api, self.ops_password_api),
                    json=variable_data,
                    verify=False
                )
                response.raise_for_status()

            self.logger_cr.info(f"Updated {len(variables)} variables in release {target_release_id}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to update release variables: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error updating release variables: {e}")
            return False

    def get_release_url(self, release_id: Optional[str] = None) -> Optional[str]:
        """
        Get the web URL for viewing a release.

        Args:
            release_id: ID of the release (uses self.release_id if not provided)

        Returns:
            Release URL if successful, None otherwise
        """
        try:
            target_release_id = release_id or self.release_id
            if not target_release_id:
                return None

            # Construct URL (adjust base URL as needed)
            base_url = self.url_api_xlr.replace('/api/v1/', '')
            clean_id = target_release_id.replace("Applications/", "").replace('/', '-')
            release_url = f"{base_url}/#/releases/{clean_id}"

            return release_url

        except Exception as e:
            self.logger_error.error(f"Error constructing release URL: {e}")
            return None

    def setup_xlr_connection(
        self,
        url_api_xlr: str,
        username: str,
        password: str
    ) -> None:
        """
        Setup XLR API connection parameters.

        Args:
            url_api_xlr: XLR API URL
            username: API username
            password: API password
        """
        self.url_api_xlr = url_api_xlr
        self.ops_username_api = username
        self.ops_password_api = password

        self.logger_cr.info("XLR connection configured for release operations")