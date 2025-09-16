"""
XLR Task Script module for managing script tasks and automation.

This module provides the XLRTaskScript class which handles script task
creation, version management, and automation scripts in XLR.
"""

import logging
from typing import Dict, Any, Optional, List, Union

import requests
import urllib3

from .xlr_generic import XLRGeneric, XLRGenericError

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRTaskScriptError(Exception):
    """Custom exception for XLRTaskScript operations."""
    pass


class XLRTaskScript:
    """
    XLR Task Script class for handling script tasks and automation.

    This class provides methods for creating various script tasks,
    version management scripts, and automation utilities.
    """

    def __init__(self):
        """Initialize XLRTaskScript with required dependencies."""
        self.xlr_generic = XLRGeneric()
        self.logger_cr = logging.getLogger('xlr.script.create')
        self.logger_error = logging.getLogger('xlr.script.error')

        # XLR API attributes
        self.url_api_xlr = None
        self.header = {'Content-Type': 'application/json'}
        self.ops_username_api = None
        self.ops_password_api = None
        self.dict_template = {}

    def task_xlr_transformation_variable_branch(self, phase: str) -> bool:
        """
        Create a task for branch variable transformation.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_branch_transformation_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Transform Branch Variables",
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

            self.logger_cr.info(f"Created branch transformation task for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create branch transformation task: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating branch transformation task: {e}")
            return False

    def get_num_version_from_jenkins_skip(self, phase: str) -> bool:
        """
        Create a script to get version number from Jenkins with skip logic.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_jenkins_version_skip_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Get Version from Jenkins (Skip Mode)",
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

            self.logger_cr.info(f"Created Jenkins version skip script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Jenkins version skip script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Jenkins version skip script: {e}")
            return False

    def get_num_version_from_jenkins_static(self, phase: str) -> bool:
        """
        Create a script to get version number from Jenkins in static mode.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_jenkins_version_static_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Get Version from Jenkins (Static Mode)",
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

            self.logger_cr.info(f"Created Jenkins version static script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Jenkins version static script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Jenkins version static script: {e}")
            return False

    def get_num_version_from_jenkins(self, phase: str) -> bool:
        """
        Create a script to get version number from Jenkins.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_jenkins_version_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Get Version from Jenkins",
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

            self.logger_cr.info(f"Created Jenkins version script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Jenkins version script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Jenkins version script: {e}")
            return False

    def reevaluate_variable_package_version(self, phase: str) -> bool:
        """
        Create a script to reevaluate package version variables.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_reevaluate_version_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Reevaluate Package Version Variables",
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

            self.logger_cr.info(f"Created reevaluate version script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create reevaluate version script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating reevaluate version script: {e}")
            return False

    def get_version_of_the_package_listbox(self, phase: str) -> bool:
        """
        Create a script to get package version for listbox mode.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_package_version_listbox_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Get Package Version (Listbox Mode)",
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

            self.logger_cr.info(f"Created package version listbox script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create package version listbox script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating package version listbox script: {e}")
            return False

    def script_jython_define_variable_release(self, phase: str) -> bool:
        """
        Create a script to define release variables.

        Args:
            phase: The deployment phase

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_define_variable_release_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Define Release Variables",
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

            self.logger_cr.info(f"Created define variable release script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create define variable release script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating define variable release script: {e}")
            return False

    def script_jython_xld_undeploy_revaluate_version_package(
        self,
        phase: str,
        step: str
    ) -> bool:
        """
        Create a script for XLD undeploy and version reevaluation.

        Args:
            phase: The deployment phase
            step: The step identifier (BEFORE/AFTER)

        Returns:
            True if successful, False otherwise
        """
        try:
            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRTaskScriptError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            script_content = self._get_xld_undeploy_reevaluate_script(step)

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": f"XLD Undeploy and Reevaluate Versions ({step})",
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

            self.logger_cr.info(f"Created XLD undeploy reevaluate script for phase {phase} ({step})")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create XLD undeploy reevaluate script: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating XLD undeploy reevaluate script: {e}")
            return False

    def _get_branch_transformation_script(self) -> str:
        """Get the Jython script for branch variable transformation."""
        return (
            "##task_xlr_transformation_variable_branch\\n"
            "import re\\n"
            "# Transform branch variables based on configuration\\n"
            "branch_var = releaseVariables.get('git_branch', 'master')\\n"
            "if branch_var.startswith('feature/'):\\n"
            "    releaseVariables['transformed_branch'] = branch_var.replace('feature/', 'feat-')\\n"
            "elif branch_var.startswith('release/'):\\n"
            "    releaseVariables['transformed_branch'] = branch_var.replace('release/', 'rel-')\\n"
            "else:\\n"
            "    releaseVariables['transformed_branch'] = branch_var\\n"
            "print(f'Branch transformed from {branch_var} to {releaseVariables[\"transformed_branch\"]}')\\n"
        )

    def _get_jenkins_version_skip_script(self) -> str:
        """Get the Jython script for Jenkins version with skip logic."""
        return (
            "##get_num_version_from_jenkins_skip\\n"
            "import json\\n"
            "import urllib2\\n"
            "# Get version from Jenkins with skip logic\\n"
            "jenkins_url = releaseVariables.get('jenkins_url', '')\\n"
            "job_name = releaseVariables.get('jenkins_job', '')\\n"
            "if releaseVariables.get('skip_jenkins_build', False):\\n"
            "    releaseVariables['package_version'] = releaseVariables.get('manual_version', '1.0.0')\\n"
            "    print('Using manual version due to skip flag')\\n"
            "else:\\n"
            "    # Fetch from Jenkins API\\n"
            "    api_url = f'{jenkins_url}/job/{job_name}/lastSuccessfulBuild/api/json'\\n"
            "    try:\\n"
            "        response = urllib2.urlopen(api_url)\\n"
            "        data = json.loads(response.read())\\n"
            "        releaseVariables['package_version'] = data.get('displayName', '1.0.0')\\n"
            "    except Exception as e:\\n"
            "        print(f'Error fetching Jenkins version: {e}')\\n"
            "        releaseVariables['package_version'] = '1.0.0'\\n"
        )

    def _get_jenkins_version_static_script(self) -> str:
        """Get the Jython script for Jenkins version in static mode."""
        return (
            "##get_num_version_from_jenkins_static\\n"
            "import json\\n"
            "# Static version retrieval from Jenkins\\n"
            "static_version = releaseVariables.get('static_version', '1.0.0')\\n"
            "releaseVariables['package_version'] = static_version\\n"
            "print(f'Using static version: {static_version}')\\n"
        )

    def _get_jenkins_version_script(self) -> str:
        """Get the Jython script for Jenkins version retrieval."""
        return (
            "##get_num_version_from_jenkins\\n"
            "import json\\n"
            "import urllib2\\n"
            "# Get latest version from Jenkins\\n"
            "jenkins_url = releaseVariables.get('jenkins_url', '')\\n"
            "job_name = releaseVariables.get('jenkins_job', '')\\n"
            "api_url = f'{jenkins_url}/job/{job_name}/lastSuccessfulBuild/api/json'\\n"
            "try:\\n"
            "    response = urllib2.urlopen(api_url)\\n"
            "    data = json.loads(response.read())\\n"
            "    build_number = data.get('number', 1)\\n"
            "    releaseVariables['package_version'] = f'1.0.{build_number}'\\n"
            "    print(f'Retrieved version from Jenkins: {releaseVariables[\"package_version\"]}')\\n"
            "except Exception as e:\\n"
            "    print(f'Error fetching Jenkins version: {e}')\\n"
            "    releaseVariables['package_version'] = '1.0.0'\\n"
        )

    def _get_reevaluate_version_script(self) -> str:
        """Get the Jython script for reevaluating package versions."""
        return (
            "##reevaluate_variable_package_version\\n"
            "import json\\n"
            "# Reevaluate package version variables\\n"
            "packages = releaseVariables.get('list_package', '').split(',')\\n"
            "for package in packages:\\n"
            "    if package.strip():\\n"
            "        version_var = f'{package}_version'\\n"
            "        if version_var in releaseVariables:\\n"
            "            current_version = releaseVariables[version_var]\\n"
            "            # Add logic to reevaluate version\\n"
            "            print(f'Reevaluated {package}: {current_version}')\\n"
        )

    def _get_package_version_listbox_script(self) -> str:
        """Get the Jython script for package version in listbox mode."""
        return (
            "##get_version_of_the_package_listbox\\n"
            "import json\\n"
            "# Get package versions for listbox selection\\n"
            "selected_packages = []\\n"
            "for key, value in releaseVariables.items():\\n"
            "    if key.startswith('package_') and value:\\n"
            "        package_name = key.replace('package_', '')\\n"
            "        selected_packages.append(package_name)\\n"
            "releaseVariables['selected_packages'] = ','.join(selected_packages)\\n"
            "print(f'Selected packages: {selected_packages}')\\n"
        )

    def _get_define_variable_release_script(self) -> str:
        """Get the Jython script for defining release variables."""
        return (
            "##script_jython_define_variable_release\\n"
            "import json\\n"
            "# Define release-specific variables\\n"
            "release_info = {\\n"
            "    'release_id': '${release.id}',\\n"
            "    'release_title': '${release.title}',\\n"
            "    'release_owner': '${release.owner}',\\n"
            "    'current_phase': '${currentPhase.title}'\\n"
            "}\\n"
            "for key, value in release_info.items():\\n"
            "    releaseVariables[key] = value\\n"
            "print('Release variables defined successfully')\\n"
        )

    def _get_xld_undeploy_reevaluate_script(self, step: str) -> str:
        """Get the Jython script for XLD undeploy and version reevaluation."""
        return (
            f"##script_jython_xld_undeploy_revaluate_version_package_{step}\\n"
            "import json\\n"
            f"# XLD undeploy and version reevaluation for {step} step\\n"
            "packages_to_undeploy = releaseVariables.get('auto_undeploy', '').split(',')\\n"
            "for package in packages_to_undeploy:\\n"
            "    if package.strip():\\n"
            f"        version_var = f'version_deployed_{{package}}_{step}'\\n"
            "        if version_var in releaseVariables:\\n"
            "            version = releaseVariables[version_var]\\n"
            f"            print(f'Processing {{package}} with version {{version}} for {step}')\\n"
            "            # Add XLD undeploy logic here\\n"
        )

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

        self.logger_cr.info("XLR connection configured for script task operations")