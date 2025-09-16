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

    def script_jython_List_package_string(self, phase: str) -> bool:
        """
        Create a Jython script to handle package management for string mode templates.

        This script manages packages when template_package_mode is 'string' and validates
        package versions, handling empty values and package selection logic.

        Args:
            phase: The phase where the script should be added

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine the URL based on phase type
            if phase in ['DEV', 'BUILD']:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[phase]['xlr_id_phase']}/tasks"
            elif phase == 'dynamic_release':
                url = f"{self.url_api_xlr}tasks/{self.dict_template[phase]['xlr_id_phase']}/tasks"
            else:
                url = f"{self.url_api_xlr}tasks/{self.dict_template[f'CREATE_CHANGE_{phase}']['xlr_id_phase']}/tasks"

            script_content = self._get_list_package_string_script()

            task_data = {
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "PACKAGE Variable for the RELEASE",
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
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'PACKAGE Variable for the RELEASE'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create package string script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating package string script for {phase}: {e}")
            return False

    def _get_list_package_string_script(self) -> str:
        """
        Get the Jython script content for package string list management.

        Returns:
            The script content as a string
        """
        return """##script_jython_List_package_string
import json,sys
list_package_manage = []
list_package_not_manage = []
list_package_empty = []
for package in releaseVariables['release_Variables_in_progress']['list_package'].split(','):
    if releaseVariables['release_Variables_in_progress']['package_title_choice'] not in releaseVariables[package.encode('utf-8')+'_version']:
        if releaseVariables[package.encode('utf-8')+'_version'] == '':
            list_package_empty.append(package.split(',')[0].encode('utf-8'))
        else:
            list_package_manage.append(package.encode('utf-8'))
    else:
        list_package_not_manage.append(package.encode('utf-8'))

if len(list_package_empty) != 0:
    try:

        print('------   ERROR in declaration   ------')

        print('Empty is not autorized on package value.')
        print('Change value for package : ')
        for package in list_package_empty:
            print(package)
        print('Change value for package : ')
        print('------   ERROR in declaration   ------')

        sys.exit(1)
    except:
        sys.exit(1)

print('Package to manage : ')
for package in list_package_manage:
    print(package)

print('Package NOT to manage : ')
for package in list_package_not_manage:
    print(package)

releaseVariables['release_Variables_in_progress']['list_package_manage'] = ','.join(list_package_manage)
releaseVariables['release_Variables_in_progress']['list_package_NOT_manage'] = ','.join(list_package_not_manage)

