"""
XLR Generic module for managing XLR templates and common operations.

This module provides the XLRGeneric class which handles core functionality
for creating and managing XLR templates, user inputs, and basic operations.
"""

import os
import sys
import json
import logging
import inspect
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRGenericError(Exception):
    """Custom exception for XLRGeneric operations."""
    pass


class XLRGeneric:
    """
    XLR Generic class for handling core XLR template operations.

    This class provides methods for creating templates, managing phases,
    and handling user inputs in XLR (XebiaLabs Release).
    """

    def __init__(self):
        """Initialize XLRGeneric with required attributes."""
        self.logger_cr = logging.getLogger('xlr.create')
        self.logger_error = logging.getLogger('xlr.error')

        # Initialize core attributes
        self.dict_template = {}
        self.parameters = {}
        self.XLR_template_id = None
        self.template_url = None
        self.ops_username_api = None
        self.ops_password_api = None
        self.url_api_xlr = None
        self.header = {'Content-Type': 'application/json'}

        # Track processing state
        self.auto_undeploy_done = False
        self.jenkins_token = False
        self.list_xlr_group_task_done = []
        self.dic_for_check = {}

    def _log_error_and_exit(self, error: Exception, context: str = "") -> None:
        """
        Log error with context and exit gracefully.

        Args:
            error: The exception that occurred
            context: Additional context for the error
        """
        frame = inspect.currentframe().f_back
        self.logger_error.error(
            f"File: {os.path.basename(frame.f_code.co_filename)} "
            f"--Class: {self.__class__.__name__} "
            f"--Function: {frame.f_code.co_name} "
            f"--Line: {frame.f_lineno}"
        )
        if context:
            self.logger_error.error(f"Context: {context}")
        self.logger_error.error(f"Error: {error}")
        raise XLRGenericError(f"{context}: {error}") from error

    def create_template(self) -> tuple[Dict[str, Any], str]:
        """
        Create a new XLR template.

        Returns:
            Tuple containing the updated dict_template and template ID

        Raises:
            XLRGenericError: If template creation fails
        """
        if not all([self.url_api_xlr, self.ops_username_api, self.ops_password_api]):
            raise XLRGenericError("Missing required API credentials or URL")

        folder_id = self.dict_template.get('template', {}).get('xlr_folder')
        if not folder_id:
            raise XLRGenericError("Missing XLR folder ID in template configuration")

        url_create_template = f"{self.url_api_xlr}templates/?folderId={folder_id}"

        try:
            release_name = self.parameters.get('general_info', {}).get('name_release', 'Unnamed Release')

            response = requests.post(
                url_create_template,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json={
                    "id": None,
                    "type": "xlrelease.Release",
                    "title": release_name,
                    "status": "TEMPLATE",
                    "scheduledStartDate": "2023-03-09T17:56:54.786+01:00",
                    "scriptUsername": self.ops_username_api,
                    "scriptUserPassword": self.ops_password_api
                },
                verify=False
            )
            response.raise_for_status()

            template_data = response.json()
            self.XLR_template_id = template_data['id']

            # Update or create template dictionary
            if 'template' not in self.dict_template:
                self.dict_template['template'] = {}

            self.dict_template['template']['xlr_id'] = self.XLR_template_id

            # Generate template URL
            self.template_url = (
                'https://release-pfi.mycloud.intranatixis.com/#/templates/'
                + self.XLR_template_id.replace("Applications/", "").replace('/', '-')
            )

            # Log success
            xlr_folder = self.parameters.get('general_info', {}).get('xlr_folder', 'Unknown')
            self.logger_cr.info(f"CREATE TEMPLATE in XLR FOLDER: {xlr_folder}")
            self.logger_cr.info(f"NAME: {release_name}")
            self.logger_cr.info(f"LINK: {self.template_url}")

            return self.dict_template, self.XLR_template_id

        except requests.exceptions.RequestException as e:
            self._log_error_and_exit(e, "Failed to create template")
        except (KeyError, TypeError) as e:
            self._log_error_and_exit(e, "Invalid template response data")

    def add_task_user_input(
        self,
        phase: str,
        type_userinput: str,
        link_task_id: str
    ) -> Optional[str]:
        """
        Add a user input task to the specified phase.

        Args:
            phase: The phase name (DEV, UAT, etc.)
            type_userinput: Type of user input (xldeploy, jenkins, etc.)
            link_task_id: The task ID to link the input to

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            if not all([phase, type_userinput, link_task_id]):
                raise ValueError("Missing required parameters for user input task")

            url = f"{self.url_api_xlr}tasks/{link_task_id}/tasks"

            task_data = {
                "id": None,
                "type": "xlrelease.UserInputTask",
                "title": f"User Input for {type_userinput} in {phase}",
                "locked": True,
                "variables": [
                    {
                        "key": f"{phase}_username_{type_userinput}",
                        "type": "StringVariable",
                        "label": f"Username for {type_userinput}",
                        "description": f"Enter username for {type_userinput} in {phase} phase"
                    },
                    {
                        "key": f"{phase}_password_{type_userinput}",
                        "type": "PasswordStringVariable",
                        "label": f"Password for {type_userinput}",
                        "description": f"Enter password for {type_userinput} in {phase} phase"
                    }
                ]
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()

            task_id = response.json().get('id')
            self.logger_cr.info(f"Added user input task for {type_userinput} in phase {phase}")

            return task_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to add user input task: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error adding user input task: {e}")
            return None

    def xlr_group_task(
        self,
        id_xlr_task: str,
        type_group: str,
        title_group: str,
        precondition: str = ""
    ) -> Optional[str]:
        """
        Create a group task in XLR.

        Args:
            id_xlr_task: Parent task ID
            type_group: Type of group (SequentialGroup, ParallelGroup)
            title_group: Title for the group
            precondition: Precondition for the group

        Returns:
            Group task ID if successful, None otherwise
        """
        try:
            if type_group not in ['SequentialGroup', 'ParallelGroup']:
                raise ValueError(f"Invalid group type: {type_group}")

            url = f"{self.url_api_xlr}tasks/{id_xlr_task}/tasks"

            group_data = {
                "id": None,
                "type": f"xlrelease.{type_group}",
                "title": title_group,
                "locked": True
            }

            if precondition:
                group_data["precondition"] = precondition

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=group_data,
                verify=False
            )
            response.raise_for_status()

            group_id = response.json().get('id')
            self.logger_cr.info(f"Created {type_group}: {title_group}")

            return group_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create group task: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating group task: {e}")
            return None

    def template_create_variable(
        self,
        key: str,
        typev: str,
        label: str = "",
        description: str = "",
        value: Any = None,
        requires_value: bool = False,
        show_on_release_start: bool = False,
        multiline: bool = False
    ) -> bool:
        """
        Create a variable in the XLR template.

        Args:
            key: Variable key/name
            typev: Variable type (StringVariable, PasswordStringVariable, etc.)
            label: Display label
            description: Variable description
            value: Default value
            requires_value: Whether value is required
            show_on_release_start: Show on release start
            multiline: Whether it's a multiline variable

        Returns:
            True if successful, False otherwise
        """
        try:
            if not key or not typev:
                raise ValueError("Variable key and type are required")

            url = f"{self.url_api_xlr}templates/{self.XLR_template_id}/variables"

            variable_data = {
                "key": key,
                "type": typev,
                "label": label,
                "description": description,
                "requiresValue": requires_value,
                "showOnReleaseStart": show_on_release_start,
                "multiline": multiline
            }

            if value is not None:
                variable_data["value"] = value

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=variable_data,
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Created template variable: {key} ({typev})")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create template variable {key}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating template variable {key}: {e}")
            return False

    def parameter_phase_task(self, phase: str) -> None:
        """
        Process parameters for a specific phase and create necessary tasks.

        Args:
            phase: The phase to process (DEV, UAT, BENCH, PRODUCTION)
        """
        try:
            self.auto_undeploy_done = False

            # Validate phase
            valid_phases = self.parameters.get('general_info', {}).get('phases', [])
            if phase not in valid_phases and phase not in ['DEV', 'BUILD', 'UAT', 'BENCH', 'PRODUCTION']:
                self.logger_error.warning(f"Phase {phase} not in valid phases list")

            self._process_development_phase(phase)
            self._process_jenkins_tasks(phase)
            self._process_phase_tasks(phase)

        except Exception as e:
            self._log_error_and_exit(e, f"Failed to process phase {phase}")

    def _process_development_phase(self, phase: str) -> None:
        """Process development-specific tasks for the phase."""
        if phase not in ['DEV', 'BUILD', 'UAT']:
            return

        # Check if XLD user input is needed
        template_mode = self.parameters.get('general_info', {}).get('template_package_mode')
        phases_list = self.parameters.get('general_info', {}).get('phases', [])

        needs_xld_input = (
            (template_mode == 'listbox' and 'DEV' not in phases_list) or
            (template_mode == 'listbox' and 'DEV' in phases_list and phase in ['UAT', 'DEV']) or
            (template_mode == 'string' and 'DEV' in phases_list and phase in ['UAT', 'DEV'])
        )

        if needs_xld_input:
            phase_data = self.dict_template.get(phase, [])
            username_exists = any(f'{phase}_username_xldeploy' in d for d in phase_data)

            if not username_exists:
                link_id = f"{self.dict_template['template']['xlr_id']}/{self.dict_template[phase]['xlr_id_phase']}"
                self.add_task_user_input(
                    phase=phase,
                    type_userinput='xldeploy',
                    link_task_id=link_id
                )

    def _process_jenkins_tasks(self, phase: str) -> None:
        """Process Jenkins-related tasks for the phase."""
        jenkins_config = self.parameters.get('jenkins')
        if not jenkins_config:
            return

        # Check if Jenkins tasks are needed for this phase
        needs_jenkins = (
            (jenkins_config and phase == 'DEV' and 'BUILD' not in self.parameters.get('general_info', {}).get('phases', [])) or
            (jenkins_config and phase == 'BUILD') or
            (self.parameters.get('general_info', {}).get('jenkins_UAT') and phase == 'UAT')
        )

        if needs_jenkins:
            self._create_jenkins_group(phase)

    def _process_phase_tasks(self, phase: str) -> None:
        """Process all tasks defined for a specific phase."""
        phases_config = self.parameters.get('Phases', {})
        if phase not in phases_config:
            return

        for task in phases_config[phase]:
            if isinstance(task, dict):
                task_type = list(task.keys())[0]
                self._process_task_by_type(phase, task_type, task)

    def _create_jenkins_group(self, phase: str) -> Optional[str]:
        """Create Jenkins group task for the phase."""
        phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
        if not phase_id:
            return None

        return self.xlr_group_task(
            id_xlr_task=phase_id,
            type_group="SequentialGroup",
            title_group="Jenkins JOBS",
            precondition=""
        )

    def _process_task_by_type(self, phase: str, task_type: str, task: Dict[str, Any]) -> None:
        """Process a task based on its type."""
        if 'xldeploy' in task_type:
            self._process_xldeploy_task(phase, task)
        elif 'launch_script_windows' in task_type:
            self._process_script_task(phase, task, 'windows')
        elif 'launch_script_linux' in task_type:
            self._process_script_task(phase, task, 'linux')
        elif task_type == 'set_variables_release':
            self._process_variable_task(phase)
        elif 'XLR_task_controlm' in task_type:
            self._process_controlm_task(phase, task)

    def _process_xldeploy_task(self, phase: str, task: Dict[str, Any]) -> None:
        """Process XL Deploy tasks."""
        # Implementation for XLD task processing
        self.logger_cr.info(f"Processing XLDeploy task for phase {phase}")

    def _process_script_task(self, phase: str, task: Dict[str, Any], script_type: str) -> None:
        """Process script execution tasks."""
        self.logger_cr.info(f"Processing {script_type} script task for phase {phase}")

    def _process_variable_task(self, phase: str) -> None:
        """Process variable setting tasks."""
        self.logger_cr.info(f"Processing variable task for phase {phase}")

    def _process_controlm_task(self, phase: str, task: Dict[str, Any]) -> None:
        """Process Control-M related tasks."""
        self.logger_cr.info(f"Processing Control-M task for phase {phase}")

    def creation_technical_task(self, phase: str, task_category: str) -> None:
        """
        Create technical tasks for a phase.

        Args:
            phase: The phase name
            task_category: Category of technical task (before_deployment, after_deployment, etc.)
        """
        try:
            technical_tasks = self.parameters.get('technical_task_list', {}).get(task_category, [])

            for task in technical_tasks:
                self.logger_cr.info(f"Creating technical task {task} for {phase} - {task_category}")
                # Implementation for creating specific technical tasks

        except Exception as e:
            self.logger_error.error(f"Failed to create technical task for {phase}: {e}")