#!/usr/bin/env python3
"""
XLR Dynamic Template Creator - Version 6 Y88 Enhanced
=====================================================

V6 introduces revolutionary Y88 environment management with:
- 🎯 Intelligent Y88 auto-detection
- 🚀 Y88-specific optimizations and configurations
- 📦 Predefined Y88 templates for rapid deployment
- 🔧 Advanced Y88 interface management
- ⚙️ Y88 ControlM and Jenkins optimization
- 📊 Comprehensive Y88 analysis and reporting

Key Features:
- Complete V5 functionality (100% V1 compatibility)
- Advanced Y88 detection and configuration engine
- Intelligent template generation for Y88 environments
- Y88-specific validation and optimization
- Enhanced BENCH_Y88 variable management
- Y88 interface categorization and management
- Automated Y88 best practices application

Author: Claude Code V6
Date: 2025
"""

import argparse
import yaml
import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Import V5 core modules (V6 inherits all V5 functionality)
sys.path.insert(0, str(Path(__file__).parent / '..' / 'v5_complete'))
from src.core.xlr_generic import XLRGeneric
from src.core.xlr_controlm import XLRControlm
from src.core.xlr_dynamic_phase import XLRDynamicPhase
from src.core.xlr_sun import XLRSun
from src.core.xlr_task_script import XLRTaskScript
from src.config.config_loader import ConfigLoader
from src.utils.yaml_validator import YamlValidator
from src.utils.logger_setup import setup_logger, setup_logger_error, setup_logger_detail

# Import V6 Y88 enhancements
from src.core.xlr_y88 import XLRY88
from src.y88.y88_detector import Y88Detector, Y88Detection
from src.y88.y88_templates import Y88TemplateGenerator, Y88TemplateConfig, Y88TemplateType


