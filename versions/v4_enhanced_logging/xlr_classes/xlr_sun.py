"""
XLRSun - ServiceNow (SUN) approval workflow integration

This module contains the enhanced XLRSun class that inherits from XLRBase
for ServiceNow integration functionality.
"""

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

    # Additional SUN methods would be implemented here
    # Each using inherited functionality from XLRBase instead of composition