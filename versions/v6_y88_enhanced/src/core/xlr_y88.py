"""
XLR Y88 Specialized Module - V6 Enhancement

This module provides comprehensive Y88 environment management with advanced features:
- Intelligent Y88 detection and configuration
- Automated BENCH_Y88 variable management
- Y88-specific XLD path generation
- Advanced interface categorization
- Y88 ControlM optimization
- Y88 Jenkins integration
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..y88.y88_detector import Y88Detector, Y88Detection, Y88ProjectType, Y88InterfaceType


@dataclass
class Y88Config:
    """Y88 configuration settings."""
    is_y88_enabled: bool = False
    auto_bench_variable: bool = True
    standard_xld_paths: bool = True
    interface_categorization: bool = True
    controlm_optimization: bool = True
    jenkins_optimization: bool = True


class XLRY88Error(Exception):
    """Custom exception for Y88 operations."""
    pass


class XLRY88:
    """
    Advanced Y88 environment management for XLR templates.

    This class provides comprehensive Y88 support including:
    - Automatic Y88 detection and configuration
    - BENCH_Y88 variable management
    - Y88-specific XLD path generation
    - Interface categorization and optimization
    - ControlM task optimization for Y88
    - Jenkins integration enhancements
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize Y88 manager."""
        self.logger = logging.getLogger(__name__)
        self.parameters = parameters or {}

        # Initialize Y88 detector
        self.detector = Y88Detector()

        # Y88 configuration
        self.y88_config = Y88Config()

        # Y88 detection result
        self.detection_result: Optional[Y88Detection] = None

        # Y88 state
        self.is_y88_environment = False
        self.y88_project_type = Y88ProjectType.CUSTOM
        self.detected_interfaces: List[Y88InterfaceType] = []

        # Y88 runtime data
        self.bench_y88_variable_created = False
        self.y88_controlm_tasks = {}
        self.y88_interface_groups = {}

        # Perform initial detection if parameters provided
        if self.parameters:
            self.detect_and_configure_y88()

    def detect_and_configure_y88(self) -> Y88Detection:
        """
        Detect Y88 environment and automatically configure optimizations.

        Returns:
            Y88Detection result with recommendations
        """
        self.logger.info("Starting Y88 detection and configuration...")

        # Perform Y88 detection
        self.detection_result = self.detector.detect_y88_environment(self.parameters)

        # Update internal state
        self.is_y88_environment = self.detection_result.is_y88
        self.y88_project_type = self.detection_result.project_type
        self.detected_interfaces = self.detection_result.detected_interfaces

        if self.is_y88_environment:
            self.logger.info(f"🎯 Y88 environment detected! Type: {self.y88_project_type.value}")
            self.logger.info(f"📦 Detected interfaces: {[i.value for i in self.detected_interfaces]}")

            # Apply automatic optimizations
            self._apply_y88_optimizations()
        else:
            self.logger.info("❌ Y88 environment not detected")

        return self.detection_result

    def _apply_y88_optimizations(self) -> None:
        """Apply automatic Y88 optimizations."""
        self.logger.info("🚀 Applying Y88 optimizations...")

        # Apply optimizations based on configuration
        if self.y88_config.auto_bench_variable and 'BENCH' in self.parameters.get('general_info', {}).get('phases', []):
            self._configure_bench_y88_variable()

        if self.y88_config.standard_xld_paths:
            self._optimize_xld_paths()

        if self.y88_config.interface_categorization:
            self._categorize_interfaces()

        if self.y88_config.controlm_optimization:
            self._optimize_controlm_tasks()

        if self.y88_config.jenkins_optimization:
            self._optimize_jenkins_config()

        self.logger.info("✅ Y88 optimizations applied successfully")

    def _configure_bench_y88_variable(self) -> None:
        """Configure BENCH_Y88 variable for Y88 environments."""
        self.logger.info("🔧 Configuring BENCH_Y88 variable...")

        # Add BENCH_Y88 to variable_release if not present
        if 'variable_release' not in self.parameters:
            self.parameters['variable_release'] = {}

        if 'BENCH_Y88' not in self.parameters['variable_release']:
            self.parameters['variable_release']['BENCH_Y88'] = True
            self.logger.info("✅ Added BENCH_Y88 to variable_release")

        self.bench_y88_variable_created = True

    def _optimize_xld_paths(self) -> None:
        """Optimize XLD paths for Y88 standards."""
        self.logger.info("📂 Optimizing XLD paths for Y88...")

        packages = self.parameters.get('template_liste_package', {})

        for package_name, package_config in packages.items():
            if self._is_y88_package(package_name, package_config):
                # Get optimized paths
                optimized_paths = self._generate_y88_xld_paths(package_name, package_config)

                # Update configuration
                package_config['XLD_application_path'] = optimized_paths['application_path']
                package_config['XLD_environment_path'] = optimized_paths['environment_path']

                self.logger.info(f"✅ Optimized XLD paths for package: {package_name}")

    def _categorize_interfaces(self) -> None:
        """Categorize Y88 interfaces by type."""
        self.logger.info("🏷️ Categorizing Y88 interfaces...")

        packages = self.parameters.get('template_liste_package', {})

        for package_name, package_config in packages.items():
            package_info = self.detector.get_y88_package_info(package_name, package_config)

            if package_info.interface_type:
                # Group interfaces by type
                if package_info.category not in self.y88_interface_groups:
                    self.y88_interface_groups[package_info.category] = []

                self.y88_interface_groups[package_info.category].append({
                    'name': package_name,
                    'type': package_info.interface_type,
                    'info': package_info
                })

        self.logger.info(f"✅ Categorized {len(self.y88_interface_groups)} interface groups")

    def _optimize_controlm_tasks(self) -> None:
        """Optimize ControlM tasks for Y88."""
        self.logger.info("⚙️ Optimizing ControlM tasks for Y88...")

        phases = self.parameters.get('Phases', {})

        for phase_name, phase_tasks in phases.items():
            if phase_name in ['BENCH', 'PRODUCTION'] and isinstance(phase_tasks, list):
                self._optimize_phase_controlm_tasks(phase_name, phase_tasks)

        self.logger.info("✅ ControlM tasks optimized for Y88")

    def _optimize_phase_controlm_tasks(self, phase: str, phase_tasks: List[Dict]) -> None:
        """Optimize ControlM tasks for a specific phase."""
        for task in phase_tasks:
            if isinstance(task, dict):
                for task_type, task_config in task.items():
                    if 'controlm' in task_type.lower():
                        # Apply Y88-specific ControlM optimizations
                        if isinstance(task_config, list):
                            optimized_tasks = []
                            for controlm_task in task_config:
                                optimized_task = self._optimize_controlm_task_name(controlm_task, phase)
                                optimized_tasks.append(optimized_task)
                            task[task_type] = optimized_tasks

    def _optimize_controlm_task_name(self, task_name: str, phase: str) -> str:
        """Optimize individual ControlM task name for Y88."""
        # Apply Y88-specific naming conventions
        if phase == 'BENCH':
            if not task_name.startswith('Y88_FOLDER_'):
                return f"Y88_FOLDER_{task_name.replace('FOLDER_', '')}"
        elif phase == 'PRODUCTION':
            if not task_name.startswith('Y88_PROD_'):
                return f"Y88_PROD_{task_name.replace('FOLDER_', '').replace('Y88_', '')}"

        return task_name

    def _optimize_jenkins_config(self) -> None:
        """Optimize Jenkins configuration for Y88."""
        self.logger.info("🔧 Optimizing Jenkins configuration for Y88...")

        jenkins_config = self.parameters.get('jenkins', {})

        if jenkins_config:
            # Ensure Y88 Jenkins server
            if 'jenkinsServer' not in jenkins_config or 'Y88' not in jenkins_config['jenkinsServer']:
                jenkins_config['jenkinsServer'] = 'Configuration/Custom/Jenkins-Y88'
                self.logger.info("✅ Set Y88 Jenkins server")

            # Optimize job names
            jenkins_jobs = jenkins_config.get('jenkinsjob', {})
            for job_name, job_config in jenkins_jobs.items():
                if 'jobName' in job_config:
                    optimized_job_name = self._optimize_jenkins_job_name(job_config['jobName'])
                    if optimized_job_name != job_config['jobName']:
                        job_config['jobName'] = optimized_job_name
                        self.logger.info(f"✅ Optimized Jenkins job for {job_name}")

    def _optimize_jenkins_job_name(self, job_name: str) -> str:
        """Optimize Jenkins job name for Y88."""
        if not job_name.startswith('Y88/'):
            # Add Y88 prefix if missing
            return f"Y88/{job_name}"
        return job_name

    def _is_y88_package(self, package_name: str, package_config: Dict[str, Any]) -> bool:
        """Check if a package is Y88-related."""
        # Check package name
        if 'y88' in package_name.lower():
            return True

        # Check paths
        app_path = package_config.get('XLD_application_path', '')
        env_path = package_config.get('XLD_environment_path', '')

        for path in [app_path, env_path]:
            if 'Y88' in path or 'y88' in path.lower():
                return True

        return False

    def _generate_y88_xld_paths(self, package_name: str, package_config: Dict[str, Any]) -> Dict[str, str]:
        """Generate optimized Y88 XLD paths."""
        package_info = self.detector.get_y88_package_info(package_name, package_config)

        # Base paths for Y88
        base_app_path = f"Applications/PFI/Y88_LOANIQ/{package_info.category}/Y88_{package_info.category}_LOANIQ"

        if package_info.interface_type:
            # Special handling for interfaces
            interface_name = package_info.interface_type.value.upper()
            base_app_path = f"Applications/PFI/Y88_LOANIQ/INT/Y88_{interface_name}"

        # Environment path with BENCH_Y88 support
        if package_info.category == 'APP':
            base_env_path = "Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/APP/<xld_prefix_env>Y88_APP_<XLD_env>_ENV"
        elif package_info.category == 'SCR':
            base_env_path = "Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/SCR/<xld_prefix_env>Y88_SCR_<XLD_env>_ENV"
        elif package_info.category == 'SDK':
            base_env_path = "Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/SDK/<xld_prefix_env>Y88_SDK_<XLD_env>_ENV"
        elif package_info.category == 'INT':
            base_env_path = "Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/INT/<xld_prefix_env>Y88_INT_<XLD_env>_ENV"
        else:
            base_env_path = f"Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/{package_info.category}/<xld_prefix_env>Y88_{package_info.category}_<XLD_env>_ENV"

        return {
            'application_path': base_app_path,
            'environment_path': base_env_path
        }

    def create_bench_y88_variable(self, phase_id: str) -> bool:
        """
        Create BENCH_Y88 variable in XLR template.

        Args:
            phase_id: XLR phase ID where to create the variable

        Returns:
            Success status
        """
        try:
            if not hasattr(self, 'url_api_xlr') or not hasattr(self, 'header'):
                self.logger.warning("XLR API not configured, skipping BENCH_Y88 variable creation")
                return False

            self.logger.info("Creating BENCH_Y88 variable...")

            variable_data = {
                "id": "null",
                "type": "xlrelease.StringVariable",
                "key": "BENCH_Y88",
                "label": "BENCH_Y88",
                "description": "Y88 BENCH environment selection",
                "value": "",
                "requiresValue": False,
                "showOnReleaseStart": False,
                "multiline": False
            }

            url = f"{self.url_api_xlr}templates/{phase_id}/variables"
            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=variable_data,
                verify=False
            )

            if response.status_code == 200:
                self.logger.info("✅ BENCH_Y88 variable created successfully")
                self.bench_y88_variable_created = True
                return True
            else:
                self.logger.error(f"Failed to create BENCH_Y88 variable: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error creating BENCH_Y88 variable: {e}")
            return False

    def create_y88_jython_script(self, template_id: str, phase: str) -> Optional[str]:
        """
        Create Y88-specific Jython script for dynamic task management.

        Args:
            template_id: XLR template ID
            phase: Phase name

        Returns:
            Task ID if successful
        """
        try:
            self.logger.info(f"Creating Y88 Jython script for phase {phase}...")

            script_content = self._generate_y88_jython_script(phase)

            script_data = {
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "title": f"Y88 Dynamic Management - {phase}",
                "script": script_content,
                "scriptType": "Jython"
            }

            url = f"{self.url_api_xlr}templates/{template_id}/tasks"
            response = requests.post(
                url,
                headers=self.header,
                auth=(self.ops_username_api, self.ops_password_api),
                json=script_data,
                verify=False
            )

            if response.status_code == 200:
                task_id = response.json().get('id')
                self.logger.info(f"✅ Y88 Jython script created: {task_id}")
                return task_id
            else:
                self.logger.error(f"Failed to create Y88 Jython script: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating Y88 Jython script: {e}")
            return None

    def _generate_y88_jython_script(self, phase: str) -> str:
        """Generate Y88-specific Jython script content."""
        script_lines = [
            "# Y88 Dynamic Management Script",
            "# Auto-generated by XLR Y88 Enhanced V6",
            "",
            "# Y88 BENCH variable management",
            "if phase == 'BENCH':",
            "    if 'env_BENCH' in releaseVariables:",
            "        releaseVariables['BENCH_Y88'] = releaseVariables['env_BENCH'].split('_')[0]",
            "        print('BENCH_Y88 set to: ' + releaseVariables['BENCH_Y88'])",
            "",
            "# Y88 interface management",
            "def manage_y88_interfaces():",
            "    interfaces = []"
        ]

        # Add interface-specific logic
        for interface in self.detected_interfaces:
            interface_name = interface.value.upper()
            script_lines.extend([
                f"    if '{interface_name}' in releaseVariables:",
                f"        interfaces.append('{interface_name}')",
            ])

        script_lines.extend([
            "    releaseVariables['Y88_active_interfaces'] = ','.join(interfaces)",
            "    print('Active Y88 interfaces: ' + releaseVariables['Y88_active_interfaces'])",
            "",
            "# Execute Y88 management",
            "manage_y88_interfaces()",
            "",
            "print('Y88 dynamic management completed for phase: ' + phase)"
        ])

        return "\\n".join(script_lines)

    def get_y88_summary(self) -> Dict[str, Any]:
        """Get comprehensive Y88 environment summary."""
        if not self.detection_result:
            return {"error": "Y88 detection not performed"}

        return {
            "is_y88_environment": self.is_y88_environment,
            "confidence": self.detection_result.confidence,
            "project_type": self.y88_project_type.value,
            "detected_interfaces": [i.value for i in self.detected_interfaces],
            "interface_groups": {k: len(v) for k, v in self.y88_interface_groups.items()},
            "recommendations": self.detection_result.recommendations,
            "optimizations_applied": {
                "bench_y88_variable": self.bench_y88_variable_created,
                "interface_categorization": len(self.y88_interface_groups) > 0,
                "controlm_optimization": len(self.y88_controlm_tasks) > 0
            },
            "suggested_configs": self.detection_result.suggested_configs
        }

    def export_y88_report(self, output_path: str) -> bool:
        """Export detailed Y88 analysis report."""
        try:
            import json
            from datetime import datetime

            report = {
                "report_generated": datetime.now().isoformat(),
                "y88_analysis": self.get_y88_summary(),
                "configuration_analysis": self.detector.analyze_y88_completeness(self.parameters),
                "detected_packages": {},
                "optimization_recommendations": self.detection_result.recommendations if self.detection_result else []
            }

            # Add package analysis
            packages = self.parameters.get('template_liste_package', {})
            for package_name, package_config in packages.items():
                if self._is_y88_package(package_name, package_config):
                    package_info = self.detector.get_y88_package_info(package_name, package_config)
                    report["detected_packages"][package_name] = {
                        "category": package_info.category,
                        "interface_type": package_info.interface_type.value if package_info.interface_type else None,
                        "controlm_mode": package_info.controlm_mode,
                        "xld_path_pattern": package_info.xld_path_pattern
                    }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Y88 report exported to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export Y88 report: {e}")
            return False

    def setup_xlr_connection(self, url_api_xlr: str, username: str, password: str, header: Dict[str, str]) -> None:
        """Setup XLR API connection for Y88 operations."""
        self.url_api_xlr = url_api_xlr
        self.ops_username_api = username
        self.ops_password_api = password
        self.header = header
        self.logger.info("✅ XLR connection configured for Y88 operations")