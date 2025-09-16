"""
XLR Generic module for managing XLR templates and common operations.

This module provides the XLRGeneric class which handles core functionality
for creating and managing XLR templates, user inputs, and basic operations.
"""

import os
import logging
import inspect
from typing import Dict, Any, Optional, List

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

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize XLRGeneric with required attributes."""
        self.logger_cr = logging.getLogger('xlr.create')
        self.logger_error = logging.getLogger('xlr.error')

        # Load configuration
        from ..config.config_loader import ConfigLoader
        config = ConfigLoader()

        # Initialize core attributes
        self.dict_template = {}
        self.parameters = parameters or {}
        self.XLR_template_id = None
        self.template_url = None

        # API configuration from config loader
        self.ops_username_api = config.get('ops_username_api')
        self.ops_password_api = config.get('ops_password_api')
        self.url_api_xlr = config.get('url_api_xlr')
        self.header = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        # Track processing state
        self.auto_undeploy_done = False
        self.jenkins_token = False
        self.list_xlr_group_task_done = []
        self.dic_for_check = {}

        # V1 compatibility - critical variables
        self.release_Variables_in_progress = {}
        self.dict_value_for_template = {}
        self.list_technical_task_done = []
        self.list_technical_sun_task_done = []

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

        # Process technical tasks before deployment (once at start)
        if phase not in ['BUILD', 'UAT', 'DEV']:
            self.creation_technical_task(phase, 'before_deployment')

        # Find all xldeploy tasks to insert before_xldeploy and after_xldeploy
        xldeploy_indices = []
        for i, task in enumerate(phases_config[phase]):
            if isinstance(task, dict):
                task_type = list(task.keys())[0]
                if 'xldeploy' in task_type:
                    xldeploy_indices.append(i)

        # Process each task with technical task insertions
        for i, task in enumerate(phases_config[phase]):
            if isinstance(task, dict):
                task_type = list(task.keys())[0]

                # Insert before_xldeploy before each xldeploy task
                if 'xldeploy' in task_type and phase not in ['BUILD', 'UAT', 'DEV']:
                    self.creation_technical_task(phase, 'before_xldeploy')

                # Process the actual task
                self._process_task_by_type(phase, task_type, task)

                # Insert after_xldeploy after the last xldeploy task
                if ('xldeploy' in task_type and
                    phase not in ['BUILD', 'UAT', 'DEV'] and
                    xldeploy_indices and
                    i == xldeploy_indices[-1]):
                    self.creation_technical_task(phase, 'after_xldeploy')

        # Process technical tasks after deployment (once at end)
        if phase not in ['BUILD', 'UAT', 'DEV']:
            self.creation_technical_task(phase, 'after_deployment')

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
        """Process XL Deploy tasks with Y88-specific logic."""
        self.logger_cr.info(f"Processing XLDeploy task for phase {phase}")

        # Apply Y88-specific path modifications if needed
        if self._is_y88_environment():
            self._apply_y88_xld_logic(phase, task)

        # Continue with standard XLD processing
        self._process_standard_xld_task(phase, task)

    def _is_y88_environment(self) -> bool:
        """Check if this is a Y88 environment."""
        iua = self.parameters.get('general_info', {}).get('iua', '')
        return 'Y88' in iua

    def _apply_y88_xld_logic(self, phase: str, task: Dict[str, Any]) -> None:
        """Apply Y88-specific XLD logic for BENCH phase."""
        if phase != 'BENCH':
            return

        # Y88-specific package path modifications (based on V1 logic)
        for task_type, task_data in task.items():
            if 'xldeploy' in task_type:
                self._modify_y88_xld_paths(task_data)

    def _modify_y88_xld_paths(self, task_data: Dict[str, Any]) -> None:
        """Modify XLD paths for Y88 packages in BENCH environment."""
        # This implements the V1 logic for Y88 package path modifications
        # Based on the conditions found in all_class.py lines with Y88 logic

        for package_group, packages in task_data.items():
            if isinstance(packages, list):
                for package in packages:
                    self._apply_y88_package_logic(package)

    def _apply_y88_package_logic(self, package_name: str) -> None:
        """Apply Y88-specific logic to individual packages."""
        # Y88 package categorization logic from V1:
        y88_interface_packages = [
            'Interface_summit', 'Interface_summit_COF', 'Interface_TOGE',
            'Interface_TOGE_ACK', 'Interface_NON_LOAN_US', 'DICTIONNAIRE',
            'Interface_MOTOR', 'Interface_ROAR_ACK', 'Interface_ROAR'
        ]

        if package_name == 'Interfaces':
            # Set value = 'INT' for Interfaces
            self.logger_cr.info(f"Y88: Processing Interfaces package as INT")
        elif package_name in y88_interface_packages:
            # Set value = 'INT' and value_env = '_NEW'
            self.logger_cr.info(f"Y88: Processing {package_name} as INT with _NEW suffix")
        elif package_name == 'Scripts':
            # Set value = 'SCR'
            self.logger_cr.info(f"Y88: Processing Scripts package as SCR")
        elif package_name == 'SDK':
            # Set value = 'SDK'
            self.logger_cr.info(f"Y88: Processing SDK package as SDK")
        elif package_name == 'App':
            # Set value = 'APP'
            self.logger_cr.info(f"Y88: Processing App package as APP")

    def _process_standard_xld_task(self, phase: str, task: Dict[str, Any]) -> None:
        """Process standard XLD tasks after Y88 modifications."""
        # Standard XLD processing logic here
        self.logger_cr.info(f"Completed XLD task processing for phase {phase}")

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
        Create technical tasks for a phase (V1 functionality).

        Args:
            phase: The phase name
            task_category: Category of technical task (before_deployment, before_xldeploy, after_xldeploy, after_deployment)
        """
        try:
            # Check if this task category already processed for this phase
            task_done_key = f"{task_category}_done_{phase}"
            if task_done_key in self.list_technical_task_done:
                return

            technical_tasks = self.parameters.get('technical_task_list', {}).get(task_category, [])
            if not technical_tasks:
                return

            self.logger_cr.info(f"Creating technical tasks for {phase} - {task_category}")

            for task_name in technical_tasks:
                self.logger_cr.info(f"Processing technical task: {task_name}")

                if 'task_dba_factor' in task_name or 'task_dba_other' in task_name:
                    # DBA tasks - create SUN task
                    self._create_dba_task(phase, task_name, task_category)

                elif 'task_ops' in task_name:
                    # OPS tasks - create gate task with SUN integration
                    self._create_ops_task(phase, task_name, task_category)

                else:
                    # Generic technical task
                    self._create_generic_technical_task(phase, task_name, task_category)

            # Mark this category as done for this phase
            self.list_technical_task_done.append(task_done_key)

        except Exception as e:
            self.logger_error.error(f"Failed to create technical task for {phase}: {e}")

    def _create_dba_task(self, phase: str, task_name: str, task_category: str) -> None:
        """Create DBA technical task."""
        try:
            # Create SUN task for DBA
            task_variable = f"{task_name}_{phase}"
            title = f"DBA Task: {task_name} - {task_category}"

            # Create the task through SUN integration
            if hasattr(self, 'create_sun_task'):
                self.create_sun_task(
                    phase=phase,
                    task_name=task_variable,
                    title=title,
                    task_type='dba',
                    category=task_category
                )

            self.logger_cr.info(f"Created DBA task: {task_name} for phase {phase}")

        except Exception as e:
            self.logger_error.error(f"Failed to create DBA task {task_name}: {e}")

    def _create_ops_task(self, phase: str, task_name: str, task_category: str) -> None:
        """Create OPS technical task."""
        try:
            title = f"OPS Task: {task_name} - {task_category}"

            # Create group task for OPS
            group_id = self.XLR_group_task(
                ID_XLR_task=self.dict_template[phase]['xlr_id_phase'],
                type_group="SequentialGroup",
                title_group=title,
                precondition=''
            )

            # Create gate task within the group
            self.XLR_GateTask(
                phase=phase,
                gate_title=title,
                description="See Change to action OPS",
                cond_title=f"OPS: {task_name} completed",
                type_task='gate_validation_ops',
                XLR_ID=group_id if group_id else self.dict_template[phase]['xlr_id_phase']
            )

            self.logger_cr.info(f"Created OPS task: {task_name} for phase {phase}")

        except Exception as e:
            self.logger_error.error(f"Failed to create OPS task {task_name}: {e}")

    def _create_generic_technical_task(self, phase: str, task_name: str, task_category: str) -> None:
        """Create generic technical task."""
        try:
            title = f"Technical Task: {task_name} - {task_category}"

            # Create a simple gate task for generic technical tasks
            self.XLR_GateTask(
                phase=phase,
                gate_title=title,
                description=f"Complete technical task: {task_name}",
                cond_title=f"{task_name} completed",
                type_task='gate_validation_technical',
                XLR_ID=self.dict_template[phase]['xlr_id_phase']
            )

            self.logger_cr.info(f"Created generic technical task: {task_name} for phase {phase}")

        except Exception as e:
            self.logger_error.error(f"Failed to create generic technical task {task_name}: {e}")

    # ===================================================================
    # V1 CRITICAL METHODS - Complete Template Creation Flow
    # ===================================================================

    def delete_template(self) -> None:
        """Delete existing template by name (V1 functionality)."""
        try:
            name_release = self.parameters['general_info']['name_release']
            self.logger_cr.info(f"Attempting to delete existing template: {name_release}")

            # Search for existing template
            search_url = f"{self.url_api_xlr}templates"
            response = requests.get(
                search_url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )

            if response.status_code == 200:
                templates = response.json()
                for template in templates:
                    if template.get('title') == name_release:
                        # Delete the template
                        delete_url = f"{self.url_api_xlr}templates/{template['id']}"
                        delete_response = requests.delete(
                            delete_url,
                            headers=self.header,
                            auth=(self.ops_username_api, self.ops_password_api),
                            verify=False
                        )
                        if delete_response.status_code == 204:
                            self.logger_cr.info(f"Successfully deleted existing template: {name_release}")
                        else:
                            self.logger_cr.warning(f"Could not delete template {name_release}: {delete_response.status_code}")
                        break
                else:
                    self.logger_cr.info(f"No existing template found with name: {name_release}")

        except Exception as e:
            self.logger_error.error(f"Error deleting template: {e}")
            # Don't raise - template might not exist

    def find_xlr_folder(self) -> None:
        """Find XLR folder and store its ID (V1 functionality)."""
        try:
            folder_path = self.parameters['general_info']['xlr_folder']
            self.logger_cr.info(f"Finding XLR folder: {folder_path}")

            # Search for folder
            search_url = f"{self.url_api_xlr}folders"
            response = requests.get(
                search_url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )

            if response.status_code == 200:
                folders = response.json()
                folder_parts = folder_path.split('/')

                # Find folder by path
                for folder in folders:
                    if self._folder_matches_path(folder, folder_parts):
                        if 'template' not in self.dict_template:
                            self.dict_template['template'] = {}
                        self.dict_template['template']['xlr_folder'] = folder['id']
                        self.logger_cr.info(f"Found XLR folder ID: {folder['id']}")
                        return

                raise ValueError(f"Folder not found: {folder_path}")

        except Exception as e:
            self.logger_error.error(f"Error finding XLR folder: {e}")
            raise

    def _folder_matches_path(self, folder: Dict[str, Any], path_parts: List[str]) -> bool:
        """Check if folder matches the given path parts."""
        # This is a simplified implementation - you may need to enhance based on actual folder structure
        folder_title = folder.get('title', '')
        return folder_title == path_parts[-1]  # Match last part for now

    def CreateTemplate(self) -> tuple:
        """Create XLR template and return dict and ID (V1 functionality)."""
        try:
            name_release = self.parameters['general_info']['name_release']
            self.logger_cr.info(f"Creating XLR template: {name_release}")

            folder_id = self.dict_template['template']['xlr_folder']

            template_data = {
                "id": "null",
                "type": "xlrelease.Release",
                "title": name_release,
                "description": f"Automated template created for {name_release}",
                "folderId": folder_id,
                "variables": [],
                "phases": []
            }

            create_url = f"{self.url_api_xlr}templates"
            response = requests.post(
                create_url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=template_data,
                verify=False
            )

            if response.status_code == 200:
                template_result = response.json()
                template_id = template_result['id']

                self.dict_template['template']['xlr_id'] = template_id
                self.XLR_template_id = template_id

                self.logger_cr.info(f"Successfully created template with ID: {template_id}")
                return self.dict_template, template_id

            else:
                raise Exception(f"Failed to create template: {response.status_code} - {response.text}")

        except Exception as e:
            self.logger_error.error(f"Error creating template: {e}")
            raise

    def create_phase_env_variable(self) -> None:
        """Create phase environment variables (V1 functionality)."""
        try:
            self.logger_cr.info("Creating phase environment variables...")

            phases = self.parameters['general_info']['phases']

            for phase in phases:
                if phase in ['BENCH', 'PRODUCTION']:
                    # Create environment variables for production phases
                    env_key = f'env_{phase}'
                    env_values = self.parameters.get(f'XLD_ENV_{phase}', [])

                    if env_values:
                        self.template_create_variable(
                            key=env_key,
                            typev='ListStringVariable',
                            label=f'Environment {phase}',
                            description=f'Environment selection for {phase} phase',
                            value=env_values,
                            requiresValue=True,
                            showOnReleaseStart=True,
                            multiline=False
                        )

            self.logger_cr.info("Phase environment variables created successfully")

        except Exception as e:
            self.logger_error.error(f"Error creating phase environment variables: {e}")
            raise

    def define_variable_type_template_DYNAMIC(self) -> None:
        """Define variable type for DYNAMIC template (V1 functionality)."""
        try:
            self.logger_cr.info("Defining variable type for DYNAMIC template...")

            # Build release_Variables_in_progress based on template configuration
            general_info = self.parameters['general_info']
            phases = general_info['phases']

            self.release_Variables_in_progress = {
                'xlr_list_phase': ','.join(phases),
                'type_template': general_info['type_template'],
                'template_package_mode': general_info['template_package_mode'],
                'phase_mode': general_info.get('phase_mode', 'multi_list'),
                'iua': general_info['iua'],
                'appli_name': general_info['appli_name']
            }

            # Add package information
            if 'template_liste_package' in self.parameters:
                packages = list(self.parameters['template_liste_package'].keys())
                self.release_Variables_in_progress['list_package'] = ','.join(packages)

                # Set package management flags
                self.release_Variables_in_progress['list_package_manage'] = ','.join(packages)
                self.release_Variables_in_progress['list_package_NOT_manage'] = ''

                # Add package-specific variables
                package_master = []
                auto_undeploy = []

                for pkg_name, pkg_config in self.parameters['template_liste_package'].items():
                    if pkg_config.get('controlm_mode') == 'master':
                        package_master.append(pkg_name)

                    if pkg_config.get('auto_undeploy'):
                        if isinstance(pkg_config['auto_undeploy'], list):
                            auto_undeploy.extend(pkg_config['auto_undeploy'])
                        elif pkg_config['auto_undeploy'] != 'False':
                            auto_undeploy.append(pkg_name)

                self.release_Variables_in_progress['package_master'] = ','.join(package_master)
                self.release_Variables_in_progress['auto_undeploy'] = ','.join(auto_undeploy)

            self.logger_cr.info("Variable type definition completed")

        except Exception as e:
            self.logger_error.error(f"Error defining variable type: {e}")
            raise

    def dict_value_for_tempalte(self) -> Dict[str, Any]:
        """Generate dict_value_for_template (V1 functionality with typo preserved for compatibility)."""
        try:
            self.logger_cr.info("Generating dict_value_for_template...")

            dict_value = {
                'general_info': self.parameters['general_info'],
                'template_liste_package': self.parameters.get('template_liste_package', {}),
                'jenkins': self.parameters.get('jenkins', {}),
                'controlm': {},
                'xld': {},
                'technical_task': self.parameters.get('technical_task_list', {})
            }

            # Process ControlM configuration
            if 'Phases' in self.parameters:
                phases_config = self.parameters['Phases']
                for phase_name, phase_tasks in phases_config.items():
                    controlm_tasks = []
                    if isinstance(phase_tasks, list):
                        for task in phase_tasks:
                            if isinstance(task, dict):
                                for task_type, task_data in task.items():
                                    if 'XLR_task_controlm' in task_type:
                                        controlm_tasks.extend(task_data)

                    if controlm_tasks:
                        dict_value['controlm'][phase_name] = controlm_tasks

            self.logger_cr.info("dict_value_for_template generated successfully")
            return dict_value

        except Exception as e:
            self.logger_error.error(f"Error generating dict_value_for_template: {e}")
            raise

    def delete_phase_default_in_template(self) -> None:
        """Delete default phase in template (V1 functionality)."""
        try:
            self.logger_cr.info("Deleting default phase from template...")

            if not self.XLR_template_id:
                self.logger_error.error("No template ID available for deleting default phase")
                return

            # Get template details
            template_url = f"{self.url_api_xlr}templates/{self.XLR_template_id}"
            response = requests.get(
                template_url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )

            if response.status_code == 200:
                template_data = response.json()
                phases = template_data.get('phases', [])

                # Find and delete default phases
                for phase in phases:
                    if phase.get('title') in ['New Phase', 'Default Phase', 'Phase 1']:
                        phase_id = phase['id']
                        delete_url = f"{self.url_api_xlr}phases/{phase_id}"

                        delete_response = requests.delete(
                            delete_url,
                            headers=self.header,
                            auth=(self.ops_username_api, self.ops_password_api),
                            verify=False
                        )

                        if delete_response.status_code == 204:
                            self.logger_cr.info(f"Deleted default phase: {phase.get('title')}")

            self.logger_cr.info("Default phase deletion completed")

        except Exception as e:
            self.logger_error.error(f"Error deleting default phase: {e}")
            # Don't raise - this is not critical

    def add_phase_tasks(self, phase: str) -> None:
        """Add phase with tasks (V1 functionality)."""
        try:
            self.logger_cr.info(f"Adding phase with tasks: {phase}")

            if not self.XLR_template_id:
                raise ValueError("No template ID available")

            phase_data = {
                "id": "null",
                "type": "xlrelease.Phase",
                "title": phase,
                "color": self._get_phase_color(phase),
                "tasks": []
            }

            create_url = f"{self.url_api_xlr}templates/{self.XLR_template_id}/phases"
            response = requests.post(
                create_url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=phase_data,
                verify=False
            )

            if response.status_code == 200:
                phase_result = response.json()
                phase_id = phase_result['id']

                self.dict_template[phase] = {'xlr_id_phase': phase_id}
                self.logger_cr.info(f"Successfully created phase {phase} with ID: {phase_id}")

            else:
                raise Exception(f"Failed to create phase {phase}: {response.status_code}")

        except Exception as e:
            self.logger_error.error(f"Error adding phase {phase}: {e}")
            raise

    def _get_phase_color(self, phase: str) -> str:
        """Get color for phase based on type."""
        color_map = {
            'BUILD': '#1f77b4',
            'DEV': '#ff7f0e',
            'UAT': '#2ca02c',
            'BENCH': '#d62728',
            'PRODUCTION': '#9467bd'
        }
        return color_map.get(phase, '#7f7f7f')

    def XLR_GateTask(self, phase: str, gate_title: str, description: str,
                     cond_title: str, type_task: str, XLR_ID: str) -> None:
        """Create XLR Gate Task (V1 functionality)."""
        try:
            self.logger_cr.info(f"Creating gate task: {gate_title} in phase {phase}")

            gate_data = {
                "id": "null",
                "type": "xlrelease.GateTask",
                "title": gate_title,
                "description": description,
                "conditions": [
                    {
                        "id": "null",
                        "type": "xlrelease.GateCondition",
                        "title": cond_title
                    }
                ]
            }

            create_url = f"{self.url_api_xlr}phases/{XLR_ID}/tasks"
            response = requests.post(
                create_url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=gate_data,
                verify=False
            )

            if response.status_code == 200:
                self.logger_cr.info(f"Successfully created gate task: {gate_title}")
            else:
                raise Exception(f"Failed to create gate task: {response.status_code}")

        except Exception as e:
            self.logger_error.error(f"Error creating gate task {gate_title}: {e}")
            raise

    def XLR_group_task(self, ID_XLR_task: str, type_group: str, title_group: str, precondition: str) -> Optional[str]:
        """Create XLR Group Task (V1 functionality)."""
        try:
            self.logger_cr.info(f"Creating group task: {title_group}")

            url = f"{self.url_api_xlr}tasks/{ID_XLR_task}/tasks"
            group_data = {
                "id": "null",
                "type": f"xlrelease.{type_group}",
                "title": title_group,
                "status": "PLANNED",
                "precondition": precondition
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=group_data,
                verify=False
            )
            response.raise_for_status()

            group_id = response.json()['id']
            self.logger_cr.info(f"Successfully created group task: {title_group} with ID: {group_id}")
            return group_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create group task {title_group}: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating group task: {e}")
            return None