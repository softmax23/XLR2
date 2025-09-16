"""
YAML Validator for XLR Template Creator V5.

This module implements comprehensive YAML validation based on V1 logic
with improved error handling and detailed validation reporting.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class YamlValidator:
    """Comprehensive YAML validator for XLR template configurations."""

    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize YAML validator.

        Args:
            parameters: YAML parameters to validate
        """
        self.parameters = parameters
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.logger = logging.getLogger(__name__)

    def validate(self) -> None:
        """
        Perform complete YAML validation.

        Raises:
            ValidationError: If validation fails
        """
        self.logger.info("Starting YAML validation...")

        # Reset error/warning lists
        self.errors = []
        self.warnings = []

        # Perform all validations
        self._validate_general_info()
        self._validate_phases()
        self._validate_packages()
        self._validate_jenkins_config()
        self._validate_xld_config()
        self._validate_technical_tasks()
        self._validate_controlm_config()
        self._validate_y88_specific()

        # Report results
        self._report_validation_results()

        # Raise exception if there are errors
        if self.errors:
            raise ValidationError(f"YAML validation failed with {len(self.errors)} errors")

        self.logger.info("YAML validation completed successfully")

    def _validate_general_info(self) -> None:
        """Validate general_info section."""
        if 'general_info' not in self.parameters:
            self.errors.append("Missing required section: general_info")
            return

        general_info = self.parameters['general_info']
        required_fields = [
            'type_template', 'xlr_folder', 'iua', 'appli_name',
            'phases', 'name_release', 'template_package_mode'
        ]

        for field in required_fields:
            if field not in general_info:
                self.errors.append(f"Missing required field in general_info: {field}")

        # Validate specific values
        if 'type_template' in general_info:
            valid_types = ['DYNAMIC', 'STATIC']
            if general_info['type_template'] not in valid_types:
                self.errors.append(f"Invalid type_template: {general_info['type_template']}. Must be one of: {valid_types}")

        if 'template_package_mode' in general_info:
            valid_modes = ['string', 'listbox']
            if general_info['template_package_mode'] not in valid_modes:
                self.errors.append(f"Invalid template_package_mode: {general_info['template_package_mode']}. Must be one of: {valid_modes}")

        if 'phase_mode' in general_info:
            valid_phase_modes = ['one_list', 'multi_list']
            if general_info['phase_mode'] not in valid_phase_modes:
                self.errors.append(f"Invalid phase_mode: {general_info['phase_mode']}. Must be one of: {valid_phase_modes}")

    def _validate_phases(self) -> None:
        """Validate phases configuration."""
        if 'general_info' not in self.parameters or 'phases' not in self.parameters['general_info']:
            return

        phases = self.parameters['general_info']['phases']
        valid_phases = ['BUILD', 'DEV', 'UAT', 'BENCH', 'PRODUCTION']

        if not isinstance(phases, list) or not phases:
            self.errors.append("phases must be a non-empty list")
            return

        for phase in phases:
            if phase not in valid_phases:
                self.errors.append(f"Invalid phase: {phase}. Must be one of: {valid_phases}")

        # Validate phase dependencies
        if 'PRODUCTION' in phases and 'BENCH' not in phases:
            self.warnings.append("PRODUCTION phase without BENCH phase may cause issues")

        # Check for Phases section
        if 'Phases' in self.parameters:
            phases_config = self.parameters['Phases']
            for phase in phases:
                if phase not in phases_config:
                    self.warnings.append(f"Phase {phase} defined in general_info but missing configuration in Phases section")

    def _validate_packages(self) -> None:
        """Validate template_liste_package section."""
        if 'template_liste_package' not in self.parameters:
            self.warnings.append("No template_liste_package defined")
            return

        packages = self.parameters['template_liste_package']
        if not isinstance(packages, dict):
            self.errors.append("template_liste_package must be a dictionary")
            return

        for package_name, package_config in packages.items():
            if not isinstance(package_config, dict):
                self.errors.append(f"Package {package_name} configuration must be a dictionary")
                continue

            # Validate required package fields
            required_package_fields = ['package_build_name']
            for field in required_package_fields:
                if field not in package_config:
                    self.warnings.append(f"Package {package_name} missing recommended field: {field}")

            # Validate mode field
            if 'mode' in package_config:
                valid_modes = ['CHECK_XLD', 'name_from_jenkins']
                if package_config['mode'] not in valid_modes:
                    self.errors.append(f"Invalid mode for package {package_name}: {package_config['mode']}")

            # Validate controlm_mode
            if 'controlm_mode' in package_config:
                valid_controlm_modes = ['Independant', 'master']
                if package_config['controlm_mode'] not in valid_controlm_modes:
                    self.errors.append(f"Invalid controlm_mode for package {package_name}: {package_config['controlm_mode']}")

    def _validate_jenkins_config(self) -> None:
        """Validate Jenkins configuration."""
        if 'jenkins' not in self.parameters:
            self.warnings.append("No Jenkins configuration found")
            return

        jenkins_config = self.parameters['jenkins']
        required_jenkins_fields = ['jenkinsServer', 'taskType', 'username']

        for field in required_jenkins_fields:
            if field not in jenkins_config:
                self.errors.append(f"Missing required Jenkins field: {field}")

        # Validate jenkinsjob section
        if 'jenkinsjob' in jenkins_config:
            jenkins_jobs = jenkins_config['jenkinsjob']
            if isinstance(jenkins_jobs, dict):
                for job_name, job_config in jenkins_jobs.items():
                    if 'jobName' not in job_config:
                        self.errors.append(f"Jenkins job {job_name} missing jobName")

    def _validate_xld_config(self) -> None:
        """Validate XLD configuration."""
        # Check for XLD environment variables
        xld_env_vars = ['XLD_ENV_DEV', 'XLD_ENV_UAT', 'XLD_ENV_BENCH', 'XLD_ENV_PRODUCTION']

        for env_var in xld_env_vars:
            if env_var in self.parameters:
                xld_env = self.parameters[env_var]
                if not isinstance(xld_env, list):
                    self.errors.append(f"{env_var} must be a list")

    def _validate_technical_tasks(self) -> None:
        """Validate technical tasks configuration."""
        if 'technical_task_list' not in self.parameters:
            return

        technical_tasks = self.parameters['technical_task_list']
        if not isinstance(technical_tasks, dict):
            self.errors.append("technical_task_list must be a dictionary")
            return

        valid_categories = ['before_deployment', 'before_xldeploy', 'after_xldeploy', 'after_deployment']
        for category in technical_tasks:
            if category not in valid_categories:
                self.warnings.append(f"Unknown technical task category: {category}")

    def _validate_controlm_config(self) -> None:
        """Validate Control-M configuration."""
        # Check for Control-M tasks in phases
        if 'Phases' in self.parameters:
            phases_config = self.parameters['Phases']
            for phase_name, phase_tasks in phases_config.items():
                if isinstance(phase_tasks, list):
                    for task in phase_tasks:
                        if isinstance(task, dict):
                            for task_type in task.keys():
                                if 'XLR_task_controlm' in task_type:
                                    # Validate Control-M task structure
                                    controlm_task = task[task_type]
                                    if not isinstance(controlm_task, list):
                                        self.errors.append(f"Control-M task in phase {phase_name} must be a list")

    def _validate_y88_specific(self) -> None:
        """Validate Y88-specific configurations."""
        if 'general_info' not in self.parameters:
            return

        iua = self.parameters['general_info'].get('iua', '')
        phases = self.parameters['general_info'].get('phases', [])

        if 'Y88' in iua:
            # Y88-specific validations
            if 'BENCH' in phases:
                self.logger.info("Y88 environment with BENCH phase detected - will apply Y88-specific logic")

            # Check for Y88-specific packages
            if 'template_liste_package' in self.parameters:
                packages = self.parameters['template_liste_package']
                y88_packages = [
                    'Interface_summit', 'Interface_summit_COF', 'Interface_TOGE',
                    'Interface_TOGE_ACK', 'Interface_NON_LOAN_US', 'DICTIONNAIRE',
                    'Interface_MOTOR', 'Interface_ROAR_ACK', 'Interface_ROAR'
                ]

                for pkg in y88_packages:
                    if pkg in packages:
                        self.logger.info(f"Y88-specific package detected: {pkg}")

    def _report_validation_results(self) -> None:
        """Report validation results."""
        if self.errors:
            self.logger.error(f"YAML Validation failed with {len(self.errors)} errors:")
            for i, error in enumerate(self.errors, 1):
                self.logger.error(f"  {i}. {error}")

        if self.warnings:
            self.logger.warning(f"YAML Validation completed with {len(self.warnings)} warnings:")
            for i, warning in enumerate(self.warnings, 1):
                self.logger.warning(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            self.logger.info("YAML validation completed with no issues")

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get validation summary.

        Returns:
            Dictionary with validation results
        """
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }