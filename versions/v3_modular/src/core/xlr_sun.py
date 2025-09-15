"""
XLR SUN module for managing ServiceNow integrations.

This module provides the XLRSun class which handles ServiceNow (SUN)
task management and integration operations.
"""

import logging
from typing import Dict, Any, Optional, List

import requests
import urllib3

from .xlr_generic import XLRGeneric, XLRGenericError

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRSunError(Exception):
    """Custom exception for XLRSun operations."""
    pass


class XLRSun:
    """
    XLR SUN class for handling ServiceNow integration operations.

    This class provides methods for creating, updating, and closing
    ServiceNow tasks from XLR releases.
    """

    def __init__(self):
        """Initialize XLRSun with required dependencies."""
        self.xlr_generic = XLRGeneric()
        self.logger_cr = logging.getLogger('xlr.sun.create')
        self.logger_error = logging.getLogger('xlr.sun.error')

        # XLR API attributes
        self.url_api_xlr = None
        self.header = {'Content-Type': 'application/json'}
        self.ops_username_api = None
        self.ops_password_api = None
        self.dict_template = {}

        # ServiceNow specific attributes
        self.sun_approver = None
        self.sun_server_config = None

    def xlr_sun_task_close_sun_task(
        self,
        task_to_close: str,
        title: str,
        id_task: str,
        type_task: str,
        phase: str
    ) -> bool:
        """
        Create a task to close ServiceNow tickets.

        Args:
            task_to_close: Variable containing the task to close
            title: Title for the close task
            id_task: Parent task ID
            type_task: Type of the task being closed
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([task_to_close, title, id_task, type_task, phase]):
                raise XLRSunError("Missing required parameters for SUN task closure")

            url = f"{self.url_api_xlr}tasks/{id_task}/tasks"

            close_task_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Close SUN Task for {title}",
                "locked": True,
                "pythonScript": {
                    "type": "servicenow.UpdateTask",
                    "id": None,
                    "server": self.sun_server_config or "Configuration/Custom/ServiceNow",
                    "sysId": task_to_close,
                    "taskData": {
                        "state": "3",  # Closed Complete
                        "work_notes": f"Task completed for {type_task} in {phase} phase",
                        "close_code": "Successful",
                        "close_notes": f"Automatically closed after {type_task} completion"
                    }
                }
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=close_task_data,
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Created SUN task closure for {title} in phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create SUN task closure: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating SUN task closure: {e}")
            return False

    def create_sun_change_request(
        self,
        phase: str,
        change_details: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a ServiceNow change request.

        Args:
            phase: The deployment phase
            change_details: Details for the change request

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRSunError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            change_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Create Change Request for {phase}",
                "locked": True,
                "variableMapping": {
                    "pythonScript.changeRequestId": f"${{change_request_id_{phase}}}"
                },
                "pythonScript": {
                    "type": "servicenow.CreateChangeRequest",
                    "id": None,
                    "server": self.sun_server_config or "Configuration/Custom/ServiceNow",
                    "shortDescription": change_details.get('short_description', f'Deployment for {phase}'),
                    "description": change_details.get('description', f'Automated deployment in {phase} environment'),
                    "category": change_details.get('category', 'Software'),
                    "priority": change_details.get('priority', '3'),
                    "riskAndImpactAnalysis": change_details.get('risk_analysis', 'Low risk automated deployment'),
                    "assignmentGroup": change_details.get('assignment_group', ''),
                    "assignedTo": self.sun_approver
                }
            }

            # Create the variable to store change request ID
            self.xlr_generic.template_create_variable(
                key=f'change_request_id_{phase}',
                typev='StringVariable',
                label=f'Change Request ID for {phase}',
                description=f'ServiceNow change request ID for {phase} phase',
                value='',
                requires_value=False,
                show_on_release_start=False,
                multiline=False
            )

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=change_data,
                verify=False
            )
            response.raise_for_status()

            task_id = response.json().get('id')
            self.logger_cr.info(f"Created SUN change request task for phase {phase}")

            return task_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create SUN change request: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating SUN change request: {e}")
            return None

    def create_sun_approval_task(
        self,
        phase: str,
        approver: str,
        approval_details: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a ServiceNow approval task.

        Args:
            phase: The deployment phase
            approver: Email of the approver
            approval_details: Details for the approval

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRSunError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            approval_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Request Approval for {phase}",
                "locked": True,
                "pythonScript": {
                    "type": "servicenow.CreateApproval",
                    "id": None,
                    "server": self.sun_server_config or "Configuration/Custom/ServiceNow",
                    "approver": approver,
                    "shortDescription": approval_details.get('short_description', f'Approval needed for {phase} deployment'),
                    "description": approval_details.get('description', f'Please approve the deployment to {phase} environment'),
                    "dueDate": approval_details.get('due_date', ''),
                    "priority": approval_details.get('priority', '2')
                }
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=approval_data,
                verify=False
            )
            response.raise_for_status()

            task_id = response.json().get('id')
            self.logger_cr.info(f"Created SUN approval task for phase {phase}")

            return task_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create SUN approval task: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating SUN approval task: {e}")
            return None

    def update_sun_task_status(
        self,
        task_id: str,
        status: str,
        work_notes: str = ""
    ) -> bool:
        """
        Update the status of a ServiceNow task.

        Args:
            task_id: ServiceNow task ID
            status: New status for the task
            work_notes: Optional work notes

        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([task_id, status]):
                raise ValueError("Task ID and status are required")

            phase_id = self.dict_template.get('PRODUCTION', {}).get('xlr_id_phase',
                       self.dict_template.get('BENCH', {}).get('xlr_id_phase'))

            if not phase_id:
                raise XLRSunError("No suitable phase ID found for SUN task update")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            update_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Update SUN Task Status to {status}",
                "locked": True,
                "pythonScript": {
                    "type": "servicenow.UpdateTask",
                    "id": None,
                    "server": self.sun_server_config or "Configuration/Custom/ServiceNow",
                    "sysId": task_id,
                    "taskData": {
                        "state": status,
                        "work_notes": work_notes or f"Status updated to {status} via XLR automation"
                    }
                }
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=update_data,
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Created SUN task status update to {status}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create SUN task status update: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating SUN task status update: {e}")
            return False

    def create_sun_incident(
        self,
        phase: str,
        incident_details: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a ServiceNow incident.

        Args:
            phase: The deployment phase
            incident_details: Details for the incident

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRSunError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            incident_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Create Incident for {phase}",
                "locked": True,
                "variableMapping": {
                    "pythonScript.incidentId": f"${{incident_id_{phase}}}"
                },
                "pythonScript": {
                    "type": "servicenow.CreateIncident",
                    "id": None,
                    "server": self.sun_server_config or "Configuration/Custom/ServiceNow",
                    "shortDescription": incident_details.get('short_description', f'Issue in {phase} deployment'),
                    "description": incident_details.get('description', f'Automated incident creation for {phase}'),
                    "urgency": incident_details.get('urgency', '3'),
                    "impact": incident_details.get('impact', '3'),
                    "category": incident_details.get('category', 'Software'),
                    "assignmentGroup": incident_details.get('assignment_group', ''),
                    "assignedTo": incident_details.get('assigned_to', self.sun_approver)
                }
            }

            # Create the variable to store incident ID
            self.xlr_generic.template_create_variable(
                key=f'incident_id_{phase}',
                typev='StringVariable',
                label=f'Incident ID for {phase}',
                description=f'ServiceNow incident ID for {phase} phase',
                value='',
                requires_value=False,
                show_on_release_start=False,
                multiline=False
            )

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=incident_data,
                verify=False
            )
            response.raise_for_status()

            task_id = response.json().get('id')
            self.logger_cr.info(f"Created SUN incident task for phase {phase}")

            return task_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create SUN incident: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating SUN incident: {e}")
            return None

    def setup_sun_configuration(
        self,
        sun_approver: str,
        sun_server_config: str = None
    ) -> None:
        """
        Setup ServiceNow configuration.

        Args:
            sun_approver: Default approver email
            sun_server_config: ServiceNow server configuration name
        """
        self.sun_approver = sun_approver
        self.sun_server_config = sun_server_config

        self.logger_cr.info("ServiceNow configuration setup completed")

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

        self.logger_cr.info("XLR connection configured for SUN operations")