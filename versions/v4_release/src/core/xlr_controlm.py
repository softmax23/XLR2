"""
XLR Control-M module for managing Control-M integrations.

This module provides the XLRControlm class which handles Control-M specific
operations like job ordering, resource management, and webhook integrations.
"""

import logging
from typing import Dict, Any, Optional, Union

import requests
import urllib3

from .xlr_generic import XLRGeneric, XLRGenericError

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRControlmError(Exception):
    """Custom exception for XLRControlm operations."""
    pass


class XLRControlm:
    """
    XLR Control-M class for handling Control-M job orchestration and monitoring.

    This class provides methods for managing Control-M jobs, folders, and resources
    through XLR (XebiaLabs Release) integration.
    """

    def __init__(self):
        """Initialize XLRControlm with required dependencies."""
        self.xlr_generic = XLRGeneric()
        self.logger_cr = logging.getLogger('xlr.controlm.create')
        self.logger_error = logging.getLogger('xlr.controlm.error')

        # Control-M specific attributes
        self.CTM_PROD = None
        self.CTM_BENCH = None
        self.url_api_controlm = None

        # XLR API attributes (inherited from parent context)
        self.url_api_xlr = None
        self.header = {'Content-Type': 'application/json'}
        self.ops_username_api = None
        self.ops_password_api = None
        self.dict_template = {}

    def webhook_controlm_resource(
        self,
        phase: str,
        grp_id_controlm: str,
        task: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a webhook task to change Control-M resource values.

        Args:
            phase: The deployment phase (DEV, UAT, PROD, etc.)
            grp_id_controlm: The Control-M group task ID
            task: Task configuration containing name and max values

        Returns:
            Task ID if successful, None otherwise

        Raises:
            XLRControlmError: If required parameters are missing
        """
        try:
            if not all([phase, grp_id_controlm, task]):
                raise XLRControlmError("Missing required parameters for resource webhook")

            if 'name' not in task or 'max' not in task:
                raise XLRControlmError("Task must contain 'name' and 'max' fields")

            # Determine CTM environment based on folder name
            # This assumes foldername is available in the context
            folder_name = getattr(self, 'current_folder_name', '')
            ctm_env = self.CTM_PROD if folder_name.lower().startswith('p') else self.CTM_BENCH

            url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

            webhook_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Change RESOURCE value {task['name']}",
                "locked": True,
                "pythonScript": {
                    "type": "webhook.JsonWebhook",
                    "id": None,
                    "URL": f"{self.url_api_controlm}/resource",
                    "method": "POST",
                    "body": {
                        "ctm": ctm_env,
                        "name": task['name'],
                        "max": int(task['max']),
                    },
                    "username": f"${{{phase}_username_controlm}}",
                    "password": f"${{{phase}_password_controlm}}"
                }
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=webhook_data,
                verify=False
            )
            response.raise_for_status()

            task_id = response.json().get('id')
            self.logger_cr.info(f"Created Control-M resource webhook for {task['name']} in phase {phase}")

            return task_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M resource webhook: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M resource webhook: {e}")
            return None

    def script_jython_date_for_controlm(self, phase: str) -> bool:
        """
        Create a Jython script task to format date for Control-M.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            if not phase:
                raise ValueError("Phase is required")

            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRControlmError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = (
                "##script_jython_date_for_controlm\n"
                "from time import strftime\n"
                "date_format = strftime('%Y%m%d')\n"
                "print(date_format)\n"
                "releaseVariables['controlm_today'] = date_format\n"
            )

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Put date from input at format for CONTROLM demand",
                "script": script_content
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()

            if 'id' in response.json():
                self.logger_cr.info(
                    f"ON PHASE: {phase.upper()} --- Add task: 'Put date from input at format for CONTROLM demand'"
                )
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M date script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M date script: {e}")
            return False

    def script_jython_date_for_xlr_task_controlm(
        self,
        phase: str,
        grp_id_controlm: str
    ) -> bool:
        """
        Create a Jython script task for XLR Control-M task date formatting.

        Args:
            phase: The deployment phase
            grp_id_controlm: The Control-M group task ID

        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([phase, grp_id_controlm]):
                raise ValueError("Phase and group ID are required")

            url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

            script_content = (  # Control-M date script content
                "##script_jython_date_for_XLR_task_controlm\n"
                "from java.util import Date, TimeZone\n"
                "from java.text import SimpleDateFormat\n"
                "now = Date()\n"
                "sdf = SimpleDateFormat('yyyy-MM-dd\\'T\\'HH:mm:ssXXX')\n"
                "sdf.setTimeZone(TimeZone.getTimeZone('UTC+1'))\n"
                "formatted_date = sdf.format(now)\n"
                "releaseVariables['controlm_today'] = formatted_date\n"
            )

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Put date from input at format for CONTROLM demand",
                "script": script_content
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()

            if 'id' in response.json():
                self.logger_cr.info(
                    f"ON PHASE: {phase.upper()} --- Add task: 'Put date from input at format for CONTROLM demand'"
                )
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create XLR Control-M date script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating XLR Control-M date script: {e}")
            return False

    def webhook_controlm_order_folder(
        self,
        phase: str,
        folder_info: Dict[str, Any],
        grp_id_controlm: str,
        task: str
    ) -> Optional[str]:
        """
        Create a webhook task to order a Control-M folder.

        Args:
            phase: The deployment phase
            folder_info: Folder configuration information
            grp_id_controlm: The Control-M group task ID
            task: Task identifier

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            if not all([phase, folder_info, grp_id_controlm, task]):
                raise XLRControlmError("Missing required parameters for folder order webhook")

            folder_name = list(folder_info.keys())[0]
            variable_name = (
                f"result_orderfolder_{task.split('_', 2)[-1]}_"
                f"{folder_name.replace('${controlm_prefix_BENCH}', '')}_{phase}"
            )

            # Create result variable
            self.xlr_generic.template_create_variable(
                key=variable_name,
                typev='StringVariable',
                label='',
                description='',
                value='',
                requires_value=False,
                show_on_release_start=False,
                multiline=False
            )

            # Determine CTM environment
            ctm_env = self.CTM_PROD if folder_name.lower().startswith('p') else self.CTM_BENCH

            url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

            folder_config = folder_info[folder_name]
            webhook_data = {
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"demand Folder {folder_name}",
                "variableMapping": {
                    "pythonScript.result": f"${{{variable_name}}}"
                },
                "locked": True,
                "pythonScript": {
                    "type": "webhook.JsonWebhook",
                    "id": None,
                    "URL": f"{self.url_api_controlm}/orderFolder",
                    "method": "POST",
                    "body": {
                        "createDuplicate": True,
                        "ctm": ctm_env,
                        "folder": folder_name,
                        "ignoreCriteria": folder_config.get('ignoreCriteria', False),
                        "hold": folder_config.get('hold', False),
                        "independantFlow": True,
                        "appendJob": folder_config.get('appendJob', False),
                        "jobs": "",
                        "orderDate": "${controlm_today}",
                        "waitForOrderDate": False
                    },
                    "username": f"${{{phase}_username_controlm}}",
                    "password": f"${{{phase}_password_controlm}}",
                    "jsonPathExpression": "Data.statuses"
                }
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=webhook_data,
                verify=False
            )
            response.raise_for_status()

            task_id = response.json().get('id')
            self.logger_cr.info(f"Created Control-M folder order webhook for {folder_name} in phase {phase}")

            return task_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M folder order webhook: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M folder order webhook: {e}")
            return None

    def set_variable_task_controlm(
        self,
        phase: str,
        grp_id_controlm: str,
        count_task_controlm_spec: str,
        job: Union[str, int]
    ) -> bool:
        """
        Create a variable setting task for Control-M.

        Args:
            phase: The deployment phase
            grp_id_controlm: The Control-M group task ID
            count_task_controlm_spec: Variable name
            job: Job value to set

        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([phase, grp_id_controlm, count_task_controlm_spec]):
                raise ValueError("Phase, group ID, and variable name are required")

            # Create the variable in template
            self.xlr_generic.template_create_variable(
                key=count_task_controlm_spec,
                typev='StringVariable',
                label='',
                description='',
                value='',
                requires_value=False,
                show_on_release_start=False,
                multiline=False
            )

            url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

            task_data = {
                "id": None,
                "locked": True,
                "type": "xlrelease.ScriptTask",
                "title": "Create variable for controlm demand",
                "script": f"releaseVariables['{count_task_controlm_spec}'] = \"{str(job)}\""
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Created Control-M variable task for {count_task_controlm_spec}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M variable task: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M variable task: {e}")
            return False

    def xlr_plugin_controlm_order_folder(
        self,
        folder_info: Dict[str, Any],
        grp_id_controlm: str
    ) -> bool:
        """
        Create a Control-M plugin task to order a folder.

        Args:
            folder_info: Folder configuration information
            grp_id_controlm: The Control-M group task ID

        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([folder_info, grp_id_controlm]):
                raise ValueError("Folder info and group ID are required")

            folder_name = list(folder_info.keys())[0]
            folder_name_clean = folder_name.replace('${controlm_prefix_BENCH}', '')
            folder_config = folder_info[folder_name]

            # Determine CTM environment
            ctm_env = self.CTM_PROD if folder_name.lower().startswith('p') else self.CTM_BENCH

            url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

            task_data = {
                "id": None,
                "locked": False,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Order Folder {folder_name}",
                "variableMapping": {
                    "pythonScript.orderDate": "${controlm_today}",
                    "pythonScript.folderId": f"${{id_{folder_name_clean}}}"
                },
                "pythonScript": {
                    "type": "controlM.OrderFolder",
                    "id": None,
                    "server": "Configuration/Custom/API_CONTROLM",
                    "ctm": ctm_env,
                    "folderName": folder_name,
                    "ignoreCriteria": folder_config.get('ignoreCriteria', False),
                    "appendJob": folder_config.get('appendJob', True),
                    "hold": folder_config.get('hold', False),
                    "jobIds": {}
                },
                "keepPreviousOutputPropertiesOnRetry": False
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Created Control-M plugin order folder task for {folder_name}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M plugin order folder task: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M plugin order folder task: {e}")
            return False

    def xlr_plugin_controlm_wait_job_status_by_id(
        self,
        folder_name: str,
        status_to_wait_for: str,
        grp_id_controlm: str
    ) -> bool:
        """
        Create a Control-M plugin task to wait for job status.

        Args:
            folder_name: Name of the folder/job
            status_to_wait_for: Status to wait for
            grp_id_controlm: The Control-M group task ID

        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([folder_name, status_to_wait_for, grp_id_controlm]):
                raise ValueError("Folder name, status, and group ID are required")

            folder_name_clean = folder_name.replace('${controlm_prefix_BENCH}', '')

            # Determine CTM environment
            ctm_env = self.CTM_PROD if folder_name.lower().startswith('p') else self.CTM_BENCH

            url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

            task_data = {
                "id": None,
                "locked": False,
                "type": "xlrelease.CustomScriptTask",
                "title": f"Wait {folder_name} in status {status_to_wait_for}",
                "pythonScript": {
                    "type": "controlM.WaitJobStatusById",
                    "id": None,
                    "server": "Configuration/Custom/API_CONTROLM",
                    "ctm": ctm_env,
                    "folderName": folder_name,
                    "attempts": 15,
                    "interval": 60,
                    "statusToFailOn": "Ended Not OK",
                    "statusToWaitFor": status_to_wait_for,
                    "jobId": f"${{id_{folder_name_clean}}}"
                },
                "keepPreviousOutputPropertiesOnRetry": False
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Created Control-M wait job status task for {folder_name}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M wait job status task: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M wait job status task: {e}")
            return False

    def setup_controlm_environment(
        self,
        url_api_controlm: str,
        ctm_prod: str,
        ctm_bench: str
    ) -> None:
        """
        Setup Control-M environment configuration.

        Args:
            url_api_controlm: Control-M API URL
            ctm_prod: Production CTM identifier
            ctm_bench: Bench/Test CTM identifier
        """
        self.url_api_controlm = url_api_controlm
        self.CTM_PROD = ctm_prod
        self.CTM_BENCH = ctm_bench

        self.logger_cr.info("Control-M environment configured")

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

        self.logger_cr.info("XLR connection configured")