"""
XLRBase - Foundation class for all XLR operations

This module contains the base class that provides core XLR functionality
shared across all specialized classes.
"""

import os, sys, requests, urllib3, inspect
import urllib3
from .xlr_logger import XLRLogger
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class XLRBase:
    """
    Base class providing core XLR functionality for all specialized classes - V4 Enhanced Logging.

    This class contains all the fundamental XLR operations that are shared
    across different specialized classes:
    - XLR API communication and authentication
    - Template creation and management
    - Variable creation and management
    - Phase and task management
    - Enhanced logging and error handling with performance tracking
    - Folder operations

    V4 Enhancements:
    - Structured logging with JSON output for monitoring
    - Performance timing and metrics
    - Enhanced error correlation
    - Automatic log rotation
    - Colored console output
    - Session statistics

    All other XLR classes inherit from this base class to avoid code
    duplication and circular dependencies.

    Attributes:
        url_api_xlr (str): XLR API base URL
        header (dict): HTTP headers for API calls
        ops_username_api (str): API username
        ops_password_api (str): API password
        parameters (dict): YAML configuration parameters
        dict_template (dict): Template metadata and IDs
        enhanced_logger (XLRLogger): Enhanced logging system
        logger_cr: Creation report logger (backward compatibility)
        logger_detail: Detailed information logger (backward compatibility)
        logger_error: Error logger (backward compatibility)
    """

    def __init__(self):
        """Initialize XLRBase with enhanced logging system."""
        # Initialize enhanced logging (will be properly set up by subclass)
        self.enhanced_logger = None

        # Backward compatibility loggers (will be set by enhanced_logger)
        self.logger_cr = None
        self.logger_detail = None
        self.logger_error = None

    def setup_enhanced_logging(self, release_name: str):
        """
        Set up enhanced logging system for this instance.

        Args:
            release_name: Name of the release for log organization
        """
        self.enhanced_logger = XLRLogger(release_name)

        # Set up backward compatibility
        self.logger_cr = self.enhanced_logger.logger_cr
        self.logger_detail = self.enhanced_logger.logger_detail
        self.logger_error = self.enhanced_logger.logger_error

        # Add context about the class
        self.enhanced_logger.add_context(
            class_name=self.__class__.__name__,
            module='xlr_base'
        )

    def template_create_variable(self, key, typev, label, description, value, requiresValue, showOnReleaseStart, multiline):
        """
        Create a variable in the XLR template with enhanced logging.

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
        if self.enhanced_logger:
            self.enhanced_logger.start_timer(f"create_variable_{key}")
            self.enhanced_logger.increment_counter('variable_operations')

        url_create_template_variable = self.url_api_xlr + "templates/" + self.dict_template['template']['xlr_id'] + "/variables"

        try:
            if self.enhanced_logger:
                self.enhanced_logger.increment_counter('api_calls')

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
                # Same message as original for compatibility
                message = "CREATE VARIABLE : " + key + " , type : " + typev
                if self.enhanced_logger:
                    self.enhanced_logger.info(message,
                                            variable_key=key,
                                            variable_type=typev,
                                            operation='create_variable')
                    self.enhanced_logger.end_timer(f"create_variable_{key}")
                else:
                    self.logger_cr.info(message)

        except requests.exceptions.RequestException as e:
            error_context = {
                'error_type': 'api_request_failed',
                'operation': 'create_variable',
                'variable_key': key,
                'variable_type': typev,
                'api_url': url_create_template_variable
            }

            if self.enhanced_logger:
                self.enhanced_logger.error("Error create variable : " + key, **error_context)
                self.enhanced_logger.error("Error call api : " + url_create_template_variable)
                self.enhanced_logger.error(str(e))
            else:
                # Original error format for compatibility
                self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error create variable : " + key)
                self.logger_error.error("Error call api : " + url_create_template_variable)
                self.logger_error.error(str(e))
            sys.exit(0)

    def CreateTemplate(self):
        """
        Create a new XLR release template with enhanced logging.

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
        template_name = self.parameters['general_info']['name_release']

        if self.enhanced_logger:
            self.enhanced_logger.start_timer('create_template')
            self.enhanced_logger.increment_counter('template_operations')

        url_createtemplate = self.url_api_xlr + "templates/?folderId=" + self.dict_template['template']['xlr_folder']

        try:
            if self.enhanced_logger:
                self.enhanced_logger.increment_counter('api_calls')

            response_createtemplate = requests.post(url_createtemplate, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": None,
                "type": "xlrelease.Release",
                "title": template_name,
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

                    # Same messages as original for compatibility
                    folder_msg = "CREATE TEMPLATE in XLR FOLDER : " + self.parameters['general_info']['xlr_folder']
                    template_msg = template_name

                    if self.enhanced_logger:
                        self.enhanced_logger.info(folder_msg,
                                                operation='create_template',
                                                template_name=template_name,
                                                template_id=self.XLR_template_id,
                                                folder=self.parameters['general_info']['xlr_folder'])
                        self.enhanced_logger.info(template_msg)
                        self.enhanced_logger.end_timer('create_template', f"Template {template_name} created successfully")
                    else:
                        self.logger_cr.info(folder_msg)
                        self.logger_cr.info(template_msg)

                    # Generate template URL (generalized from original)
                    if hasattr(self, 'url_api_xlr'):
                        base_url = self.url_api_xlr.replace('/api/v1/', '')
                        self.template_url = base_url + '/#/templates/' + self.XLR_template_id.replace("Applications/", "").replace('/', '-')
                    else:
                        self.template_url = 'Template created with ID: ' + self.XLR_template_id

                except (TypeError, Exception) as e:
                    error_context = {
                        'error_type': 'template_creation_failed',
                        'operation': 'create_template',
                        'template_name': template_name
                    }

                    if self.enhanced_logger:
                        self.enhanced_logger.error("Update Dico 'dict_template' in error", **error_context)
                        self.enhanced_logger.error(str(e))
                    else:
                        self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error")
                        self.logger_error.error(str(e))
                    sys.exit(0)

            return self.dict_template, self.XLR_template_id

        except requests.exceptions.RequestException as e:
            error_context = {
                'error_type': 'api_request_failed',
                'operation': 'create_template',
                'template_name': template_name,
                'api_url': url_createtemplate
            }

            if self.enhanced_logger:
                self.enhanced_logger.error("Error creation template in XLR: " + template_name, **error_context)
                self.enhanced_logger.error("Error call api : " + url_createtemplate)
                self.enhanced_logger.error(str(e))
            else:
                self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error creation template in XLR: " + template_name)
                self.logger_error.error("Error call api : " + url_createtemplate)
                self.logger_error.error(str(e))
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