import argparse,yaml,sys,json,configparser
import logging,os
from script_py.xlr_create_template_change.logging import setup_logger,setup_logger_error,setup_logger_detail
from script_py.xlr_create_template_change.check_yaml_file import check_yaml_file
from xlr_classes import XLRGeneric,XLRControlm,XLRDynamicPhase,XLRSun,XLRTaskScript

class XLRCreateTemplate(XLRGeneric,XLRSun,XLRTaskScript,XLRControlm,XLRDynamicPhase):
    """
    Main class for creating XLR (XebiaLabs Release) templates.

    This class inherits from multiple specialized classes to provide comprehensive
    XLR template generation capabilities including:
    - XLRGeneric: Base XLR operations and template management
    - XLRSun: SUN (Service Now) integration for approval workflows
    - XLRTaskScript: Custom script task generation
    - XLRControlm: Control-M batch job scheduling integration
    - XLRDynamicPhase: Dynamic phase management based on configuration

    The class orchestrates the creation of deployment pipelines across multiple
    environments (DEV, UAT, BENCH, PRODUCTION) with automated approval workflows,
    job scheduling, and deployment coordination.
    """
    def __init__(self,parameters):
            """
            Initialize the XLR template creation process.

            Args:
                parameters (dict): YAML configuration loaded as dictionary containing:
                    - general_info: Basic release metadata and configuration
                    - template_liste_package: Package definitions and build information
                    - jenkins: Jenkins integration configuration
                    - Phases: Phase-specific deployment sequences
                    - technical_task_list: Pre/post deployment technical tasks

            Sets up:
            - API configuration and credentials
            - Logging infrastructure
            - Template validation
            - Phase and variable initialization
            """
            ## Load configuration file for XLR API calls to create template
            with open('_conf/xlr_create_template_change.ini', 'r') as file:
                for line in file:
                    key, value = line.strip().split('=')
                    setattr(self, key, value)
            self.header= {'content-type':'application/json','Accept': 'application/json'}
            ## Initialize YAML file variables in parameters
            self.parameters = parameters
            ## Create directory if not exist for log file of template creation
            if not os.path.exists('log/'+self.parameters['general_info']['name_release']):
                os.makedirs('log/'+self.parameters['general_info']['name_release'])
            ## Create logging files
            self.logger_cr = setup_logger('LOG_CR', 'log/'+self.parameters['general_info']['name_release']+'/CR.log')
            self.logger_detail = setup_logger_detail('LOG_INFO', 'log/'+self.parameters['general_info']['name_release']+'/info.log')
            self.logger_error = setup_logger_error('LOG_ERROR', 'log/'+self.parameters['general_info']['name_release']+'/error.log')
            ## Initialize list variables to manage XLR task creation for technical actions - OPS or DBA
            self.list_technical_task_done = []
            ## Initialize list variables to manage XLR SUN task creation for technical actions - OPS or DBA
            self.list_technical_sun_task_done = []
            ## Initialize list variables to manage GROUP XLR TASK creation for CONTROLM - XLDEPLOY TASK
            self.list_xlr_group_task_done = []
            ## Initialize variable to store template URL
            self.template_url = ''
            ## Initialize dictionary variable to validate input YAML file
            self.dic_for_check = {}
            ## Initialize dictionary variable to manage input YAML file
            self.dict_template = {}
            ## Function to validate YAML file
            check_yaml_file(self)
            clear = lambda: os.system('clear')
            clear()
            # super().__init__(parameters)
            self.logger_cr.info("")
            self.logger_cr.info("BEGIN")
            self.logger_cr.info("")
            ## Delete existing template according to YAML variable: name_release
            self.delete_template()
            ## Get folder id defined in YAML ['general_info']['xlr_folder']
            ## and store XLR folder id in self.dict_template['template']['xlr_folder']
            self.find_xlr_folder()
            ## Create template and store template id in self.dict_template['template']['xlr_id'] and in variable: self.XLR_template_id
            self.dict_template,self.XLR_template_id = self.CreateTemplate()
            ## Create variables to manage template environments
            self.create_phase_env_variable()
            ## Create XLR variable release_Variables_in_progress
            self.dict_value_for_template = self.dict_value_for_tempalte()
            self.define_variable_type_template_DYNAMIC()
            self.template_create_variable('release_Variables_in_progress',
                                                'MapStringStringVariable',
                                                '',
                                                '',
                                                self.release_Variables_in_progress,
                                                False,
                                                False,
                                                False )
            ## Create dynamic phase of template
            self.dynamics_phase_done = self.dynamic_phase_dynamic()
            ## Create variables used across tasks
            self.template_create_variable(key='ops_username_api',typev='StringVariable',label='ops_username_api',description='',value=self.ops_username_api,requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='ops_password_api',typev='PasswordStringVariable',label='ops_password_api',description='',value=self.ops_password_api,requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='email_owner_release',typev='StringVariable',label='email_owner_release',description='',value='',requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='xlr_list_phase_selection',typev='StringVariable',label='xlr_list_phase_selection',description='',value='',requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='IUA',typev='StringVariable',label='IUA',description='',value=self.parameters['general_info']['iua'],requiresValue=False,showOnReleaseStart=False,multiline=False )

    def createphase(self,phase):
        """
        Create a specific deployment phase in the XLR template.

        Args:
            phase (str): Phase name to create (DEV, UAT, BENCH, PRODUCTION)

        Returns:
            str: Template URL for the created template

        Handles different phase types:
        - Development phases (BUILD, DEV, UAT): Standard deployment workflow
        - Production phases (BENCH, PRODUCTION): SUN approval workflow integration

        Each phase includes:
        - Gate tasks for validation checkpoints
        - Environment-specific deployment tasks
        - Technical tasks (OPS/DBA) as configured
        - Email notifications
        - Approval workflows for production environments
        """
        ## Counter for step numbers for SUN tasks
        self.count_task = 10
        if phase in[ 'BUILD','DEV','UAT']:
            ## Delete default phase
            self.delete_phase_default_in_template()
            ## Create phase in XLR
            self.add_phase_tasks(phase=phase)
            ## Add XLR GATE task at beginning of phase to validate release after dynamic_release phase
            self.XLR_GateTask(phase=phase,
                              gate_title="Validation_release_template",
                              description='',
                              cond_title= 'Validation_release_template OK',
                              type_task='Validation_release_template',
                              XLR_ID=self.dict_template[phase]['xlr_id_phase'])
            ## Create XLR tasks on phase according to YAML description in 'phase' key
            self.parameter_phase_task(phase)
            self.XLR_GateTask(phase=phase,
                                gate_title='DEV team: Validate installation in '+phase,
                                description='',
                                cond_title= 'DEV team: Validate the delivery in '+ phase,
                                type_task='gate_validation_moe',
                                XLR_ID=self.dict_template[phase]['xlr_id_phase'])
        elif phase == 'BENCH' or phase == 'PRODUCTION':
            self.delete_phase_default_in_template()
            self.add_phase_sun(phase)
            self.parameter_phase_sun(phase)
            self.XLRSun_creation_technical_task(phase,'after_deployment')
            self.XLR_GateTask(phase='CREATE_CHANGE_'+phase,
                              gate_title="Validation creation SNOW  ${"+phase+".sun.id}",
                              description='',
                              cond_title= None,
                              type_task='Validation SNOW creation',
                              XLR_ID=self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'])
            if self.parameters['general_info'].get('Template_standard_id') is not None and phase == 'PRODUCTION':
                self.change_state_sun(phase,'Scheduled')
            else:
                self.change_state_sun(phase,'Initial validation')
                self.change_wait_state(phase,'WaitForInitialChangeApproval')
            self.add_phase_tasks(phase)
            self.XLR_GateTask(phase=phase,
                              gate_title='OPS TASK : Validation of the SNOW ${'+phase+'.sun.id}',
                              description='',
                              cond_title='change put in state deploiement ${'+phase+'.sun.id}',
                              type_task='check_sun_by_ops',
                              XLR_ID=self.dict_template[phase]['xlr_id_phase'])
            if phase == 'BENCH':
                self.change_state_sun(phase,'Scheduled')
            self.change_state_sun(phase,'Implement')
            self.webhook_get_email_ops_on_change(phase)
            self.script_jython_get_email_ops_on_change(phase)
            self.parameter_phase_task(phase)
            self.creation_technical_task(phase,'after_deployment')
            for item in self.parameters['Phases'][phase]:
                    if "email_close_release" in item:
                        email_item = item["email_close_release"]
                        self.task_notification(phase=phase,email_item=email_item,aim='email_close_release')
            if phase != 'BENCH':
                self.XLR_GateTask(phase=phase,
                                gate_title='DEV team: Validate installation in '+phase,
                                description='',
                                cond_title= 'DEV team: Validate the delivery in '+ phase,
                                type_task='gate_validation_moe',
                                XLR_ID=self.dict_template[phase]['xlr_id_phase'])

            for item in self.parameters['Phases'][phase]:
                    if "email_end_release" in item:
                        email_item = item["email_end_release"]
                        self.task_notification(phase=phase,email_item=email_item,aim='email_end_release')
            self.XLRSun_close_sun(phase)
        return self.template_url

    def define_variable_type_template_DYNAMIC(self):
                """
                Define and create XLR template variables based on configuration.

                Creates different types of variables depending on template configuration:
                - Package version variables for deployment tracking
                - SUN change management variables for approval workflows
                - Jenkins integration variables for build parameter passing
                - Release-specific custom variables

                Variable types created:
                - StringVariable: Basic text variables
                - PasswordStringVariable: Secure credential storage
                - ListStringVariable: Multi-selection variables
                - MapStringStringVariable: Key-value pair variables

                The function adapts variable creation based on:
                - Number of packages (single vs multi-package)
                - Template package mode (string vs listbox)
                - Phase configuration (DEV-only vs production)
                - Jenkins name resolution requirements
                """
                if len(self.parameters['template_liste_package']) == 1 and self.parameters['general_info']['template_package_mode'] == 'listbox':
                        if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0] == 'DEV':
                            pass
                        else:
                            XLRGeneric.template_create_variable(self,key=self.dict_value_for_template['package'][0]+'_version', typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)

                elif len(self.parameters['template_liste_package']) == 1 and self.parameters['general_info']['template_package_mode'] == 'string':
                    if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0]  == 'DEV':
                        pass
                    else:
                        self.add_variable_deliverable_item_showOnReleaseStart()
                    list_package = []

                elif self.parameters['general_info']['template_package_mode'] == 'string' :
                        self.add_variable_deliverable_item_showOnReleaseStart()

                elif self.parameters['general_info']['template_package_mode'] == 'listbox' :
                        list_package = []
                        for package,package_value in self.parameters['template_liste_package'].items():
                            list_package.append(package)
                            XLRGeneric.template_create_variable(self,key=package+'_version', typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)

                if 'BENCH' in self.parameters['general_info']['phases'] or 'PRODUCTION' in self.parameters['general_info']['phases']:
                    if 'DEV' not in self.parameters['general_info']['phases'] or 'UAT' not in self.parameters['general_info']['phases']:
                        XLRGeneric.template_create_variable(self,key='Title_SUN_CHANGE', typev='StringVariable', label='Title_SUN_CHANGE', description='Title in SUN change', value='', requiresValue=True, showOnReleaseStart=True, multiline=False)
                        XLRGeneric.template_create_variable(self,key='Long_description_SUN_CHANGE', typev='StringVariable', label='Description in SUN change', description='', value='', requiresValue=True, showOnReleaseStart=True, multiline=True)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and 'BENCH' in self.parameters['general_info']['phases']  and len(self.parameters['general_info']['phases']) != 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=False, showOnReleaseStart=True, multiline=False)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and len(self.parameters['general_info']['phases']) == 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=True, showOnReleaseStart=True, multiline=False)
                    else:
                        XLRGeneric.template_create_variable(self,key='Title_SUN_CHANGE', typev='StringVariable', label='Title_SUN_CHANGE', description='Title in SUN change', value='', requiresValue=False, showOnReleaseStart=True, multiline=False)
                        XLRGeneric.template_create_variable(self,key='Long_description_SUN_CHANGE', typev='StringVariable', label='Description in SUN change', description='', value='', requiresValue=False, showOnReleaseStart=True, multiline=True)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and 'BENCH' in self.parameters['general_info']['phases']  and len(self.parameters['general_info']['phases']) != 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=False, showOnReleaseStart=True, multiline=False)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and len(self.parameters['general_info']['phases']) == 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=True, showOnReleaseStart=True, multiline=False)

                if self.parameters.get('variable_release') is not None:
                    for variable in self.parameters['variable_release']:
                        if variable == 'Date':
                             requiresValue = False
                             showOnReleaseStart = False
                             value = None
                        else:
                             requiresValue = True
                             showOnReleaseStart = True
                             value = self.parameters['variable_release'][variable]
                        XLRGeneric.template_create_variable(self,key=variable, typev='StringVariable', label='', description='', value=value, requiresValue=requiresValue, showOnReleaseStart=showOnReleaseStart, multiline=False)

                self.name_from_jenkins_value = 'no'
                for package,package_value in self.parameters['template_liste_package'].items():
                    if  package in self.release_Variables_in_progress['list_package']:
                        if package_value.get('mode') is not None:
                            if package_value['mode'] == 'name_from_jenkins':
                                self.name_from_jenkins_value = 'yes'
                                XLRGeneric.template_create_variable(self,key='VARIABLE_XLR_ID_'+package+'_version',
                                                                    typev='StringVariable',
                                                                    label='',
                                                                    description='',
                                                                    value='',
                                                                    requiresValue=False,
                                                                    showOnReleaseStart=False,
                                                                    multiline=False)


    def dynamic_phase_dynamic(self):
        """
        Create the dynamic_release phase for template customization.

        Returns:
            str: 'done' when phase creation is complete, or None if skipped

        The dynamic_release phase contains Jython scripts that customize the template
        at runtime based on user selections. This phase handles:

        - Phase deletion: Removes unselected phases from the release
        - Package filtering: Removes unselected packages from deployment
        - Jenkins job management: Removes unnecessary build jobs
        - Control-M task management: Removes unneeded batch job tasks
        - XLD task management: Removes unselected deployment tasks
        - Technical task management: Removes unselected technical tasks
        - Variable initialization: Sets up runtime variables

        The dynamic phase is skipped if:
        - Only one phase is configured
        - Only one package is configured
        - No technical tasks are configured

        This allows for simplified templates when dynamic behavior is not needed.
        """
        ## Create a dictionary variable to manage creation of XLR tasks for technical OPS and DBA tasks
        self.dict_value_for_template_technical_task = self.dict_value_for_tempalte_technical_task()
         ## No dynamic phase if there is only one phase, one package and technical_task does not exist
        if self.dict_value_for_template_technical_task.get('technical_task') is None and len(self.dict_value_for_template.get('template_liste_phase')) == 1 and len(self.list_package) == 1:
            pass
        else:
            ## Create dynamic_release phase to add jython tasks
            self.dict_template = self.add_phase_tasks('dynamic_release')
            ## If we have jenkins and package name is provided by jenkins to XLR
            ## key:value 'mode : name_from_jenkins' present in template_liste_package
            ## Create task to retrieve XLD ids of variables type: 'VARIABLE_XLR_ID_'+package+'_version' in release
            ## which will be transmitted through jenkins jobs
            if self.name_from_jenkins_value == "yes":
                XLRTaskScript.task_xlr_if_name_from_jenkins(self,'dynamic_release')
            ## Create jython task to manage deletion of phases not requested at release start
            if len( self.parameters['general_info']['phases']) > 1:
                ## Case where in YAML we set phase_mode: one_list (choice list)
                if self.parameters['general_info']['phase_mode'] == 'one_list':
                    if self.parameters['general_info']['template_package_mode'] == 'string':
                            XLRDynamicPhase.XLRJython_delete_phase_one_list_template_package_mode_string(self,'dynamic_release')
                    else:
                        XLRDynamicPhase.XLRJython_delete_phase_one_list(self,'dynamic_release')
                ## Case where in YAML we set phase_mode: multi_list one list per ENV defined in general_info/phases
                elif  self.parameters['general_info']['phase_mode'] == 'multi_list':
                    XLRDynamicPhase.XLRJython_delete_phase_list_multi_list(self,'dynamic_release')
            ## Create jython task to create a package list managed by release
            if self.parameters['general_info']['template_package_mode']  == 'string':
                    if len(self.parameters['template_liste_package']) > 1:
                        XLRDynamicPhase.script_jython_List_package_string(self,'dynamic_release')
            ## Case for creation, jython task to define environment prefix for BENCH P or Q according to choice made at release start MCO or PRJ
            if 'BENCH' in self.parameters['general_info']['phases'] and (self.parameters.get('XLD_ENV_BENCH') is not None and len(self.parameters['XLD_ENV_BENCH']) >= 2):
                XLRDynamicPhase.script_jython_define_xld_prefix_new(self,'dynamic_release')
                XLRGeneric.template_create_variable(self,key='controlm_prefix_BENCH', typev='StringVariable', label='controlm_prefix_BENCH', description='', value='B', requiresValue=False, showOnReleaseStart=False, multiline=False)
            ## Create XLR jython task to delete unnecessary jenkins jobs if jenkins section is filled in YAML
            ## If there is more than one package, otherwise it means template only manages one package, so no need for task to delete jenkins
            ## And if DEV phase is requested in YAML in general_info/phases section
            if self.parameters.get('jenkins') is not None:
                if len(self.parameters['template_liste_package']) > 1:
                    if 'DEV' in self.parameters['general_info']['phases']  or 'BUILD' in self.parameters['general_info']['phases']:
                            if self.parameters['general_info']['template_package_mode'] == 'string':
                                XLRDynamicPhase.script_jython_dynamic_delete_task_jenkins_string(self,'dynamic_release')
                            elif self.parameters['general_info']['template_package_mode'] == 'listbox':
                                XLRDynamicPhase.script_jython_dynamic_delete_task_jenkins_listbox(self,'dynamic_release')
            ## Create XLR jython task to manage deletion of XLR Controlm tasks if present in YAML
            ## key : XLR_task_controlm present in YAML
            if  self.dict_value_for_template.get('controlm') is not None and len(self.dict_value_for_template['controlm']) !=0:
                    if self.parameters.get('XLD_ENV_BENCH') and len(self.parameters['XLD_ENV_BENCH']) >2:
                        XLRDynamicPhase.script_jython_dynamic_delete_task_controlm_multibench(self,'dynamic_release')
                    else:
                        XLRDynamicPhase.script_jython_dynamic_delete_task_controlm(self,'dynamic_release')
            ## Create XLR jython task to delete XLR XLD tasks according to packages requested in release
            if len(self.parameters['template_liste_package']) > 1:
                XLRDynamicPhase.script_jython_dynamic_delete_task_xld(self,'dynamic_release')

            if  self.parameters.get('technical_task_list') is not None:
                XLRGeneric.template_create_variable(self,key='dict_value_for_template_technical_task',typev='StringVariable',label='dict_value_for_template_technical_task',description='',value=self.dict_value_for_template_technical_task,requiresValue=False,showOnReleaseStart=False,multiline=False )

                if ('PRODUCTION' in self.parameters['general_info']['phases'] or 'BENCH' in self.parameters['general_info']['phases']) and self.parameters['general_info']['technical_task_mode'] == 'listbox':
                    XLRDynamicPhase.XLRJythonScript_release_delete_technical_task_ListStringVariable(self,'dynamic_release')
                elif ('PRODUCTION' in self.parameters['general_info']['phases'] or 'BENCH' in self.parameters['general_info']['phases']) and self.parameters['general_info']['technical_task_mode'] == 'string':
                    XLRDynamicPhase.XLRJythonScript_dynamic_release_delete_technical_task_StringVariable(self,'dynamic_release')

            if self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH' :
                XLRTaskScript.script_jython_put_value_version(self,'dynamic_release')
            if self.parameters.get('variable_release') is not None and 'Date' in self.parameters['variable_release']:
                XLRTaskScript.script_jython_define_variable_release(self,'dynamic_release')
            return 'done'


