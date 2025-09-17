#!/usr/bin/env python3
"""
XLR Task Script Management Class - V7 Pure
==========================================

Task and script management for XLR templates.
Provides script execution, task creation, and automation functionality.
"""

import requests
from typing import Dict, Any, List
from .xlr_generic import XLRGeneric


class XLRTaskScript(XLRGeneric):
    """
    Task and script management class for XLR template operations.

    Provides functionality for:
    - Script task creation
    - Automation scripts
    - Variable management
    - User input tasks
    """

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize task script management."""
        super().__init__(parameters)

    def script_jython(self, phase: str, task_id: str) -> None:
        """Create Jython script task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        script_content = f'''
# Jython Script for Task ID: {task_id}
# Phase: {phase}

from com.xebialabs.xlrelease.api.model import Variable
from java.util import Date

# Add your Jython logic here
print("Executing Jython script for task: {task_id}")

# Example: Set a release variable
releaseApi.setVariable("script_execution_time", str(Date()))
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"Jython Script - {task_id}",
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
            self.logger_detail.debug(f"Jython script task created: {task_id}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating Jython script task {task_id}: {str(e)}")

    def launch_script_windows(self, phase: str, grp_id_task: str, sunscript_windows_item: Dict[str, Any], type_userinput: str, index: int) -> None:
        """Launch Windows script task."""
        url = f"{self.url_api_xlr}tasks/{grp_id_task}/tasks"

        script_name = sunscript_windows_item.get('name', f'windows_script_{index}')
        script_path = sunscript_windows_item.get('path', 'C:\\scripts\\default.bat')
        script_args = sunscript_windows_item.get('arguments', '')

        task_data = {
            "id": "null",
            "type": "remoteScript.PowerShell",
            "title": f"Windows Script - {script_name}",
            "locked": True,
            "script": f"& '{script_path}' {script_args}",
            "host": f"${{{phase}_windows_host}}",
            "username": f"${{{phase}_windows_username}}",
            "password": f"${{{phase}_windows_password}}"
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
            self.logger_detail.debug(f"Windows script task created: {script_name}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating Windows script task {script_name}: {str(e)}")

    def launch_script_linux(self, phase: str, grp_id_task: str, sunscript_linux_item: Dict[str, Any], type_userinput: str, index: int) -> None:
        """Launch Linux script task."""
        url = f"{self.url_api_xlr}tasks/{grp_id_task}/tasks"

        script_name = sunscript_linux_item.get('name', f'linux_script_{index}')
        script_path = sunscript_linux_item.get('path', '/scripts/default.sh')
        script_args = sunscript_linux_item.get('arguments', '')

        task_data = {
            "id": "null",
            "type": "remoteScript.Unix",
            "title": f"Linux Script - {script_name}",
            "locked": True,
            "script": f"{script_path} {script_args}",
            "host": f"${{{phase}_linux_host}}",
            "username": f"${{{phase}_linux_username}}",
            "password": f"${{{phase}_linux_password}}"
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
            self.logger_detail.debug(f"Linux script task created: {script_name}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating Linux script task {script_name}: {str(e)}")

    def script_jython_get_user_from_task(self, phase: str, task_id: str) -> None:
        """Create Jython script to get user from task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        script_content = f'''
# Get User from Task Script
# Task ID: {task_id}
# Phase: {phase}

from com.xebialabs.xlrelease.api.model import Variable

# Get current user information
current_user = getCurrentUser()
task_owner = getTaskOwner("{task_id}")

# Set release variables
releaseApi.setVariable("current_user", current_user)
releaseApi.setVariable("task_owner", task_owner)

print("Current user: " + current_user)
print("Task owner: " + task_owner)
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"Get User from Task - {task_id}",
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
            self.logger_detail.debug(f"Get user script task created: {task_id}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating get user script task {task_id}: {str(e)}")

    def script_jython_define_variable_release(self, phase: str) -> None:
        """Create Jython script to define release variables."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        script_content = f'''
# Define Release Variables Script
# Phase: {phase}

from com.xebialabs.xlrelease.api.model import Variable
from java.util import Date

# Define common release variables
release_name = release.getTitle()
release_id = release.getId()
current_phase = "{phase}"
execution_date = str(Date())

# Set release variables
releaseApi.setVariable("release_name", release_name)
releaseApi.setVariable("release_id", release_id)
releaseApi.setVariable("current_phase", current_phase)
releaseApi.setVariable("execution_date", execution_date)

print("Release variables defined for phase: {phase}")
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"Define Release Variables - {phase}",
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
            self.logger_detail.debug(f"Define variables script task created for phase: {phase}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating define variables script task for {phase}: {str(e)}")

    def get_num_version_from_jenkins(self, phase: str) -> None:
        """Create task to get version number from Jenkins."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        task_data = {
            "id": "null",
            "type": "jenkins.Build",
            "title": "Get Version from Jenkins",
            "locked": True,
            "jobName": "${jenkins_job_name}",
            "server": f"${{{phase}_jenkins_server}}",
            "username": f"${{{phase}_jenkins_username}}",
            "password": f"${{{phase}_jenkins_password}}",
            "buildParameters": {
                "ACTION": "GET_VERSION"
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
            self.logger_detail.debug(f"Jenkins version task created for phase: {phase}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating Jenkins version task for {phase}: {str(e)}")

    def python_technical_task(self, phase: str) -> None:
        """Create Python technical task."""
        if phase not in self.dict_template:
            self.logger_error.error(f"Phase {phase} not found in template")
            return

        phase_id = self.dict_template[phase]['xlr_id_phase']
        url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

        script_content = f'''
# Python Technical Task
# Phase: {phase}

import os
import json
from datetime import datetime

# Technical task logic
print("Executing Python technical task for phase: {phase}")

# Example: Environment validation
env_vars = os.environ
print(f"Environment variables count: {{len(env_vars)}}")

# Set task completion status
task_status = {{"phase": "{phase}", "status": "completed", "timestamp": datetime.now().isoformat()}}
print(f"Task status: {{json.dumps(task_status)}}")
'''

        task_data = {
            "id": "null",
            "type": "xlrelease.ScriptTask",
            "title": f"Python Technical Task - {phase}",
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
            self.logger_detail.debug(f"Python technical task created for phase: {phase}")
        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Error creating Python technical task for {phase}: {str(e)}")