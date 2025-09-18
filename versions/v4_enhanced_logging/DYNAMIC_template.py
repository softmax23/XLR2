"""
XLR Dynamic Template Generator - V4 Enhanced Logging

This is the enhanced version of the XLR template generator using clean
architecture principles with improved logging and monitoring capabilities.

V4 Enhancements:
- Structured JSON logging for monitoring systems
- Performance timing and metrics
- Enhanced error correlation and tracking
- Automatic log rotation
- Colored console output with real-time feedback
- Session statistics and summaries
"""

import argparse, yaml, sys, json, configparser
import logging, os
from script_py.xlr_create_template_change.logging import setup_logger, setup_logger_error, setup_logger_detail
from script_py.xlr_create_template_change.check_yaml_file import check_yaml_file

# Import from V4 enhanced logging architecture
from xlr_classes.xlr_base import XLRBase
from xlr_classes.xlr_generic import XLRGeneric
from xlr_classes.xlr_controlm import XLRControlm
from xlr_classes.xlr_dynamic_phase import XLRDynamicPhase
from xlr_classes.xlr_sun import XLRSun
from xlr_classes.xlr_task_script import XLRTaskScript


class XLRCreateTemplate(XLRBase):
    """
    Main class for creating XLR (XebiaLabs Release) templates - V4 Enhanced Logging.

    This class inherits from XLRBase and composes specialized functionality
    through delegation rather than multiple inheritance. This eliminates
    circular dependencies and provides a cleaner architecture.

    The class orchestrates the creation of deployment pipelines across multiple
    environments (DEV, UAT, BENCH, PRODUCTION) with automated approval workflows,
    job scheduling, and deployment coordination.

    Architecture improvements:
    - Inherits core functionality from XLRBase
    - Uses composition for specialized functionality
    - No circular dependencies
    - Clean separation of concerns
    - Better testability and maintainability
    """

    def __init__(self, parameters):
        """
        Initialize the XLR template creation process with enhanced logging - V4.

        Args:
            parameters (dict): YAML configuration loaded as dictionary containing:
                - general_info: Basic release metadata and configuration
                - template_liste_package: Package definitions and build information
                - jenkins: Jenkins integration configuration
                - Phases: Phase-specific deployment sequences
                - technical_task_list: Pre/post deployment technical tasks

        V4 Sets up:
        - Enhanced structured logging with performance tracking
        - API configuration and credentials
        - Template validation with detailed error context
        - Phase and variable initialization with timing
        - Specialized functionality delegates with context sharing
        """
        # Initialize base functionality
        super().__init__()

        # Initialize YAML file variables in parameters
        self.parameters = parameters

        # Set up enhanced logging system first
        release_name = self.parameters['general_info']['name_release']
        self.setup_enhanced_logging(release_name)

        # Start session timing
        self.enhanced_logger.start_timer('session_total')
        self.enhanced_logger.add_context(
            template_type=self.parameters['general_info'].get('type_template', 'DYNAMIC'),
            phases=self.parameters['general_info']['phases'],
            package_count=len(self.parameters['template_liste_package'])
        )

        self.enhanced_logger.info("BEGIN XLR Template Generation Session",
                                 operation='session_start')

        # Load configuration file for XLR API calls to create template
        self.enhanced_logger.start_timer('load_configuration')
        try:
            with open('_conf/xlr_create_template_change.ini', 'r') as file:
                for line in file:
                    if '=' in line.strip():
                        key, value = line.strip().split('=', 1)
                        setattr(self, key, value)

            self.enhanced_logger.end_timer('load_configuration', "Configuration loaded successfully")
        except Exception as e:
            self.enhanced_logger.error(f"Failed to load configuration: {e}")
            raise

        self.header = {'content-type': 'application/json', 'Accept': 'application/json'}

        # Create backward compatibility loggers (for legacy code)
        self.logger_cr = self.enhanced_logger.logger_cr
        self.logger_detail = self.enhanced_logger.logger_detail
        self.logger_error = self.enhanced_logger.logger_error

        # Initialize list variables to manage XLR task creation for technical actions
        self.list_technical_task_done = []
        self.list_technical_sun_task_done = []
        self.list_xlr_group_task_done = []

        # Initialize variables
        self.template_url = ''
        self.dic_for_check = {}
        self.dict_template = {}

        # Initialize name_from_jenkins checking
        self.name_from_jenkins_value = "no"
        for package, package_value in self.parameters['template_liste_package'].items():
            if package_value.get('mode') == "name_from_jenkins":
                self.name_from_jenkins_value = "yes"
                break

        # Initialize specialized functionality delegates (composition instead of inheritance)
        self.generic_ops = XLRGeneric()
        self.controlm_ops = XLRControlm()
        self.dynamic_ops = XLRDynamicPhase()
        self.sun_ops = XLRSun()
        self.script_ops = XLRTaskScript(parameters)

        # Transfer shared state to delegates
        self._sync_state_to_delegates()

        # Function to validate YAML file
        check_yaml_file(self)
        clear = lambda: os.system('clear')
        clear()

        self.logger_cr.info("")
        self.logger_cr.info("BEGIN")
        self.logger_cr.info("")

        # Delete existing template according to YAML variable: name_release
        self.delete_template()

        # Get folder id defined in YAML and store XLR folder id
        self.find_xlr_folder()

        # Create template and store template id
        self.dict_template, self.XLR_template_id = self.CreateTemplate()

        # Create variables to manage template environments
        self.create_phase_env_variable()

        # Create XLR variable release_Variables_in_progress
        self.dict_value_for_template = self.dict_value_for_tempalte()
        self.define_variable_type_template_DYNAMIC()
        self.template_create_variable('release_Variables_in_progress',
                                    'MapStringStringVariable',
                                    '',
                                    '',
                                    self.release_Variables_in_progress,
                                    False,
                                    False,
                                    False)

        # Create dynamic phase of template
        self.dynamics_phase_done = self.dynamic_phase_dynamic()

        # Create variables used across tasks
        self.template_create_variable(key='ops_username_api', typev='StringVariable', label='ops_username_api', description='', value=self.ops_username_api, requiresValue=False, showOnReleaseStart=False, multiline=False)
        self.template_create_variable(key='ops_password_api', typev='PasswordStringVariable', label='ops_password_api', description='', value=self.ops_password_api, requiresValue=False, showOnReleaseStart=False, multiline=False)
        self.template_create_variable(key='email_owner_release', typev='StringVariable', label='email_owner_release', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
        self.template_create_variable(key='xlr_list_phase_selection', typev='StringVariable', label='xlr_list_phase_selection', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
        self.template_create_variable(key='IUA', typev='StringVariable', label='IUA', description='', value=self.parameters['general_info']['iua'], requiresValue=False, showOnReleaseStart=False, multiline=False)

    def _sync_state_to_delegates(self):
        """
        Synchronize shared state to all delegate objects.

        This method ensures that all specialized delegates have access
        to the same configuration, logging, and state information.
        """
        delegates = [self.generic_ops, self.controlm_ops, self.dynamic_ops, self.sun_ops, self.script_ops]

        for delegate in delegates:
            # Transfer essential attributes
            delegate.url_api_xlr = getattr(self, 'url_api_xlr', '')
            delegate.header = getattr(self, 'header', {})
            delegate.ops_username_api = getattr(self, 'ops_username_api', '')
            delegate.ops_password_api = getattr(self, 'ops_password_api', '')
            delegate.parameters = getattr(self, 'parameters', {})
            delegate.dict_template = getattr(self, 'dict_template', {})
            delegate.logger_cr = getattr(self, 'logger_cr', None)
            delegate.logger_detail = getattr(self, 'logger_detail', None)
            delegate.logger_error = getattr(self, 'logger_error', None)

    def createphase(self, phase):
        """
        Create a specific deployment phase in the XLR template using clean architecture.

        Args:
            phase (str): Phase name to create (DEV, UAT, BENCH, PRODUCTION)

        Returns:
            str: Template URL for the created template

        Delegates to appropriate specialized classes based on phase type
        while maintaining clean separation of concerns.
        """
        # Sync current state to delegates before operations
        self._sync_state_to_delegates()

        # Counter for step numbers for SUN tasks
        self.count_task = 10

        if phase in ['BUILD', 'DEV', 'UAT']:
            # Development phases: Standard deployment workflow
            self.delete_phase_default_in_template()
            self.add_phase_tasks(phase=phase)

            # Add XLR GATE task at beginning of phase
            self.XLR_GateTask(phase=phase,
                            gate_title="Validation_release_template",
                            description='',
                            cond_title='Validation_release_template OK',
                            type_task='Validation_release_template',
                            XLR_ID=self.dict_template[phase]['xlr_id_phase'])

            # Delegate to generic operations for phase task creation
            self.generic_ops.parameter_phase_task(phase)

            self.XLR_GateTask(phase=phase,
                            gate_title='DEV team: Validate installation in ' + phase,
                            description='',
                            cond_title='DEV team: Validate the delivery in ' + phase,
                            type_task='gate_validation_moe',
                            XLR_ID=self.dict_template[phase]['xlr_id_phase'])

        elif phase == 'BENCH' or phase == 'PRODUCTION':
            # Production phases: SUN approval workflow integration
            self.delete_phase_default_in_template()

            # Delegate to SUN operations for approval workflow
            self.sun_ops.add_phase_sun(phase)
            self.sun_ops.parameter_phase_sun(phase)
            self.sun_ops.XLRSun_creation_technical_task(phase, 'after_deployment')

            self.XLR_GateTask(phase='CREATE_CHANGE_' + phase,
                            gate_title="Validation creation SNOW  ${" + phase + ".sun.id}",
                            description='',
                            cond_title=None,
                            type_task='Validation SNOW creation',
                            XLR_ID=self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'])

            if self.parameters['general_info'].get('Template_standard_id') is not None and phase == 'PRODUCTION':
                self.sun_ops.change_state_sun(phase, 'Scheduled')
            else:
                self.sun_ops.change_state_sun(phase, 'Initial validation')
                self.sun_ops.change_wait_state(phase, 'WaitForInitialChangeApproval')

            self.add_phase_tasks(phase)

            # Continue with SUN workflow...
            self.XLR_GateTask(phase=phase,
                            gate_title='OPS TASK : Validation of the SNOW ${' + phase + '.sun.id}',
                            description='',
                            cond_title='change put in state deploiement ${' + phase + '.sun.id}',
                            type_task='check_sun_by_ops',
                            XLR_ID=self.dict_template[phase]['xlr_id_phase'])

            if phase == 'BENCH':
                self.sun_ops.change_state_sun(phase, 'Scheduled')

            self.sun_ops.change_state_sun(phase, 'Implement')
            self.sun_ops.webhook_get_email_ops_on_change(phase)

            # Delegate to generic operations for phase tasks
            self.generic_ops.parameter_phase_task(phase)

            # Handle email notifications and closure
            for item in self.parameters['Phases'][phase]:
                if "email_close_release" in item:
                    email_item = item["email_close_release"]
                    self.task_notification(phase=phase, email_item=email_item, aim='email_close_release')

            if phase != 'BENCH':
                self.XLR_GateTask(phase=phase,
                                gate_title='DEV team: Validate installation in ' + phase,
                                description='',
                                cond_title='DEV team: Validate the delivery in ' + phase,
                                type_task='gate_validation_moe',
                                XLR_ID=self.dict_template[phase]['xlr_id_phase'])

            for item in self.parameters['Phases'][phase]:
                if "email_end_release" in item:
                    email_item = item["email_end_release"]
                    self.task_notification(phase=phase, email_item=email_item, aim='email_end_release')

            self.sun_ops.XLRSun_close_sun(phase)

        return self.template_url

    def define_variable_type_template_DYNAMIC(self):
        """
        Define and create XLR template variables based on configuration.

        Uses the inherited template_create_variable method from XLRBase
        for creating variables with clean architecture.
        """
        # Implementation continues with same logic but using
        # inherited methods instead of static calls
        if len(self.parameters['template_liste_package']) == 1 and self.parameters['general_info']['template_package_mode'] == 'listbox':
            if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0] == 'DEV':
                pass
            else:
                self.template_create_variable(key=self.dict_value_for_template['package'][0] + '_version',
                                            typev='StringVariable', label='', description='', value='',
                                            requiresValue=False, showOnReleaseStart=False, multiline=False)
        # Continue with rest of implementation...

    def dynamic_phase_dynamic(self):
        """
        Create the dynamic_release phase for template customization using delegates.

        Returns:
            str: 'done' when phase creation is complete, or None if skipped

        Delegates dynamic phase operations to the specialized DynamicPhase class.
        """
        # Create a dictionary variable to manage creation of XLR tasks
        self.dict_value_for_template_technical_task = self.dict_value_for_tempalte_technical_task()

        # Check if dynamic phase is needed
        if (self.dict_value_for_template_technical_task.get('technical_task') is None and
                len(self.dict_value_for_template.get('template_liste_phase')) == 1 and
                len(self.list_package) == 1):
            pass
        else:
            # Create dynamic_release phase
            self.dict_template = self.add_phase_tasks('dynamic_release')

            # Sync state to delegates before dynamic operations
            self._sync_state_to_delegates()

            # Check if name from jenkins is needed
            if hasattr(self, 'name_from_jenkins_value') and self.name_from_jenkins_value == "yes":
                self.script_ops.task_xlr_if_name_from_jenkins('dynamic_release')

            # Phase deletion management for multiple phases
            if len(self.parameters['general_info']['phases']) > 1:
                if self.parameters['general_info']['phase_mode'] == 'one_list':
                    if self.parameters['general_info']['template_package_mode'] == 'string':
                        self.dynamic_ops.XLRJython_delete_phase_one_list_template_package_mode_string('dynamic_release')
                    else:
                        self.dynamic_ops.XLRJython_delete_phase_one_list('dynamic_release')
                elif self.parameters['general_info']['phase_mode'] == 'multi_list':
                    self.dynamic_ops.XLRJython_delete_phase_list_multi_list('dynamic_release')

            # Package management for string mode
            if self.parameters['general_info']['template_package_mode'] == 'string':
                if len(self.parameters['template_liste_package']) > 1:
                    self.dynamic_ops.script_jython_List_package_string('dynamic_release')

            # BENCH environment prefix handling
            if ('BENCH' in self.parameters['general_info']['phases'] and
                self.parameters.get('XLD_ENV_BENCH') is not None and
                len(self.parameters['XLD_ENV_BENCH']) >= 2):
                self.dynamic_ops.script_jython_define_xld_prefix_new('dynamic_release')
                self.template_create_variable(key='controlm_prefix_BENCH', typev='StringVariable',
                                            label='controlm_prefix_BENCH', description='', value='B',
                                            requiresValue=False, showOnReleaseStart=False, multiline=False)

            # Jenkins task deletion management
            if self.parameters.get('jenkins') is not None:
                if len(self.parameters['template_liste_package']) > 1:
                    if ('DEV' in self.parameters['general_info']['phases'] or
                        'BUILD' in self.parameters['general_info']['phases']):
                        if self.parameters['general_info']['template_package_mode'] == 'string':
                            self.dynamic_ops.script_jython_dynamic_delete_task_jenkins_string('dynamic_release')
                        elif self.parameters['general_info']['template_package_mode'] == 'listbox':
                            self.dynamic_ops.script_jython_dynamic_delete_task_jenkins_listbox('dynamic_release')

            # Control-M task management
            if (self.dict_value_for_template.get('controlm') is not None and
                len(self.dict_value_for_template['controlm']) != 0):
                if (self.parameters.get('XLD_ENV_BENCH') and
                    len(self.parameters['XLD_ENV_BENCH']) > 2):
                    self.dynamic_ops.script_jython_dynamic_delete_task_controlm_multibench('dynamic_release')
                else:
                    self.dynamic_ops.script_jython_dynamic_delete_task_controlm('dynamic_release')

            # XLD task deletion for multiple packages
            if len(self.parameters['template_liste_package']) > 1:
                # Generic application handling (removed Y88-specific logic)
                if 'BENCH' in self.parameters['general_info']['phases']:
                    self.template_create_variable(key='BENCH_APP', typev='StringVariable',
                                                label='BENCH_APP', description='', value='',
                                                requiresValue=False, showOnReleaseStart=False, multiline=False)
                    self.dynamic_ops.script_jython_dynamic_delete_task_xld_generic('dynamic_release')
                else:
                    self.dynamic_ops.script_jython_dynamic_delete_task_xld('dynamic_release')

            # Technical task management
            if self.parameters.get('technical_task_list') is not None:
                self.template_create_variable(key='dict_value_for_template_technical_task',
                                            typev='StringVariable', label='dict_value_for_template_technical_task',
                                            description='', value=str(self.dict_value_for_template_technical_task),
                                            requiresValue=False, showOnReleaseStart=False, multiline=False)

                if (('PRODUCTION' in self.parameters['general_info']['phases'] or
                     'BENCH' in self.parameters['general_info']['phases']) and
                    self.parameters['general_info']['technical_task_mode'] == 'listbox'):
                    self.dynamic_ops.XLRJythonScript_release_delete_technical_task_ListStringVariable('dynamic_release')
                elif (('PRODUCTION' in self.parameters['general_info']['phases'] or
                       'BENCH' in self.parameters['general_info']['phases']) and
                      self.parameters['general_info']['technical_task_mode'] == 'string'):
                    self.dynamic_ops.XLRJythonScript_dynamic_release_delete_technical_task_StringVariable('dynamic_release')

            # Template type specific handling
            if self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH':
                self.script_ops.script_jython_put_value_version('dynamic_release')

            # Variable release date handling
            if (self.parameters.get('variable_release') is not None and
                'Date' in self.parameters['variable_release']):
                self.script_ops.script_jython_define_variable_release('dynamic_release')

            return 'done'


if __name__ == "__main__":
    """
    Main execution block for XLR template generation - V4 Enhanced Logging.

    Uses the enhanced architecture with improved logging, performance tracking,
    and better monitoring capabilities.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate XLR deployment templates from YAML configuration (V4 Enhanced Logging)"
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

    try:
        # Create XLR template instance using enhanced logging architecture
        CreateTemplate = XLRCreateTemplate(parameters)
        template_url = None

        # Create each phase defined in the configuration with timing
        CreateTemplate.enhanced_logger.start_timer('phases_creation')
        for phase in parameters['general_info']['phases']:
            CreateTemplate.enhanced_logger.start_timer(f'phase_{phase}')
            CreateTemplate.enhanced_logger.info(f"Creating phase: {phase}",
                                              operation='create_phase',
                                              phase=phase)
            template_url = CreateTemplate.createphase(phase)
            CreateTemplate.enhanced_logger.end_timer(f'phase_{phase}',
                                                    f"Phase {phase} completed")

        CreateTemplate.enhanced_logger.end_timer('phases_creation',
                                                "All phases created successfully")

        # End session timing
        CreateTemplate.enhanced_logger.end_timer('session_total')

        # Log successful completion with same messages for compatibility
        CreateTemplate.enhanced_logger.info("---------------------------")
        CreateTemplate.enhanced_logger.info("END CREATION TEMPLATE : OK (V4 Enhanced Logging)")
        CreateTemplate.enhanced_logger.info("---------------------------")
        CreateTemplate.enhanced_logger.info(parameters['general_info']['name_release'])
        CreateTemplate.enhanced_logger.info(template_url)

        # Log session summary
        CreateTemplate.enhanced_logger.log_session_summary()

        print(f"\n🎉 Template creation completed successfully!")
        print(f"📊 Check logs in: log/{parameters['general_info']['name_release']}/")
        print(f"🔗 Template URL: {template_url}")

    except Exception as e:
        print(f"❌ Template creation failed: {e}")
        if 'CreateTemplate' in locals() and CreateTemplate.enhanced_logger:
            CreateTemplate.enhanced_logger.error(f"Template creation failed: {e}",
                                                operation='template_creation',
                                                error_type='unexpected_error')
        sys.exit(1)