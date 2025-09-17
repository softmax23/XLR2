#!/usr/bin/env python3
"""
XLR SUN Integration Class - V7 Pure
===================================

SUN (Service Update Notification) integration for XLR templates.
Provides SUN task management, change tracking, and incident handling.
"""

import requests
from typing import Dict, Any, List
from .xlr_generic import XLRGeneric


class XLRSun(XLRGeneric):
    """
    SUN integration class for XLR template operations.

    Provides functionality for:
    - SUN change management
    - Incident creation and tracking
    - State management
    - DBA factor handling
    """

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize SUN integration."""
        super().__init__(parameters)

        # SUN Configuration
        self.url_api_sun = parameters.get('sun_api_url', 'https://sun-api.example.com/api/')

    def parameter_phase_sun(self, phase: str) -> Dict[str, Any]:
        """Configure SUN parameters for a phase."""
        sun_config = {
            'phase': phase,
            'environment': phase.lower(),
            'change_required': True if phase in ['PRODUCTION', 'BENCH'] else False,
            'dba_approval': True if phase in ['PRODUCTION'] else False
        }

        self.logger_detail.debug(f"SUN parameters configured for phase: {phase}")
        return sun_config

    def add_phase_sun(self, phase: str) -> None:
        """Add SUN-specific phase configuration."""
        if phase not in self.dict_template:
            self.dict_template[phase] = {}

        # Configure SUN parameters for this phase
        sun_params = self.parameter_phase_sun(phase)
        self.dict_template[phase]['sun_config'] = sun_params

        self.logger_cr.info(f"SUN phase configuration added for: {phase}")

    def add_task_date_for_sun_change(self, phase: str) -> None:
        """Add task to set date for SUN change."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        script_content = '''
# Set date for SUN change
import java.text.SimpleDateFormat as SimpleDateFormat
import java.util.Date as Date

# Format date for SUN system
date_formatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
current_date = date_formatter.format(Date())