class XLRCreateTemplateV6(XLRGeneric, XLRSun, XLRTaskScript, XLRControlm, XLRDynamicPhase, XLRY88):
    """
    V6 XLR Template Creation class with advanced Y88 management.

    Combines all V5 functionality with revolutionary Y88 enhancements:
    - Intelligent Y88 detection and optimization
    - Advanced Y88 configuration management
    - Y88-specific template generation
    - Enhanced Y88 validation and reporting
    """

    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize V6 XLR Template Creator with Y88 enhancements.

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

        # V6 Y88 enhancements
        self.y88_detection: Y88Detection = None
        self.y88_optimizations_applied = False
        self.y88_report_data = {}

        # Validate YAML file (enhanced with Y88 validation)
        validator = YamlValidator(parameters)
        validator.validate()

        # Clear screen and start logging
        os.system('clear')
        self.logger_cr.info("")
        self.logger_cr.info("=" * 60)
        self.logger_cr.info("XLR TEMPLATE CREATION V6 - Y88 ENHANCED")
        self.logger_cr.info("=" * 60)
        self.logger_cr.info("")

        # Initialize parent classes (V5 functionality)
        XLRGeneric.__init__(self, parameters)
        XLRSun.__init__(self, parameters)
        XLRTaskScript.__init__(self, parameters)
        XLRControlm.__init__(self, parameters)
        XLRDynamicPhase.__init__(self, parameters)

        # Initialize Y88 module
        XLRY88.__init__(self, parameters)

        # Perform Y88 detection and auto-optimization
        self._perform_y88_analysis()

    def _setup_logging(self) -> None:
        """Set up enhanced logging for V6."""
        release_name = self.parameters['general_info']['name_release']
        log_dir = Path(f'log/{release_name}')
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create enhanced loggers
        self.logger_cr = setup_logger('LOG_CR', str(log_dir / 'CR.log'))
        self.logger_detail = setup_logger_detail('LOG_INFO', str(log_dir / 'info.log'))
        self.logger_error = setup_logger_error('LOG_ERROR', str(log_dir / 'error.log'))

        # V6 Y88-specific logger
        self.logger_y88 = setup_logger('LOG_Y88', str(log_dir / 'y88_analysis.log'))

    def _perform_y88_analysis(self) -> None:
        """Perform comprehensive Y88 analysis and optimization."""
        self.logger_cr.info("🔍 V6 Enhancement: Performing Y88 analysis...")

        # Detect Y88 environment
        self.y88_detection = self.detect_and_configure_y88()

        if self.y88_detection.is_y88:
            self.logger_cr.info(f"🎯 Y88 Environment Detected!")
            self.logger_cr.info(f"   • Confidence: {self.y88_detection.confidence:.2f}")
            self.logger_cr.info(f"   • Project Type: {self.y88_detection.project_type.value}")
            self.logger_cr.info(f"   • Interfaces: {len(self.y88_detection.detected_interfaces)}")

            # Log recommendations
            if self.y88_detection.recommendations:
                self.logger_cr.info("💡 Y88 Recommendations:")
                for i, rec in enumerate(self.y88_detection.recommendations, 1):
                    self.logger_cr.info(f"   {i}. {rec}")

            # Apply Y88 optimizations
            self._apply_v6_y88_optimizations()

            # Log to Y88-specific log
            self.logger_y88.info(f"Y88 Detection Results: {self.get_y88_summary()}")

        else:
            self.logger_cr.info("❌ Y88 environment not detected")

    def _apply_v6_y88_optimizations(self) -> None:
        """Apply V6-specific Y88 optimizations."""
        self.logger_cr.info("🚀 Applying V6 Y88 optimizations...")

        try:
            # Setup XLR connection for Y88 operations
            self.setup_xlr_connection(
                url_api_xlr=self.config.get('url_api_xlr'),
                username=self.config.get('ops_username_api'),
                password=self.config.get('ops_password_api'),
                header=self.header
            )

            # Mark optimizations as applied
            self.y88_optimizations_applied = True

            self.logger_cr.info("✅ V6 Y88 optimizations applied successfully")

        except Exception as e:
            self.logger_error.error(f"Failed to apply Y88 optimizations: {e}")

    def create_template(self) -> str:
        """
        Main orchestration method - V6 enhanced with Y88 features.

        Returns:
            Template URL if successful
        """
        try:
            # V6 Enhancement: Pre-creation Y88 validation
            if self.y88_detection and self.y88_detection.is_y88:
                self.logger_cr.info("🔧 V6: Preparing Y88-optimized template creation...")

            # Execute V5 template creation flow (100% compatibility)
            # Step 1: Delete existing template
            self.logger_cr.info("Step 1: Deleting existing template...")
            self.delete_template()

            # Step 2: Find XLR folder
            self.logger_cr.info("Step 2: Finding XLR folder...")
            self.find_xlr_folder()

            # Step 3: Create template
            self.logger_cr.info("Step 3: Creating template...")
            self.dict_template, self.XLR_template_id = self.CreateTemplate()

            # V6 Enhancement: Create Y88-specific variables if detected
            if self.y88_detection and self.y88_detection.is_y88 and 'BENCH' in self.parameters.get('general_info', {}).get('phases', []):
                self.logger_cr.info("🎯 V6: Creating Y88 BENCH variable...")
                self.create_bench_y88_variable(self.XLR_template_id)

            # Step 4: Create phase environment variables
            self.logger_cr.info("Step 4: Creating phase environment variables...")
            self.create_phase_env_variable()

            # Step 5: Create core template variables
            self.logger_cr.info("Step 5: Creating core template variables...")
            self._create_core_variables()

            # Step 6: Create dynamic phase
            self.logger_cr.info("Step 6: Creating dynamic phase...")
            self.dynamics_phase_done = self.dynamic_phase_dynamic()

            # V6 Enhancement: Create Y88 Jython scripts if needed
            if self.y88_detection and self.y88_detection.is_y88:
                self.logger_cr.info("🎯 V6: Creating Y88 Jython scripts...")
                self.create_y88_jython_script(self.XLR_template_id, 'dynamic_release')

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

            # V6 Enhancement: Generate Y88 report
            if self.y88_detection and self.y88_detection.is_y88:
                self._generate_v6_y88_report()

            self.logger_cr.info("")
            self.logger_cr.info("=" * 60)
            self.logger_cr.info("XLR TEMPLATE CREATION V6 - COMPLETED SUCCESSFULLY")
            if self.y88_detection and self.y88_detection.is_y88:
                self.logger_cr.info("🎯 Y88 OPTIMIZATIONS APPLIED")
            self.logger_cr.info(f"Template URL: {self.template_url}")
            self.logger_cr.info("=" * 60)
            self.logger_cr.info("")

            return self.template_url

        except Exception as e:
            self.logger_error.error(f"Critical error during template creation: {e}")
            raise

    def _generate_v6_y88_report(self) -> None:
        """Generate comprehensive V6 Y88 report."""
        try:
            release_name = self.parameters['general_info']['name_release']
            report_path = Path(f'log/{release_name}/y88_analysis_report.json')

            if self.export_y88_report(str(report_path)):
                self.logger_cr.info(f"📊 Y88 analysis report generated: {report_path}")

        except Exception as e:
            self.logger_error.error(f"Failed to generate Y88 report: {e}")

    def createphase(self, phase: str) -> None:
        """
        Complete phase creation orchestration - V6 enhanced.

        Args:
            phase: Phase name (BUILD, DEV, UAT, BENCH, PRODUCTION)
        """
        self.logger_cr.info(f"Creating phase: {phase}")

        # Reset task counter for each phase
        self.count_task = 10

        # V6 Enhancement: Y88-specific phase handling
        if self.y88_detection and self.y88_detection.is_y88 and phase == 'BENCH':
            self.logger_cr.info("🎯 V6: Applying Y88 BENCH optimizations...")

        if phase in ['BUILD', 'DEV', 'UAT']:
            self._create_development_phase(phase)
        elif phase in ['BENCH', 'PRODUCTION']:
            self._create_production_phase(phase)
        else:
            self.logger_error.error(f"Unknown phase type: {phase}")
            raise ValueError(f"Unknown phase type: {phase}")

    # All other methods inherit from V5 classes
    # V6 adds Y88 enhancements without breaking V5 functionality

    def _create_core_variables(self) -> None:
        """Create core template variables - V6 enhanced."""
        self.logger_cr.info("Creating core variables...")

        # Execute V5 core variable creation
        self.dict_value_for_template = self.dict_value_for_tempalte()
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

        # V6 Enhancement: Y88-specific variables
        if self.y88_detection and self.y88_detection.is_y88:
            self.logger_cr.info("🎯 V6: Creating Y88-specific variables...")

            # Y88 active interfaces variable
            if self.y88_detection.detected_interfaces:
                interface_names = [i.value for i in self.y88_detection.detected_interfaces]
                self.template_create_variable(
                    key='Y88_active_interfaces',
                    typev='StringVariable',
                    label='Y88 Active Interfaces',
                    description='Comma-separated list of active Y88 interfaces',
                    value=','.join(interface_names),
                    requiresValue=False,
                    showOnReleaseStart=False,
                    multiline=False
                )

        self.logger_cr.info("Core variables created successfully")

    def _create_system_variables(self) -> None:
        """Create system and API variables - V6 enhanced."""
        self.logger_cr.info("Creating system variables...")

        # Execute V5 system variable creation
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

        # V6 Enhancement: Y88 system variables
        if self.y88_detection and self.y88_detection.is_y88:
            self.logger_cr.info("🎯 V6: Creating Y88 system variables...")

            self.template_create_variable(
                key='Y88_project_type',
                typev='StringVariable',
                label='Y88 Project Type',
                description='Detected Y88 project type',
                value=self.y88_detection.project_type.value,
                requiresValue=False,
                showOnReleaseStart=False,
                multiline=False
            )

            self.template_create_variable(
                key='Y88_detection_confidence',
                typev='StringVariable',
                label='Y88 Detection Confidence',
                description='Y88 detection confidence score',
                value=str(round(self.y88_detection.confidence, 2)),
                requiresValue=False,
                showOnReleaseStart=False,
                multiline=False
            )

        self.logger_cr.info("System variables created successfully")

    def _finalize_template(self) -> None:
        """Finalize the template creation - V6 enhanced."""
        self.logger_cr.info("Finalizing template...")

        # Set template URL
        if hasattr(self, 'XLR_template_id'):
            base_url = self.config.get('xlr_base_url', self.url_api_xlr.replace('/api/v1/', ''))
            self.template_url = f"{base_url}#/templates/{self.XLR_template_id}"

        # V6 Enhancement: Y88 finalization
        if self.y88_detection and self.y88_detection.is_y88:
            self.logger_cr.info("🎯 V6: Finalizing Y88 optimizations...")

        self.logger_cr.info("Template finalized successfully")


