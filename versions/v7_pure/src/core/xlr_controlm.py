#!/usr/bin/env python3
"""
XLR ControlM Integration Class - V7 Pure
========================================

ControlM integration for XLR templates.
Provides ControlM job management, resource control, and webhook functionality.
"""

import requests
from typing import Dict, Any
from .xlr_generic import XLRGeneric


class XLRControlm(XLRGeneric):
    """
    ControlM integration class for XLR template operations.

    Provides functionality for:
    - ControlM resource management
    - Job scheduling and control
    - Webhook integrations
    - ControlM-specific task creation
    """

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize ControlM integration."""
        super().__init__(parameters)

        # ControlM Configuration
        self.url_api_controlm = parameters.get('controlm_api_url', 'https://controlm-api.example.com/api/')
        self.CTM_PROD = parameters.get('ctm_prod', 'CTM_PROD')
        self.CTM_BENCH = parameters.get('ctm_bench', 'CTM_BENCH')

    def webhook_controlm_ressource(self, phase: str, grp_id_controlm: str, task: Dict[str, Any]) -> None:
        """Create ControlM resource webhook task."""
        url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.CustomScriptTask",
            "title": f'Change RESSOURCE value {task["name"]}',
            "locked": True,
            "pythonScript": {
                "type": "webhook.JsonWebhook",
                "id": "null",
                "URL": f"{self.url_api_controlm}/resource",
                "method": "POST",
                "body": {
                    "ctm": self.CTM_PROD if task.get('foldername', '').lower().startswith('p') else self.CTM_BENCH,
                    "name": task['name'],
                    "max": int(task['max'])
                },
                "username": f"${{{phase}_username_controlm}}",
                "password": f"${{{phase}_password_controlm}}"
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
            self.logger_detail.debug(f"ControlM resource task created: {task['name']}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating ControlM resource task {task['name']}: {str(e)}")

    def script_jython_date_for_controlm(self, phase: str) -> None:
        """Create Jython script for ControlM date handling."""
        url = f"{self.url_api_xlr}tasks/{self.dict_template[phase]['xlr_id_phase']}/tasks"

        script_content = '''
# Jython script for ControlM date formatting
import java.text.SimpleDateFormat as SimpleDateFormat
import java.util.Date as Date

# Format date for ControlM
date_formatter = SimpleDateFormat("yyyyMMdd")
current_date = date_formatter.format(Date())

# Set release variable
releaseApi.setVariable("controlm_date", current_date)
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": "Format Date for ControlM",
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
            self.logger_detail.debug(f"ControlM date script created for phase: {phase}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating ControlM date script for {phase}: {str(e)}")

    def webhook_controlm_order_folder(self, phase: str, folder_info: Dict[str, Any], grp_id_controlm: str, task: Dict[str, Any]) -> None:
        """Create ControlM order folder webhook task."""
        url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.CustomScriptTask",
            "title": f'Order ControlM Folder {folder_info["name"]}',
            "locked": True,
            "pythonScript": {
                "type": "webhook.JsonWebhook",
                "id": "null",
                "URL": f"{self.url_api_controlm}/run/order",
                "method": "POST",
                "body": {
                    "ctm": self.CTM_PROD if folder_info.get('environment', '').lower() == 'prod' else self.CTM_BENCH,
                    "folder": folder_info['name'],
                    "date": "${controlm_date}"
                },
                "username": f"${{{phase}_username_controlm}}",
                "password": f"${{{phase}_password_controlm}}"
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
            self.logger_detail.debug(f"ControlM order folder task created: {folder_info['name']}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating ControlM order folder task {folder_info['name']}: {str(e)}")

    def XLR_plugin_controlm_OrderFolder(self, folder_info: Dict[str, Any], grp_id_controlm: str) -> None:
        """Create ControlM order folder plugin task."""
        url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

        task_data = {
            "id": "null",
            "type": "controlm.OrderFolder",
            "title": f'Order Folder {folder_info["name"]}',
            "locked": True,
            "server": "${controlm_server}",
            "folder": folder_info['name'],
            "date": "${controlm_date}",
            "username": "${controlm_username}",
            "password": "${controlm_password}"
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
            self.logger_detail.debug(f"ControlM plugin order folder task created: {folder_info['name']}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating ControlM plugin task {folder_info['name']}: {str(e)}")

    def XLR_plugin_controlm_WaitJobStatusById(self, foldername: str, statusToWaitFor: str, grp_id_controlm: str) -> None:
        """Create ControlM wait job status task."""
        url = f"{self.url_api_xlr}tasks/{grp_id_controlm}/tasks"

        task_data = {
            "id": "null",
            "type": "controlm.WaitForJobStatus",
            "title": f'Wait for {foldername} - {statusToWaitFor}',
            "locked": True,
            "server": "${controlm_server}",
            "jobName": foldername,
            "statusToWaitFor": statusToWaitFor,
            "username": "${controlm_username}",
            "password": "${controlm_password}",
            "pollInterval": 30,
            "timeout": 3600
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
            self.logger_detail.debug(f"ControlM wait job status task created: {foldername}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating ControlM wait job task {foldername}: {str(e)}")

    def add_task_sun_controlm_resource(self, phase: str, type_task: str, title: str) -> None:
        """Add ControlM resource task for SUN integration."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": title,
            "locked": True,
            "script": f'''
# ControlM Resource Management Script
# Type: {type_task}
# Phase: {phase}

from com.xebialabs.xlrelease.api.model import Variable

# Add your ControlM resource management logic here
print("Managing ControlM resource: {title}")
'''
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
            self.logger_detail.debug(f"ControlM resource task added: {title}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error adding ControlM resource task {title}: {str(e)}")

    def add_task_sun_controlm(self, phase: str, type_task: str, foldername: str, cases: str, idtask: str) -> None:
        """Add ControlM task for SUN integration."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"ControlM {type_task} - {foldername}",
            "locked": True,
            "script": f'''
# ControlM Task Script
# Folder: {foldername}
# Cases: {cases}
# Task ID: {idtask}

from com.xebialabs.xlrelease.api.model import Variable

# Add your ControlM task logic here
print("Executing ControlM task: {foldername}")
'''
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
            self.logger_detail.debug(f"ControlM task added: {foldername}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error adding ControlM task {foldername}: {str(e)}")