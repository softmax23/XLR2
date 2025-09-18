"""
XLRGeneric - Enhanced XLR operations and template management

This module contains the enhanced XLRGeneric class that inherits from XLRBase
and provides extended functionality for XLR template operations.
"""

from .xlr_base import XLRBase

class XLRGeneric(XLRBase):
    """
    Enhanced XLR template operations class.

    This class extends XLRBase with additional functionality for:
    - Advanced template management
    - Complex phase operations
    - Package and environment handling
    - Integration with deployment tools
    - Advanced task creation and management

    Inherits all core functionality from XLRBase and adds specialized
    operations for comprehensive deployment automation.
    """

    def __init__(self):
        """
        Initialize XLRGeneric with base functionality.

        Inherits all base XLR operations without the need for composition.
        """
        super().__init__()

    def parameter_phase_task(self, phase):
        """
        Configure phase-specific tasks based on YAML configuration.

        Args:
            phase (str): Phase name (DEV, UAT, BENCH, PRODUCTION)

        Processes the phase configuration from YAML and creates appropriate
        tasks for the phase including deployment tasks, technical tasks,
        and integration tasks.
        """
        self.auto_undeploy_done = False

        if not hasattr(self, 'parameters') or 'Phases' not in self.parameters:
            return

        if phase not in self.parameters['Phases']:
            return

        # Process each task in the phase
        for numtask, task in enumerate(self.parameters['Phases'][phase]):
            if not isinstance(task, dict):
                continue

            task_key = list(task.keys())[0] if task.keys() else None
            if not task_key:
                continue

            # Handle XL Deploy tasks
            if 'xldeploy' in task_key:
                self.creation_technical_task(phase, 'before_deployment')
                self.creation_technical_task(phase, 'before_xldeploy')

                # Create XLD group if not already created
                if f'xld_XLR_grp_{phase}' not in getattr(self, 'list_xlr_group_task_done', []):
                    if not hasattr(self, 'list_xlr_group_task_done'):
                        self.list_xlr_group_task_done = []

                    self.xld_ID_XLR_group_task_grp = self.XLR_group_task(
                        ID_XLR_task=self.dict_template[phase]['xlr_id_phase'],
                        type_group='SequentialGroup',
                        title_group='XLD DEPLOY',
                        precondition=''
                    )
                    self.list_xlr_group_task_done.append(f'xld_XLR_grp_{phase}')

                # Process XLD deployment tasks
                for demand_xld, xld_value in task[task_key].items():
                    if hasattr(self, 'list_package') and xld_value[0] in self.list_package:
                        precondition = ''
                        if hasattr(self, 'add_task_xldeploy'):
                            self.add_task_xldeploy(xld_value, phase, precondition, self.xld_ID_XLR_group_task_grp)

                # Check if this is the last xldeploy task
                list_remaining_xld = []
                for num, dictionnaire in enumerate(self.parameters['Phases'][phase]):
                    if num > numtask and isinstance(dictionnaire, dict):
                        dict_key = list(dictionnaire.keys())[0] if dictionnaire.keys() else None
                        if dict_key and 'xldeploy' in dict_key:
                            list_remaining_xld.append(num)

                if len(list_remaining_xld) == 0:
                    self.creation_technical_task(phase, 'after_xldeploy')

            # Handle Windows script tasks
            elif 'launch_script_windows' in task_key:
                for group_win_task in task[task_key]:
                    if isinstance(group_win_task, dict):
                        for index, script_windows_item in enumerate(group_win_task.get(list(group_win_task.keys())[0], [])):
                            if hasattr(self, 'add_task_launch_script_windows'):
                                self.add_task_launch_script_windows(script_windows_item, phase, index)

            # Handle Linux script tasks
            elif 'launch_script_linux' in task_key:
                for group_linux_task in task[task_key]:
                    if isinstance(group_linux_task, dict):
                        for index, script_linux_item in enumerate(group_linux_task.get(list(group_linux_task.keys())[0], [])):
                            if hasattr(self, 'add_task_launch_script_linux'):
                                self.add_task_launch_script_linux(script_linux_item, phase, index)

            # Handle Control-M resource tasks
            elif 'controlm_resource' in task_key:
                if hasattr(self, 'add_task_controlm_resource'):
                    self.add_task_controlm_resource(phase, task[task_key].items(), '')

            # Handle Control-M tasks
            elif 'controlm' in task_key:
                self.creation_technical_task(phase, 'before_deployment')

                for grtp_controlm, grtp_controlm_value in task[task_key].items():
                    if isinstance(grtp_controlm_value, str):
                        controlm_value_tempo = {grtp_controlm_value: None}
                        grtp_controlm_value = controlm_value_tempo

                    # Create group for STOP/START/CLEAN operations
                    if any(operation in grtp_controlm for operation in ['STOP', 'START', 'CLEAN']):
                        if 'STOP' in grtp_controlm:
                            title_grp = 'STOP'
                        elif 'START' in grtp_controlm:
                            title_grp = 'START'
                        elif 'CLEAN' in grtp_controlm:
                            title_grp = 'CLEAN'

                        group_key = f'CONTROLM_XLR_grp_{title_grp}_{phase}'
                        if group_key not in getattr(self, 'list_xlr_group_task_done', []):
                            if not hasattr(self, 'list_xlr_group_task_done'):
                                self.list_xlr_group_task_done = []

                            self.CONTROLM_ID_XLR_group_task_grp = self.XLR_group_task(
                                ID_XLR_task=self.dict_template[phase]['xlr_id_phase'],
                                type_group='SequentialGroup',
                                title_group=f'CONTROLM : {title_grp}',
                                precondition=''
                            )
                            self.list_xlr_group_task_done.append(group_key)

                    # Process Control-M items
                    grtp_controlm_value_notype_group = grtp_controlm_value.copy()
                    grtp_controlm_value_notype_group.pop('type_group', None)

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

                                if hasattr(self, 'add_task_controlm'):
                                    self.add_task_controlm(phase, task_key, folder_name, cases,
                                                         getattr(self, 'CONTROLM_ID_XLR_group_task_grp', None))

            # Handle Control-M spec tasks
            elif 'controlmspec' in task_key:
                self.creation_technical_task(phase, 'before_deployment')

                if isinstance(task[task_key], dict) and task[task_key].get('mode') is not None:
                    if task[task_key]['mode'] == 'profil':
                        if hasattr(self, 'add_task_controlm_spec_profil'):
                            self.add_task_controlm_spec_profil(phase, task[task_key])
                    elif task[task_key]['mode'] == 'free':
                        self.template_create_variable(
                            'CONTROLM_DEMAND', 'StringVariable', 'CONTROLM DEMAND', '',
                            task[task_key].get('render', ''), False, True, True
                        )

    def creation_technical_task(self, phase, cat_technicaltask):
        """
        Create technical tasks for OPS and DBA activities.

        Args:
            phase (str): Phase name
            cat_technicaltask (str): Category of technical task

        Creates specialized tasks for technical activities that need
        to be performed as part of the deployment process.
        """
        if hasattr(self, 'dict_value_for_template_technical_task') and len(self.dict_value_for_template_technical_task) != 0:
            if 'technical_task' in self.dict_value_for_template_technical_task:
                if cat_technicaltask in self.dict_value_for_template_technical_task['technical_task']:
                    if cat_technicaltask + '_done_' + phase not in self.list_technical_task_done:
                        if self.dict_value_for_template_technical_task['technical_task'].get(cat_technicaltask) is not None:
                            for technical_task in self.dict_value_for_template_technical_task['technical_task'][cat_technicaltask]:
                                if 'task_dba_factor' in technical_task or 'task_dba_other' in technical_task:
                                    precondition = ''
                                    # Use self method to avoid circular imports
                                    if hasattr(self, 'XLRSun_check_status_sun_task'):
                                        self.XLRSun_check_status_sun_task(
                                            phase,
                                            self.dict_value_for_template_technical_task['technical_task'][cat_technicaltask][technical_task]['xlr_sun_task_variable_name'] + "_" + phase,
                                            technical_task,
                                            cat_technicaltask,
                                            precondition
                                        )
                                elif 'task_ops' in technical_task:
                                    title = self.dict_value_for_template_technical_task['technical_task'][cat_technicaltask][technical_task]['sun_title']
                                    precondition = ''
                                    self.grp_id = self.XLR_group_task(
                                        ID_XLR_task=self.dict_template[phase]['xlr_id_phase'],
                                        type_group="SequentialGroup",
                                        title_group=title,
                                        precondition=''
                                    )
                                    self.XLR_GateTask(
                                        phase=phase,
                                        gate_title=title,
                                        description="See Change to action OPS",
                                        cond_title=None,
                                        type_task='check_sun_by_ops',
                                        XLR_ID=self.grp_id
                                    )
                                    if (self.parameters['general_info']['type_template'] != 'SEMI_DYNAMIC' and
                                        'INC' not in self.parameters['general_info']['type_template']):
                                        if phase != 'DEV' and phase != 'UAT':
                                            task_to_close = '${' + self.dict_value_for_template_technical_task['technical_task'][cat_technicaltask][technical_task]['xlr_sun_task_variable_name'] + "_" + phase + '}'
                                            if hasattr(self, 'XLRSun_task_close_sun_task'):
                                                self.XLRSun_task_close_sun_task(task_to_close, task_to_close, self.grp_id, 'task_ops', phase)

        self.list_technical_task_done.append(cat_technicaltask + '_done_' + phase)

    def add_task_user_input(self, phase, type_userinput, link_task_id):
        """
        Add user input tasks for interactive deployment steps.

        Args:
            phase (str): Phase name
            type_userinput (str): Type of user input required
            link_task_id (str): Parent task ID

        Creates tasks that require user interaction during deployment.
        """
        import requests

        # Create variables for username and password
        for value in [phase + '_username_' + type_userinput, phase + '_password_' + type_userinput]:
            if 'password' in value:
                self.template_create_variable(
                    key=value, typev='PasswordStringVariable', label=value, description='',
                    value='', requiresValue=False, showOnReleaseStart=False, multiline=False
                )
            else:
                if 'controlm' in type_userinput:
                    default_value = getattr(self, 'ops_username_controlm', '')
                elif 'windows' in type_userinput:
                    default_value = getattr(self, 'ops_username_windows', '')
                else:
                    default_value = ''

                self.template_create_variable(
                    key=value, typev='StringVariable', label=value, description='',
                    value=default_value, requiresValue=False, showOnReleaseStart=False, multiline=False
                )

        # Prepare variables for user input task
        variables_userinput = []
        l_name_variable = []

        if hasattr(self, 'dict_template') and 'variables' in self.dict_template:
            for value in self.dict_template['variables']:
                if list(value.keys())[0] == phase + '_username_' + type_userinput:
                    variables_userinput.append(value[phase + '_username_' + type_userinput])
                    l_name_variable.append(phase + '_username_' + type_userinput)
                elif list(value.keys())[0] == phase + '_password_' + type_userinput:
                    variables_userinput.append(value[phase + '_password_' + type_userinput])
                    l_name_variable.append(phase + '_password_' + type_userinput)

        # Create user input task
        url = self.url_api_xlr + 'tasks/' + link_task_id + '/tasks'
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.UserInputTask",
                "title": "Please enter user password for " + type_userinput + ' on ' + phase,
                "status": "PLANNED",
                "variables": variables_userinput
            }, verify=False)
            response.raise_for_status()

            if hasattr(self, 'logger_cr'):
                self.logger_cr.info(f"CREATE USER INPUT TASK: {type_userinput} for phase {phase}")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error(f"Error creating user input task: {e}")
            raise

    # Additional methods would be implemented here
    # Each using inherited functionality from XLRBase