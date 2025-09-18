"""
XLRBase - Foundation class for all XLR operations

This module contains the base class that provides core XLR functionality
shared across all specialized classes.
"""

from base64 import b64encode
import os,sys,requests,urllib3,inspect,configparser,json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class XLRBase:
    """
    Base class providing core XLR functionality for all specialized classes.

    This class contains all the fundamental XLR operations that are shared
    across different specialized classes:
    - XLR API communication and authentication
    - Template creation and management
    - Variable creation and management
    - Phase and task management
    - Logging and error handling
    - Folder operations

    All other XLR classes inherit from this base class to avoid code
    duplication and circular dependencies.

    Attributes:
        url_api_xlr (str): XLR API base URL
        header (dict): HTTP headers for API calls
        ops_username_api (str): API username
        ops_password_api (str): API password
        parameters (dict): YAML configuration parameters
        dict_template (dict): Template metadata and IDs
        logger_cr: Creation report logger
        logger_detail: Detailed information logger
        logger_error: Error logger
    """

    def template_create_variable(self, key, typev, label, description, value, requiresValue, showOnReleaseStart, multiline):
        """
        Create a variable in the XLR template.

        Args:
            key (str): Variable name/key
            typev (str): Variable type (StringVariable, PasswordStringVariable, etc.)
            label (str): Display label for the variable
            description (str): Variable description
            value (str): Default value
            requiresValue (bool): Whether value is required at release start
            showOnReleaseStart (bool): Whether to show in release start form
            multiline (bool): Whether to use multiline input

        Creates various types of variables in the XLR template for:
        - Configuration parameters
        - Environment selection
        - Package versions
        - Approval workflow data
        - Runtime customization
        """
        url_create_template_variable = self.url_api_xlr + "templates/" + self.dict_template['template']['xlr_id'] + "/variables"
        try:
            response_create_template_variable = requests.post(url_create_template_variable, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "key": key,
                "type": typev,
                "requiresValue": requiresValue,
                "showOnReleaseStart": showOnReleaseStart,
                "label": label,
                "description": description,
                "multiline": multiline,
                "value": value,
                "valueProvider": None
            }, verify=False)
            response_create_template_variable.raise_for_status()
            if 'id' in response_create_template_variable.json():
                self.logger_cr.info("CREATE VARIABLE : " + key + " , type : " + typev)
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error create variable : " + key)
            self.logger_error.error("Error call api : " + url_create_template_variable)
            self.logger_error.error(e)
            sys.exit(0)

    def CreateTemplate(self):
        """
        Create a new XLR release template.

        Returns:
            tuple: (dict_template, XLR_template_id) containing template metadata

        Creates a new XLR release template in the specified folder with:
        - Template title from configuration
        - TEMPLATE status for reuse
        - Script authentication credentials
        - Proper API authentication

        Raises:
            SystemExit: On template creation failure or API errors
        """
        url_createtemplate = self.url_api_xlr + "templates/?folderId=" + self.dict_template['template']['xlr_folder']
        try:
            response_createtemplate = requests.post(url_createtemplate, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": None,
                "type": "xlrelease.Release",
                "title": self.parameters['general_info']['name_release'],
                "status": "TEMPLATE",
                "scheduledStartDate": "2023-03-09T17:56:54.786+01:00",
                "scriptUsername": self.ops_username_api,
                "scriptUserPassword": self.ops_password_api
            }, verify=False)
            response_createtemplate.raise_for_status()
            if 'template' not in self.dict_template:
                try:
                    self.XLR_template_id = response_createtemplate.json()['id']
                    self.dict_template.update({'template': {'xlr_id': response_createtemplate.json()['id']}})
                    self.logger_cr.info("CREATE TEMPLATE in XLR FOLDER : " + self.parameters['general_info']['xlr_folder'])
                    self.logger_cr.info(self.parameters['general_info']['name_release'])
                    self.template_url = 'https://release-pfi.mycloud.intranatixis.com/#/templates/' + self.XLR_template_id.replace("Applications/", "").replace('/', '-')
                except (TypeError, Exception) as e:
                    self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Update Dico 'dict_template' in error")
                    self.logger_error.error(e)
                    sys.exit(0)
            return self.dict_template, self.XLR_template_id
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error creation template in XLR: " + self.parameters['general_info']['name_release'])
            self.logger_error.error("Error call api : " + url_createtemplate)
            self.logger_error.error(e)
            sys.exit(0)

    def delete_template(self):
        """
        Delete existing XLR template if it exists.

        Searches for and deletes any existing template with the same name
        to ensure clean template creation. This prevents conflicts when
        regenerating templates and ensures the latest configuration is used.

        The deletion is performed by:
        1. Searching for templates by name
        2. Checking template status
        3. Deleting found templates
        4. Logging the deletion operation
        """
        url_search_template = self.url_api_xlr + "templates?title=" + self.parameters['general_info']['name_release']
        try:
            response_search_template = requests.get(url_search_template, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), verify=False)
            response_search_template.raise_for_status()
            if response_search_template.json():
                for template in response_search_template.json():
                    if template['title'] == self.parameters['general_info']['name_release'] and template['status'] == 'TEMPLATE':
                        url_delete_template = self.url_api_xlr + "templates/" + template['id']
                        response_delete_template = requests.delete(url_delete_template, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), verify=False)
                        response_delete_template.raise_for_status()
                        self.logger_cr.info("DELETE TEMPLATE : " + template['title'])
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error delete template : " + self.parameters['general_info']['name_release'])
            self.logger_error.error("Error call api : " + url_search_template)
            self.logger_error.error(e)
            sys.exit(0)

    def find_xlr_folder(self):
        """
        Find and validate XLR folder for template creation.

        Returns:
            str: XLR folder ID for template placement

        Searches for the specified folder in XLR and validates access.
        Updates dict_template with folder information for template creation.
        """
        url_find_xlr_folder = self.url_api_xlr + "folders/find?byPath=" + self.parameters['general_info']['xlr_folder']
        try:
            response_find_xlr_folder = requests.get(url_find_xlr_folder, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), verify=False)
            response_find_xlr_folder.raise_for_status()
            if 'id' in response_find_xlr_folder.json():
                self.dict_template = {'template': {'xlr_folder': response_find_xlr_folder.json()['id']}}
                self.logger_cr.info("XLR FOLDER FOUND : " + self.parameters['general_info']['xlr_folder'])
                return response_find_xlr_folder.json()['id']
            else:
                self.logger_error.error("XLR FOLDER NOT FOUND : " + self.parameters['general_info']['xlr_folder'])
                sys.exit(0)
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error find XLR folder : " + self.parameters['general_info']['xlr_folder'])
            self.logger_error.error("Error call api : " + url_find_xlr_folder)
            self.logger_error.error(e)
            sys.exit(0)

    def delete_phase_default_in_template(self):
        """
        Delete the default 'New Phase' created automatically by XLR.

        XLR templates are created with a default phase called 'New Phase'.
        This method removes it to start with a clean template structure.
        """
        url_delete_phase_default = self.url_api_xlr + "phases/search?phaseTitle=New Phase&releaseId=" + self.dict_template['template']['xlr_id'] + "&phaseVersion=ALL"
        try:
            response = requests.get(url_delete_phase_default, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), verify=False)
            response.raise_for_status()
            if len(response.json()) != 0:
                delete_phase = self.url_api_xlr + "phases/" + response.json()[0]['id']
                delete_response = requests.delete(delete_phase, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), verify=False)
                delete_response.raise_for_status()
                self.logger_cr.info("DELETED DEFAULT PHASE: New Phase")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error deleting default phase: " + str(e))

    def create_phase_env_variable(self):
        """
        Create environment variables for phase management in XLR template.

        Creates variables for environment selection based on the configuration:
        - Single phase: Creates simple variable or listbox for multiple environments
        - Multiple phases: Creates selection variables for phase management
        """
        if self.parameters['general_info']['type_template'] == 'CAB':
            phase = 'PRODUCTION'
            self.template_create_variable(key='env_' + self.parameters['general_info']['phases'][0],
                                        typev='StringVariable', label='', description='',
                                        value=phase, requiresValue=False, showOnReleaseStart=False, multiline=False)
        else:
            # Single phase configuration
            if len(self.parameters['general_info']['phases']) == 1:
                phase_name = self.parameters['general_info']['phases'][0]
                if self.parameters.get('XLD_ENV_' + phase_name) is None:
                    self.template_create_variable(key='env_' + phase_name,
                                                typev='StringVariable', label='', description='',
                                                value=phase_name, requiresValue=False, showOnReleaseStart=False, multiline=False)
                # Multiple environments for single phase
                elif len(self.parameters['XLD_ENV_' + phase_name]) > 1:
                    # Create listbox variable for environment selection
                    self.create_variable_list_box_env(key='env_' + phase_name,
                                                    value=self.parameters['XLD_ENV_' + phase_name])
                    # Control-M prefix for BENCH environment
                    if phase_name == 'BENCH':
                        self.template_create_variable(key='controlm_prefix_' + phase_name,
                                                    typev='StringVariable', label='controlm_prefix_' + phase_name,
                                                    description='', value='', requiresValue=False,
                                                    showOnReleaseStart=False, multiline=False)

            # Multiple phases configuration
            elif len(self.parameters['general_info']['phases']) > 1:
                # Handle phase selection mode
                if self.parameters['general_info'].get('phase_mode') == 'one_list':
                    if (self.parameters['general_info']['template_package_mode'] == 'listbox' and
                        'DEV' in self.parameters['general_info']['phases']):
                        choice_env = self.parameters['general_info']['phases'].copy()
                        choice_env.remove('DEV')
                    elif 'BUILD' in self.parameters['general_info']['phases']:
                        choice_env = self.parameters['general_info']['phases'].copy()
                        choice_env.remove('BUILD')

                # Create environment variables for each phase
                for phase in self.parameters['general_info']['phases']:
                    if self.parameters.get('XLD_ENV_' + phase) is not None:
                        if len(self.parameters['XLD_ENV_' + phase]) > 1:
                            self.create_variable_list_box_env(key='env_' + phase,
                                                            value=self.parameters['XLD_ENV_' + phase])

    def create_variable_list_box_env(self, key, value):
        """
        Create a listbox variable for environment selection in XLR.

        Args:
            key (str): Variable name
            value (list): List of environment options
        """
        url_create_variable = self.url_api_xlr + "templates/" + self.dict_template['template']['xlr_id'] + "/variables"
        try:
            response = requests.post(url_create_variable, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "key": key,
                "type": "xlrelease.ListBoxVariable",
                "requiresValue": True,
                "showOnReleaseStart": True,
                "label": key,
                "description": "Select environment for " + key,
                "multiline": False,
                "possibleValues": value,
                "value": value[0] if value else ""
            }, verify=False)
            response.raise_for_status()
            self.logger_cr.info("CREATE LISTBOX VARIABLE: " + key)
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating listbox variable " + key + ": " + str(e))

    def dict_value_for_tempalte(self):
        """
        Create dictionary of template values and initialize package management variables.

        Returns:
            dict: Template configuration dictionary

        This method processes the YAML configuration to create runtime variables
        for package management, environment selection, and deployment coordination.
        """
        dict_value_for_template = {}
        self.release_Variables_in_progress = {}
        self.release_Variables_in_progress['template_liste_phase'] = ','.join(map(str, self.parameters['general_info']['phases']))

        # BENCH environment handling
        if self.parameters.get('XLD_ENV_BENCH') is not None:
            xld_env_bench = ','.join(self.parameters['XLD_ENV_BENCH'])
            self.release_Variables_in_progress['list_env_BENCH'] = xld_env_bench

        # Initialize package management variables
        self.package_name_from_jenkins = []
        self.package_master = []
        self.list_package = []
        self.auto_undeploy = []
        self.list_auto_undeploy = []
        self.transformation_variable_branch = False
        self.list_package_name = []
        self.check_xld_exist = False
        self.set_undeploy_task = False

        # Process each package configuration
        for package, package_value in self.parameters['template_liste_package'].items():
            self.list_package.append(package)

            # Track master packages for Control-M dependencies
            if package_value['controlm_mode'] == 'master':
                self.package_master.append(package)

            # Handle packages with name_from_jenkins mode
            if package_value.get('mode') == "name_from_jenkins":
                self.template_create_variable(key=package + '_XLR_ID', typev='StringVariable',
                                            label='', description='', value='',
                                            requiresValue=False, showOnReleaseStart=False, multiline=False)
                self.transformation_variable_branch = True
                self.package_name_from_jenkins.append(package)

            # Build package name list
            if package_value['package_build_name'] != 'NAME PACKAGE':
                self.list_package_name.append(package + '-' + package_value['package_build_name'])

            # Check XLD mode
            if package_value.get('mode') == 'CHECK_XLD':
                self.check_xld_exist = True

            # Handle auto-undeploy configuration
            if package_value.get('auto_undeploy') is not None:
                if isinstance(package_value['auto_undeploy'], list):
                    listundeploy = '-'.join(package_value['auto_undeploy'])
                    self.auto_undeploy.append(package + ':' + listundeploy)
                    self.list_auto_undeploy.append(package)
                    self.set_undeploy_task = True
                elif package_value['auto_undeploy']:
                    self.auto_undeploy.append({package: 'yes'})
                    self.list_auto_undeploy.append(package)
                    self.set_undeploy_task = True

        dict_value_for_template['package'] = self.list_package
        dict_value_for_template['template_liste_phase'] = self.parameters['general_info']['phases']
        return dict_value_for_template

    def dict_value_for_tempalte_technical_task(self):
        """
        Create dictionary for technical task management.

        Returns:
            dict: Technical task configuration dictionary

        Processes technical tasks defined in the YAML configuration
        for before/after deployment operations.
        """
        dict_value_for_template_technical_task = {}

        if self.parameters.get('technical_task_list') is not None:
            dict_value_for_template_technical_task['technical_task'] = self.parameters['technical_task_list']

        return dict_value_for_template_technical_task

    def task_notification(self, phase, email_item, aim):
        """
        Create email notification task in XLR template.

        Args:
            phase (str): Phase name where notification is created
            email_item (dict): Email configuration from YAML
            aim (str): Type of notification ('email_close_release' or 'email_end_release')

        Creates email notification tasks for deployment lifecycle events
        with appropriate recipients and content.
        """
        if aim == "email_close_release":
            toAddresses = "${email_owner_release}"
            ccAddresses = ""
            if email_item.get('cc') is not None:
                ccAddresses = ", ".join(email_item["cc"])
        elif aim == "email_end_release":
            toAddresses = ", ".join(email_item["destinataire"])
            ccAddresses = "ops.team@company.com"

        task_release = 'Applications/' + self.dict_template['template']['xlr_id'] + '/' + self.dict_template[phase]['xlr_id_phase']
        url_task_notification = self.url_api_xlr + 'tasks/' + task_release + '/tasks'

        try:
            if aim == 'email_close_release':
                response = requests.post(url_task_notification, headers=self.header,
                                       auth=(self.ops_username_api, self.ops_password_api), json={
                    "id": "null",
                    "locked": True,
                    "type": "xlrelease.CustomScriptTask",
                    "title": "EMAIL : Close Release ${release.title}",
                    "pythonScript": {
                        "type": "nxsCustomNotification.MailNotification",
                        "id": "null",
                        "smtpServer": "Configuration/Custom/Server Mail",
                        "fromAddress": "ops.team@company.com",
                        "toAddresses": toAddresses,
                        "ccAddresses": ccAddresses,
                        "priority": "Normal",
                        "subject": "XLR - Deployment FINISH - Release name : ${release.title}",
                        "body": ("The XLR Release : ${release.title} is finished OK.\n"
                               "Please close the release to close the SUN CHANGE.\n"
                               "Description:\n"
                               "${Long_description_SUN_CHANGE}\n"
                               "Link to release: https://your-xlr-instance.com/${release.id}\n"
                               "Thanks")
                    }
                }, verify=False)
            elif aim == 'email_end_release':
                response = requests.post(url_task_notification, headers=self.header,
                                       auth=(self.ops_username_api, self.ops_password_api), json={
                    "id": "null",
                    "locked": True,
                    "type": "xlrelease.CustomScriptTask",
                    "title": "EMAIL : End Release ${release.title}",
                    "pythonScript": {
                        "type": "nxsCustomNotification.MailNotification",
                        "id": "null",
                        "smtpServer": "Configuration/Custom/Server Mail",
                        "fromAddress": "ops.team@company.com",
                        "toAddresses": toAddresses,
                        "ccAddresses": ccAddresses,
                        "priority": "Normal",
                        "subject": "XLR - Deployment END - Release name : ${release.title}",
                        "body": ("The XLR Release : ${release.title} has ended.\n"
                               "Link to release: https://your-xlr-instance.com/${release.id}\n"
                               "Thanks")
                    }
                }, verify=False)

            response.raise_for_status()
            self.logger_cr.info("CREATE EMAIL TASK: " + aim + " for phase " + phase)

        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating email notification " + aim + ": " + str(e))

    def define_variable_type_template_DYNAMIC(self):
        """
        Define and create template variables based on configuration mode.

        Creates different types of variables based on template configuration:
        - Package version variables
        - Environment selection variables
        - Phase selection variables
        """
        # Single package with listbox mode
        if (len(self.parameters['template_liste_package']) == 1 and
            self.parameters['general_info']['template_package_mode'] == 'listbox'):
            if not (len(self.parameters['general_info']['phases']) == 1 and
                   self.parameters['general_info']['phases'][0] == 'DEV'):
                package_name = self.dict_value_for_template['package'][0]
                self.template_create_variable(key=package_name + '_version',
                                            typev='StringVariable', label='', description='', value='',
                                            requiresValue=False, showOnReleaseStart=False, multiline=False)

        # Multiple packages or other modes
        else:
            for package in self.dict_value_for_template['package']:
                self.template_create_variable(key=package + '_version',
                                            typev='StringVariable', label='', description='', value='',
                                            requiresValue=False, showOnReleaseStart=False, multiline=False)

    def add_phase_tasks(self, phase):
        """
        Add a new phase to the XLR template.

        Args:
            phase (str): Phase name (DEV, UAT, BENCH, PRODUCTION, dynamic_release)

        Returns:
            dict: Updated dict_template with new phase information

        Creates a new phase in the XLR template with:
        - Phase-specific configuration
        - Task organization structure
        - Environment-appropriate settings
        - Integration with parent template

        Different phase types:
        - Development phases: Standard deployment workflow
        - Production phases: Approval workflow integration
        - Dynamic phase: Runtime template customization
        """
        url_add_phase_tasks = self.url_api_xlr + "templates/" + self.dict_template['template']['xlr_id'] + "/phases"
        try:
            response_add_phase_tasks = requests.post(url_add_phase_tasks, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.Phase",
                "title": phase,
                "flagStatus": "OK"
            }, verify=False)
            response_add_phase_tasks.raise_for_status()
            if 'id' in response_add_phase_tasks.json():
                self.dict_template.update({phase: {'xlr_id_phase': response_add_phase_tasks.json()['id']}})
                self.dict_template[phase].update({'xlr_id_phase_full': self.dict_template['template']['xlr_id'] + '/' + response_add_phase_tasks.json()['id']})
                self.logger_cr.info("CREATE PHASE : " + phase)
                return self.dict_template
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error add phase : " + phase)
            self.logger_error.error("Error call api : " + url_add_phase_tasks)
            self.logger_error.error(e)
            sys.exit(0)

    def XLR_group_task(self, ID_XLR_task, type_group, title_group, precondition):
        """
        Create a group task in XLR for organizing related tasks.

        Args:
            ID_XLR_task (str): Parent task or phase ID
            type_group (str): Type of group (SequentialGroup, ParallelGroup)
            title_group (str): Display title for the group
            precondition (str): Precondition expression for group execution

        Returns:
            str: Created group task ID

        Group tasks are used to organize related deployment tasks and
        control their execution order and dependencies.
        """
        url_group_task = self.url_api_xlr + "tasks/" + ID_XLR_task + "/tasks"
        try:
            response_group_task = requests.post(url_group_task, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease." + type_group,
                "title": title_group,
                "locked": False,
                "precondition": precondition
            }, verify=False)
            response_group_task.raise_for_status()
            if 'id' in response_group_task.json():
                self.logger_cr.info("CREATE GROUP TASK : " + title_group)
                return response_group_task.json()['id']
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error create group task : " + title_group)
            self.logger_error.error("Error call api : " + url_group_task)
            self.logger_error.error(e)
            sys.exit(0)

    def XLR_GateTask(self, phase, gate_title, description, cond_title, type_task, XLR_ID):
        """
        Create a gate task for manual approval or validation.

        Args:
            phase (str): Phase name where gate is created
            gate_title (str): Title of the gate task
            description (str): Detailed description
            cond_title (str): Condition title for gate completion
            type_task (str): Type classification for logging
            XLR_ID (str): XLR phase or task ID where gate is created

        Gate tasks provide manual checkpoints in the deployment pipeline
        for validation, approval, or confirmation before proceeding.
        """
        url_gate_task = self.url_api_xlr + "tasks/" + XLR_ID + "/tasks"
        try:
            response_gate_task = requests.post(url_gate_task, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.GateTask",
                "title": gate_title,
                "locked": False,
                "description": description,
                "conditions": [
                    {
                        "id": "null",
                        "type": "xlrelease.GateCondition",
                        "title": cond_title if cond_title else gate_title + " condition"
                    }
                ]
            }, verify=False)
            response_gate_task.raise_for_status()
            if 'id' in response_gate_task.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task GATE : " + gate_title + " - type : " + type_task)
        except requests.exceptions.RequestException as e:
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error create gate task : " + gate_title)
            self.logger_error.error("Error call api : " + url_gate_task)
            self.logger_error.error(e)
            sys.exit(0)

    def add_task_xldeploy(self, xld_value, phase, precondition, grp_id_xldeploy):
        """
        Add XL Deploy task for package deployment.

        Args:
            xld_value (list): XLD configuration values [package_name, ...]
            phase (str): Phase name
            precondition (str): Task precondition
            grp_id_xldeploy (str): XLD group task ID

        Creates XL Deploy tasks for automated deployment of packages.
        """
        if xld_value and len(xld_value) > 0:
            package_name = xld_value[0]
            self.add_task_xldeploy_auto(package_name, phase, grp_id_xldeploy)

    def add_task_xldeploy_auto(self, package_xld, phase, grp_id_xldeploy):
        """
        Create automated XL Deploy task for package deployment.

        Args:
            package_xld (str): Package name to deploy
            phase (str): Phase name (DEV, UAT, BENCH, PRODUCTION)
            grp_id_xldeploy (str): XLD group task ID

        Creates XLD deployment task with environment-specific configuration.
        """
        import requests

        # Environment-specific XLD configuration
        if phase == 'DEV':
            xld_prefix_env = 'D'
            if hasattr(self, 'parameters') and self.parameters.get('XLD_ENV_DEV') is not None:
                xld_env = '${env_' + phase + '}'
            elif hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('xld_standard'):
                xld_env = '10-DEV'
                xld_directory_env = 'DEV'
            else:
                xld_env = 'DEV'
            xld_directory_env = 'DEV'
        elif phase == 'UAT':
            xld_prefix_env = 'U'
            if hasattr(self, 'parameters') and self.parameters.get('XLD_ENV_UAT') is not None:
                xld_env = '${env_' + phase + '}'
            elif hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('xld_standard'):
                xld_env = '30-UAT'
                xld_directory_env = 'UAT'
            else:
                xld_env = 'UAT'
            xld_directory_env = 'UAT'
        elif phase == 'BENCH':
            if hasattr(self, 'parameters') and self.parameters.get('XLD_ENV_BENCH') is not None and len(self.parameters['XLD_ENV_BENCH']) > 1:
                xld_prefix_env = "${controlm_prefix_BENCH}"
            elif hasattr(self, 'parameters') and 'NXFFA' in self.parameters.get('general_info', {}).get('iua', ''):
                xld_prefix_env = 'Q'
            else:
                xld_prefix_env = 'B'
            if hasattr(self, 'parameters') and self.parameters.get('XLD_ENV_BENCH') is not None:
                xld_env = '${env_' + phase + '}'
            elif hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('xld_standard'):
                xld_env = '40-BENCH'
                xld_directory_env = 'BCH'
            else:
                xld_env = 'BCH'
            xld_directory_env = 'BCH'
        elif phase == 'PRODUCTION':
            xld_prefix_env = 'P'
            if hasattr(self, 'parameters') and self.parameters.get('XLD_ENV_PRODUCTION') is not None:
                xld_env = '${env_' + phase + '}'
            elif hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('xld_standard'):
                xld_env = '50-PROD'
                xld_directory_env = 'PRD'
            else:
                xld_env = 'PRD'
            xld_directory_env = 'PRD'
        else:
            xld_prefix_env = 'D'
            xld_env = phase
            xld_directory_env = phase

        # Find package configuration
        package_value = package_xld
        if hasattr(self, 'parameters') and 'template_liste_package' in self.parameters:
            for pkg in self.parameters['template_liste_package']:
                if package_xld in pkg:
                    package_value = pkg
                    break

        # Determine deployment paths
        if hasattr(self, 'parameters') and 'Y88' in self.parameters.get('general_info', {}).get('iua', '') and phase == 'BENCH':
            value_env = ''
            if package_xld == 'Interfaces':
                value = 'INT'
            elif package_xld == 'Scripts':
                value = 'SCR'
            elif package_xld == 'SDK':
                value = 'SDK'
            elif package_xld == 'App':
                value = 'APP'
            else:
                value = 'APP'
            tempo_XLD_environment_path = 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/${BENCH_Y88}/${BENCH_Y88}_01/' + value + '/<xld_prefix_env>Y88_' + value + '_<XLD_env>_01_ENV' + value_env
            xld_path_deploymentEnvironment = tempo_XLD_environment_path.replace('<XLD_env>', xld_env).replace('<xld_prefix_env>', xld_prefix_env).replace('<ENV>', xld_directory_env)
        else:
            # Default environment path
            xld_path_deploymentEnvironment = f"Environments/{package_xld}/{xld_prefix_env}{package_xld}_{xld_env}_ENV"

        # Package version variable
        if hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('type_template') == 'MULTIPACKAGE_AT_ONCE':
            version_package = package_value
        else:
            version_package = "${" + package_value + "_version}"

        # Deployment package path
        deployment_package = f"Applications/{package_xld}/{version_package}"

        url = self.url_api_xlr + 'tasks/' + grp_id_xldeploy + '/tasks'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": 'XLD-Deploy ' + package_xld,
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "server": "Configuration/Custom/XLDeploy PFI PROD",
                    "type": "xldeploy.Deploy",
                    "continueIfStepFails": False,
                    "displayStepLogs": True,
                    "retryCounter": {
                        "currentContinueRetrial": "0",
                        "currentPollingTrial": "0"
                    },
                    "id": "null",
                    "username": "${" + phase + "_username_xldeploy}",
                    "password": '${' + phase + '_password_xldeploy}',
                    "deploymentPackage": deployment_package,
                    "deploymentEnvironment": xld_path_deploymentEnvironment,
                    "overrideDeployedProps": {},
                    "rollbackOnFailure": False,
                    "cancelOnError": False,
                    "failOnPause": False,
                    "keepPreviousOutputPropertiesOnRetry": False
                }
            }, verify=False)
            response.raise_for_status()
            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD-Deploy " + package_xld + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : XLDEPLOY : " + package_xld)
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))
            sys.exit(0)

    def add_task_launch_script_windows(self, script_item, phase, index):
        """
        Add Windows script launch task.

        Args:
            script_item (dict): Script configuration
            phase (str): Phase name
            index (int): Script index

        Creates task for executing Windows scripts during deployment.
        """
        import requests

        if not isinstance(script_item, dict):
            return

        script_name = list(script_item.keys())[0] if script_item.keys() else f"windows_script_{index}"
        script_config = script_item.get(script_name, {})

        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'Windows Script: {script_name}',
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "server": "Configuration/Custom/Remote Script",
                    "type": "remoteScript.PowerShell",
                    "id": "null",
                    "username": "${" + phase + "_username_windows}",
                    "password": "${" + phase + "_password_windows}",
                    "address": script_config.get('server', '${windows_server}'),
                    "remotePath": script_config.get('path', ''),
                    "script": script_config.get('script', ''),
                    "options": script_config.get('options', [])
                }
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Windows Script: " + script_name + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating Windows script task: " + script_name)
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_launch_script_linux(self, script_item, phase, index):
        """
        Add Linux script launch task.

        Args:
            script_item (dict): Script configuration
            phase (str): Phase name
            index (int): Script index

        Creates task for executing Linux scripts during deployment.
        """
        import requests

        if not isinstance(script_item, dict):
            return

        script_name = list(script_item.keys())[0] if script_item.keys() else f"linux_script_{index}"
        script_config = script_item.get(script_name, {})

        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'Linux Script: {script_name}',
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "server": "Configuration/Custom/Remote Script",
                    "type": "remoteScript.Unix",
                    "id": "null",
                    "username": "${" + phase + "_username_linux}",
                    "password": "${" + phase + "_password_linux}",
                    "address": script_config.get('server', '${linux_server}'),
                    "remotePath": script_config.get('path', ''),
                    "script": script_config.get('script', ''),
                    "options": script_config.get('options', [])
                }
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Linux Script: " + script_name + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating Linux script task: " + script_name)
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_controlm_resource(self, phase, resource_items, precondition):
        """
        Add Control-M resource management task.

        Args:
            phase (str): Phase name
            resource_items: Resource configuration items
            precondition (str): Task precondition

        Creates tasks for managing Control-M resources.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'

        for resource_name, resource_config in resource_items:
            try:
                response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                    "id": "null",
                    "type": "xlrelease.CustomScriptTask",
                    "title": f'Control-M Resource: {resource_name}',
                    "status": "PLANNED",
                    "locked": False,
                    "waitForScheduledStartDate": True,
                    "pythonScript": {
                        "server": "Configuration/Custom/Control-M",
                        "type": "controlm.ResourceManagement",
                        "id": "null",
                        "username": "${" + phase + "_username_controlm}",
                        "password": "${" + phase + "_password_controlm}",
                        "resourceName": resource_name,
                        "resourceConfig": resource_config if isinstance(resource_config, dict) else {}
                    }
                }, verify=False)
                response.raise_for_status()
                if response.content and 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Control-M Resource: " + resource_name + "'")
            except requests.exceptions.RequestException as e:
                self.logger_error.error("Error creating Control-M resource task: " + resource_name)
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))

    def add_task_controlm(self, phase, task_key, folder_name, cases, grp_id_controlm):
        """
        Add Control-M task for job management.

        Args:
            phase (str): Phase name
            task_key (str): Task key identifier
            folder_name (str): Control-M folder name
            cases (str): Special cases configuration
            grp_id_controlm (str): Control-M group task ID

        Creates Control-M job management tasks.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + (grp_id_controlm or self.dict_template[phase]['xlr_id_phase']) + '/tasks'

        operation = 'START'
        if 'STOP' in task_key:
            operation = 'STOP'
        elif 'CLEAN' in task_key:
            operation = 'CLEAN'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'Control-M {operation}: {folder_name}',
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "server": "Configuration/Custom/Control-M",
                    "type": "controlm.JobManagement",
                    "id": "null",
                    "username": "${" + phase + "_username_controlm}",
                    "password": "${" + phase + "_password_controlm}",
                    "folderName": folder_name,
                    "operation": operation,
                    "cases": cases
                }
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Control-M " + operation + ": " + folder_name + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating Control-M task: " + folder_name)
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_controlm_spec_profil(self, phase, spec_config):
        """
        Add Control-M specification profile task.

        Args:
            phase (str): Phase name
            spec_config (dict): Specification configuration

        Creates Control-M specification profile tasks.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": 'Control-M Spec Profile',
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "server": "Configuration/Custom/Control-M",
                    "type": "controlm.SpecProfile",
                    "id": "null",
                    "username": "${" + phase + "_username_controlm}",
                    "password": "${" + phase + "_password_controlm}",
                    "profileConfig": spec_config
                }
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Control-M Spec Profile'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating Control-M spec profile task")
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_xldeploy_get_last_version(self, demandxld, xld_value, phase, grp_id_xldeploy):
        """
        Add XLD task to get the latest version of a package.

        Args:
            demandxld (str): Package demand name
            xld_value (list): XLD configuration values
            phase (str): Phase name
            grp_id_xldeploy (str): XLD group task ID

        Creates XLD task to retrieve the latest version of a package.
        """
        import requests

        package_value = demandxld
        if hasattr(self, 'parameters') and 'template_liste_package' in self.parameters:
            for package in self.parameters['template_liste_package']:
                if demandxld in package:
                    package_value = package
                    break

        version_package = "${" + demandxld + "_version}"
        url = self.url_api_xlr + 'tasks/' + grp_id_xldeploy + '/tasks'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": 'XLD-Deploy Search last version : ' + demandxld,
                "status": "PLANNED",
                "color": "#00ff00",
                "variableMapping": {
                    "pythonScript.packageId": version_package,
                },
                "locked": False,
                "waitForScheduledStartDate": True,
                "checkAttributes": False,
                "pythonScript": {
                    "server": "Configuration/Custom/XLDeploy PFI PROD",
                    "type": "xld.GetLatestVersion",
                    "id": "null",
                    "username": "${" + phase + "_username_xldeploy}",
                    "password": '${' + phase + '_password_xldeploy}',
                    "connectionFailureCount": 0,
                    "applicationId": f"Applications/{demandxld}",
                    "stripApplications": False,
                    "throwOnFail": False
                }
            }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD-Deploy Search last version : " + package_value + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : XLDEPLOY : " + package_value + " with title : 'XLD-Deploy Search last version : '" + package_value)
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))
            sys.exit(0)

    def XLRSun_check_status_sun_task(self, phase, type_task, technical_task, cat_technicaltask, precondition):
        """
        Create task to check status of ServiceNow task until completion.

        Args:
            phase (str): Phase name
            type_task (str): Type of SUN task variable name
            technical_task (str): Technical task identifier
            cat_technicaltask (str): Category of technical task
            precondition (str): Task precondition

        Creates XLR task that polls ServiceNow task status until it's closed.
        """
        import requests

        typesun_task_number = "${" + type_task + "}"

        # Get task title from configuration
        title = "Check SUN Task Status"
        if hasattr(self, 'dict_value_for_template_technical_task'):
            try:
                title = self.dict_value_for_template_technical_task['technical_task'][cat_technicaltask][technical_task]['sun_title']
            except (KeyError, TypeError):
                title = f"Check SUN Task Status - {technical_task}"

        # Handle precondition for SKIP templates
        if hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('type_template') == 'SKIP':
            try:
                variable_xlr = self.dict_value_for_template_technical_task['technical_task'][cat_technicaltask][technical_task]['xlr_item_name']
                precondition = f"'{variable_xlr}' in releaseVariables['{cat_technicaltask}']"
            except (KeyError, TypeError):
                precondition = ''
        else:
            precondition = ''

        # Create check URL
        if phase.startswith('CREATE_CHANGE_'):
            phase_key = phase
        else:
            phase_key = 'CREATE_CHANGE_' + phase if phase in ['BENCH', 'PRODUCTION'] else phase

        # Handle phase dict structure
        if hasattr(self, 'dict_template') and 'template' in self.dict_template and phase_key in self.dict_template:
            task_release = self.dict_template['template']['xlr_id'] + '/' + self.dict_template[phase_key]['xlr_id_phase']
        else:
            # Fallback for when dict_template is not fully initialized
            task_release = f"template_id/phase_id_{phase}"

        url_check_status = self.url_api_xlr + 'tasks/' + task_release + '/tasks'
        api_url = f"https://itaas.api.intranatixis.com/support/sun/change/v1/getTasks?id=${{{phase}.sun.id}}&offset=0"

        # Create Jython script for checking SUN task status
        script_content = (
            "##check_status_sun_task\n"
            "import ssl\n"
            "import base64\n"
            "import urllib2\n"
            "import json\n"
            "import time\n"
            "context = ssl._create_unverified_context()\n"
            "def call_api():\n"
            f"   api_url = '{api_url}'\n"
            "   password = release.passwordVariableValues['$' + '{ops_password_api}']\n"
            "   login = '${ops_username_api}'\n"
            "   auth_header = 'Basic ' + base64.b64encode(login + ':' + password)\n"
            "   request = urllib2.Request(api_url)\n"
            "   request.add_header('Authorization', auth_header)\n"
            "   response = urllib2.urlopen(request, context=context)\n"
            "   data = json.loads(response.read())\n"
            "   return data\n"
            "while True:\n"
            "    result = call_api()\n"
            f"    state = next(task['state'] for task in result['Data'] if task['number'] == '{typesun_task_number}')\n"
            f"    print('Task Sun State:' + state + ' from Change: ${{{phase}.sun.id}}')\n"
            "    if state == 'Closed':\n"
            f"        print('Task Sun State:' + state + ' from Change: ${{{phase}.sun.id}}')\n"
            "        break\n"
            "    time.sleep(300)\n"
        )

        try:
            response = requests.post(url_check_status, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": False,
                "title": title,
                "script": script_content
            }, verify=False)
            response.raise_for_status()

            if response.content and 'id' in response.json():
                if hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('type_template') == 'SKIP':
                    self.logger_cr.info("ON PHASE : " + phase + " --- Add task : 'Check status - " + title + "' with precondition : " + precondition)
                else:
                    self.logger_cr.info("ON PHASE : " + phase + " --- Add task : 'Check status - " + title + "'")

        except requests.exceptions.RequestException as e:
            self.logger_error.error("Detail ERROR: ON PHASE : " + phase + " --- Add task : Check status - " + title)
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error call api : " + url_check_status)
            self.logger_error.error(str(e))
            sys.exit(0)

    def XLRSun_task_close_sun_task(self, task_to_close, title, id_task, type_task, phase):
        """
        Create task to close ServiceNow task associated with deployment.

        Args:
            task_to_close (str): ServiceNow task number to close
            title (str): Task title
            id_task (str): Parent XLR task ID
            type_task (str): Type of task (xldeploy, task_ops, etc.)
            phase (str): Phase name

        Creates XLR task that closes the corresponding ServiceNow task when deployment is complete.
        """
        import requests

        if 'xldeploy' in type_task:
            # Close task for XLD deployment
            try:
                response = requests.post(self.url_api_xlr + 'tasks/' + id_task + '/tasks',
                                       headers=self.header,
                                       auth=(self.ops_username_api, self.ops_password_api),
                                       json={
                    "id": "null",
                    "type": "xlrelease.CustomScriptTask",
                    "title": "Close SUN task for XLD deployment",
                    "owner": "${release.owner}",
                    "locked": False,
                    "status": "PLANNED",
                    "pythonScript": {
                        "type": "servicenowNxs.UpdateTask",
                        "id": "null",
                        "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                        "taskNumber": task_to_close,
                        "status": "Close complete",
                        "closeNotes": "XLD deployment completed successfully",
                        "updateAs": "${change_user_assign}"
                    }
                }, verify=False)
                response.raise_for_status()

                if response.content and 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : SUN closing for XLD task")

            except requests.exceptions.RequestException as e:
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : SUN closing for XLD task")
                self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : " + self.url_api_xlr + 'tasks/' + id_task + '/tasks')
                self.logger_error.error(str(e))
                sys.exit(0)
        else:
            # Close task for other operations (OPS tasks, etc.)
            try:
                response = requests.post(self.url_api_xlr + 'tasks/' + id_task + '/tasks',
                                       headers=self.header,
                                       auth=(self.ops_username_api, self.ops_password_api),
                                       json={
                    "id": "null",
                    "type": "xlrelease.CustomScriptTask",
                    "title": "Close task " + title,
                    "owner": "${release.owner}",
                    "locked": True,
                    "status": "PLANNED",
                    "pythonScript": {
                        "type": "servicenowNxs.UpdateTask",
                        "id": "null",
                        "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                        "taskNumber": task_to_close,
                        "status": "Close complete",
                        "closeNotes": "Task completed successfully",
                        "updateAs": "${change_user_assign}"
                    }
                }, verify=False)
                response.raise_for_status()

                if response.content and 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : Close task " + title)

            except requests.exceptions.RequestException as e:
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : Close task " + title)
                self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : " + self.url_api_xlr + 'tasks/' + id_task + '/tasks')
                self.logger_error.error(str(e))
                sys.exit(0)