# Set release variable
releaseApi.setVariable("sun_change_date", current_date)
print("SUN change date set to: " + current_date)
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": "Set Date for SUN Change",
            "locked": True,
            "script": script_content
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
            self.logger_detail.debug(f"SUN date task created for phase: {phase}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN date task for {phase}: {str(e)}")

    def add_task_sun_change(self, phase: str, sun_bench: str) -> None:
        """Add SUN change task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.CustomScriptTask",
            "title": f"Create SUN Change - {sun_bench}",
            "locked": True,
            "pythonScript": {
                "type": "webhook.JsonWebhook",
                "id": "null",
                "URL": f"{self.url_api_sun}/change/create",
                "method": "POST",
                "body": {
                    "title": f"Release {self.parameters['general_info']['name_release']}",
                    "description": f"Deployment for {phase} environment",
                    "environment": sun_bench,
                    "scheduled_date": "${sun_change_date}",
                    "requester": "${release.owner}"
                },
                "username": f"${{{phase}_username_sun}}",
                "password": f"${{{phase}_password_sun}}"
            }
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
            self.logger_detail.debug(f"SUN change task created for {phase} - {sun_bench}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN change task for {phase}: {str(e)}")

    def change_state_sun(self, phase: str, state: str) -> None:
        """Change SUN state."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.CustomScriptTask",
            "title": f"Change SUN State to {state}",
            "locked": True,
            "pythonScript": {
                "type": "webhook.JsonWebhook",
                "id": "null",
                "URL": f"{self.url_api_sun}/change/state",
                "method": "PUT",
                "body": {
                    "change_id": "${sun_change_id}",
                    "new_state": state,
                    "comment": f"State changed to {state} via XLR"
                },
                "username": f"${{{phase}_username_sun}}",
                "password": f"${{{phase}_password_sun}}"
            }
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
            self.logger_detail.debug(f"SUN state change task created: {state}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN state change task: {str(e)}")

    def sun_create_inc(self, name_phase: str, state: str, env: str, task: str, spec: str) -> None:
        """Create SUN incident."""
        if name_phase not in self.dict_template:
            self.logger_error.error(f"Phase {name_phase} not found in template")
            return

        phase_id = self.dict_template[name_phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.CustomScriptTask",
            "title": f"Create SUN Incident - {task}",
            "locked": True,
            "pythonScript": {
                "type": "webhook.JsonWebhook",
                "id": "null",
                "URL": f"{self.url_api_sun}/incident/create",
                "method": "POST",
                "body": {
                    "title": f"Incident for {task}",
                    "description": f"Environment: {env}, State: {state}, Spec: {spec}",
                    "priority": "Medium",
                    "environment": env,
                    "phase": name_phase
                },
                "username": f"${{{name_phase}_username_sun}}",
                "password": f"${{{name_phase}_password_sun}}"
            }
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
            self.logger_detail.debug(f"SUN incident creation task created: {task}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN incident task: {str(e)}")

    def add_task_sun_dba_factor(self, task: str, phase: str, precondition: str) -> None:
        """Add SUN DBA factor task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.UserInputTask",
            "title": f"DBA Approval - {task}",
            "locked": True,
            "precondition": precondition,
            "description": f"DBA approval required for: {task}",
            "variables": [
                {
                    "key": f"dba_approval_{task.lower().replace(' ', '_')}",
                    "type": "xlrelease.BooleanVariable",
                    "label": f"DBA Approval for {task}",
                    "description": f"Please approve DBA factor for {task}",
                    "value": False,
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
            self.logger_detail.debug(f"SUN DBA factor task created: {task}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN DBA factor task: {str(e)}")

    def XLRSun_close_sun(self, phase: str) -> None:
        """Close SUN change."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.CustomScriptTask",
            "title": "Close SUN Change",
            "locked": True,
            "pythonScript": {
                "type": "webhook.JsonWebhook",
                "id": "null",
                "URL": f"{self.url_api_sun}/change/close",
                "method": "PUT",
                "body": {
                    "change_id": "${sun_change_id}",
                    "status": "CLOSED",
                    "resolution": "SUCCESSFUL",
                    "comments": "Change completed successfully via XLR"
                },
                "username": f"${{{phase}_username_sun}}",
                "password": f"${{{phase}_password_sun}}"
            }
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
            self.logger_detail.debug(f"SUN close task created for phase: {phase}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN close task for {phase}: {str(e)}")

    def XLRSun_task_close_sun_task(self, task_to_close: str, title: str, id_task: str, type_task: str, phase: str) -> None:
        """Close specific SUN task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        script_content = f'''
# Close SUN Task Script
# Task to close: {task_to_close}
# Title: {title}
# ID: {id_task}
# Type: {type_task}

from com.xebialabs.xlrelease.api.model import Variable

# Add your SUN task closure logic here
print("Closing SUN task: {task_to_close}")
releaseApi.setVariable("sun_task_closed", True)
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"Close SUN Task - {title}",
            "locked": True,
            "script": script_content
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
            self.logger_detail.debug(f"SUN task close created: {title}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating SUN task close: {str(e)}")

    def XLRSun_sun_template_create_variable(self, key: str, typev: str, label: str, description: str, value: str, requiresValue: bool, showOnReleaseStart: bool, multiline: bool) -> None:
        """Create SUN-specific template variable."""
        # Use parent class method with SUN prefix
        sun_key = f"sun_{key}" if not key.startswith('sun_') else key
        self.template_create_variable(
            sun_key, typev, label, description, value,
            requiresValue, showOnReleaseStart, multiline
        )
        self.logger_detail.debug(f"SUN variable created: {sun_key}")

    def XLRSun_creation_technical_task(self, phase: str, cat_technicaltask: str) -> None:
        """Create SUN technical task."""
        # Simplified implementation for V7 Pure
        technical_tasks = {
            'before_deployment': 'Pre-deployment technical validation',
            'before_xldeploy': 'Pre-XLDeploy technical preparation',
            'after_xldeploy': 'Post-XLDeploy technical validation',
            'after_deployment': 'Post-deployment technical verification'
        }

        task_title = technical_tasks.get(cat_technicaltask, f'Technical Task - {cat_technicaltask}')

        if f"{cat_technicaltask}_done_{phase}" not in self.list_technical_sun_task_done:
            self.logger_cr.info(f"ON PHASE: CREATE_CHANGE_{phase.upper()} --- Add SUN task: 'Technical Task': {cat_technicaltask}")

            # Create technical task variable
            self.template_create_variable(
                key=f"sun_technical_{cat_technicaltask}_{phase}",
                typev="StringVariable",
                label=f"SUN Technical {cat_technicaltask.replace('_', ' ').title()}",
                description=f"SUN technical task for {cat_technicaltask} in {phase}",
                value="",
                requiresValue=False,
                showOnReleaseStart=False,
                multiline=False
            )

            # Create the technical task
            self.creation_technical_task(phase, cat_technicaltask)

            # Mark as done
            self.list_technical_sun_task_done.append(f"{cat_technicaltask}_done_{phase}")
            self.count_task += 10

    def update_variable(self, key: str, value: str, requiresValue: bool, showOnReleaseStart: bool) -> None:
        """Update or create variable."""
        # Simplified implementation - create variable
        self.template_create_variable(
            key=key,
            typev="StringVariable",
            label=key.replace('_', ' ').title(),
            description=f"Updated variable for {key}",
            value=value,
            requiresValue=requiresValue,
            showOnReleaseStart=showOnReleaseStart,
            multiline=False
        )