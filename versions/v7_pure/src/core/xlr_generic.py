#!/usr/bin/env python3
"""
XLR Generic Core Class - V7 Pure
===============================

Base class for XLR template operations.
Provides fundamental XLR API interactions and template management.
"""

import os
import sys
import requests
import urllib3
import logging
from typing import Dict, Any

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRGeneric:
    """
    Base class for XLR template operations.

    Provides core functionality for:
    - Template creation and management
    - Variable creation
    - Phase management
    - Task creation
    - API interactions
    """

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize XLR Generic with parameters."""
        self.parameters = parameters
        self.dict_template = {}

        # XLR API Configuration
        self.url_api_xlr = parameters.get('xlr_api_url', 'https://release-pfi.mycloud.intranatixis.com/api/v1/')
        self.ops_username_api = parameters.get('xlr_username', os.getenv('XLR_USERNAME', 'admin'))
        self.ops_password_api = parameters.get('xlr_password', os.getenv('XLR_PASSWORD', 'admin'))

        # Headers for API calls
        self.header = {
            'content-type': 'application/json',
            'Accept': 'application/json'
        }

        # Initialize attributes
        self.XLR_template_id = None
        self.template_url = None
        self.count_task = 10

        # Initialize tracking lists
        self.list_technical_task_done = []
        self.list_technical_sun_task_done = []
        self.list_xlr_group_task_done = []

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging for XLR operations."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # Creation logger
        self.logger_cr = logging.getLogger('xlr_creation')
        self.logger_cr.setLevel(logging.INFO)
        if not self.logger_cr.handlers:
            ch_cr = logging.StreamHandler()
            ch_cr.setFormatter(logging.Formatter(log_format))
            self.logger_cr.addHandler(ch_cr)

        # Detail logger
        self.logger_detail = logging.getLogger('xlr_detail')
        self.logger_detail.setLevel(logging.DEBUG)
        if not self.logger_detail.handlers:
            ch_detail = logging.StreamHandler()
            ch_detail.setFormatter(logging.Formatter(log_format))
            self.logger_detail.addHandler(ch_detail)

        # Error logger
        self.logger_error = logging.getLogger('xlr_error')
        self.logger_error.setLevel(logging.ERROR)
        if not self.logger_error.handlers:
            ch_error = logging.StreamHandler()
            ch_error.setFormatter(logging.Formatter(log_format))
            self.logger_error.addHandler(ch_error)

    def find_xlr_folder(self) -> None:
        """Find XLR folder and update template dictionary."""
        url = f"{self.url_api_xlr}folders/find?byPath={self.parameters['general_info']['xlr_folder']}"

        try:
            response = requests.get(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )

            if "Could not find folder" in str(response.content):
                self.logger_cr.info(f"XLR folder: {self.parameters['general_info']['xlr_folder']} Not found.")
                self.logger_error.error("Detail ERROR")
                self.logger_error.error(f"Error call api: {url}")
                self.logger_error.error(f"The folder: {self.parameters['general_info']['xlr_folder']} doesn't exist")
                sys.exit(0)

            response.raise_for_status()
            self.logger_cr.info(f"XLR folder search: {self.parameters['general_info']['xlr_folder']} found.")

            if 'template' not in self.dict_template:
                try:
                    self.dict_template.update({'template': {'xlr_folder': response.json()['id']}})
                except (TypeError, Exception) as e:
                    self.logger_error.error(f"Update dict_template in error: {url}")
                    self.logger_error.error(str(e))
                    sys.exit(0)
            else:
                try:
                    self.dict_template['template'].update({'xlr_folder': response.json()['id']})
                except (TypeError, Exception) as e:
                    self.logger_error.error(f"Update dict_template in error: {url}")
                    self.logger_error.error(str(e))
                    sys.exit(0)

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error call api: {url}")
            self.logger_error.error("Detail ERROR")
            self.logger_error.error(str(e))
            sys.exit(0)

    def delete_template(self) -> None:
        """Delete existing template if it exists."""
        url_find_template = f"{self.url_api_xlr}templates?title={self.parameters['general_info']['name_release']}"

        try:
            response = requests.get(
                url_find_template,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )

            if "Could not find folder" in str(response.content):
                self.logger_error.error("Detail ERROR")
                self.logger_error.error(f"Error call api: {url_find_template}")
                self.logger_error.error(f"The folder: {self.parameters['general_info']['xlr_folder']} doesn't exist")
                sys.exit(0)

            response.raise_for_status()

            if response.content:
                if len(response.json()) == 0:
                    self.logger_cr.info(f"SEARCH TEMPLATE: No template found with name: {self.parameters['general_info']['name_release']}")
                else:
                    self.logger_cr.info(f"SEARCH TEMPLATE: Template {self.parameters['general_info']['name_release']} found.")

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error call api: {url_find_template}")
            self.logger_error.error("Detail ERROR")
            self.logger_error.error(str(e))
            sys.exit(0)

        count_template = 0
        template_present = 'no'
        template_id_to_delete = None

        for template in response.json():
            if template['title'] == self.parameters['general_info']['name_release']:
                template_present = 'yes'
                template_id_to_delete = template['id']
                count_template += 1

        if template_present == 'yes' and count_template == 1:
            delete_template_url = f"{self.url_api_xlr}templates/{template_id_to_delete}"
            header = {'content-type': 'application/json', 'Accept': 'application/json'}

            try:
                response_delete = requests.delete(
                    delete_template_url,
                    headers=header,
                    auth=(self.ops_username_api, self.ops_password_api),
                    verify=False
                )

                if response_delete.status_code == 204:
                    self.logger_cr.info("DELETE TEMPLATE: DONE")

                response_delete.raise_for_status()

            except requests.exceptions.RequestException as e:
                self.logger_error.error(f"Error call api: {delete_template_url}")
                self.logger_error.error("Detail ERROR")
                self.logger_error.error(str(e))
                sys.exit(0)

        elif count_template > 1:
            self.logger_error.error(f"DELETE TEMPLATE: There is more than one template with name: {self.parameters['general_info']['name_release']}")
            sys.exit(0)
        elif count_template == 0:
            pass

    def CreateTemplate(self) -> tuple:
        """Create the main XLR template."""
        url_createtemplate = f"{self.url_api_xlr}templates/?folderId={self.dict_template['template']['xlr_folder']}"

        try:
            response_createtemplate = requests.post(
                url_createtemplate,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json={
                    "id": None,
                    "type": "xlrelease.Release",
                    "title": self.parameters['general_info']['name_release'],
                    "status": "TEMPLATE",
                    "scheduledStartDate": "2023-03-09T17:56:54.786+01:00",
                    "scriptUsername": self.ops_username_api,
                    "scriptUserPassword": self.ops_password_api
                },
                verify=False
            )

            response_createtemplate.raise_for_status()

            self.XLR_template_id = response_createtemplate.json()['id']

            if 'template' not in self.dict_template:
                try:
                    self.dict_template.update({'template': {'xlr_id': self.XLR_template_id}})
                    self.logger_cr.info(f"CREATE TEMPLATE in XLR FOLDER: {self.parameters['general_info']['xlr_folder']}")
                    self.logger_cr.info(self.parameters['general_info']['name_release'])
                    self.template_url = f'https://release-pfi.mycloud.intranatixis.com/#/templates/{self.XLR_template_id.replace("Applications/", "").replace("/", "-")}'
                except (TypeError, Exception) as e:
                    self.logger_error.error("Update dict_template in error")
                    self.logger_error.error(str(e))
                    sys.exit(0)
            else:
                try:
                    self.dict_template['template'].update({'xlr_id': self.XLR_template_id})
                    self.template_url = f'https://release-pfi.mycloud.intranatixis.com/#/templates/{self.XLR_template_id.replace("Applications/", "").replace("/", "-")}'
                    self.logger_cr.info("")
                    self.logger_cr.info(f"CREATE TEMPLATE In FOLDER XLR: {self.parameters['general_info']['xlr_folder']}")
                    self.logger_cr.info("")
                    self.logger_cr.info(f"                 NAME : {self.parameters['general_info']['name_release']}")
                    self.logger_cr.info(f"                 LINK : {self.template_url}")
                    self.logger_cr.info("")
                except (TypeError, Exception) as e:
                    self.logger_error.error("Update dict_template in error")
                    self.logger_error.error(str(e))
                    sys.exit(0)

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating template: {url_createtemplate}")
            self.logger_error.error(str(e))
            sys.exit(0)

        return self.dict_template, self.XLR_template_id

    def template_create_variable(self, key: str, typev: str, label: str, description: str, value: str, requiresValue: bool, showOnReleaseStart: bool, multiline: bool) -> None:
        """Create a variable in the template."""
        url = f"{self.url_api_xlr}templates/{self.dict_template['template']['xlr_id']}/variables"

        variable_data = {
            "id": None,
            "type": f"xlrelease.{typev}",
            "key": key,
            "requiresValue": requiresValue,
            "showOnReleaseStart": showOnReleaseStart,
            "label": label,
            "description": description,
            "multiline": multiline,
            "value": value
        }

        try:
            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=variable_data,
                verify=False
            )
            response.raise_for_status()
            self.logger_detail.debug(f"Variable created: {key}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating variable {key}: {str(e)}")
            sys.exit(0)

    def XLR_group_task(self, ID_XLR_task: str, type_group: str, title_group: str, precondition: str) -> str:
        """Create a group task in XLR."""
        url = f"{self.url_api_xlr}tasks/{ID_XLR_task}/tasks"

        task_data = {
            "id": "null",
            "type": f"xlrelease.{type_group}",
            "title": title_group,
            "locked": True,
            "precondition": precondition
        }

        try:
            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()
            group_id = response.json()['id']
            self.logger_detail.debug(f"Group task created: {title_group}")
            return group_id
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating group task {title_group}: {str(e)}")
            sys.exit(0)

    def add_task_user_input(self, phase: str, type_userinput: str, link_task_id: str) -> None:
        """Add user input task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.UserInputTask",
            "title": f"User Input - {type_userinput}",
            "locked": True,
            "description": f"Please provide {type_userinput} credentials",
            "variables": [
                {
                    "key": f"{phase}_{type_userinput}_username",
                    "type": "xlrelease.StringVariable",
                    "label": f"{type_userinput.title()} Username",
                    "required": True
                },
                {
                    "key": f"{phase}_{type_userinput}_password",
                    "type": "xlrelease.PasswordStringVariable",
                    "label": f"{type_userinput.title()} Password",
                    "required": True
                }
            ]
        }

        try:
            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()
            self.logger_detail.debug(f"User input task created for {phase} - {type_userinput}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating user input task for {phase}: {str(e)}")

    def create_phase_env_variable(self) -> None:
        """Create phase environment variables."""
        self.logger_cr.info("Creating phase environment variables...")

        for phase in self.parameters['general_info']['phases']:
            # Create environment variable for each phase
            self.template_create_variable(
                key=f"{phase}_environment",
                typev="StringVariable",
                label=f"{phase} Environment",
                description=f"Environment name for {phase} phase",
                value=phase.lower(),
                requiresValue=True,
                showOnReleaseStart=True,
                multiline=False
            )

    def delete_phase_default_in_template(self) -> None:
        """Delete default phase from template."""
        self.logger_cr.info("Deleting default phase...")
        # In V7 Pure, we create phases manually, so no default phase to delete
        self.logger_detail.debug("No default phase to delete in V7 Pure")

    def parameter_phase_task(self, phase: str) -> None:
        """Configure phase task parameters."""
        self.auto_undeploy_done = False

        if phase in ['DEV', 'BUILD', 'UAT']:
            # Simplified logic for V7 Pure - basic phase configuration
            if self.parameters.get('general_info', {}).get('template_package_mode') == 'listbox':
                # Add user input for XLDeploy if needed
                if phase not in self.dict_template or f"{phase}_username_xldeploy" not in str(self.dict_template.get(phase, {})):
                    self.add_task_user_input(
                        phase=phase,
                        type_userinput='xldeploy',
                        link_task_id=f"{self.dict_template['template']['xlr_id']}/{self.dict_template[phase]['xlr_id_phase']}"
                    )

            # Handle Jenkins integration if configured
            if self.parameters.get('jenkins') is not None and phase == 'DEV':
                self.logger_detail.debug(f"Jenkins integration detected for phase: {phase}")
                # Simplified Jenkins handling for V7 Pure

        self.logger_detail.debug(f"Phase task parameters configured for: {phase}")

    def XLR_GateTask(self, phase: str, gate_title: str, description: str, cond_title: str, type_task: str, XLR_ID: str) -> None:
        """Create XLR Gate Task."""
        description = description or ''

        try:
            response = requests.post(
                f"{self.url_api_xlr}tasks/{XLR_ID}/tasks",
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json={
                    "id": "null",
                    "type": "xlrelease.GateTask",
                    "title": gate_title,
                    "description": description,
                },
                verify=False
            )
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info(f"ON PHASE: {phase} --- Add task: 'GATE': {type_task}")

                    # Add condition if specified
                    if cond_title is not None:
                        url_create_condition = f"{self.url_api_xlr}tasks/{response.json()['id']}/conditions"
                        try:
                            response_condition = requests.post(
                                url_create_condition,
                                headers=self.header,
                                auth=(self.ops_username_api, self.ops_password_api),
                                json={
                                    "title": cond_title,
                                    "checked": False,
                                },
                                verify=False
                            )
                            response_condition.raise_for_status()
                        except requests.exceptions.RequestException as e:
                            self.logger_error.error(f"Detail ERROR: ON PHASE: {phase} --- Add task: condition to GATE: {type_task}")
                            self.logger_error.error(f"Error call api: {url_create_condition}")
                            self.logger_error.error(str(e))
                            sys.exit(0)

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Detail ERROR: ON PHASE: {phase} --- Add task: 'GATE': {type_task}")
            self.logger_error.error(f"Error call api: {self.url_api_xlr}tasks/{XLR_ID}/tasks")
            self.logger_error.error(str(e))
            sys.exit(0)

    def add_variable_deliverable_item_showOnReleaseStart(self) -> None:
        """Add deliverable item variables that show on release start."""
        if self.parameters.get('template_liste_package') is not None:
            if len(self.parameters['template_liste_package']) >= 1:
                self.add_variable_showOnReleaseStart(self.parameters['template_liste_package'])

    def add_variable_showOnReleaseStart(self, template_liste_package: Dict[str, Any]) -> None:
        """Add variables that show on release start."""
        for package_name, package_value in template_liste_package.items():
            # Simplified logic for V7 Pure
            if 'BUILD' in self.parameters['general_info']['phases']:
                value_des = 'NO DEPLOY'
            elif self.parameters['general_info'].get('package_mode') == 'generic':
                if 'DEV' in self.parameters['general_info']['phases']:
                    value_des = 'BRANCH NAME'
                else:
                    value_des = '<version>'
            else:
                value_des = 'LATEST'

            # Create variable for package choice
            self.template_create_variable(
                key=f"package_choice_{package_name}",
                typev="StringVariable",
                label=f"Package Choice for {package_name}",
                description=f"Choose deployment option for {package_name}",
                value=value_des,
                requiresValue=True,
                showOnReleaseStart=True,
                multiline=False
            )

    def creation_technical_task(self, phase: str, cat_technicaltask: str) -> None:
        """Create technical task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"Technical Task - {cat_technicaltask}",
            "locked": True,
            "script": f"""
