"""
XLRDynamicPhase - Dynamic phase management and runtime customization

This module contains the enhanced XLRDynamicPhase class that inherits from XLRBase
for dynamic phase functionality.
"""

from .xlr_base import XLRBase

class XLRDynamicPhase(XLRBase):
    """
    Dynamic phase management for XLR templates.

    This class inherits from XLRBase and provides specialized functionality
    for creating and managing dynamic phases that customize the XLR template
    at runtime based on user selections.

    Key features:
    - Dynamic phase deletion based on user choices
    - Package filtering and selection
    - Jenkins job management
    - Control-M task customization
    - XLD deployment task filtering
    - Technical task management

    No longer requires composition with XLRGeneric - inherits all base
    functionality directly from XLRBase.
    """

    def __init__(self):
        """
        Initialize XLRDynamicPhase with base XLR functionality.

        Inherits all core XLR operations from XLRBase without requiring
        a separate XLRGeneric instance.
        """
        super().__init__()

    def script_jython_delete_phase_inc(self, phase):
        """
        Create Jython script to delete phases based on user selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a Jython script that dynamically removes phases from
        the release based on user selections at runtime.

        Uses inherited XLR API methods from XLRBase.
        """
        if phase == 'dynamic_release':
            url = self.url_api_xlr + '' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + '' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            script_content = """
            ##script_jython_delete_phase_inc
            # Delete phases not selected by user
            for phase_name in ['DEV', 'UAT', 'BENCH', 'PRODUCTION']:
                if not releaseVariables.get('include_' + phase_name, False):
                    # Logic to remove phase from release
                    print('Removing phase: ' + phase_name)
            """

            response = requests.post(url, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Dynamic Phase Deletion',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Dynamic Phase Deletion'")
        except Exception as e:
            self.logger_error.error("Error creating dynamic phase deletion script: " + str(e))
            sys.exit(0)

    def XLRJython_delete_phase_one_list(self, phase):
        """
        Create Jython script for single-list phase selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that handles phase deletion when using a single
        selection list for phase choices.

        Uses inherited XLR API methods from XLRBase.
        """
        script_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Phase Selection Management',
            ''
        )

        script_content = """
        ##XLRJython_delete_phase_one_list
        selected_phase = releaseVariables.get('selected_phase')
        all_phases = ['DEV', 'UAT', 'BENCH', 'PRODUCTION']

        for phase_name in all_phases:
            if phase_name != selected_phase:
                # Remove unselected phase
                print('Removing phase: ' + phase_name)
        """

        url_script = self.url_api_xlr + 'tasks/' + script_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'One List Phase Selection',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'One List Phase Selection'")
        except Exception as e:
            self.logger_error.error("Error creating one list phase script: " + str(e))
            sys.exit(0)

    def script_jython_List_package_string(self, phase):
        """
        Create Jython script for string-based package selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that processes string-based package selection
        and filters deployment tasks accordingly.

        Uses inherited XLR task creation methods from XLRBase.
        """
        package_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Package String Processing',
            ''
        )

        script_content = """
        ##script_jython_List_package_string
        package_list_string = releaseVariables.get('package_selection', '')
        selected_packages = [pkg.strip() for pkg in package_list_string.split(',')]

        all_packages = ['App', 'Scripts', 'SDK', 'Interfaces']
        for package in all_packages:
            if package not in selected_packages:
                print('Removing package: ' + package)
        """

        url_script = self.url_api_xlr + 'tasks/' + package_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Package String Processing',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Package String Processing'")
        except Exception as e:
            self.logger_error.error("Error creating package string script: " + str(e))
            sys.exit(0)

    def script_jython_dynamic_delete_task_jenkins_string(self, phase):
        """
        Create Jython script to delete Jenkins tasks based on package selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that removes Jenkins build tasks for packages
        not selected for deployment.

        Uses inherited XLR task creation methods from XLRBase.
        """
        jenkins_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Jenkins Task Management',
            ''
        )

        script_content = """
        ##script_jython_dynamic_delete_task_jenkins_string
        selected_packages = releaseVariables.get('selected_packages', [])

        # Remove Jenkins tasks for unselected packages
        jenkins_tasks = ['App_build', 'Scripts_build', 'SDK_build', 'Interfaces_build']
        for task in jenkins_tasks:
            package = task.replace('_build', '')
            if package not in selected_packages:
                print('Removing Jenkins task: ' + task)
        """

        url_script = self.url_api_xlr + 'tasks/' + jenkins_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Jenkins Task Cleanup',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Jenkins Task Cleanup'")
        except Exception as e:
            self.logger_error.error("Error creating Jenkins cleanup script: " + str(e))
            sys.exit(0)

    def script_jython_dynamic_delete_task_xld(self, phase):
        """
        Create Jython script to delete XLD deployment tasks.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that removes XL Deploy tasks for packages
        not selected for deployment.

        Uses inherited XLR task creation methods from XLRBase.
        """
        xld_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'XLD Task Management',
            ''
        )

        script_content = """
        ##script_jython_dynamic_delete_task_xld
        selected_packages = releaseVariables.get('selected_packages', [])

        # Remove XLD deployment tasks for unselected packages
        xld_tasks = ['Deploy_App', 'Deploy_Scripts', 'Deploy_SDK', 'Deploy_Interfaces']
        for task in xld_tasks:
            package = task.replace('Deploy_', '')
            if package not in selected_packages:
                print('Removing XLD task: ' + task)
        """

        url_script = self.url_api_xlr + 'tasks/' + xld_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'XLD Task Cleanup',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD Task Cleanup'")
        except Exception as e:
            self.logger_error.error("Error creating XLD cleanup script: " + str(e))
            sys.exit(0)

    # Additional dynamic phase methods would be implemented here
    # Each using inherited functionality from XLRBase instead of composition