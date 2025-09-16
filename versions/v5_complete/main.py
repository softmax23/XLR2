#!/usr/bin/env python3
"""
XLR Dynamic Template Creator - Version 5 Complete
=================================================

This version implements the complete functionality from V1 with improved modular architecture.
It includes all critical features: flow orchestration, gates, SUN integration, and complete variable management.

Key Features:
- Complete createphase() flow orchestration
- XLR Gates management for phase validation
- Full SUN/ServiceNow integration
- Complete variable management (including release_Variables_in_progress)
- Y88-specific logic
- Environment variable management
- YAML validation
- Comprehensive error handling and logging

Author: Claude Code V5
Date: 2025
"""

import argparse
import yaml
import sys
import os
import logging
from typing import Dict, Any
from pathlib import Path

# Import all core modules
from src.core.xlr_generic import XLRGeneric
from src.core.xlr_controlm import XLRControlm
from src.core.xlr_dynamic_phase import XLRDynamicPhase
from src.core.xlr_sun import XLRSun
from src.core.xlr_task_script import XLRTaskScript
from src.config.config_loader import ConfigLoader
from src.utils.yaml_validator import YamlValidator
from src.utils.logger_setup import setup_logger, setup_logger_error, setup_logger_detail


class XLRCreateTemplate(XLRGeneric, XLRSun, XLRTaskScript, XLRControlm, XLRDynamicPhase):
    """
    Main XLR Template Creation class that orchestrates the complete template creation process.

    This class inherits from all the core modules and implements the complete flow
    from V1 with improved error handling and modular architecture.
    """

    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize the XLR Template Creator with complete setup.

        Args:
            parameters: YAML configuration parameters
        """
        # Load configuration
        self.config = ConfigLoader()

        # Set up API headers
        self.header = {
            'content-type': 'application/json',
            'Accept': 'application/json'
        }

        # Store parameters
        self.parameters = parameters

        # Create logging directories
        self._setup_logging()

        # Initialize tracking lists
        self.list_technical_task_done = []
        self.list_technical_sun_task_done = []
        self.list_xlr_group_task_done = []

        # Initialize template URL and dictionaries
        self.template_url = ''
        self.dic_for_check = {}
        self.dict_template = {}

        # Initialize counters
        self.count_task = 10

        # Validate YAML file
        validator = YamlValidator(parameters)
        validator.validate()

        # Clear screen and start logging
        os.system('clear')
        self.logger_cr.info("")
        self.logger_cr.info("=" * 60)
        self.logger_cr.info("XLR TEMPLATE CREATION V5 - BEGIN")
        self.logger_cr.info("=" * 60)
        self.logger_cr.info("")

        # Initialize parent classes
        super().__init__(parameters)

    def _setup_logging(self) -> None:
        """Set up logging directories and loggers."""
        release_name = self.parameters['general_info']['name_release']
        log_dir = Path(f'log/{release_name}')
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create loggers
        self.logger_cr = setup_logger('LOG_CR', str(log_dir / 'CR.log'))
        self.logger_detail = setup_logger_detail('LOG_INFO', str(log_dir / 'info.log'))
        self.logger_error = setup_logger_error('LOG_ERROR', str(log_dir / 'error.log'))

    def create_template(self) -> str:
        """
        Main orchestration method - implements the complete V1 flow.

        Returns:
            Template URL if successful
        """
        try:
            # Step 1: Delete existing template
            self.logger_cr.info("Step 1: Deleting existing template...")
            self.delete_template()

            # Step 2: Find XLR folder
            self.logger_cr.info("Step 2: Finding XLR folder...")
            self.find_xlr_folder()

            # Step 3: Create template
            self.logger_cr.info("Step 3: Creating template...")
            self.dict_template, self.XLR_template_id = self.CreateTemplate()

            # Step 4: Create phase environment variables
            self.logger_cr.info("Step 4: Creating phase environment variables...")
            self.create_phase_env_variable()

            # Step 5: Create core template variables
            self.logger_cr.info("Step 5: Creating core template variables...")
            self._create_core_variables()

            # Step 6: Create dynamic phase
            self.logger_cr.info("Step 6: Creating dynamic phase...")
            self.dynamics_phase_done = self.dynamic_phase_dynamic()

            # Step 7: Create API and system variables
            self.logger_cr.info("Step 7: Creating API and system variables...")
            self._create_system_variables()

            # Step 8: Process all phases
            self.logger_cr.info("Step 8: Processing all phases...")
            phases = self.parameters['general_info']['phases']
            for phase in phases:
                self.logger_cr.info(f"Processing phase: {phase}")
                self.createphase(phase)

            # Step 9: Finalization
            self.logger_cr.info("Step 9: Finalizing template...")
            self._finalize_template()

            self.logger_cr.info("")
            self.logger_cr.info("=" * 60)
            self.logger_cr.info("XLR TEMPLATE CREATION V5 - COMPLETED SUCCESSFULLY")
            self.logger_cr.info(f"Template URL: {self.template_url}")
            self.logger_cr.info("=" * 60)
            self.logger_cr.info("")

            return self.template_url

        except Exception as e:
            self.logger_error.error(f"Critical error during template creation: {e}")
            raise

    def createphase(self, phase: str) -> None:
        """
        Complete phase creation orchestration - implements V1 createphase() logic.

        Args:
            phase: Phase name (BUILD, DEV, UAT, BENCH, PRODUCTION)
        """
        self.logger_cr.info(f"Creating phase: {phase}")

        # Reset task counter for each phase
        self.count_task = 10

        if phase in ['BUILD', 'DEV', 'UAT']:
            self._create_development_phase(phase)
        elif phase in ['BENCH', 'PRODUCTION']:
            self._create_production_phase(phase)
        else:
            self.logger_error.error(f"Unknown phase type: {phase}")
            raise ValueError(f"Unknown phase type: {phase}")

    def _create_development_phase(self, phase: str) -> None:
        """Create development phase (BUILD, DEV, UAT)."""
        self.logger_cr.info(f"Creating development phase: {phase}")

        # Delete default phase
        self.delete_phase_default_in_template()

        # Create phase tasks
        self.add_phase_tasks(phase=phase)

        # Add initial validation gate
        self.XLR_GateTask(
            phase=phase,
            gate_title="Validation_release_template",
            description='',
            cond_title='Validation_release_template OK',
            type_task='Validation_release_template',
            XLR_ID=self.dict_template[phase]['xlr_id_phase']
        )

        # Process phase-specific tasks
        self.parameter_phase_task(phase)

        # Add final validation gate
        self.XLR_GateTask(
            phase=phase,
            gate_title=f'DEV team: Validate installation in {phase}',
            description='',
            cond_title=f'DEV team: Validate the delivery in {phase}',
            type_task='gate_validation_moe',
            XLR_ID=self.dict_template[phase]['xlr_id_phase']
        )

        self.logger_cr.info(f"Development phase {phase} created successfully")

    def _create_production_phase(self, phase: str) -> None:
        """Create production phase (BENCH, PRODUCTION)."""
        self.logger_cr.info(f"Creating production phase: {phase}")

        # Delete default phase
        self.delete_phase_default_in_template()

        # Add SUN phase
        self.add_phase_sun(phase)

        # Process SUN-specific tasks
        self.parameter_phase_sun(phase)

        # Create technical tasks for after deployment
        self.XLRSun_creation_technical_task(phase, 'after_deployment')

        self.logger_cr.info(f"Production phase {phase} created successfully")

    def _create_core_variables(self) -> None:
        """Create core template variables including release_Variables_in_progress."""
        self.logger_cr.info("Creating core variables...")

        # Generate template values
        self.dict_value_for_template = self.dict_value_for_tempalte()

        # Define variable type for template
        self.define_variable_type_template_DYNAMIC()

        # Create the critical release_Variables_in_progress variable
        self.template_create_variable(
            key='release_Variables_in_progress',
            typev='MapStringStringVariable',
            label='release_Variables_in_progress',
            description='',
            value=self.release_Variables_in_progress,
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        self.logger_cr.info("Core variables created successfully")

    def _create_system_variables(self) -> None:
        """Create system and API variables."""
        self.logger_cr.info("Creating system variables...")

        # API credentials
        self.template_create_variable(
            key='ops_username_api',
            typev='StringVariable',
            label='ops_username_api',
            description='',
            value=self.ops_username_api,
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        self.template_create_variable(
            key='ops_password_api',
            typev='PasswordStringVariable',
            label='ops_password_api',
            description='',
            value=self.ops_password_api,
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        # Release management variables
        self.template_create_variable(
            key='email_owner_release',
            typev='StringVariable',
            label='email_owner_release',
            description='',
            value='',
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        self.template_create_variable(
            key='xlr_list_phase_selection',
            typev='StringVariable',
            label='xlr_list_phase_selection',
            description='',
            value='',
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        # IUA variable
        self.template_create_variable(
            key='IUA',
            typev='StringVariable',
            label='IUA',
            description='',
            value=self.parameters['general_info']['iua'],
            requiresValue=False,
            showOnReleaseStart=False,
            multiline=False
        )

        self.logger_cr.info("System variables created successfully")

    def _finalize_template(self) -> None:
        """Finalize the template creation."""
        self.logger_cr.info("Finalizing template...")

        # Set template URL
        if hasattr(self, 'XLR_template_id'):
            base_url = self.config.get('xlr_base_url', self.url_api_xlr.replace('/api/v1/', ''))
            self.template_url = f"{base_url}#/templates/{self.XLR_template_id}"

        self.logger_cr.info("Template finalized successfully")


def main():
    """Main entry point for the XLR Template Creation script V5."""
    parser = argparse.ArgumentParser(
        description='XLR Dynamic Template Creator - Version 5 Complete',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main.py --infile template.yaml

Features in V5:
- Complete V1 functionality with modular architecture
- Full createphase() flow orchestration
- XLR Gates management
- Complete SUN/ServiceNow integration
- All critical variables including release_Variables_in_progress
- Y88-specific logic
- Environment variable management
- Comprehensive error handling
        """
    )

    parser.add_argument(
        '--infile',
        required=True,
        help='Path to the YAML template configuration file'
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set up logging level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        # Load YAML configuration
        with open(args.infile, 'r', encoding='utf-8') as file:
            parameters = yaml.safe_load(file)

        if not parameters:
            print("Error: Empty or invalid YAML file")
            sys.exit(1)

        # Create and run template creator
        creator = XLRCreateTemplate(parameters)
        template_url = creator.create_template()

        print("\n" + "="*60)
        print("✅ XLR TEMPLATE CREATION V5 COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📋 Template Name: {parameters['general_info']['name_release']}")
        print(f"🔗 Template URL: {template_url}")
        print(f"📁 Logs Directory: log/{parameters['general_info']['name_release']}/")
        print("="*60)

        return 0

    except FileNotFoundError:
        print(f"❌ Error: File '{args.infile}' not found")
        return 1
    except yaml.YAMLError as e:
        print(f"❌ Error: Invalid YAML file - {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())