print('Update releaseVariables release_Variables_in_progress with list_package_manage : '+ releaseVariables['release_Variables_in_progress']['list_package_manage'])
print('Update releaseVariables release_Variables_in_progress with list_package_NOT_manage : '+ releaseVariables['release_Variables_in_progress']['list_package_NOT_manage'])
"""

    def script_jython_dynamic_delete_task_controlm_multibench(self, phase: str) -> bool:
        """
        Create a Jython script to handle ControlM task cleanup for multi-bench environments.

        This script manages package masters and deletes ControlM tasks based on package
        management logic for multiple bench environments.

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

            script_content = self._get_controlm_multibench_script()

            task_data = {
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI",
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
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create Control-M multibench script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating Control-M multibench script for {phase}: {e}")
            return False

    def _get_controlm_multibench_script(self) -> str:
        """
        Get the Jython script content for ControlM multibench task deletion.

        Returns:
            The script content as a string
        """
        return """##script_jython_dynamic_delete_task_controlm_multibench
import json
def delete_task(phase,title):
    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')
    if len(taskstodelete) != 0:
        taskApi.delete(str(taskstodelete[0]))
        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"'

## Test if in releaseVariables['release_Variables_in_progress']['list_package_manage'] at the start of the release is in the list of releaseVariables['release_Variables_in_progress']['package_master']
## If TRUE, we keep controlm task  associed only to CONTROLM folder link to packages master list
##
## if FALSE( there is no package from 'package_master' list in  'list_package_manage' )
##    so the jython will delete only CONTROLM task link o package define in variable releaseVariables['dict_value_for_template']
##
package_master_active = any(item in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(',') for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))
##
## we loop on each phase define in releaseVariables['release_Variables_in_progress']['xlr_list_phase']
##   we will delete CONTROLM task
for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):
       if phase != 'BUILD' and phase != 'UAT' and phase != 'DEV' and 'CREATE_CHANGE_' not in phase:
           count_titlegroup = 0
           if package_master_active:
               for titlegroup  in releaseVariables['template_list_controlm_'+phase]:
                   listfolder_delete = []
                   listfolder = []
                   for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):
                       listpackfolder = []
                       listfolder.append(item.split('-')[0])
                       for pack in item.split('-')[1:]:
                           listpackfolder.append(pack.encode('utf-8'))
                       check = all(item not in listpackfolder for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))
                       if check:
                           listfolder_delete.append(item.split('-')[0])

                   print("PACKAGE_MASTER_ACTIVE : FOR "+ titlegroup+" --- DELETE : "+ str(listfolder_delete))

                   for folderdelete in listfolder_delete:
                       print("DELETE TASK : 'CONTROLM : "+folderdelete+"'")
                       print(delete_task(phase,'CONTROLM : '+folderdelete))
           else:
               print("NOT PACKAGE_MASTER_ACTIVE")
               for item  in releaseVariables['dict_value_for_template']['controlm']:
                   listfolder = []
                   for listfolder2 in releaseVariables['dict_value_for_template']['controlm'][item].split(','):
                       listfolder.append(listfolder2.split('-')[0])
                   for folderdelete in listfolder:
                       print("DELETE TASK : 'CONTROLM : "+folderdelete+"'")
                       print(delete_task(phase,'CONTROLM : '+folderdelete))
"""

    def script_jython_dynamic_delete_task_xld(self, phase: str) -> bool:
        """
        Create a Jython script to handle XLD task cleanup.

        This script manages XLD task deletion based on package management logic
        and auto-undeploy configurations.

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

            script_content = self._get_xld_delete_script()

            task_data = {
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "DELETE XLD TASK",
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
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'DELETE XLD TASK'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create XLD delete script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating XLD delete script for {phase}: {e}")
            return False

    def script_jython_dynamic_delete_task_xld_Y88(self, phase: str) -> bool:
        """
        Create a Jython script to handle XLD task cleanup for Y88 environments.

        This script includes specific Y88 environment handling with BENCH environment
        configuration and enhanced package management logic.

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

            script_content = self._get_xld_y88_delete_script()

            task_data = {
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": "DELETE XLD TASK",
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
                self.logger_cr.info(f"ON PHASE: {phase.upper()} --- Add task: 'DELETE XLD TASK'")
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger_error.error(f"Failed to create XLD Y88 delete script for {phase}: {e}")
            return False
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating XLD Y88 delete script for {phase}: {e}")
            return False

    def _get_xld_delete_script(self) -> str:
        """
        Get the Jython script content for XLD task deletion.

        Returns:
            The script content as a string
        """
        return """##script_jython_dynamic_delete_task_xld
import json
list_package_to_not_undeploy = []
list_package_package_name_from_jenkins = []
### function to delete a task XLR, it work with name phase and the title of the task
def delete_task(phase,title):
    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')
    if len(taskstodelete) != 0:
        taskApi.delete(str(taskstodelete[0]))
        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"'

if releaseVariables['release_Variables_in_progress']['auto_undeploy'] != '':
   for item in releaseVariables['release_Variables_in_progress']['auto_undeploy'].split(','):
               key = item.split(':')[0]
               value = item.split(':')[1]
               if '-' in value or value != 'yes':
                   valuesplit = value.split('-')
                   for value2 in valuesplit:
                       if value2 in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):
                               list_package_to_not_undeploy.append(key)
               elif value.encode('utf-8') == 'yes':
                               list_package_to_not_undeploy.append(key.encode('utf-8'))
for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):
    if 'BUILD' not in phase:
        for pack in releaseVariables['release_Variables_in_progress']['list_package'].split(','):
               if pack not in list_package_to_not_undeploy:
                   if pack not in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):
                       print(delete_task(phase,'Deploy '+pack.encode('utf-8')))
                       print(delete_task('CREATE_CHANGE_'+phase,'XLD-Deploy '+pack.encode('utf-8')))
        list_package_really_undeploy = []
        for pack in releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(','):
           if pack not in list_package_to_not_undeploy:
                    list_package_really_undeploy.append(pack)
                    print(delete_task(phase,'Undeploy '+pack.encode('utf-8')))
        for pack in releaseVariables['release_Variables_in_progress']['list_package_not_manage'].split(','):
              print(delete_task(phase,'Check XLD package exist '+pack.encode('utf-8')))
              if pack in releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(','):
                list_package_package_name_from_jenkins.append(pack)
        if len(list_package_really_undeploy) == len(releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(',')):
            print(delete_task(phase,'Delete undeploy if necessary'))
            print(delete_task(phase,'Re evaluate version package for undeploy'))
            print(delete_task(phase,'Check Version package in XLD BEFORE'))
        if len(list_package_package_name_from_jenkins) == len(releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(',')):
            print(delete_task(phase,'Check if XLD package exist'))
            print(delete_task(phase,'Delete jenkins task if package ever exist in XLD'))
"""

    def _get_xld_y88_delete_script(self) -> str:
        """
        Get the Jython script content for XLD Y88 task deletion.

        Returns:
            The script content as a string
        """
        return """##script_jython_dynamic_delete_task_xld_Y88
import json
list_package_to_not_undeploy = []
list_package_package_name_from_jenkins = []
### function to delete a task XLR, it work with name phase and the title of the task
def delete_task(phase,title):
    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')
    if len(taskstodelete) != 0:
        taskApi.delete(str(taskstodelete[0]))
        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"'

if 'BENCH' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):
   releaseVariables['BENCH_Y88'] = releaseVariables['env_BENCH']
### Creation of a list 'list_package_to_not_undeploy'
### below the format of the value 'auto_undeploy' in variable XLR 'dict_value_for_template'
### PACKAGE_UNDEPLOY , value of package name to undeploy
### and after the list of package when it must be undeploy
### The value of PACKAGE_UNDEPLOY must be in in key list_auto_undeploy in variable XLR 'dict_value_for_template'
###  in the case below SDK must be undeploy when App is inthe list of package to deploy by the release
### 'auto_undeploy': [
###
###                         'PACKAGE_UNDEPLOY': 'PACKAGE1-PACKAGE2'
###                     ,
###
###                         'SDK': 'App'
###
###                 ]
for item in releaseVariables['release_Variables_in_progress']['auto_undeploy'].split(','):
               key = item.split(':')[0]
               value = item.split(':')[1]
               if '-' in value or value != 'yes':
                   valuesplit = value.split('-')
                   for value2 in valuesplit:
                       if value2 in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):
                               list_package_to_not_undeploy.append(key)
               elif value.encode('utf-8') == 'yes':
                               list_package_to_not_undeploy.append(key.encode('utf-8'))
### on each phase we will delete task XLD specific at the demand
for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):
    if 'BUILD' not in phase:
        for pack in releaseVariables['release_Variables_in_progress']['list_package'].split(','):
               if pack not in list_package_to_not_undeploy:
                   if pack not in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):
                       print(delete_task(phase,'Deploy '+pack.encode('utf-8')))
                       print(delete_task('CREATE_CHANGE_'+phase,'XLD-Deploy '+pack.encode('utf-8')))
        list_package_really_undeploy = []
        for pack in releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(','):
           if pack not in list_package_to_not_undeploy:
                    list_package_really_undeploy.append(pack)
                    print(delete_task(phase,'Undeploy '+pack.encode('utf-8')))
        for pack in releaseVariables['release_Variables_in_progress']['list_package_not_manage'].split(','):
              print(delete_task(phase,'Check XLD package exist '+pack.encode('utf-8')))
              if pack in releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(','):
                list_package_package_name_from_jenkins.append(pack)
        if len(list_package_really_undeploy) == len(releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(',')):
            print(delete_task(phase,'Delete undeploy if necessary'))
            print(delete_task(phase,'Re evaluate version package for undeploy'))
            print(delete_task(phase,'Check Version package in XLD BEFORE'))
        if len(list_package_package_name_from_jenkins) == len(releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(',')):
            print(delete_task(phase,'Check if XLD package exist'))
            print(delete_task(phase,'Delete jenkins task if package ever exist in XLD'))
"""

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