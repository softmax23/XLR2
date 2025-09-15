


import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

import yaml

from script_py.xlr_create_template_change.logging import (
    setup_logger,
    setup_logger_error,
    setup_logger_detail
)
from script_py.xlr_create_template_change.check_yaml_file import check_yaml_file
from all_class import (
    XLRGeneric,
    XLRControlm,
    XLRDynamicPhase,
    XLRSun,
    XLRTaskScript
)
class XLRCreateTemplate(XLRGeneric, XLRSun, XLRTaskScript, XLRControlm, XLRDynamicPhase):
    """
    XLR Template Creation and Management Class

    This class handles the creation and configuration of XLR templates
    based on YAML configuration files.
    """

    CONFIG_FILE_PATH = '_conf/xlr_create_template_change.ini'

    def __init__(self, parameters: Dict[str, Any]):
        self._validate_parameters(parameters)
        self._load_configuration()
        self.parameters = parameters
        self._setup_logging()
        self._initialize_variables()
        self._setup_template()

    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate required parameters in the YAML configuration."""
        required_keys = ['general_info']
        for key in required_keys:
            if key not in parameters:
                raise ValueError(f"Missing required key '{key}' in parameters")

        general_info = parameters['general_info']
        required_general_keys = ['name_release', 'phases']
        for key in required_general_keys:
            if key not in general_info:
                raise ValueError(f"Missing required key 'general_info.{key}' in parameters")

    def _load_configuration(self) -> None:
        """Load configuration from INI file with proper error handling."""
        config_path = Path(self.CONFIG_FILE_PATH)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.CONFIG_FILE_PATH}")

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if line and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            setattr(self, key.strip(), value.strip())
                        except ValueError:
                            logging.warning(f"Invalid line {line_num} in config file: {line}")
        except IOError as e:
            raise IOError(f"Error reading configuration file: {e}")

    def _setup_logging(self) -> None:
        """Setup logging directories and loggers."""
        self.header = {
            'content-type': 'application/json',
            'Accept': 'application/json'
        }

        log_dir = Path('log') / self.parameters['general_info']['name_release']
        log_dir.mkdir(parents=True, exist_ok=True)

        base_path = str(log_dir)
        self.logger_cr = setup_logger('LOG_CR', f'{base_path}/CR.log')
        self.logger_detail = setup_logger_detail('LOG_INFO', f'{base_path}/info.log')
        self.logger_error = setup_logger_error('LOG_ERROR', f'{base_path}/error.log')

    def _initialize_variables(self) -> None:
        """Initialize class variables and data structures."""
        self.list_technical_task_done = []
        self.list_technical_sun_task_done = []
        self.list_xlr_group_task_done = []
        self.template_url = ''
        self.dic_for_check = {}
        self.dict_template = {}
        self.name_from_jenkins_value = 'no'

    def _setup_template(self) -> None:
        """Setup and initialize the XLR template."""
        try:
            check_yaml_file(self)
            self._clear_screen()

            self.logger_cr.info("")
            self.logger_cr.info("BEGIN TEMPLATE CREATION")
            self.logger_cr.info("")

            self._initialize_template_components()
            self._create_template_variables()

        except Exception as e:
            self.logger_error.error(f"Error during template setup: {e}")
            raise

    def _clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def _initialize_template_components(self) -> None:
        """Initialize core template components."""
        self.delete_template()
        self.find_xlr_folder()
        self.dict_template, self.XLR_template_id = self.CreateTemplate()
        self.create_phase_env_variable()

        self.dict_value_for_template = self.dict_value_for_tempalte()
        self.define_variable_type_template_DYNAMIC()

        self.template_create_variable(
            'release_Variables_in_progress',
            'MapStringStringVariable',
            '', '',
            self.release_Variables_in_progress,
            False, False, False
        )

        self.dynamics_phase_done = self.dynamic_phase_dynamic()

    def _create_template_variables(self) -> None:
        """Create standard template variables."""
        variables_config = [
            ('ops_username_api', 'StringVariable', getattr(self, 'ops_username_api', '')),
            ('ops_password_api', 'PasswordStringVariable', getattr(self, 'ops_password_api', '')),
            ('email_owner_release', 'StringVariable', ''),
            ('xlr_list_phase_selection', 'StringVariable', ''),
            ('IUA', 'StringVariable', self.parameters['general_info'].get('iua', ''))
        ]

        for var_name, var_type, var_value in variables_config:
            self.template_create_variable(
                key=var_name,
                typev=var_type,
                label=var_name,
                description='',
                value=var_value,
                requiresValue=False,
                showOnReleaseStart=False,
                multiline=False
            )
    def createphase(self, phase: str) -> str:
        """
        Create and configure a specific phase in the XLR template.

        Args:
            phase: The phase name to create (BUILD, DEV, UAT, BENCH, PRODUCTION)

        Returns:
            The template URL after phase creation
        """
        self.count_task = 10

        if phase in ['BUILD', 'DEV', 'UAT']:
            return self._create_development_phase(phase)
        elif phase in ['BENCH', 'PRODUCTION']:
            return self._create_production_phase(phase)
        else:
            raise ValueError(f"Unknown phase: {phase}")

    def _create_development_phase(self, phase: str) -> str:
        """
        Create a development phase (BUILD, DEV, UAT).

        Args:
            phase: The development phase name

        Returns:
            The template URL
        """
        self.delete_phase_default_in_template()
        self.add_phase_tasks(phase=phase)

        # Add validation gate at the beginning
        self._add_validation_gate(phase, "Validation_release_template")

        # Create phase tasks based on YAML configuration
        self.parameter_phase_task(phase)

        # Add final validation gate
        self._add_development_validation_gate(phase)

        return self.template_url

    def _add_validation_gate(self, phase: str, gate_title: str) -> None:
        """
        Add a validation gate to a phase.

        Args:
            phase: The phase name
            gate_title: The title of the validation gate
        """
        self.XLR_GateTask(
            phase=phase,
            gate_title=gate_title,
            description='',
            cond_title=f'{gate_title} OK',
            type_task='Validation_release_template',
            XLR_ID=self.dict_template[phase]['xlr_id_phase']
        )

    def _add_development_validation_gate(self, phase: str) -> None:
        """
        Add development team validation gate.

        Args:
            phase: The phase name
        """
        self.XLR_GateTask(
            phase=phase,
            gate_title=f'DEV team: Validate installation in {phase}',
            description='',
            cond_title=f'DEV team: Validate the delivery in {phase}',
            type_task='gate_validation_moe',
            XLR_ID=self.dict_template[phase]['xlr_id_phase']
        )

    def _create_production_phase(self, phase: str) -> str:
        """
        Create a production phase (BENCH, PRODUCTION).

        Args:
            phase: The production phase name

        Returns:
            The template URL
        """
        self.delete_phase_default_in_template()
        self.add_phase_sun(phase)
        self.parameter_phase_sun(phase)
        self.XLRSun_creation_technical_task(phase, 'after_deployment')

        # Add SNOW validation gate
        self._add_snow_validation_gate(phase)

        # Configure SUN change state based on template type
        self._configure_sun_change_state(phase)

        self.add_phase_tasks(phase)

        # Add OPS validation gate
        self._add_ops_validation_gate(phase)

        # Configure change states and notifications
        self._configure_phase_states_and_notifications(phase)

        # Add final validations and notifications
        self._add_final_phase_validations(phase)

        self.XLRSun_close_sun(phase)
        return self.template_url

    def _add_snow_validation_gate(self, phase: str) -> None:
        """
        Add SNOW validation gate for production phases.

        Args:
            phase: The phase name
        """
        self.XLR_GateTask(
            phase=f'CREATE_CHANGE_{phase}',
            gate_title=f"Validation creation SNOW ${{{phase}.sun.id}}",
            description='',
            cond_title=None,
            type_task='Validation SNOW creation',
            XLR_ID=self.dict_template[f'CREATE_CHANGE_{phase}']['xlr_id_phase']
        )

    def _configure_sun_change_state(self, phase: str) -> None:
        """
        Configure SUN change state based on template configuration.

        Args:
            phase: The phase name
        """
        has_standard_template = (self.parameters['general_info'].get('Template_standard_id') is not None)

        if has_standard_template and phase == 'PRODUCTION':
            self.change_state_sun(phase, 'Scheduled')
        else:
            self.change_state_sun(phase, 'Initial validation')
            self.change_wait_state(phase, 'WaitForInitialChangeApproval')

    def _add_ops_validation_gate(self, phase: str) -> None:
        """
        Add OPS validation gate for production phases.

        Args:
            phase: The phase name
        """
        self.XLR_GateTask(
            phase=phase,
            gate_title=f'OPS TASK : Validation of the SNOW ${{{phase}.sun.id}}',
            description='',
            cond_title=f'change put in state deploiement ${{{phase}.sun.id}}',
            type_task='check_sun_by_ops',
            XLR_ID=self.dict_template[phase]['xlr_id_phase']
        )

    def _configure_phase_states_and_notifications(self, phase: str) -> None:
        """
        Configure phase states and notifications.

        Args:
            phase: The phase name
        """
        if phase == 'BENCH':
            self.change_state_sun(phase, 'Scheduled')

        self.change_state_sun(phase, 'Implement')
        self.webhook_get_email_ops_on_change(phase)
        self.script_jython_get_email_ops_on_change(phase)
        self.parameter_phase_task(phase)
        self.creation_technical_task(phase, 'after_deployment')

        # Process email close release notifications
        self._process_email_notifications(phase, 'email_close_release')

    def _add_final_phase_validations(self, phase: str) -> None:
        """
        Add final phase validations and notifications.

        Args:
            phase: The phase name
        """
        if phase != 'BENCH':
            self._add_development_validation_gate(phase)

        # Process email end release notifications
        self._process_email_notifications(phase, 'email_end_release')

    def _process_email_notifications(self, phase: str, notification_type: str) -> None:
        """
        Process email notifications for a phase.

        Args:
            phase: The phase name
            notification_type: Type of notification (email_close_release or email_end_release)
        """
        if phase not in self.parameters.get('Phases', {}):
            return

        for item in self.parameters['Phases'][phase]:
            if notification_type in item:
                email_item = item[notification_type]
                self.task_notification(
                    phase=phase,
                    email_item=email_item,
                    aim=notification_type
                )
    def define_variable_type_template_DYNAMIC(self) -> None:
        """
        Define dynamic template variables based on configuration.

        This method processes the template configuration and creates the appropriate
        variables for different package modes and phases.
        """
        template_info = self.parameters['general_info']
        template_packages = self.parameters.get('template_liste_package', {})
        package_count = len(template_packages)
        phase_count = len(template_info['phases'])
        package_mode = template_info['template_package_mode']

        # Handle single package scenarios
        if package_count == 1:
            self._handle_single_package_variables(package_mode, phase_count, template_info)
        else:
            self._handle_multiple_package_variables(package_mode, template_packages)

        # Handle SUN change variables for production phases
        self._create_sun_change_variables(template_info)

        # Handle custom release variables
        self._create_custom_release_variables()

        # Handle Jenkins integration variables
        self._create_jenkins_variables(template_packages)

    def _handle_single_package_variables(self, package_mode: str, phase_count: int, template_info: Dict[str, Any]) -> None:
        """
        Handle variable creation for single package templates.

        Args:
            package_mode: The package mode (listbox or string)
            phase_count: Number of phases
            template_info: General template information
        """
        is_dev_only = (phase_count == 1 and template_info['phases'][0] == 'DEV')

        if package_mode == 'listbox' and not is_dev_only:
            package_name = self.dict_value_for_template['package'][0]
            self._create_package_version_variable(package_name)
        elif package_mode == 'string' and not is_dev_only:
            self.add_variable_deliverable_item_showOnReleaseStart()

    def _handle_multiple_package_variables(self, package_mode: str, template_packages: Dict[str, Any]) -> None:
        """
        Handle variable creation for multiple package templates.

        Args:
            package_mode: The package mode (listbox or string)
            template_packages: Dictionary of template packages
        """
        if package_mode == 'string':
            self.add_variable_deliverable_item_showOnReleaseStart()
        elif package_mode == 'listbox':
            for package_name in template_packages.keys():
                self._create_package_version_variable(package_name)

    def _create_package_version_variable(self, package_name: str) -> None:
        """
        Create a package version variable.

        Args:
            package_name: Name of the package
        """
        XLRGeneric.template_create_variable(
            self,
            key=f'{package_name}_version',
            typev='StringVariable',
            label='',
            description='',
            value='',
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

    def _create_sun_change_variables(self, template_info: Dict[str, Any]) -> None:
        """
        Create SUN change variables for production phases.

        Args:
            template_info: General template information
        """
        phases = template_info['phases']
        has_production_phases = bool(set(phases) & {'BENCH', 'PRODUCTION'})

        if not has_production_phases:
            return

        has_dev_phases = bool(set(phases) & {'DEV', 'UAT'})
        requires_value = not has_dev_phases

        # Create SUN change title and description variables
        sun_variables = [
            ('Title_SUN_CHANGE', 'Title_SUN_CHANGE', 'Title in SUN change', False),
            ('Long_description_SUN_CHANGE', 'Description in SUN change', '', True)
        ]

        for var_key, var_label, var_desc, is_multiline in sun_variables:
            XLRGeneric.template_create_variable(
                self,
                key=var_key,
                typev='StringVariable',
                label=var_label,
                description=var_desc,
                value='',
                requiresValue=requires_value,
                showOnReleaseStart=True,
                multiline=is_multiline
            )

        # Create BENCH.sun.id variable if needed
        self._create_bench_sun_id_variable(phases, requires_value)

    def _create_bench_sun_id_variable(self, phases: list, _: bool) -> None:
        """
        Create BENCH.sun.id variable based on phase configuration.

        Args:
            phases: List of phases
            base_requires_value: Base requirement value
        """
        has_production = 'PRODUCTION' in phases
        has_bench = 'BENCH' in phases
        phase_count = len(phases)

        if has_production and has_bench and phase_count != 1:
            requires_value = False
        elif has_production and phase_count == 1:
            requires_value = True
        else:
            return

        XLRGeneric.template_create_variable(
            self,
            key='BENCH.sun.id',
            typev='StringVariable',
            label='SUN Change BENCH',
            description='Number SUN Change BENCH',
            value='',
            requiresValue=requires_value,
            showOnReleaseStart=True,
            multiline=False
        )

    def _create_custom_release_variables(self) -> None:
        """
        Create custom release variables for EV9 IUA.
        """
        variable_release = self.parameters.get('variable_release')
        if not variable_release or 'EV9' not in self.parameters['general_info']['iua']:
            return

        for variable, value in variable_release.items():
            if variable == 'Date':
                requires_value = False
                show_on_start = False
                var_value = None
            else:
                requires_value = True
                show_on_start = True
                var_value = value

            XLRGeneric.template_create_variable(
                self,
                key=variable,
                typev='StringVariable',
                label='',
                description='',
                value=var_value,
                requiresValue=requires_value,
                showOnReleaseStart=show_on_start,
                multiline=False
            )

    def _create_jenkins_variables(self, template_packages: Dict[str, Any]) -> None:
        """
        Create Jenkins integration variables.

        Args:
            template_packages: Dictionary of template packages
        """
        self.name_from_jenkins_value = 'no'

        for package_name, package_config in template_packages.items():
            if (package_name in self.release_Variables_in_progress['list_package'] and
                package_config.get('mode') == 'name_from_jenkins'):

                self.name_from_jenkins_value = 'yes'
                XLRGeneric.template_create_variable(
                    self,
                    key=f'VARIABLE_XLR_ID_{package_name}_version',
                    typev='StringVariable',
                    label='',
                    description='',
                    value='',
                    requiresValue=False,
                    showOnReleaseStart=False,
                    multiline=False
                )

    
    def dynamic_phase_dynamic(self) -> str:
        """
        Create and configure the dynamic phase of the template.

        This method handles the creation of Jython tasks for managing
        dynamic aspects of the template like phase deletion, package
        management, and technical tasks.

        Returns:
            'done' when phase creation is complete
        """
        # Create dictionary variable to manage XLR tasks for technical OPS and DBA tasks
        self.dict_value_for_template_technical_task = self.dict_value_for_tempalte_technical_task()

        # No dynamic phase if there's only one phase, one package, and no technical_task exists
        if (self.dict_value_for_template_technical_task.get('technical_task') is None and
            len(self.dict_value_for_template.get('template_liste_phase', [])) == 1 and
            len(getattr(self, 'list_package', [])) == 1):
            return 'done'

        # Create dynamic_release phase to add Jython tasks
        self.dict_template = self.add_phase_tasks('dynamic_release')

        self._handle_jenkins_integration()
        self._handle_phase_management()
        self._handle_package_management()
        self._handle_bench_environment_configuration()
        self._handle_jenkins_task_cleanup()
        self._handle_controlm_task_cleanup()
        self._handle_xld_task_cleanup()
        self._handle_technical_task_configuration()
        self._handle_template_specific_tasks()

        return 'done'

    def _handle_jenkins_integration(self) -> None:
        """
        Handle Jenkins integration for packages with 'name_from_jenkins' mode.
        """
        if self.name_from_jenkins_value == "yes":
            XLRTaskScript.task_xlr_if_name_from_jenkins(self, 'dynamic_release')

    def _handle_phase_management(self) -> None:
        """
        Handle phase management based on phase mode configuration.
        """
        if len(self.parameters['general_info']['phases']) <= 1:
            return

        phase_mode = self.parameters['general_info']['phase_mode']
        package_mode = self.parameters['general_info']['template_package_mode']

        if phase_mode == 'one_list':
            if package_mode == 'string':
                XLRDynamicPhase.XLRJython_delete_phase_one_list_template_package_mode_string(self, 'dynamic_release')
            else:
                XLRDynamicPhase.XLRJython_delete_phase_one_list(self, 'dynamic_release')
        elif phase_mode == 'multi_list':
            XLRDynamicPhase.XLRJython_delete_phase_list_multi_list(self, 'dynamic_release')

    def _handle_package_management(self) -> None:
        """
        Handle package management for string mode templates.
        """
        if (self.parameters['general_info']['template_package_mode'] == 'string' and
            len(self.parameters['template_liste_package']) > 1):
            XLRDynamicPhase.script_jython_List_package_string(self, 'dynamic_release')

    def _handle_bench_environment_configuration(self) -> None:
        """
        Handle BENCH environment configuration for LoanIQ.
        """
        phases = self.parameters['general_info']['phases']
        xld_env_bench = self.parameters.get('XLD_ENV_BENCH', [])

        if 'BENCH' in phases and len(xld_env_bench) >= 2:
            XLRDynamicPhase.script_jython_define_xld_prefix_new(self, 'dynamic_release')
            XLRGeneric.template_create_variable(
                self,
                key='controlm_prefix_BENCH',
                typev='StringVariable',
                label='controlm_prefix_BENCH',
                description='',
                value='B',
                requiresValue=False,
                showOnReleaseStart=False,
                multiline=False
            )

    def _handle_jenkins_task_cleanup(self) -> None:
        """
        Handle Jenkins task cleanup for multi-package templates.
        """
        if (self.parameters.get('jenkins') is None or
            len(self.parameters['template_liste_package']) <= 1):
            return

        phases = self.parameters['general_info']['phases']
        if not (set(phases) & {'DEV', 'BUILD'}):
            return

        package_mode = self.parameters['general_info']['template_package_mode']
        if package_mode == 'string':
            XLRDynamicPhase.script_jython_dynamic_delete_task_jenkins_string(self, 'dynamic_release')
        elif package_mode == 'listbox':
            XLRDynamicPhase.script_jython_dynamic_delete_task_jenkins_listbox(self, 'dynamic_release')

    def _handle_controlm_task_cleanup(self) -> None:
        """
        Handle ControlM task cleanup based on configuration.
        """
        controlm_tasks = self.dict_value_for_template.get('controlm')
        if not controlm_tasks or len(controlm_tasks) == 0:
            return

        xld_env_bench = self.parameters.get('XLD_ENV_BENCH', [])
        if len(xld_env_bench) > 2:
            XLRDynamicPhase.script_jython_dynamic_delete_task_controlm_multibench(self, 'dynamic_release')
        else:
            XLRDynamicPhase.script_jython_dynamic_delete_task_controlm(self, 'dynamic_release')

    def _handle_xld_task_cleanup(self) -> None:
        """
        Handle XLD task cleanup for multi-package templates.
        """
        if len(self.parameters['template_liste_package']) <= 1:
            return

        iua = self.parameters['general_info']['iua']
        phases = self.parameters['general_info']['phases']

        if 'Y88' in iua and 'BENCH' in phases:
            XLRGeneric.template_create_variable(
                self,
                key='BENCH_Y88',
                typev='StringVariable',
                label='BENCH_Y88',
                description='',
                value='',
                requiresValue=False,
                showOnReleaseStart=False,
                multiline=False
            )
            XLRDynamicPhase.script_jython_dynamic_delete_task_xld_Y88(self, 'dynamic_release')
        else:
            XLRDynamicPhase.script_jython_dynamic_delete_task_xld(self, 'dynamic_release')

    def _handle_technical_task_configuration(self) -> None:
        """
        Handle technical task configuration and cleanup.
        """
        if self.parameters.get('technical_task_list') is None:
            return

        XLRGeneric.template_create_variable(
            self,
            key='dict_value_for_template_technical_task',
            typev='StringVariable',
            label='dict_value_for_template_technical_task',
            description='',
            value=self.dict_value_for_template_technical_task,
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        phases = self.parameters['general_info']['phases']
        has_production_phases = bool(set(phases) & {'PRODUCTION', 'BENCH'})

        if not has_production_phases:
            return

        task_mode = self.parameters['general_info']['technical_task_mode']
        if task_mode == 'listbox':
            XLRDynamicPhase.XLRJythonScript_release_delete_technical_task_ListStringVariable(self, 'dynamic_release')
        elif task_mode == 'string':
            XLRDynamicPhase.XLRJythonScript_dynamic_release_delete_technical_task_StringVariable(self, 'dynamic_release')

    def _handle_template_specific_tasks(self) -> None:
        """
        Handle template-specific tasks and variable management.
        """
        template_type = self.parameters['general_info'].get('type_template')
        if template_type == 'FROM_NAME_BRANCH':
            XLRTaskScript.script_jython_put_value_version(self, 'dynamic_release')

        variable_release = self.parameters.get('variable_release')
        if variable_release and 'Date' in variable_release:
            XLRTaskScript.script_jython_define_variable_release(self, 'dynamic_release')
        
        
def main() -> None:
    """
    Main entry point for the XLR Template Creation script.
    """
    parser = argparse.ArgumentParser(
        description='Create XLR templates from YAML configuration files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python DYNAMIC_template.py --infile template.yaml

The YAML file should contain the template configuration including:
- general_info: Basic template information
- template_liste_package: Package definitions
- Phases: Phase-specific configurations
        """
    )
    parser.add_argument(
        '--infile',
        nargs=1,
        required=True,
        help="YAML configuration file to process",
        type=argparse.FileType('r', encoding='utf-8'),
        metavar='FILE'
    )

    try:
        arguments = parser.parse_args()
    except SystemExit:
        return

    try:
        parameters_yaml = yaml.safe_load(arguments.infile[0])
    except yaml.YAMLError as e:
        print(f'Error loading YAML file: {e}')
        print('Please check your file format and try again.')
        sys.exit(10)
    except Exception as e:
        print(f'Unexpected error reading file: {e}')
        sys.exit(11)

    try:
        # Convert YAML to JSON and back to ensure proper format
        json_data = json.dumps(parameters_yaml)
        parameters = json.loads(json_data)

        # Setup logging directory
        log_dir = Path('log') / parameters['general_info']['name_release']
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = setup_logger('LOG_START', str(log_dir / 'CR.log'))

        # Create and process template
        template_creator = XLRCreateTemplate(parameters)

        for phase in parameters['general_info']['phases']:
            template_url = template_creator.createphase(phase)

        # Log completion
        logger.info("---------------------------")
        logger.info("TEMPLATE CREATION COMPLETED SUCCESSFULLY")
        logger.info("---------------------------")
        logger.info(f"Release Name: {parameters['general_info']['name_release']}")
        logger.info(f"Template URL: {template_url}")

    except KeyError as e:
        print(f'Missing required configuration key: {e}')
        sys.exit(12)
    except Exception as e:
        print(f'Error during template creation: {e}')
        sys.exit(13)


if __name__ == "__main__":
    main()
