"""
Y88 Auto-Detection Module - V6 Enhancement

This module automatically detects Y88 environments and suggests optimal configurations.
It analyzes YAML templates and provides intelligent recommendations for Y88-specific setups.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class Y88ProjectType(Enum):
    """Y88 project types."""
    LOANIQ_CORE = "loaniq_core"
    LOANIQ_INTERFACES = "loaniq_interfaces"
    LOANIQ_FULL = "loaniq_full"
    CUSTOM = "custom"


class Y88InterfaceType(Enum):
    """Y88 interface types."""
    SUMMIT = "summit"
    SUMMIT_COF = "summit_cof"
    TOGE = "toge"
    TOGE_ACK = "toge_ack"
    NON_LOAN_US = "non_loan_us"
    NON_LOAN_APAC = "non_loan_apac"
    MOTOR = "motor"
    ROAR = "roar"
    ROAR_ACK = "roar_ack"
    DICTIONNAIRE = "dictionnaire"


@dataclass
class Y88Detection:
    """Y88 detection result."""
    is_y88: bool
    confidence: float
    project_type: Y88ProjectType
    detected_interfaces: List[Y88InterfaceType]
    recommendations: List[str]
    suggested_configs: Dict[str, Any]


@dataclass
class Y88PackageInfo:
    """Y88 package information."""
    name: str
    category: str  # APP, SCR, SDK, INT
    interface_type: Optional[Y88InterfaceType]
    xld_path_pattern: str
    controlm_mode: str


class Y88Detector:
    """
    Advanced Y88 environment detection and configuration suggester.

    This class analyzes YAML templates and automatically detects Y88 patterns,
    suggests optimal configurations, and provides intelligent recommendations.
    """

    def __init__(self):
        """Initialize Y88 detector."""
        self.logger = logging.getLogger(__name__)

        # Y88 patterns for detection
        self.y88_patterns = {
            'iua': [r'.*Y88.*', r'NXY88', r'.*y88.*'],
            'paths': [r'.*Y88_LOANIQ.*', r'.*y88.*', r'.*Y88.*'],
            'jenkins': [r'.*Y88.*', r'.*y88.*'],
            'packages': [r'.*Y88_.*', r'.*y88.*'],
            'controlm': [r'.*Y88.*', r'.*PY88.*']
        }

        # Y88 interface detection patterns
        self.interface_patterns = {
            Y88InterfaceType.SUMMIT: [r'.*summit.*', r'.*SUMMIT.*'],
            Y88InterfaceType.SUMMIT_COF: [r'.*summit.*cof.*', r'.*SUMMIT.*COF.*'],
            Y88InterfaceType.TOGE: [r'.*toge.*', r'.*TOGE.*'],
            Y88InterfaceType.TOGE_ACK: [r'.*toge.*ack.*', r'.*TOGE.*ACK.*'],
            Y88InterfaceType.NON_LOAN_US: [r'.*non.*loan.*us.*', r'.*NON.*LOAN.*US.*'],
            Y88InterfaceType.NON_LOAN_APAC: [r'.*non.*loan.*apac.*', r'.*NON.*LOAN.*APAC.*'],
            Y88InterfaceType.MOTOR: [r'.*motor.*', r'.*MOTOR.*'],
            Y88InterfaceType.ROAR: [r'roar(?!.*ack)', r'ROAR(?!.*ACK)'],
            Y88InterfaceType.ROAR_ACK: [r'.*roar.*ack.*', r'.*ROAR.*ACK.*'],
            Y88InterfaceType.DICTIONNAIRE: [r'.*dictionnaire.*', r'.*DICTIONNAIRE.*']
        }

    def detect_y88_environment(self, parameters: Dict[str, Any]) -> Y88Detection:
        """
        Detect if the configuration is for a Y88 environment.

        Args:
            parameters: YAML configuration parameters

        Returns:
            Y88Detection object with detection results and recommendations
        """
        self.logger.info("Starting Y88 environment detection...")

        confidence_scores = []
        detected_interfaces = []
        recommendations = []

        # 1. Check IUA for Y88 patterns
        iua_score = self._check_iua_patterns(parameters)
        confidence_scores.append(iua_score)

        # 2. Check paths for Y88 patterns
        path_score = self._check_path_patterns(parameters)
        confidence_scores.append(path_score)

        # 3. Check Jenkins configuration
        jenkins_score = self._check_jenkins_patterns(parameters)
        confidence_scores.append(jenkins_score)

        # 4. Check package names
        package_score = self._check_package_patterns(parameters)
        confidence_scores.append(package_score)

        # 5. Check ControlM patterns
        controlm_score = self._check_controlm_patterns(parameters)
        confidence_scores.append(controlm_score)

        # 6. Detect interfaces
        detected_interfaces = self._detect_interfaces(parameters)

        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # Determine if it's Y88
        is_y88 = overall_confidence > 0.6

        # Determine project type
        project_type = self._determine_project_type(parameters, detected_interfaces)

        # Generate recommendations
        recommendations = self._generate_recommendations(parameters, detected_interfaces, overall_confidence)

        # Generate suggested configurations
        suggested_configs = self._generate_suggested_configs(parameters, detected_interfaces, project_type)

        result = Y88Detection(
            is_y88=is_y88,
            confidence=overall_confidence,
            project_type=project_type,
            detected_interfaces=detected_interfaces,
            recommendations=recommendations,
            suggested_configs=suggested_configs
        )

        self.logger.info(f"Y88 detection completed. Is Y88: {is_y88}, Confidence: {overall_confidence:.2f}")

        return result

    def _check_iua_patterns(self, parameters: Dict[str, Any]) -> float:
        """Check IUA field for Y88 patterns."""
        iua = parameters.get('general_info', {}).get('iua', '')

        for pattern in self.y88_patterns['iua']:
            if re.match(pattern, str(iua), re.IGNORECASE):
                return 1.0

        return 0.0

    def _check_path_patterns(self, parameters: Dict[str, Any]) -> float:
        """Check XLD paths for Y88 patterns."""
        packages = parameters.get('template_liste_package', {})
        matches = 0
        total_paths = 0

        for package_name, package_config in packages.items():
            app_path = package_config.get('XLD_application_path', '')
            env_path = package_config.get('XLD_environment_path', '')

            for path in [app_path, env_path]:
                if path:
                    total_paths += 1
                    for pattern in self.y88_patterns['paths']:
                        if re.search(pattern, path, re.IGNORECASE):
                            matches += 1
                            break

        return matches / total_paths if total_paths > 0 else 0.0

    def _check_jenkins_patterns(self, parameters: Dict[str, Any]) -> float:
        """Check Jenkins configuration for Y88 patterns."""
        jenkins_config = parameters.get('jenkins', {})

        jenkins_server = jenkins_config.get('jenkinsServer', '')
        username = jenkins_config.get('username', '')

        score = 0.0
        checks = 0

        # Check server
        if jenkins_server:
            checks += 1
            for pattern in self.y88_patterns['jenkins']:
                if re.search(pattern, jenkins_server, re.IGNORECASE):
                    score += 1.0
                    break

        # Check username
        if username:
            checks += 1
            for pattern in self.y88_patterns['jenkins']:
                if re.search(pattern, username, re.IGNORECASE):
                    score += 1.0
                    break

        # Check job names
        jenkins_jobs = jenkins_config.get('jenkinsjob', {})
        for job_name, job_config in jenkins_jobs.items():
            job_path = job_config.get('jobName', '')
            if job_path:
                checks += 1
                for pattern in self.y88_patterns['jenkins']:
                    if re.search(pattern, job_path, re.IGNORECASE):
                        score += 1.0
                        break

        return score / checks if checks > 0 else 0.0

    def _check_package_patterns(self, parameters: Dict[str, Any]) -> float:
        """Check package names for Y88 patterns."""
        packages = parameters.get('template_liste_package', {})
        matches = 0
        total_packages = len(packages)

        for package_name, package_config in packages.items():
            build_name = package_config.get('package_build_name', '')

            # Check package name and build name
            for name in [package_name, build_name]:
                if name:
                    for pattern in self.y88_patterns['packages']:
                        if re.search(pattern, str(name), re.IGNORECASE):
                            matches += 1
                            break

        return matches / total_packages if total_packages > 0 else 0.0

    def _check_controlm_patterns(self, parameters: Dict[str, Any]) -> float:
        """Check ControlM configuration for Y88 patterns."""
        phases = parameters.get('Phases', {})
        matches = 0
        total_controlm_tasks = 0

        for phase_name, phase_tasks in phases.items():
            if isinstance(phase_tasks, list):
                for task in phase_tasks:
                    if isinstance(task, dict):
                        for task_type, task_config in task.items():
                            if 'controlm' in task_type.lower():
                                total_controlm_tasks += 1

                                # Check ControlM task names
                                if isinstance(task_config, list):
                                    for controlm_task in task_config:
                                        for pattern in self.y88_patterns['controlm']:
                                            if re.search(pattern, str(controlm_task), re.IGNORECASE):
                                                matches += 1
                                                break

        return matches / total_controlm_tasks if total_controlm_tasks > 0 else 0.0

    def _detect_interfaces(self, parameters: Dict[str, Any]) -> List[Y88InterfaceType]:
        """Detect Y88 interfaces in the configuration."""
        detected_interfaces = []
        packages = parameters.get('template_liste_package', {})

        for package_name, package_config in packages.items():
            for interface_type, patterns in self.interface_patterns.items():
                for pattern in patterns:
                    if (re.search(pattern, package_name, re.IGNORECASE) or
                        re.search(pattern, package_config.get('package_build_name', ''), re.IGNORECASE)):
                        if interface_type not in detected_interfaces:
                            detected_interfaces.append(interface_type)
                        break

        return detected_interfaces

    def _determine_project_type(self, parameters: Dict[str, Any], interfaces: List[Y88InterfaceType]) -> Y88ProjectType:
        """Determine the Y88 project type based on configuration."""
        packages = parameters.get('template_liste_package', {})

        # Check for core components
        has_app = any('app' in name.lower() for name in packages.keys())
        has_scripts = any('script' in name.lower() for name in packages.keys())
        has_sdk = any('sdk' in name.lower() for name in packages.keys())

        # Check for interfaces
        has_interfaces = len(interfaces) > 0

        if has_app and has_scripts and has_sdk and has_interfaces:
            return Y88ProjectType.LOANIQ_FULL
        elif has_interfaces and not (has_app or has_scripts or has_sdk):
            return Y88ProjectType.LOANIQ_INTERFACES
        elif (has_app or has_scripts or has_sdk) and not has_interfaces:
            return Y88ProjectType.LOANIQ_CORE
        else:
            return Y88ProjectType.CUSTOM

    def _generate_recommendations(self, parameters: Dict[str, Any], interfaces: List[Y88InterfaceType], confidence: float) -> List[str]:
        """Generate recommendations for Y88 configuration optimization."""
        recommendations = []

        if confidence > 0.8:
            recommendations.append("🎯 High confidence Y88 detection - Consider using Y88 optimized templates")

        # Check for BENCH phase and Y88
        phases = parameters.get('general_info', {}).get('phases', [])
        if 'BENCH' in phases and not any('BENCH_Y88' in str(parameters).upper() for _ in [1]):
            recommendations.append("🔧 Add BENCH_Y88 variable for optimal Y88 BENCH phase management")

        # Interface recommendations
        if len(interfaces) > 5:
            recommendations.append("📦 Consider grouping interfaces by type for better organization")

        # ControlM recommendations
        if any('controlm' in str(parameters).lower() for _ in [1]):
            recommendations.append("⚙️ Use Y88-specific ControlM prefixes (BDCP_, PDCP_)")

        # XLD path recommendations
        if not any('Y88_LOANIQ' in str(parameters) for _ in [1]):
            recommendations.append("📂 Consider using standard Y88 XLD path structure")

        return recommendations

    def _generate_suggested_configs(self, parameters: Dict[str, Any], interfaces: List[Y88InterfaceType], project_type: Y88ProjectType) -> Dict[str, Any]:
        """Generate suggested configuration improvements."""
        suggestions = {}

        # Suggest BENCH_Y88 variable if missing
        if 'BENCH' in parameters.get('general_info', {}).get('phases', []):
            suggestions['add_bench_y88_variable'] = True

        # Suggest standard Y88 XLD paths
        suggestions['standard_xld_paths'] = {
            'base_path': 'Environments/PFI/Y88_LOANIQ/7.6',
            'app_pattern': '<ENV>/<ENV>/<XLD_env>/APP/<xld_prefix_env>Y88_APP_<XLD_env>_ENV',
            'scr_pattern': '<ENV>/<ENV>/<XLD_env>/SCR/<xld_prefix_env>Y88_SCR_<XLD_env>_ENV',
            'sdk_pattern': '<ENV>/<ENV>/<XLD_env>/SDK/<xld_prefix_env>Y88_SDK_<XLD_env>_ENV',
            'int_pattern': '<ENV>/<ENV>/<XLD_env>/INT/<xld_prefix_env>Y88_INT_<XLD_env>_ENV'
        }

        # Suggest ControlM configurations
        suggestions['controlm_prefixes'] = {
            'bench': 'BDCP_',
            'production': 'PDCP_'
        }

        # Suggest Jenkins configuration
        suggestions['jenkins_config'] = {
            'server': 'Configuration/Custom/Jenkins-Y88',
            'username_pattern': '*y88*_jenkins@company.com'
        }

        return suggestions

    def get_y88_package_info(self, package_name: str, package_config: Dict[str, Any]) -> Y88PackageInfo:
        """Get detailed Y88 package information."""
        # Determine category
        if 'app' in package_name.lower():
            category = 'APP'
        elif 'script' in package_name.lower():
            category = 'SCR'
        elif 'sdk' in package_name.lower():
            category = 'SDK'
        elif 'interface' in package_name.lower() or 'int' in package_name.lower():
            category = 'INT'
        else:
            category = 'CUSTOM'

        # Determine interface type
        interface_type = None
        for itype, patterns in self.interface_patterns.items():
            for pattern in patterns:
                if re.search(pattern, package_name, re.IGNORECASE):
                    interface_type = itype
                    break
            if interface_type:
                break

        # Determine ControlM mode
        controlm_mode = package_config.get('controlm_mode', 'master')
        if category == 'INT' or interface_type:
            controlm_mode = 'Independant'

        # Generate XLD path pattern
        xld_path_pattern = f"Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/{category}/<xld_prefix_env>Y88_{category}_<XLD_env>_ENV"

        return Y88PackageInfo(
            name=package_name,
            category=category,
            interface_type=interface_type,
            xld_path_pattern=xld_path_pattern,
            controlm_mode=controlm_mode
        )

    def analyze_y88_completeness(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Y88 configuration completeness and suggest improvements."""
        analysis = {
            'completeness_score': 0.0,
            'missing_components': [],
            'optimization_suggestions': [],
            'configuration_gaps': []
        }

        # Check for standard Y88 components
        packages = parameters.get('template_liste_package', {})
        expected_components = ['App', 'Scripts', 'SDK', 'Interfaces']
        found_components = []

        for package_name in packages.keys():
            if 'app' in package_name.lower():
                found_components.append('App')
            elif 'script' in package_name.lower():
                found_components.append('Scripts')
            elif 'sdk' in package_name.lower():
                found_components.append('SDK')
            elif 'interface' in package_name.lower():
                found_components.append('Interfaces')

        found_components = list(set(found_components))
        missing_components = [comp for comp in expected_components if comp not in found_components]

        analysis['missing_components'] = missing_components
        analysis['completeness_score'] = len(found_components) / len(expected_components)

        # Check for Y88-specific configurations
        if 'BENCH' in parameters.get('general_info', {}).get('phases', []):
            if 'BENCH_Y88' not in str(parameters):
                analysis['configuration_gaps'].append('Missing BENCH_Y88 variable')

        # Check for proper Y88 ControlM prefixes
        controlm_found = False
        phases = parameters.get('Phases', {})
        for phase_name, phase_tasks in phases.items():
            if phase_name in ['BENCH', 'PRODUCTION']:
                # Check for proper Y88 ControlM naming
                phase_str = str(phase_tasks)
                if 'Y88' in phase_str:
                    controlm_found = True

        if not controlm_found and phases:
            analysis['configuration_gaps'].append('Y88 ControlM tasks not properly configured')

        return analysis