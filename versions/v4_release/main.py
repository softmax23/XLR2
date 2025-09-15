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


def create_template_with_modular_approach(parameters: dict, logger: logging.Logger) -> str:
    """Create XLR template using the modular approach."""
    try:
        # Initialize core components
        xlr_generic = XLRGeneric()
        xlr_controlm = XLRControlm()
        xlr_dynamic_phase = XLRDynamicPhase()
        xlr_sun = XLRSun()
        xlr_task_script = XLRTaskScript()

        # Setup XLR connections for all components (you'll need to configure these)
        xlr_api_config = {
            'url': 'https://your-xlr-server/api/v1/',  # Configure this
            'username': 'your-username',  # Configure this
            'password': 'your-password'   # Configure this
        }

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
            url_api_controlm='https://your-controlm-server/api/',  # Configure this
            ctm_prod='PROD_CTM',   # Configure this
            ctm_bench='BENCH_CTM'  # Configure this
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

        # Process phases from template configuration
        phases = parameters.get('general_info', {}).get('phases', [])

        for phase in phases:
            logger.info(f"Processing phase: {phase}")

            # Process phase-specific tasks
            xlr_generic.parameter_phase_task(phase)

            # Add Control-M tasks if needed
            if parameters.get('controlm_integration'):
                xlr_controlm.script_jython_date_for_controlm(phase)

            # Add ServiceNow integration if needed
            if parameters.get('servicenow_integration'):
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

        template_url = f"https://your-xlr-server/#/templates/{template_id.replace('Applications/', '').replace('/', '-')}"
        logger.info(f"Release Name: {parameters['general_info']['name_release']}")
        logger.info(f"Template URL: {template_url}")

        return template_url

    except Exception as e:
        logger.error(f"Error during template creation: {e}")
        raise


def main():
    """Main entry point for the XLR Template Creation script."""
    parser = argparse.ArgumentParser(
        description='XLR Dynamic Template Creator - Version 3 Modular',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python3 main.py --infile src/config/template.yaml
  python3 main.py --infile /path/to/your/template.yaml

The YAML file should contain the template configuration including:
- general_info: Basic template information
- template_liste_package: Package definitions
- Phases: Phase-specific configurations

Features:
- Modular architecture with separated responsibilities
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
        template_url = create_template_with_modular_approach(parameters, logger)

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