"""
XLR Dynamic Phase module for managing dynamic phase operations.

This module provides the XLRDynamicPhase class which handles dynamic phase
creation, deletion, and management in XLR templates.
"""

import logging
from typing import Dict, Any, Optional, List

import requests
import urllib3

from .xlr_generic import XLRGeneric, XLRGenericError

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XLRDynamicPhaseError(Exception):
    """Custom exception for XLRDynamicPhase operations."""
    pass


class XLRDynamicPhase:
    """
    XLR Dynamic Phase class for handling dynamic phase operations.

    This class provides methods for creating, deleting, and managing
    phases dynamically in XLR templates based on user selections.
    """

    def __init__(self):
        """Initialize XLRDynamicPhase with required dependencies."""
        self.xlr_generic = XLRGeneric()
        self.logger_cr = logging.getLogger('xlr.dynamic.create')
        self.logger_error = logging.getLogger('xlr.dynamic.error')

        # XLR API attributes
        self.url_api_xlr = None
        self.header = {'Content-Type': 'application/json'}
        self.ops_username_api = None
        self.ops_password_api = None
        self.dict_template = {}

    def script_jython_delete_phase_inc(self, phase: str) -> bool:
        """
        Create a Jython script to delete unused phases from release.

        Args:
            phase: The phase where the deletion script should be added

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine the URL based on phase type
            if phase == 'dynamic_release':
                url = f"{self.url_api_xlr}tasks/{self.dict_template[phase]['xlr_id_phase']}/tasks"
            else:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[f'CREATE_CHANGE_{phase}']['xlr_id_phase']}/tasks"

            script_content = self._get_delete_phase_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "RELEASE DELETE PHASE",
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

            if response.content and 'id' in response.json():
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'RELEASE DELETE PHASE'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create delete phase script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating delete phase script for {phase}: {e}")
            return False

    def script_jython_define_xld_prefix_new(self, phase: str) -> bool:
        """
        Create a Jython script to define XLD prefix for multi-bench environments.

        Args:
            phase: The phase where the script should be added

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine the URL based on phase type
            if phase in ['DEV', 'dynamic_release']:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[phase]['xlr_id_phase']}/tasks"
            else:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[f'CREATE_CHANGE_{phase}']['xlr_id_phase']}/tasks"

            script_content = self._get_xld_prefix_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "XLD VARIABLE: Definition Value if MULTIBENCH",
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

            if response.content and 'id' in response.json():
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'XLD VARIABLE: Definition Value if MULTIBENCH'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create XLD prefix script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating XLD prefix script for {phase}: {e}")
            return False

    def script_jython_dynamic_delete_task_controlm(self, phase: str) -> bool:
        """
        Create a Jython script to delete Control-M tasks with master option.

        Args:
            phase: The phase where the script should be added

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine the URL based on phase type
            if phase in ['DEV', 'dynamic_release']:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[phase]['xlr_id_phase']}/tasks"
            else:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[f'CREATE_CHANGE_{phase}']['xlr_id_phase']}/tasks"

            script_content = self._get_delete_controlm_task_script()

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "DELETE CONTROL-M TASK WITH MASTER OPTION",
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

            if response.content and 'id' in response.json():
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'DELETE CONTROL-M TASK WITH MASTER OPTION'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M delete script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M delete script for {phase}: {e}")
            return False

    def jython_delete_jenkins_task_if_xld_package(self, phase: str) -> bool:
        """
        Create a Jython script to delete Jenkins tasks if XLD package conditions are met.

        Args:
            phase: The phase where the script should be added

        Returns:
            True if successful, False otherwise
        """
        try:
            script_content = self._get_delete_jenkins_task_script()

            phase_id = self.dict_template.get(phase, {}).get('xlr_id_phase')
            if not phase_id:
                raise XLRDynamicPhaseError(f"No phase ID found for phase {phase}")

            url = f"{self.url_api_xlr}tasks/{phase_id}/tasks"

            task_data = {
                "id": None,
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "Delete Jenkins tasks if XLD package check fails",
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

            self.logger_cr.info(f"Created Jenkins deletion script for phase {phase}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Jenkins deletion script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Jenkins deletion script for {phase}: {e}")
            return False

    def create_dynamic_phase(
        self,
        phase_name: str,
        phase_config: Dict[str, Any],
        parent_id: str
    ) -> Optional[str]:
        """
        Create a dynamic phase in XLR.

        Args:
            phase_name: Name of the phase to create
            phase_config: Configuration for the phase
            parent_id: Parent template/release ID

        Returns:
            Phase ID if successful, None otherwise
        """
        try:
            url = f"{self.url_api_xlr}phases"

            phase_data = {
                "id": None,
                "type": "xlrelease.Phase",
                "title": phase_name,
                "status": "PLANNED",
                "releaseId": parent_id,
                "color": phase_config.get('color', '#00875A'),
                "description": phase_config.get('description', f"Dynamic phase for {phase_name}")
            }

            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=phase_data,
                verify=False
            )
            response.raise_for_status()

            phase_id = response.json().get('id')
            self.logger_cr.info(f"Created dynamic phase: {phase_name}")

            return phase_id

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create dynamic phase {phase_name}: {e}")
            return None
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating dynamic phase {phase_name}: {e}")
            return None

    def delete_dynamic_phase(self, phase_id: str) -> bool:
        """
        Delete a dynamic phase from XLR.

        Args:
            phase_id: ID of the phase to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.url_api_xlr}phases/{phase_id}"

            response = requests.delete(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                verify=False
            )
            response.raise_for_status()

            self.logger_cr.info(f"Deleted dynamic phase: {phase_id}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to delete dynamic phase {phase_id}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error deleting dynamic phase {phase_id}: {e}")
            return False

    def _get_delete_phase_script(self) -> str:
        """Get the Jython script for deleting phases."""
        return (
            "##script_jython_delete_phase_inc\\n"
            "import json\\n"
            "releaseVariables['Release_Email_requester'] = userApi.getUser('${release.owner}').email\\n"
            "def delete_phase(phase_name):\\n"
            "    xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase_name, '${release.id}')\\n"
            "    if len(xlr_id_phase_to_delete) != 0:\\n"
            "        phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\\n"
            "list_phase = []\\n"
            "for phase in ${dict_value_for_template}['template_liste_phase']:\\n"
            "    if not releaseVariables[phase]:\\n"
            "        if 'PRODUCTION' in phase:\\n"
            "            list_phase.append('PRODUCTION')\\n"
            "        elif 'BENCH' in phase:\\n"
            "            list_phase.append('BENCH')\\n"
            "            if 'BUILD' in ${dict_value_for_template}['template_liste_phase']:\\n"
            "                list_phase.append('BUILD')\\n"
            "for phase in list_phase:\\n"
            "    delete_phase(phase)\\n"
        )

    def _get_xld_prefix_script(self) -> str:
        """Get the Jython script for XLD prefix definition."""
        return (
            "##script_jython_define_xld_prefix_new\\n"
            "import json\\n"
            "# In case of two BENCH environments, determine special values for ENV CONTROLM and XLD variables\\n"
            "# Check if there is a key in variable 'release_Variables_in_progress[list_env_BENCH]'\\n"
            "# Value should be type '<XLD_VALUE_ENV_1>;<PREFIX_LETTER>,<XLD_VALUE_ENV_2>;<PREFIX_LETTER>'\\n"
            "# Example: MCO;Q,PRJ;B\\n"
            "for bench_value in ${release_Variables_in_progress}['list_env_BENCH'].split(','):\\n"
            "    if releaseVariables['env_BENCH'] == bench_value.split(';')[0]:\\n"
            "        if ';' not in bench_value:\\n"
            "            releaseVariables['controlm_prefix_BENCH'] = 'B'\\n"
            "        else:\\n"
            "            releaseVariables['controlm_prefix_BENCH'] = bench_value.split(';')[1]\\n"
            "    else:\\n"
            "        print('Error in definition Prefix BENCH')\\n"
            "if 'BENCH' in releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'].split(','):\\n"
            "    releaseVariables['BENCH_Y88'] = releaseVariables['env_BENCH'].split('_')[0]\\n"
        )

    def _get_delete_controlm_task_script(self) -> str:
        """Get the Jython script for deleting Control-M tasks."""
        return (
            "##script_jython_dynamic_delete_task_controlm\\n"
            "import json\\n"
            "def delete_task(phase, title):\\n"
            "    tasks_to_delete = taskApi.searchTasksByTitle(title, phase, '${release.id}')\\n"
            "    for task_id in tasks_to_delete:\\n"
            "        taskApi.deleteTask(str(task_id))\\n"
            "# Process deletion based on master options\\n"
            "if releaseVariables.get('master_option_enabled', False):\\n"
            "    for phase in ['DEV', 'UAT', 'BENCH', 'PRODUCTION']:\\n"
            "        if releaseVariables.get(f'delete_{phase}_controlm', False):\\n"
            "            delete_task(phase, 'Control-M Task')\\n"
        )

    def _get_delete_jenkins_task_script(self) -> str:
        """Get the Jython script for deleting Jenkins tasks."""
        return (
            "##jython_delete_jenkins_task_if_xld_package\\n"
            "import json\\n"
            "def delete_jenkins_task(phase, package_name):\\n"
            "    jenkins_tasks = taskApi.searchTasksByTitle(f'Jenkins Build {package_name}', phase, '${release.id}')\\n"
            "    for task_id in jenkins_tasks:\\n"
            "        taskApi.deleteTask(str(task_id))\\n"
            "# Check XLD package existence and delete Jenkins tasks if needed\\n"
            "for package in ${release_Variables_in_progress}['list_package'].split(','):\\n"
            "    check_var = f'check_xld_{package}'\\n"
            "    if releaseVariables.get(check_var, False) == False:\\n"
            "        delete_jenkins_task('${phase}', package)\\n"
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

        self.logger_cr.info("XLR connection configured for dynamic phase operations")