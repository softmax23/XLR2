"""
XLRTaskScript - Custom script task generation and management

This module contains the enhanced XLRTaskScript class that inherits from XLRBase
for custom script generation functionality.
"""

from .xlr_base import XLRBase

class XLRTaskScript(XLRBase):
    """
    Custom script task generation and management for XLR templates.

    This class inherits from XLRBase and provides specialized functionality
    for creating various types of script tasks within XLR templates.

    Key features:
    - Variable manipulation and calculation
    - Dynamic content generation
    - Jenkins integration and parameter passing
    - Date/time formatting for external systems
    - Release metadata management
    - Custom business logic execution

    No longer requires composition with XLRGeneric - inherits all base
    functionality directly from XLRBase.
    """

    def __init__(self, parameters):
        """
        Initialize XLRTaskScript with configuration parameters and base XLR functionality.

        Args:
            parameters (dict): YAML configuration containing template settings

        Inherits all core XLR operations from XLRBase and stores configuration
        for creating context-appropriate script tasks.
        """
        super().__init__()
        self.parameters = parameters

    def script_jython_get_user_from_task(self, phase, task_id):
        """
        Create Jython script to extract user information from tasks.

        Args:
            phase (str): Phase name
            task_id (str): Task ID to extract user from

        Creates a script that retrieves user information from completed
        tasks for auditing and notification purposes.

        Uses inherited XLR API methods from XLRBase.
        """
        url_user_script = self.url_api_xlr + 'tasks/' + task_id + '/tasks'

        script_content = """
        ##script_jython_get_user_from_task
        import urllib2
        import base64
        import json

        # Get user information from completed task
        task_id = '""" + task_id + """'
        api_url = '""" + self.url_api_xlr + """tasks/' + task_id

        password = release.passwordVariableValues['${ops_password_api}']
        login = '${ops_username_api}'
        auth_header = 'Basic ' + base64.b64encode(login + ':' + password)

        request = urllib2.Request(api_url)
        request.add_header('Authorization', auth_header)
        response = urllib2.urlopen(request)
        task_data = json.loads(response.read())

        if 'owner' in task_data:
            releaseVariables['task_owner'] = task_data['owner']
            print('Task owner: ' + task_data['owner'])
        """

        try:
            response = requests.post(url_user_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Get User from Task',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Get User from Task'")
        except Exception as e:
            self.logger_error.error("Error creating user extraction script: " + str(e))
            sys.exit(0)

    def script_jython_put_value_version(self, phase):
        """
        Create Jython script to set version values from branch names.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that extracts version information from Git branch
        names and sets appropriate release variables.

        Uses inherited XLR API methods from XLRBase.
        """
        version_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Version Processing',
            ''
        )

        script_content = """
        ##script_jython_put_value_version
        import re

        # Extract version from branch name
        branch_name = releaseVariables.get('branch_name', '')

        # Pattern to extract version: feature/v1.2.3 -> 1.2.3
        version_pattern = r'[vV]?(\d+\.\d+\.\d+)'
        match = re.search(version_pattern, branch_name)

        if match:
            version = match.group(1)
            releaseVariables['extracted_version'] = version
            print('Extracted version: ' + version)

            # Set package-specific versions
            for package in ['App', 'Scripts', 'SDK', 'Interfaces']:
                var_name = package + '_version'
                if var_name in releaseVariables:
                    releaseVariables[var_name] = version
                    print('Set ' + var_name + ' to: ' + version)
        else:
            print('No version found in branch name: ' + branch_name)
        """

        url_script = self.url_api_xlr + 'tasks/' + version_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Extract Version from Branch',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Extract Version from Branch'")
        except Exception as e:
            self.logger_error.error("Error creating version extraction script: " + str(e))
            sys.exit(0)

    def script_jython_define_variable_release(self, phase):
        """
        Create Jython script to define release-specific variables.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that sets up release-specific variables including
        dates, environment information, and custom metadata.

        Uses inherited XLR API methods from XLRBase.
        """
        variable_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Release Variable Definition',
            ''
        )

        script_content = """
        ##script_jython_define_variable_release
        from java.util import Date
        from java.text import SimpleDateFormat

        # Set current date if Date variable exists
        if 'Date' in releaseVariables:
            current_date = Date()
            date_format = SimpleDateFormat('yyyy-MM-dd HH:mm:ss')
            formatted_date = date_format.format(current_date)
            releaseVariables['Date'] = formatted_date
            print('Set release date: ' + formatted_date)

        # Set additional release metadata
        releaseVariables['release_environment'] = '""" + phase + """'
        releaseVariables['release_timestamp'] = str(current_date.getTime())

        print('Release environment: """ + phase + """')
        print('Release timestamp: ' + releaseVariables['release_timestamp'])
        """

        url_script = self.url_api_xlr + 'tasks/' + variable_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Define Release Variables',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Define Release Variables'")
        except Exception as e:
            self.logger_error.error("Error creating release variable script: " + str(e))
            sys.exit(0)

    def task_xlr_if_name_from_jenkins(self, phase):
        """
        Create task to handle package names provided by Jenkins.

        Args:
            phase (str): Phase name where the task is created

        Creates a script that processes package names and versions
        provided by Jenkins jobs for dynamic package deployment.

        Uses inherited XLR task creation methods from XLRBase.
        """
        jenkins_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Jenkins Name Processing',
            ''
        )

        script_content = """
        ##task_xlr_if_name_from_jenkins
        # Process package information from Jenkins
        jenkins_packages = {}

        # Check for Jenkins-provided package variables
        for var_name in releaseVariables.keys():
            if var_name.startswith('VARIABLE_XLR_ID_') and var_name.endswith('_version'):
                package_name = var_name.replace('VARIABLE_XLR_ID_', '').replace('_version', '')
                jenkins_value = releaseVariables[var_name]

                if jenkins_value:
                    jenkins_packages[package_name] = jenkins_value
                    print('Jenkins provided ' + package_name + ': ' + jenkins_value)

                    # Set the main package version variable
                    main_var = package_name + '_version'
                    if main_var in releaseVariables:
                        releaseVariables[main_var] = jenkins_value
                        print('Updated ' + main_var + ' to: ' + jenkins_value)

        # Store processed package information
        releaseVariables['jenkins_packages'] = str(jenkins_packages)
        print('Processed Jenkins packages: ' + str(jenkins_packages))
        """

        url_script = self.url_api_xlr + 'tasks/' + jenkins_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Process Jenkins Package Names',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Process Jenkins Package Names'")
        except Exception as e:
            self.logger_error.error("Error creating Jenkins name processing script: " + str(e))
            sys.exit(0)

    # Additional script methods would be implemented here
    # Each using inherited functionality from XLRBase instead of composition