# Technical Task: {cat_technicaltask}
# Phase: {phase}

print("Executing technical task: {cat_technicaltask}")
# Add your technical task logic here
"""
        }

        try:
            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=task_data,
                verify=False
            )
            response.raise_for_status()
            self.logger_detail.debug(f"Technical task created: {cat_technicaltask}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating technical task {cat_technicaltask}: {str(e)}")

    def create_variable_bolean(self, value: str) -> None:
        """Create boolean variable."""
        self.template_create_variable(
            key=value,
            typev="BooleanVariable",
            label=value.replace('_', ' ').title(),
            description=f"Boolean flag for {value}",
            value="false",
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

    def add_phase_tasks(self, phase: str) -> Dict[str, Any]:
        """Add phase to template."""
        url_add_phase_tasks = f"{self.url_api_xlr}phases/{self.XLR_template_id}/phase"

        try:
            response_url_add_phase_tasks = requests.post(
                url_add_phase_tasks,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json={
                    "id": None,
                    "type": "xlrelease.Phase",
                    "flagStatus": "OK",
                    "title": phase,
                    "status": "PLANNED",
                    "color": "#00FF00"
                },
                verify=False
            )

            response_url_add_phase_tasks.raise_for_status()

            if response_url_add_phase_tasks.content:
                if 'id' in response_url_add_phase_tasks.json():
                    self.logger_cr.info(f"       ADD PHASE: {phase}")
                    self.dict_template[phase] = {
                        'xlr_id_phase': response_url_add_phase_tasks.json()["id"],
                        'xlr_id_phase_full': response_url_add_phase_tasks.json()["id"]
                    }
                    self.logger_cr.info(f"               CREATION PHASE NAME: {phase} OK")
                else:
                    self.logger_error.error(f"ERROR on ADD PHASE: {phase}")
                    self.logger_error.error(response_url_add_phase_tasks.content)
                    sys.exit(0)

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Detail ERROR on ADD PHASE: {phase}")
            self.logger_error.error(f"Error call api: {url_add_phase_tasks}")
            self.logger_error.error(str(e))
            sys.exit(0)

        return self.dict_template

    def define_variable_type_template_DYNAMIC(self) -> None:
        """Define dynamic template variables."""
        # Simplified implementation for V7 Pure
        self.logger_detail.debug("Defining dynamic template variables...")

        # Create basic dynamic variables
        dynamic_vars = [
            ("template_mode", "StringVariable", "Template Mode", "Dynamic template mode", "STANDARD"),
            ("deployment_type", "StringVariable", "Deployment Type", "Type of deployment", "STANDARD"),
            ("validation_required", "BooleanVariable", "Validation Required", "Require validation", "true")
        ]

        for var_key, var_type, var_label, var_desc, var_value in dynamic_vars:
            self.template_create_variable(
                key=var_key,
                typev=var_type,
                label=var_label,
                description=var_desc,
                value=var_value,
                requiresValue=False,
                showOnReleaseStart=True,
                multiline=False
            )

        self.logger_detail.debug("Dynamic template variables defined")