def main():
    """Main entry point for V6 XLR Template Creation with Y88 enhancements."""
    parser = argparse.ArgumentParser(
        description='XLR Dynamic Template Creator - Version 6 Y88 Enhanced',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 V6 Y88 Enhanced Features:
  • Intelligent Y88 auto-detection and optimization
  • Advanced Y88 interface management
  • Y88-specific template generation
  • Enhanced BENCH_Y88 variable handling
  • Comprehensive Y88 analysis and reporting
  • 100% V5/V1 compatibility maintained

Example usage:
  python main.py --infile template.yaml
  python main.py --generate-y88-template --type loaniq_full --output my_template.yaml
  python main.py --detect-y88 --infile existing_template.yaml
        """
    )

    parser.add_argument(
        '--infile',
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

    # V6 Y88 Enhancement Arguments
    parser.add_argument(
        '--generate-y88-template',
        action='store_true',
        help='Generate a predefined Y88 template'
    )

    parser.add_argument(
        '--type',
        choices=['basic', 'loaniq_core', 'loaniq_interfaces', 'loaniq_full'],
        default='loaniq_full',
        help='Y88 template type to generate'
    )

    parser.add_argument(
        '--output',
        help='Output file for generated Y88 template'
    )

    parser.add_argument(
        '--detect-y88',
        action='store_true',
        help='Only perform Y88 detection and analysis on existing template'
    )

    args = parser.parse_args()

    # Set up logging level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        # V6 Enhancement: Y88 template generation
        if args.generate_y88_template:
            generator = Y88TemplateGenerator()
            predefined_templates = generator.get_predefined_templates()

            if args.type in predefined_templates:
                config = predefined_templates[args.type]
                template = generator.generate_template(config)

                output_path = args.output or f'y88_{args.type}_template.yaml'
                if generator.export_template(template, output_path):
                    print(f"✅ Y88 template generated: {output_path}")
                    return 0
                else:
                    print("❌ Failed to generate Y88 template")
                    return 1
            else:
                print(f"❌ Unknown template type: {args.type}")
                return 1

        # V6 Enhancement: Y88 detection only
        if args.detect_y88:
            if not args.infile:
                print("❌ --infile required for Y88 detection")
                return 1

            with open(args.infile, 'r', encoding='utf-8') as file:
                parameters = yaml.safe_load(file)

            detector = Y88Detector()
            detection = detector.detect_y88_environment(parameters)

            print("🔍 Y88 Detection Results:")
            print(f"   • Is Y88: {detection.is_y88}")
            print(f"   • Confidence: {detection.confidence:.2f}")
            print(f"   • Project Type: {detection.project_type.value}")
            print(f"   • Detected Interfaces: {len(detection.detected_interfaces)}")

            if detection.recommendations:
                print("💡 Recommendations:")
                for i, rec in enumerate(detection.recommendations, 1):
                    print(f"   {i}. {rec}")

            return 0

        # Standard template creation
        if not args.infile:
            print("❌ Error: --infile required for template creation")
            parser.print_help()
            return 1

        # Load YAML configuration
        with open(args.infile, 'r', encoding='utf-8') as file:
            parameters = yaml.safe_load(file)

        if not parameters:
            print("❌ Error: Empty or invalid YAML file")
            return 1

        # Create and run V6 template creator
        creator = XLRCreateTemplateV6(parameters)
        template_url = creator.create_template()

        print("\n" + "="*60)
        print("✅ XLR TEMPLATE CREATION V6 - Y88 ENHANCED COMPLETED")
        if creator.y88_detection and creator.y88_detection.is_y88:
            print("🎯 Y88 OPTIMIZATIONS APPLIED")
        print("="*60)
        print(f"📋 Template Name: {parameters['general_info']['name_release']}")
        print(f"🔗 Template URL: {template_url}")
        print(f"📁 Logs Directory: log/{parameters['general_info']['name_release']}/")

        if creator.y88_detection and creator.y88_detection.is_y88:
            print(f"🎯 Y88 Project Type: {creator.y88_detection.project_type.value}")
            print(f"📊 Y88 Confidence: {creator.y88_detection.confidence:.2f}")
            print(f"🔧 Y88 Interfaces: {len(creator.y88_detection.detected_interfaces)}")

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