if __name__ == "__main__":
    """
    Main execution block for XLR template generation.

    Command line usage:
        python3 DYNAMIC_template.py --infile template.yaml

    Process:
    1. Parse command line arguments to get YAML configuration file
    2. Load and validate YAML configuration
    3. Set up logging infrastructure for the release
    4. Initialize XLR template creation process
    5. Create each configured phase in sequence
    6. Log completion status and template URL

    Exit codes:
    - 0: Success
    - 10: YAML parsing error
    - Other: Various XLR API or configuration errors
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate XLR deployment templates from YAML configuration"
    )
    parser.add_argument('--infile', nargs=1,
                        help="YAML file to be processed",
                        type=argparse.FileType('r'),
                        required=True)
    arguments = parser.parse_args()

    # Load and validate YAML configuration
    try:
        parameters_yaml = yaml.safe_load(arguments.infile[0])
    except yaml.YAMLError as e:
        print('Error Loading file, it s not yaml reading format:', e)
        print('Please change your file defintion.')
        sys.exit(10)

    # Convert YAML to JSON and back to ensure proper data structure
    json_data = json.dumps(parameters_yaml)
    parameters = json.loads(json_data)

    # Set up logging directory for this release
    log_dir = 'log/' + parameters['general_info']['name_release']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Initialize main logger
    logger = setup_logger('LOG_START', log_dir + '/CR.log')

    # Create XLR template instance and process all phases
    CreateTemplate = XLRCreateTemplate(parameters)
    template_url = None

    # Create each phase defined in the configuration
    for phase in parameters['general_info']['phases']:
        template_url = CreateTemplate.createphase(phase)

    # Log successful completion
    logger.info("---------------------------")
    logger.info("END CREATION TEMPLATE : OK")
    logger.info("---------------------------")
    logger.info(parameters['general_info']['name_release'])
    logger.info(template_url)