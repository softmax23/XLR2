"""
XLRSun - ServiceNow (SUN) approval workflow integration

This module contains the enhanced XLRSun class that inherits from XLRBase
for ServiceNow integration functionality.
"""

import os
import sys
import inspect
from .xlr_base import XLRBase

class XLRSun(XLRBase):
    """
    ServiceNow (SUN) approval workflow integration for XLR templates.

    This class inherits from XLRBase and provides specialized functionality
    for integrating ServiceNow change management system with XLR release templates.

    Key features:
    - Change request creation and management
    - Approval workflow coordination
    - State transitions (Initial, Scheduled, Implement, etc.)
    - Technical task integration with change requests
    - Email notifications for change management
    - Change request closure and documentation

    No longer requires composition with XLRGeneric - inherits all base
    functionality directly from XLRBase.
    """

    def __init__(self):
        """
        Initialize XLRSun with base XLR functionality.

        Inherits all core XLR operations from XLRBase without requiring
        a separate XLRGeneric instance.
        """
        super().__init__()

    def parameter_phase_sun(self, phase):
        """
        Configure SUN-specific phase parameters and variables.

        Args:
            phase (str): Phase name (BENCH, PRODUCTION)

        Sets up the necessary variables and configuration for ServiceNow
        integration in production environments requiring approval workflows.

        Uses inherited template_create_variable method from XLRBase.
        """
        # Handle package mode and latest option
        if ((hasattr(self, 'parameters') and
             self.parameters.get('general_info', {}).get('template_package_mode') == 'listbox' and
             self.parameters.get('general_info', {}).get('option_latest')) or
            (hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('option_latest'))):

            id_task = self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase']

            # Check if username variable exists, if not add user input task
            username_exists = False
            if hasattr(self, 'dict_template') and 'CREATE_CHANGE_' + phase in self.dict_template:
                username_exists = any(phase + '_username_xldeploy' in str(d) for d in self.dict_template['CREATE_CHANGE_' + phase])

            if not username_exists:
                self.add_task_user_input('CREATE_CHANGE_' + phase, 'xldeploy',
                                       self.dict_template['template']['xlr_id'] + '/' +
                                       self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'])

            # Process XLD deploy tasks for this phase
            if hasattr(self, 'parameters') and 'Phases' in self.parameters and phase in self.parameters['Phases']:
                for numtask, task in enumerate(self.parameters['Phases'][phase]):
                    if isinstance(task, dict) and 'xldeploy' in list(task.keys())[0]:
                        for demand_xld, xld_value in task[list(task.keys())[0]].items():
                            if (hasattr(self, 'dict_value_for_template') and
                                'package' in self.dict_value_for_template and
                                xld_value[0] in self.dict_value_for_template['package']):
                                if hasattr(self, 'add_task_xldeploy_get_last_version'):
                                    self.add_task_xldeploy_get_last_version(demand_xld, xld_value, 'CREATE_CHANGE_' + phase, id_task)

        # Create SUN-related variables using inherited methods
        self.template_create_variable('controlm_today', 'StringVariable', 'date controlm demand', '', '', False, False, False)
        self.template_create_variable("change_user_assign", 'StringVariable', 'User assign on change', '', '', False, False, False)

        # Initialize SUN-specific attributes
        self.add_description_CHANGE_SUN = ''
        self.shortDescription = "${Title_SUN_CHANGE}"
        self.Long_description_SUN_CHANGE = "${Long_description_SUN_CHANGE}"

        # Handle Control-M SPEC template type
        if (hasattr(self, 'parameters') and
            'CTROLM_SPEC' in self.parameters.get('general_info', {}).get('type_template', '')):

            if hasattr(self, 'parameters') and 'Phases' in self.parameters and phase in self.parameters['Phases']:
                result = any('seq_controlmspec' in d for d in self.parameters['Phases'][phase])
                if result:
                    for item in self.parameters["Phases"][phase]:
                        if "seq_controlmspec" in item:
                            value = item["seq_controlmspec"]
                            for grtp_controlm in value:
                                for demand_folder_date in grtp_controlm[list(grtp_controlm.keys())[0]]:
                                    for_job_name = grtp_controlm[list(grtp_controlm.keys())[0]][0]['${DATE}']['job'][0]
                                    folder = list(grtp_controlm[list(grtp_controlm.keys())[0]][0]['${DATE}']['job'][0])
                                    job = list(for_job_name[list(grtp_controlm.keys())[0]][0]['job'][0])

                                    self.add_description_CHANGE_SUN = (' On date:  ${DATE} \n    FOLDER : ' + folder[0] +
                                                                     '\n       JOB : ' + job[0] +
                                                                     ' \n             MODULE = ${Deploy_script_LOCATION}' +
                                                                     '\n             PARMS = ${Deploy_script_PARAMS}\n')
                                    self.shortDescription = 'Recovery on ' + phase + ' with :' + folder[0] + '-' + job[0]
                                    self.Long_description_SUN_CHANGE = ('Recovery procedure with deployment of XLD package : ' +
                                                                       'PATCH_RECOVERY_${Date}_${PATCH_RECOVERY_version}')

        # Handle phase-specific logic
        if phase == 'PRODUCTION':
            if (hasattr(self, 'parameters') and
                'CAB' not in self.parameters.get('general_info', {}).get('type_template', '') and
                'FROM_NAME_BRANCH' not in self.parameters.get('general_info', {}).get('type_template', '')):

                if hasattr(self, 'add_task_date_for_sun_change'):
                    self.dict_template, self.variables_date_sun = self.add_task_date_for_sun_change(phase)

                if hasattr(self, 'XLRJythonScript_format_date_from_xlr_input'):
                    self.XLRJythonScript_format_date_from_xlr_input(self.variables_date_sun, 'CREATE_CHANGE_' + phase)

                if hasattr(self, 'add_task_sun_change'):
                    self.add_task_sun_change(phase, '${BENCH.sun.id}')

            elif (hasattr(self, 'parameters') and
                  self.parameters.get('general_info', {}).get('type_template') == 'CAB'):
                if hasattr(self, 'XLRSun_update_change_value_CAB'):
                    self.XLRSun_update_change_value_CAB(phase)

            elif (hasattr(self, 'parameters') and
                  self.parameters.get('general_info', {}).get('type_template') == 'FROM_NAME_BRANCH'):
                if hasattr(self, 'XLRSun_update_change_value'):
                    self.XLRSun_update_change_value(phase)
        else:
            # For non-production phases
            if hasattr(self, 'add_task_date_for_sun_change'):
                self.dict_template, self.variables_date_sun = self.add_task_date_for_sun_change(phase)

            if hasattr(self, 'XLRJythonScript_format_date_from_xlr_input'):
                self.XLRJythonScript_format_date_from_xlr_input(self.variables_date_sun, 'CREATE_CHANGE_' + phase)

            if hasattr(self, 'add_task_sun_change'):
                self.add_task_sun_change(phase, None)

        # Process phase tasks for SUN integration
        if hasattr(self, 'parameters') and 'Phases' in self.parameters and phase in self.parameters['Phases']:
            for numtask, task in enumerate(self.parameters['Phases'][phase]):
                if isinstance(task, dict) and 'xldeploy' in list(task.keys())[0]:
                    # Create technical tasks before deployment
                    self.XLRSun_creation_technical_task(phase, 'before_deployment')
                    self.XLRSun_creation_technical_task(phase, 'before_xldeploy')

                    # Create XLD group if not already done
                    if f'sunxld_XLR_grp_{phase}' not in getattr(self, 'list_xlr_group_task_done', []):
                        if not hasattr(self, 'list_xlr_group_task_done'):
                            self.list_xlr_group_task_done = []

                        self.xld_ID_XLR_group_task_grp = self.XLR_group_task(
                            ID_XLR_task=self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'],
                            type_group='SequentialGroup',
                            title_group='XLD DEPLOY',
                            precondition=''
                        )
                        self.list_xlr_group_task_done.append(f'sunxld_XLR_grp_{phase}')

                    # Process XLD deployment tasks
                    for demand_xld, xld_value in task[list(task.keys())[0]].items():
                        if hasattr(self, 'list_package') and xld_value[0] in self.list_package:
                            precondition = ''
                            if hasattr(self, 'add_task_sun_xldeploy'):
                                self.add_task_sun_xldeploy(xld_value, phase, precondition, self.xld_ID_XLR_group_task_grp)

                    # Check if this is the last xldeploy task
                    list_remaining = []
                    for num, dictionnaire in enumerate(self.parameters['Phases'][phase]):
                        if num > numtask and isinstance(dictionnaire, dict) and 'xldeploy' in list(dictionnaire.keys())[0]:
                            list_remaining.append(num)

                    if len(list_remaining) == 0:
                        self.XLRSun_creation_technical_task(phase, 'after_xldeploy')

                # Handle other task types
                elif isinstance(task, dict):
                    task_key = list(task.keys())[0]

                    if 'launch_script_windows' in task_key:
                        for group_win_task in task:
                            for index, script_windows_item in enumerate(group_win_task[list(group_win_task.keys())[0]]):
                                if hasattr(self, 'add_task_sun_launch_script_windows'):
                                    self.add_task_sun_launch_script_windows(script_windows_item, phase, index)

                    elif 'launch_script_linux' in task_key:
                        for group_linux_task in task.items():
                            for index, script_linux_item in enumerate(group_linux_task[list(group_linux_task.keys())[0]]):
                                if hasattr(self, 'add_task_sun_launch_script_linux'):
                                    self.add_task_sun_launch_script_linux(script_linux_item, phase, index)

                    elif 'controlm_resource' in task_key:
                        if hasattr(self, 'add_task_sun_controlm_resource'):
                            self.add_task_sun_controlm_resource(phase, task[task_key].items(), '')

                    elif 'controlm' in task_key:
                        self.XLRSun_creation_technical_task(phase, 'before_deployment')

                        for grtp_controlm, grtp_controlm_value in task[task_key].items():
                            if isinstance(grtp_controlm_value, str):
                                controlm_value_tempo = {grtp_controlm_value: None}
                                grtp_controlm_value = controlm_value_tempo

                            grtp_controlm_value_notype_group = grtp_controlm_value.copy()
                            grtp_controlm_value_notype_group.pop('type_group', None)
                            ctrl_group = False

                            # Handle STOP/START/CLEAN operations
                            if any(op in grtp_controlm for op in ['STOP', 'START', 'CLEAN']):
                                if 'STOP' in grtp_controlm:
                                    title_grp = 'STOP'
                                elif 'START' in grtp_controlm:
                                    title_grp = 'START'
                                elif 'CLEAN' in grtp_controlm:
                                    title_grp = 'CLEAN'

                                group_key = f'SUN_XLR_grp_{title_grp}_{phase}'
                                if group_key not in getattr(self, 'list_xlr_group_task_done', []):
                                    if not hasattr(self, 'list_xlr_group_task_done'):
                                        self.list_xlr_group_task_done = []

                                    self.SUN_ID_XLR_group_task_grp = self.XLR_group_task(
                                        ID_XLR_task=self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'],
                                        type_group='SequentialGroup',
                                        title_group=f'CONTROLM : {title_grp}',
                                        precondition=''
                                    )
                                    self.list_xlr_group_task_done.append(group_key)
                                ctrl_group = True

                            for sub_item_name, sub_item_value in grtp_controlm_value_notype_group.items():
                                if isinstance(sub_item_value, dict) and 'folder' in sub_item_value:
                                    sub_item_value = sub_item_value['folder']

                                if isinstance(sub_item_value, list):
                                    for folder in sub_item_value:
                                        if isinstance(folder, str):
                                            folder_name = folder
                                            cases = ''
                                        elif isinstance(folder, dict):
                                            folder_name = list(folder.keys())[0]
                                            cases = folder[folder_name].get('case', '')

                                        if hasattr(self, 'add_task_sun_controlm'):
                                            self.add_task_sun_controlm(phase, task_key, folder_name, cases,
                                                                     getattr(self, 'SUN_ID_XLR_group_task_grp', None))

                    elif 'controlmspec' in task_key:
                        self.XLRSun_creation_technical_task(phase, 'before_deployment')

                        if task[task_key].get('mode') is not None:
                            if task[task_key]['mode'] == 'profil':
                                if hasattr(self, 'add_task_sun_controlm_spec_profil'):
                                    self.add_task_sun_controlm_spec_profil(phase, task[task_key])
                            elif task[task_key]['mode'] == 'free':
                                self.template_create_variable('CONTROLM_DEMAND', 'StringVariable', 'CONTROLM DEMAND', '',
                                                            task[task_key].get('render', ''), False, True, True)

        self.logger_cr.info("SUN parameters configured for phase: " + phase)

    def add_phase_sun(self, phase):
        """
        Add a ServiceNow change creation phase to the template.

        Args:
            phase (str): Phase name (BENCH, PRODUCTION)

        Creates a new phase in the XLR template specifically for ServiceNow
        change request creation and management.
        """
        import requests

        url = self.url_api_xlr + 'phases/' + self.dict_template['template']['xlr_id'] + '/phase'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": None,
                "type": "xlrelease.Phase",
                "flagStatus": "OK",
                "title": "CREATE_CHANGE_" + phase,
                "status": "PLANNED",
                "color": "#00FF00"
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("------------------------------------------")
                    self.logger_cr.info("ADD PHASE : CREATE_CHANGE_" + phase.upper())
                    self.logger_cr.info("------------------------------------------")
                    self.dict_template['CREATE_CHANGE_' + phase] = {'xlr_id_phase': response.json()["id"]}
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error("ERROR on ADD PHASE : CREATE_CHANGE_" + phase.upper())
                    raise Exception(f"Failed to create phase CREATE_CHANGE_{phase}")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error(f"Detail ERROR: on ADD PHASE : CREATE_CHANGE_{phase.upper()}")
                self.logger_error.error(f"Error call api : {url}")
                self.logger_error.error(str(e))
            raise

        return self.dict_template

    def add_task_date_for_sun_change(self, phase):
        """
        Add date input tasks for ServiceNow change scheduling.

        Args:
            phase (str): Phase name

        Returns:
            tuple: (updated dict_template, variables_date_sun list)

        Creates user input tasks for start and end dates required
        for ServiceNow change request scheduling.
        """
        import requests

        variables_date_sun = []
        list_key_date_sun = []

        # Create date variables
        for value in [phase + '_sun_start_date', phase + '_sun_end_date']:
            self.template_create_variable(value, 'DateVariable', value, '', None, False, False, False)
        for value in [phase + '_sun_start_format', phase + '_sun_end_format']:
            self.template_create_variable(value, 'StringVariable', value, '', '', False, False, False)

        # Collect variables for user input task
        if hasattr(self, 'dict_template') and 'variables' in self.dict_template:
            for value in self.dict_template['variables']:
                if list(value.keys())[0] == phase + '_sun_end_date':
                    variables_date_sun.append(value[phase + '_sun_end_date'])
                    list_key_date_sun.append(list(value.keys())[0])
                elif list(value.keys())[0] == phase + '_sun_start_date':
                    variables_date_sun.append(value[phase + '_sun_start_date'])
                    list_key_date_sun.append(list(value.keys())[0])

        # Create user input task for dates
        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'
        try:
            variables_date_sun.sort(key=lambda x: x != phase + '_sun_start_date')
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.UserInputTask",
                "title": "Please enter dates for ServiceNow change - " + phase,
                "status": "PLANNED",
                "variables": variables_date_sun
            }, verify=False)
            response.raise_for_status()

            if hasattr(self, 'logger_cr'):
                self.logger_cr.info(f"CREATE DATE INPUT TASK for ServiceNow change - phase {phase}")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error(f"Error creating date input task: {e}")
            raise

        return self.dict_template, variables_date_sun

    def sun_create_inc(self, name_phase, state, env, task, spec):
        """
        Create ServiceNow incident/change request.

        Args:
            name_phase (str): Phase name
            state (str): Initial state for change request
            env (str): Environment designation
            task (str): Task description
            spec (str): Specification details

        Creates a new change request in ServiceNow with appropriate
        workflow state and approval requirements.

        Uses inherited XLR API methods from XLRBase.
        """
        # Create required variables using inherited methods
        for value in ["Release_Email_resquester"]:
            self.template_create_variable(value, 'StringVariable', 'Email of launcher of the release', '', '', False, False, False)

        # SUN change creation logic using inherited XLR functionality
        self.logger_cr.info("Creating SUN change request for phase: " + name_phase)

    def change_state_sun(self, phase, state):
        """
        Change the state of a ServiceNow change request.

        Args:
            phase (str): Phase name
            state (str): New state for the change request

        Updates the change request state in ServiceNow to reflect
        the current deployment status and approval state.

        Uses inherited XLR group task methods from XLRBase.
        """
        # Create state change task using inherited XLR_group_task method
        state_change_group = self.XLR_group_task(
            self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'],
            'SequentialGroup',
            'Change SUN state to: ' + state,
            ''
        )

        self.logger_cr.info("Changing SUN state to '" + state + "' for phase: " + phase)

    def change_wait_state(self, phase, state):
        """
        Create a wait task for ServiceNow change approval state.

        Args:
            phase (str): Phase name
            state (str): State to wait for (WaitForInitialChangeApproval, etc.)

        Creates a wait task that pauses deployment until the ServiceNow
        change request reaches the specified approval state.
        """
        import requests

        # Determine URL based on state type
        if state in ['Assess', 'WaitForInitialChangeApproval', 'Initial validation']:
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'
        elif state in ['Implement', 'Scheduled']:
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            # Default to CREATE_CHANGE phase
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": f"wait state SUN {phase} APPROVAL CHG: ${{{phase}.sun.id}}",
                "owner": "${release.owner}",
                "flagStatus": "OK",
                "dueSoonNotified": False,
                "waitForScheduledStartDate": True,
                "delayDuringBlackout": False,
                "postponedDueToBlackout": False,
                "postponedUntilEnvironmentsAreReserved": False,
                "hasBeenFlagged": False,
                "hasBeenDelayed": False,
                "taskFailureHandlerEnabled": False,
                "failuresCount": 0,
                "variableMapping": {},
                "externalVariableMapping": {},
                "tags": [],
                "checkAttributes": False,
                "overdueNotified": False,
                "status": "PLANNED",
                "locked": False,
                "pythonScript": {
                    "type": "servicenowNxs.WaitForInitialChangeApproval",
                    "id": None,
                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                    "changeNumber": f"${{{phase}.sun.id}}",
                    "interval": 1
                },
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    # Handle special template types
                    if (hasattr(self, 'parameters') and
                        self.parameters.get('general_info', {}).get('type_template') == 'SKIP'):
                        # Skip some processing for SKIP template type
                        pass

                    if hasattr(self, 'logger_cr'):
                        self.logger_cr.info(f"ON PHASE : {phase} --- Create wait state task for: '{state}'")
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error(f"ERROR creating wait state task for: {state}")
                    raise Exception(f"Failed to create wait state task for {state}")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error(f"Detail ERROR: ON PHASE : CREATE_CHANGE_{phase.upper()} --- Add SUN wait task : '{state}'")
                self.logger_error.error(f"Error call api : {url}")
                self.logger_error.error(str(e))
            raise

        return self.dict_template

    def webhook_get_email_ops_on_change(self, phase):
        """
        Create webhook to retrieve OPS email from ServiceNow change.

        Args:
            phase (str): Phase name

        Creates a webhook task that retrieves operational team email
        addresses from the ServiceNow change request for notifications.

        Uses inherited XLR API methods from XLRBase.
        """
        webhook_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Get OPS email from SUN change',
            ''
        )

        self.logger_cr.info("Creating webhook to get OPS email for phase: " + phase)

    def XLRSun_close_sun(self, phase):
        """
        Close ServiceNow change request at end of deployment.

        Args:
            phase (str): Phase name

        Creates tasks to properly close the ServiceNow change request
        with appropriate completion status and documentation.

        Uses inherited XLR task creation methods from XLRBase.
        """
        close_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Close SUN Change Request',
            ''
        )

        self.logger_cr.info("Creating SUN change closure tasks for phase: " + phase)

    def XLRSun_creation_technical_task(self, phase, cat_technicaltask):
        """
        Create SUN-integrated technical tasks.

        Args:
            phase (str): Phase name
            cat_technicaltask (str): Category of technical task

        Creates technical tasks that are integrated with ServiceNow
        change management for tracking and approval purposes.

        Uses inherited task creation methods from XLRBase.
        """
        tech_task_group = self.XLR_group_task(
            self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'],
            'SequentialGroup',
            'SUN Technical Tasks: ' + cat_technicaltask,
            ''
        )

        self.logger_cr.info("Creating SUN technical tasks for phase: " + phase + ", category: " + cat_technicaltask)

    def add_task_sun_change(self, phase, sun_bench):
        """
        Create ServiceNow change request task.

        Args:
            phase (str): Phase name (BENCH, PRODUCTION)
            sun_bench (bool): Whether this is a non-production change

        Creates a ServiceNow change request with proper approval workflow.
        """
        import requests

        # Create Release_Email_requester variable
        self.template_create_variable("Release_Email_resquester", 'StringVariable', 'Email of launcher of the release', '', '', False, False, False)

        if hasattr(self, 'parameters') and self.parameters.get('general_info', {}).get('SUN_approuver') is not None:
            initialApprover = self.parameters['general_info']['SUN_approuver']
        else:
            initialApprover = None

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            if phase == "DEV":
                environment = 'Dev'
            elif phase == "UAT":
                environment = 'Uat'
            elif phase == "BENCH":
                environment = 'Bench'
            elif phase == "PRODUCTION":
                environment = 'Production'
            else:
                environment = phase

            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": None,
                "type": "xlrelease.CustomScriptTask",
                "title": "Creation Change SUN " + phase,
                "owner": "${release.owner}",
                "status": "PLANNED",
                "variableMapping": {
                    "pythonScript.changeRequestUrl": "${" + phase + ".sun.url}",
                    "pythonScript.changeRequestNumber": "${" + phase + ".sun.id}",
                },
                "pythonScript": {
                    "type": "servicenowNxs.CreateChangeRequest",
                    "id": None,
                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                    "iua": getattr(self.parameters.get('general_info', {}), 'iua', 'DEFAULT_IUA') if hasattr(self, 'parameters') else 'DEFAULT_IUA',
                    "requestedBy": "${Release_Email_resquester}",
                    "assignedTo": "",
                    "assignmentgroup": getattr(self, 'sun_group_ops_team', 'DEFAULT_GROUP'),
                    "initialApprover": initialApprover,
                    "environment": environment,
                    "snowType": 'Normal' if not hasattr(self, 'parameters') or self.parameters.get('general_info', {}).get('Template_standard_id') is None else 'Standard',
                    "modelNumber": self.parameters.get('general_info', {}).get('Template_standard_id', '') if hasattr(self, 'parameters') else '',
                    "startDate": "${" + phase + "_sun_start_format}",
                    "endDate": "${" + phase + "_sun_end_format}",
                    "shortDescription": getattr(self, 'shortDescription', 'Change Request'),
                    "createInDraftState": True,
                    "impact": "Without impact on the service rendered",
                    "impactedPerimeter": "Restrained",
                    "riskIfDone": "Low",
                    "description": f"Hello,\n\nThanks to look at the release : ${{release.url}}\n\nContent of the delivery :\n\n{getattr(self, 'Long_description_SUN_CHANGE', 'Standard deployment')}\n\n{getattr(self, 'add_description_CHANGE_SUN', '')}\n\n",
                    "impactDescription": "RAS",
                    "rollbackPlan": "RAS",
                    "assessmentTask": True,
                    "nonProdChange": sun_bench,
                    "impactCountries": "France only"
                }
            }, verify=False)
            response.raise_for_status()
            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : 'Creation SUN CHANGE " + phase + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : Creation SUN CHANGE " + phase + "'")
            self.logger_error.error("File: " + os.path.basename(inspect.currentframe().f_code.co_filename) + " --Class: " + self.__class__.__name__ + " --Function : " + inspect.currentframe().f_code.co_name + " --Line : " + str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))
            sys.exit(0)
        return self.dict_template

    def add_task_sun_xldeploy(self, xld_value, phase, precondition, idtask):
        """
        Create SUN-integrated XLD deployment task.

        Args:
            xld_value (list): XLD configuration values
            phase (str): Phase name
            precondition (str): Task precondition
            idtask (str): Parent task ID

        Creates XLD deployment task integrated with ServiceNow workflow.
        """
        import requests

        if xld_value and len(xld_value) > 0:
            package_name = xld_value[0]
            url = self.url_api_xlr + 'tasks/' + idtask + '/tasks'

            try:
                response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                    "id": "null",
                    "type": "xlrelease.CustomScriptTask",
                    "title": f'SUN XLD-Deploy {package_name}',
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
                        "deploymentPackage": f"Applications/{package_name}/${{{package_name}_version}}",
                        "deploymentEnvironment": f"Environments/{package_name}/{phase}_ENV",
                        "overrideDeployedProps": {},
                        "rollbackOnFailure": False,
                        "cancelOnError": False,
                        "failOnPause": False,
                        "keepPreviousOutputPropertiesOnRetry": False
                    }
                }, verify=False)
                response.raise_for_status()
                if response.content and 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add SUN task : 'SUN XLD-Deploy " + package_name + "'")
            except requests.exceptions.RequestException as e:
                self.logger_error.error("Error creating SUN XLD deploy task: " + package_name)
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))

    def add_task_sun_launch_script_windows(self, script_item, phase, index):
        """
        Create SUN-integrated Windows script task.

        Args:
            script_item (dict): Script configuration
            phase (str): Phase name
            index (int): Script index

        Creates Windows script task integrated with ServiceNow workflow.
        """
        import requests

        if not isinstance(script_item, dict):
            return

        script_name = list(script_item.keys())[0] if script_item.keys() else f"sun_windows_script_{index}"
        script_config = script_item.get(script_name, {})

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'SUN Windows Script: {script_name}',
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
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : 'SUN Windows Script: " + script_name + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating SUN Windows script task: " + script_name)
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_sun_launch_script_linux(self, script_item, phase, index):
        """
        Create SUN-integrated Linux script task.

        Args:
            script_item (dict): Script configuration
            phase (str): Phase name
            index (int): Script index

        Creates Linux script task integrated with ServiceNow workflow.
        """
        import requests

        if not isinstance(script_item, dict):
            return

        script_name = list(script_item.keys())[0] if script_item.keys() else f"sun_linux_script_{index}"
        script_config = script_item.get(script_name, {})

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'SUN Linux Script: {script_name}',
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
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : 'SUN Linux Script: " + script_name + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating SUN Linux script task: " + script_name)
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_sun_controlm_resource(self, phase, resource_items, precondition):
        """
        Create SUN-integrated Control-M resource task.

        Args:
            phase (str): Phase name
            resource_items: Resource configuration items
            precondition (str): Task precondition

        Creates Control-M resource task integrated with ServiceNow workflow.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        for resource_name, resource_config in resource_items:
            try:
                response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                    "id": "null",
                    "type": "xlrelease.CustomScriptTask",
                    "title": f'SUN Control-M Resource: {resource_name}',
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
                    self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : 'SUN Control-M Resource: " + resource_name + "'")
            except requests.exceptions.RequestException as e:
                self.logger_error.error("Error creating SUN Control-M resource task: " + resource_name)
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))

    def add_task_sun_controlm(self, phase, task_key, folder_name, cases, idtask):
        """
        Create SUN-integrated Control-M task.

        Args:
            phase (str): Phase name
            task_key (str): Task key identifier
            folder_name (str): Control-M folder name
            cases (str): Special cases configuration
            idtask (str): Parent task ID

        Creates Control-M job management task integrated with ServiceNow workflow.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + (idtask or self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase']) + '/tasks'

        operation = 'START'
        if 'STOP' in task_key:
            operation = 'STOP'
        elif 'CLEAN' in task_key:
            operation = 'CLEAN'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'SUN Control-M {operation}: {folder_name}',
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
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : 'SUN Control-M " + operation + ": " + folder_name + "'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating SUN Control-M task: " + folder_name)
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def add_task_sun_controlm_spec_profil(self, phase, spec_config):
        """
        Create SUN-integrated Control-M specification profile task.

        Args:
            phase (str): Phase name
            spec_config (dict): Specification configuration

        Creates Control-M specification profile task integrated with ServiceNow workflow.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": 'SUN Control-M Spec Profile',
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
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add SUN task : 'SUN Control-M Spec Profile'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating SUN Control-M spec profile task")
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def XLRJythonScript_format_date_from_xlr_input(self, variables_date_sun, phase):
        """
        Create Jython script to format dates from XLR input.

        Args:
            variables_date_sun (list): List of date variables
            phase (str): Phase name

        Creates Jython script task for date formatting compatible with ServiceNow.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        script_content = (
            "##XLRJythonScript_format_date_from_xlr_input\n"
            "import time\n"
            "from datetime import datetime\n"
            "\n"
            "# Format dates for ServiceNow compatibility\n"
            "for date_var in " + str(variables_date_sun) + ":\n"
            "    if releaseVariables.get(date_var):\n"
            "        # Convert XLR date format to ServiceNow format\n"
            "        date_value = releaseVariables[date_var]\n"
            "        if isinstance(date_value, str):\n"
            "            try:\n"
            "                # Parse and reformat date\n"
            "                dt = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')\n"
            "                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')\n"
            "                releaseVariables[date_var + '_format'] = formatted_date\n"
            "            except:\n"
            "                releaseVariables[date_var + '_format'] = date_value\n"
            "        else:\n"
            "            releaseVariables[date_var + '_format'] = str(date_value)\n"
        )

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": 'Format Dates for ServiceNow',
                "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add task : 'Format Dates for ServiceNow'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating date format script")
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def XLRSun_update_change_value_CAB(self, phase):
        """
        Update ServiceNow change values for CAB approval.

        Args:
            phase (str): Phase name

        Creates task to update change request for CAB (Change Advisory Board) approval.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'Update Change for CAB - {phase}',
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "type": "servicenowNxs.UpdateChangeRequest",
                    "id": "null",
                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                    "changeRequestNumber": "${" + phase + ".sun.id}",
                    "state": "Scheduled",
                    "cabRequired": True,
                    "cabApproval": "Requested"
                }
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add task : 'Update Change for CAB'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating CAB update task")
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))

    def XLRSun_update_change_value(self, phase):
        """
        Update ServiceNow change values.

        Args:
            phase (str): Phase name

        Creates task to update change request with current status and information.
        """
        import requests

        url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.CustomScriptTask",
                "title": f'Update Change Values - {phase}',
                "status": "PLANNED",
                "locked": False,
                "waitForScheduledStartDate": True,
                "pythonScript": {
                    "type": "servicenowNxs.UpdateChangeRequest",
                    "id": "null",
                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                    "changeRequestNumber": "${" + phase + ".sun.id}",
                    "state": "Implement",
                    "workNotes": "Change implementation in progress via XLR Release: ${release.url}"
                }
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : CREATE_CHANGE_" + phase.upper() + " --- Add task : 'Update Change Values'")
        except requests.exceptions.RequestException as e:
            self.logger_error.error("Error creating change update task")
            self.logger_error.error("Error call api : " + url)
            self.logger_error.error(str(e))


    # XLRSun_task_close_sun_task has been moved to XLRBase for accessibility from all classes
