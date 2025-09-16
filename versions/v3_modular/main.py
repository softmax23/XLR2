#!/usr/bin/env python3
"""
XLR Dynamic Template - Version 3 Modular
Main entry point with YAML parameter support.

Usage:
    python3 main.py --infile template.yaml
"""

import argparse
import sys
import json
import logging
from pathlib import Path

import yaml

# Import the new modular classes
from src.core import (
    XLRGeneric,
    XLRControlm,
    XLRDynamicPhase,
    XLRSun,
    XLRTaskScript
)
from src.config import ConfigLoader


def setup_logging(log_dir: Path) -> logging.Logger:
    """Setup logging configuration."""
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'xlr_creation.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('xlr.main')


def load_template_config(template_path: str) -> dict:
    """Load template configuration from YAML file."""
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Template file not found: {template_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error loading YAML file: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error reading file: {e}")
        sys.exit(3)


def create_template_with_modular_approach(parameters: dict, logger: logging.Logger, config_path: str = None) -> str:
    """Create XLR template using the modular approach."""
    try:
        # Load configuration
        config_loader = ConfigLoader(config_path)
        if not config_loader.validate_config():
            raise ValueError("Invalid configuration file")

        # Initialize core components
        xlr_generic = XLRGeneric()
        xlr_controlm = XLRControlm()
        xlr_dynamic_phase = XLRDynamicPhase()
        xlr_sun = XLRSun()
        xlr_task_script = XLRTaskScript()

        # Get configuration from config file
        xlr_api_config = config_loader.get_xlr_config()
        controlm_config = config_loader.get_controlm_config()

        logger.info(f"Loaded XLR configuration from: {config_loader.config_path}")

        # Configure XLR connections for all components
        for component in [xlr_generic, xlr_controlm, xlr_dynamic_phase, xlr_sun, xlr_task_script]:
            if hasattr(component, 'setup_xlr_connection'):
                component.setup_xlr_connection(
                    xlr_api_config['url'],
                    xlr_api_config['username'],
                    xlr_api_config['password']
                )

        # Setup Control-M specific configuration
        xlr_controlm.setup_controlm_environment(
            url_api_controlm=controlm_config['api_url'],
            ctm_prod=controlm_config['production_environment'],
            ctm_bench=controlm_config['bench_environment']
        )

        # Setup ServiceNow configuration
        xlr_sun.setup_sun_configuration(
            sun_approver=parameters.get('general_info', {}).get('SUN_approuver', 'default@company.com')
        )

        # Set parameters from template config
        xlr_generic.parameters = parameters

        logger.info("Starting modular template creation")
        logger.info(f"Template name: {parameters.get('general_info', {}).get('name_release', 'Unknown')}")

        # Create template
        dict_template, template_id = xlr_generic.create_template()

        logger.info(f"Template created successfully: {template_id}")

        # Create dynamic phase if template type is DYNAMIC
        if parameters.get('general_info', {}).get('type_template') == 'DYNAMIC':
            phase_config = {
                'color': '#FD8A00',
                'description': 'Dynamic phase for managing conditional deployment phases'
            }
            dynamic_phase_id = xlr_dynamic_phase.create_dynamic_phase(
                phase_name="dynamic_release",
                phase_config=phase_config,
                parent_id=template_id
            )
            if dynamic_phase_id:
                logger.info(f"Created dynamic phase with ID: {dynamic_phase_id}")

                # Add dynamic phase scripts based on template configuration
                _add_dynamic_phase_tasks(parameters, xlr_dynamic_phase, xlr_task_script)

        # Process phases from template configuration
        phases = parameters.get('general_info', {}).get('phases', [])

        for phase in phases:
            logger.info(f"Processing phase: {phase}")

            # Process phase-specific tasks (includes ControlM tasks from YAML)
            xlr_generic.parameter_phase_task(phase)

            # Add ServiceNow integration for production phases (automatic like in V1)
            if phase in ['BENCH', 'PRODUCTION']:
                change_details = {
                    'short_description': f'Deployment for {phase}',
                    'description': f'Automated deployment in {phase} environment',
                    'category': 'Software',
                    'priority': '3'
                }
                xlr_sun.create_sun_change_request(phase, change_details)

        logger.info("=" * 50)
        logger.info("MODULAR TEMPLATE CREATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)

        # Build template URL using base URL from config
        base_url = xlr_api_config['url'].replace('/api/v1/', '')
        template_url = f"{base_url}/#/templates/{template_id.replace('Applications/', '').replace('/', '-')}"
        logger.info(f"Release Name: {parameters['general_info']['name_release']}")
        logger.info(f"Template URL: {template_url}")

        return template_url

    except Exception as e:
        logger.error(f"Error during template creation: {e}")
        raise


def _add_dynamic_phase_tasks(parameters, xlr_dynamic_phase, xlr_task_script):
    """
    Add dynamic phase tasks based on template configuration.

    This replicates the logic from V1's dynamic_phase_dynamic() method.
    """
    # Basic dynamic phase setup
    xlr_dynamic_phase.script_jython_delete_phase_inc('dynamic_release')

    # Handle Jenkins integration
    _handle_jenkins_integration(parameters, xlr_task_script)

    # Handle phase management
    _handle_phase_management(parameters, xlr_dynamic_phase)

    # Handle package management
    _handle_package_management(parameters, xlr_dynamic_phase)

    # Handle BENCH environment configuration
    _handle_bench_environment_configuration(parameters, xlr_dynamic_phase)

    # Handle various task cleanups
    _handle_jenkins_task_cleanup(parameters, xlr_dynamic_phase)
    _handle_controlm_task_cleanup(parameters, xlr_dynamic_phase)
    _handle_xld_task_cleanup(parameters, xlr_dynamic_phase)

    # Handle technical task configuration
    _handle_technical_task_configuration(parameters, xlr_dynamic_phase)

    # Handle template-specific tasks
    _handle_template_specific_tasks(parameters, xlr_task_script)


def _handle_jenkins_integration(parameters, xlr_task_script):
    """Handle Jenkins integration for packages with 'name_from_jenkins' mode."""
    template_packages = parameters.get('template_liste_package', {})
    for package_name, package_config in template_packages.items():
        if package_config.get('mode') == 'name_from_jenkins':
            # Call appropriate Jenkins integration method
            # xlr_task_script.task_xlr_if_name_from_jenkins('dynamic_release')
            break


def _handle_phase_management(parameters, xlr_dynamic_phase):
    """Handle phase management based on phase mode configuration."""
    phases = parameters.get('general_info', {}).get('phases', [])
    if len(phases) <= 1:
        return

    phase_mode = parameters.get('general_info', {}).get('phase_mode', '')
    package_mode = parameters.get('general_info', {}).get('template_package_mode', '')

    if phase_mode == 'one_list':
        if package_mode == 'string':
            # xlr_dynamic_phase.XLRJython_delete_phase_one_list_template_package_mode_string('dynamic_release')
            pass
        else:
            # xlr_dynamic_phase.XLRJython_delete_phase_one_list('dynamic_release')
            pass
    elif phase_mode == 'multi_list':
        # xlr_dynamic_phase.XLRJython_delete_phase_list_multi_list('dynamic_release')
        pass


def _handle_package_management(parameters, xlr_dynamic_phase):
    """Handle package management for string mode templates."""
    package_mode = parameters.get('general_info', {}).get('template_package_mode', '')
    template_packages = parameters.get('template_liste_package', {})

    if package_mode == 'string' and len(template_packages) > 1:
        xlr_dynamic_phase.script_jython_List_package_string('dynamic_release')


def _handle_bench_environment_configuration(parameters, xlr_dynamic_phase):
    """Handle BENCH environment configuration for LoanIQ."""
    phases = parameters.get('general_info', {}).get('phases', [])
    xld_env_bench = parameters.get('XLD_ENV_BENCH', [])

    if 'BENCH' in phases and len(xld_env_bench) >= 2:
        xlr_dynamic_phase.script_jython_define_xld_prefix_new('dynamic_release')


def _handle_jenkins_task_cleanup(parameters, xlr_dynamic_phase):
    """Handle Jenkins task cleanup for multi-package templates."""
    if parameters.get('jenkins') is None:
        return

    template_packages = parameters.get('template_liste_package', {})
    if len(template_packages) <= 1:
        return

    phases = parameters.get('general_info', {}).get('phases', [])
    if not (set(phases) & {'DEV', 'BUILD'}):
        return

    package_mode = parameters.get('general_info', {}).get('template_package_mode', '')
    if package_mode == 'string':
        # xlr_dynamic_phase.script_jython_dynamic_delete_task_jenkins_string('dynamic_release')
        pass
    elif package_mode == 'listbox':
        # xlr_dynamic_phase.script_jython_dynamic_delete_task_jenkins_listbox('dynamic_release')
        pass


def _handle_controlm_task_cleanup(parameters, xlr_dynamic_phase):
    """Handle ControlM task cleanup based on configuration."""
    # Check if any phase has ControlM tasks
    phases_config = parameters.get('Phases', {})
    has_controlm_tasks = False

    for phase_name, phase_tasks in phases_config.items():
        for task in phase_tasks:
            if isinstance(task, dict) and any('XLR_task_controlm' in key for key in task.keys()):
                has_controlm_tasks = True
                break
        if has_controlm_tasks:
            break

    if not has_controlm_tasks:
        return

    xld_env_bench = parameters.get('XLD_ENV_BENCH', [])
    if len(xld_env_bench) > 2:
        xlr_dynamic_phase.script_jython_dynamic_delete_task_controlm_multibench('dynamic_release')
    else:
        xlr_dynamic_phase.script_jython_dynamic_delete_task_controlm('dynamic_release')


def _handle_xld_task_cleanup(parameters, xlr_dynamic_phase):
    """Handle XLD task cleanup for multi-package templates."""
    template_packages = parameters.get('template_liste_package', {})
    if len(template_packages) <= 1:
        return

    iua = parameters.get('general_info', {}).get('iua', '')
    phases = parameters.get('general_info', {}).get('phases', [])

    if 'Y88' in iua and 'BENCH' in phases:
        # Create Y88-specific BENCH variable (like in V1)
        from .src.core.xlr_generic import XLRGeneric
        xlr_generic = XLRGeneric(parameters)
        xlr_generic.template_create_variable(
            key='BENCH_Y88',
            typev='StringVariable',
            label='BENCH_Y88',
            description='',
            value='',
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )
        xlr_dynamic_phase.script_jython_dynamic_delete_task_xld_Y88('dynamic_release')
    else:
        xlr_dynamic_phase.script_jython_dynamic_delete_task_xld('dynamic_release')


def _handle_technical_task_configuration(parameters, xlr_dynamic_phase):
    """Handle technical task configuration and cleanup."""
    if parameters.get('technical_task_list') is None:
        return

    phases = parameters.get('general_info', {}).get('phases', [])
    has_production_phases = bool(set(phases) & {'PRODUCTION', 'BENCH'})

    if not has_production_phases:
        return

    task_mode = parameters.get('general_info', {}).get('technical_task_mode', '')
    if task_mode == 'listbox':
        # xlr_dynamic_phase.XLRJythonScript_release_delete_technical_task_ListStringVariable('dynamic_release')
        pass
    elif task_mode == 'string':
        # xlr_dynamic_phase.XLRJythonScript_dynamic_release_delete_technical_task_StringVariable('dynamic_release')
        pass


def _handle_template_specific_tasks(parameters, xlr_task_script):
    """Handle template-specific tasks and variable management."""
    template_type = parameters.get('general_info', {}).get('type_template', '')
    if template_type == 'FROM_NAME_BRANCH':
        # xlr_task_script.script_jython_put_value_version('dynamic_release')
        pass

    variable_release = parameters.get('variable_release')
    if variable_release and 'Date' in variable_release:
        xlr_task_script.script_jython_define_variable_release('dynamic_release')


def main():
    """Main entry point for the XLR Template Creation script."""
    parser = argparse.ArgumentParser(
        description='XLR Dynamic Template Creator - Version 3 Modular',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python3 main.py --infile src/config/template.yaml
  python3 main.py --infile /path/to/your/template.yaml --config config.yaml

The YAML file should contain the template configuration including:
- general_info: Basic template information
- template_liste_package: Package definitions
- Phases: Phase-specific configurations

Features:
- Modular architecture with separated responsibilities
- External configuration file for URLs and credentials
- Robust error handling and logging
- Type hints and modern Python practices
- Maintainable and extensible code structure
        """
    )

    parser.add_argument(
        '--infile',
        required=True,
        help="YAML configuration file to process",
        type=str,
        metavar='FILE'
    )

    parser.add_argument(
        '--config',
        help="Configuration file with URLs and credentials (default: config.yaml)",
        type=str,
        metavar='CONFIG_FILE',
        default=None
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        return

    # Load template configuration
    parameters = load_template_config(args.infile)

    # Setup logging directory
    release_name = parameters.get('general_info', {}).get('name_release', 'unknown_release')
    log_dir = Path('logs') / release_name
    logger = setup_logging(log_dir)

    try:
        # Create template using modular approach
        template_url = create_template_with_modular_approach(parameters, logger, args.config)

        print(f"\n✅ Template creation completed successfully!")
        print(f"📋 Release Name: {parameters['general_info']['name_release']}")
        print(f"🔗 Template URL: {template_url}")

    except KeyError as e:
        print(f"❌ Missing required configuration key: {e}")
        sys.exit(4)
    except Exception as e:
        print(f"❌ Error during template creation: {e}")
        sys.exit(5)


if __name__ == "__main__":
    main()