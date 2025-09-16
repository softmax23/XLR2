"""
Y88 Template Generator - V6 Enhancement

This module provides predefined Y88 templates and intelligent template generation
for different Y88 project types and configurations.
"""

import yaml
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .y88_detector import Y88ProjectType, Y88InterfaceType


class Y88TemplateType(Enum):
    """Y88 template types."""
    BASIC = "basic"
    LOANIQ_CORE = "loaniq_core"
    LOANIQ_INTERFACES = "loaniq_interfaces"
    LOANIQ_FULL = "loaniq_full"
    CUSTOM = "custom"


@dataclass
class Y88TemplateConfig:
    """Y88 template configuration."""
    template_type: Y88TemplateType
    project_name: str
    iua: str
    phases: List[str]
    interfaces: List[Y88InterfaceType]
    enable_jenkins: bool = True
    enable_controlm: bool = True
    enable_sun: bool = True


class Y88TemplateGenerator:
    """
    Advanced Y88 template generator.

    Provides predefined templates and intelligent generation for Y88 environments.
    """

    def __init__(self):
        """Initialize Y88 template generator."""
        self.logger = logging.getLogger(__name__)

        # Standard Y88 configurations
        self.standard_phases = ["DEV", "UAT", "BENCH", "PRODUCTION"]
        self.standard_environments = {
            'DEV': ['DEV_01', 'DEV_02', 'DEV_03'],
            'UAT': ['UAT_01', 'UAT_02', 'UAT_03'],
            'BENCH': ['MCO;Q', 'PRJ;B'],
            'PRODUCTION': ['PRD_01']
        }

        # Y88 interface definitions
        self.interface_definitions = {
            Y88InterfaceType.SUMMIT: {
                'package_name': 'Interface_summit',
                'build_name': 'Y88_INTERFACE_SUMMIT_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/Y88_INTERFACE_SUMMIT'
            },
            Y88InterfaceType.SUMMIT_COF: {
                'package_name': 'Interface_summit_COF',
                'build_name': 'Y88_INTERFACE_SUMMIT_COF_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/Y88_INTERFACE_SUMMIT_COF'
            },
            Y88InterfaceType.TOGE: {
                'package_name': 'Interface_TOGE',
                'build_name': 'Y88_INTERFACE_TOGE_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/TOGE'
            },
            Y88InterfaceType.TOGE_ACK: {
                'package_name': 'Interface_TOGE_ACK',
                'build_name': 'Y88_INTERFACE_TOGE_ACK_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/TOGE_ACK'
            },
            Y88InterfaceType.NON_LOAN_US: {
                'package_name': 'Interface_NON_LOAN_US',
                'build_name': 'Y88_INTERFACE_NON_LOAN_US_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/Y88_INTERFACE_NON_LOAN'
            },
            Y88InterfaceType.MOTOR: {
                'package_name': 'Interface_MOTOR',
                'build_name': 'Y88_INTERFACE_MOTOR_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/MOTOR'
            },
            Y88InterfaceType.ROAR: {
                'package_name': 'Interface_ROAR',
                'build_name': 'Y88_INTERFACE_ROAR_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/ROAR'
            },
            Y88InterfaceType.ROAR_ACK: {
                'package_name': 'Interface_ROAR_ACK',
                'build_name': 'Y88_INTERFACE_ROAR_ACK_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Interface/job/ROAR_ACK'
            },
            Y88InterfaceType.DICTIONNAIRE: {
                'package_name': 'DICTIONNAIRE',
                'build_name': 'Y88_DICTIONARIES_BUILD-V<version>',
                'jenkins_job': 'Y88/job/Other/job/Y88-Dictionaries/'
            }
        }

    def generate_template(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """
        Generate Y88 template based on configuration.

        Args:
            config: Y88 template configuration

        Returns:
            Complete YAML template dictionary
        """
        self.logger.info(f"Generating Y88 template: {config.template_type.value}")

        template = {}

        # Generate general info
        template['general_info'] = self._generate_general_info(config)

        # Generate technical tasks
        template['technical_task_list'] = self._generate_technical_tasks(config)

        # Generate packages
        template['template_liste_package'] = self._generate_packages(config)

        # Generate Jenkins configuration
        if config.enable_jenkins:
            template['jenkins'] = self._generate_jenkins_config(config)

        # Generate environments
        template.update(self._generate_environments(config))

        # Generate variable release
        template['variable_release'] = self._generate_variable_release(config)

        # Generate phases
        template['Phases'] = self._generate_phases(config)

        self.logger.info(f"✅ Y88 template generated successfully")

        return template

    def _generate_general_info(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate general info section."""
        return {
            'type_template': 'DYNAMIC',
            'xlr_folder': f'PFI/Y88_LoanIQ/{config.project_name}',
            'iua': config.iua,
            'appli_name': 'LoanIQ',
            'phases': config.phases,
            'name_release': f'{config.iua}_{config.template_type.value.upper()}_TEMPLATE',
            'SUN_approuver': f'{config.iua.lower()}.admin@company.com',
            'technical_task_mode': 'string',
            'template_package_mode': 'string',
            'phase_mode': 'multi_list',
            'option_latest': False,
            'xld_group': True
        }

    def _generate_technical_tasks(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate technical tasks configuration."""
        return {
            'before_deployment': [
                'task_ops',
                'task_dba_other'
            ],
            'before_xldeploy': [
                'task_ops'
            ],
            'after_xldeploy': [
                'task_ops',
                'task_dba_other',
                'task_dba_factor'
            ],
            'after_deployment': [
                'task_ops',
                'task_dba_factor'
            ]
        }

    def _generate_packages(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate packages configuration."""
        packages = {}

        # Core packages based on template type
        if config.template_type in [Y88TemplateType.LOANIQ_CORE, Y88TemplateType.LOANIQ_FULL]:
            # App package
            packages['App'] = {
                'package_build_name': 'LoanIQ_app_7.6.2.1.<version>',
                'controlm_mode': 'master',
                'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/APP/Y88_APP_LOANIQ_76/',
                'XLD_environment_path': 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/APP/<xld_prefix_env>Y88_APP_<XLD_env>_ENV',
                'auto_undeploy': False,
                'mode': 'CHECK_XLD'
            }

            # Scripts package
            packages['Scripts'] = {
                'package_build_name': 'PKG_SCRIPTS-V7.6-<version>',
                'controlm_mode': 'master',
                'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/APP/Y88_SCR_LOANIQ/',
                'XLD_environment_path': 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/SCR/<xld_prefix_env>Y88_SCR_<XLD_env>_ENV',
                'auto_undeploy': False,
                'mode': 'CHECK_XLD'
            }

            # SDK package
            packages['SDK'] = {
                'package_build_name': 'BUILD-SDK-76-V<version>',
                'controlm_mode': 'master',
                'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/APP/Y88_SDK_LOANIQ/',
                'XLD_environment_path': 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/SDK/<xld_prefix_env>Y88_SDK_<XLD_env>_ENV',
                'auto_undeploy': ['App'],
                'mode': 'CHECK_XLD'
            }

        # Interface packages
        if config.template_type in [Y88TemplateType.LOANIQ_INTERFACES, Y88TemplateType.LOANIQ_FULL]:
            # Core interfaces package
            packages['Interfaces'] = {
                'package_build_name': 'BUILD-76-V<version>',
                'controlm_mode': 'Independant',
                'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/INT/Y88_INT_LOANIQ/',
                'XLD_environment_path': 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/INT/<xld_prefix_env>Y88_INT_<XLD_env>_ENV',
                'auto_undeploy': False,
                'mode': 'CHECK_XLD'
            }

            # Specific interfaces
            for interface_type in config.interfaces:
                if interface_type in self.interface_definitions:
                    interface_def = self.interface_definitions[interface_type]
                    packages[interface_def['package_name']] = {
                        'package_build_name': interface_def['build_name'],
                        'controlm_mode': 'Independant',
                        'XLD_application_path': f'Applications/PFI/Y88_LOANIQ/INT/{interface_def["package_name"]}/',
                        'XLD_environment_path': 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/INT/<xld_prefix_env>Y88_INT_<XLD_env>_ENV_NEW',
                        'auto_undeploy': False,
                        'mode': 'CHECK_XLD' if interface_type != Y88InterfaceType.DICTIONNAIRE else 'name_from_jenkins'
                    }

        return packages

    def _generate_jenkins_config(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate Jenkins configuration."""
        jenkins_config = {
            'jenkinsServer': 'Configuration/Custom/Jenkins-Y88',
            'taskType': 'jenkins.Build',
            'username': f'{config.iua.lower()}_jenkins@company.com',
            'apiToken': '${apiToken_jenkins_iua}',
            'valueapiToken': '11a474dedca78e202f62f82c6544eb7778',
            'password': None,
            'jenkinsjob': {}
        }

        # Core jobs
        if config.template_type in [Y88TemplateType.LOANIQ_CORE, Y88TemplateType.LOANIQ_FULL]:
            jenkins_config['jenkinsjob']['App'] = {
                'jobName': 'Y88/job/Projet_y88-loaniq-Package',
                'parameters': ['BRANCH_NAME=${App_version}'],
                'precondition': 'None'
            }

            jenkins_config['jenkinsjob']['Scripts'] = {
                'jobName': 'Y88/job/y88-loaniq-scripts-7.6-Pipeline',
                'parameters': ['BRANCH_NAME=${Scripts_version}'],
                'precondition': 'None'
            }

            jenkins_config['jenkinsjob']['SDK'] = {
                'jobName': 'Y88/job/y88-sdk-foundation-7.6-Pipeline',
                'parameters': ['BRANCH_NAME=${SDK_version}'],
                'precondition': 'None'
            }

        # Interface jobs
        if config.template_type in [Y88TemplateType.LOANIQ_INTERFACES, Y88TemplateType.LOANIQ_FULL]:
            jenkins_config['jenkinsjob']['Interfaces'] = {
                'jobName': 'Y88/job/Y88-Interface-7.6-Pipeline',
                'parameters': ['BRANCH_NAME=${Interfaces_version}'],
                'precondition': 'None'
            }

            # Specific interface jobs
            for interface_type in config.interfaces:
                if interface_type in self.interface_definitions:
                    interface_def = self.interface_definitions[interface_type]
                    job_key = interface_def['package_name']

                    if interface_type == Y88InterfaceType.DICTIONNAIRE:
                        jenkins_config['jenkinsjob'][job_key] = {
                            'jobName': interface_def['jenkins_job'],
                            'parameters': ['VARIABLE_XLR_ID'],
                            'precondition': 'None'
                        }
                    else:
                        jenkins_config['jenkinsjob'][job_key] = {
                            'jobName': interface_def['jenkins_job'],
                            'parameters': [f'BRANCH_NAME=${{{job_key}_version}}'],
                            'precondition': 'None'
                        }

        return jenkins_config

    def _generate_environments(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate environment configurations."""
        environments = {}

        for phase in config.phases:
            env_key = f'XLD_ENV_{phase}'
            environments[env_key] = self.standard_environments.get(phase, [f'{phase}_01'])

        return environments

    def _generate_variable_release(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate variable release configuration."""
        variables = {
            'Date': True,
            'Version': True,
            'Environment': True
        }

        # Add BENCH_Y88 if BENCH phase is present
        if 'BENCH' in config.phases:
            variables['BENCH_Y88'] = True

        return variables

    def _generate_phases(self, config: Y88TemplateConfig) -> Dict[str, Any]:
        """Generate phases configuration."""
        phases = {}

        for phase in config.phases:
            phase_config = []

            # Development phases (DEV, UAT)
            if phase in ['DEV', 'UAT']:
                phase_config = self._generate_dev_phase_config(config)

            # Production phases (BENCH, PRODUCTION)
            elif phase in ['BENCH', 'PRODUCTION']:
                phase_config = self._generate_prod_phase_config(config, phase)

            phases[phase] = phase_config

        return phases

    def _generate_dev_phase_config(self, config: Y88TemplateConfig) -> List[Dict[str, Any]]:
        """Generate development phase configuration."""
        phase_config = []

        # Core components deployment
        if config.template_type in [Y88TemplateType.LOANIQ_CORE, Y88TemplateType.LOANIQ_FULL]:
            # Sequential deployments
            phase_config.extend([
                {'seq_xldeploy': {'XLD App': ['App']}},
                {'seq_xldeploy': {'XLD Scripts': ['Scripts']}},
                {'seq_xldeploy': {'XLD SDK': ['SDK']}}
            ])

        # Interface deployments
        if config.template_type in [Y88TemplateType.LOANIQ_INTERFACES, Y88TemplateType.LOANIQ_FULL]:
            phase_config.append({'seq_xldeploy': {'XLD Interfaces': ['Interfaces']}})

            # Specific interfaces
            for interface_type in config.interfaces:
                if interface_type in self.interface_definitions:
                    interface_def = self.interface_definitions[interface_type]
                    package_name = interface_def['package_name']
                    phase_config.append({
                        'seq_xldeploy': {f'XLD {package_name}': [package_name]}
                    })

        return phase_config

    def _generate_prod_phase_config(self, config: Y88TemplateConfig, phase: str) -> List[Dict[str, Any]]:
        """Generate production phase configuration."""
        phase_config = []

        # ControlM STOP tasks
        if config.enable_controlm:
            phase_config.extend(self._generate_controlm_stop_tasks(config, phase))

        # XLD deployments
        phase_config.extend(self._generate_dev_phase_config(config))

        # ControlM START tasks
        if config.enable_controlm:
            phase_config.extend(self._generate_controlm_start_tasks(config, phase))

        return phase_config

    def _generate_controlm_stop_tasks(self, config: Y88TemplateConfig, phase: str) -> List[Dict[str, Any]]:
        """Generate ControlM STOP tasks."""
        controlm_tasks = []

        prefix = 'BDCP_OSTOP_${controlm_prefix_BENCH}' if phase == 'BENCH' else 'PDCP_OSTOP_P'

        # Core applications STOP
        if config.template_type in [Y88TemplateType.LOANIQ_CORE, Y88TemplateType.LOANIQ_FULL]:
            controlm_tasks.append({
                'XLR_task_controlm': {
                    'STOP LOANIQ': {
                        'type_group': 'SequentialGroup',
                        'folder': {
                            f'{prefix}Y88_XLR': {
                                'hold': False if phase == 'BENCH' else True,
                                'case': ['App', 'Scripts', 'SDK']
                            }
                        }
                    }
                }
            })

        # Interfaces STOP
        if config.template_type in [Y88TemplateType.LOANIQ_INTERFACES, Y88TemplateType.LOANIQ_FULL]:
            controlm_tasks.append({
                'XLR_task_controlm': {
                    'STOP Interfaces': {
                        'type_group': 'SequentialGroup',
                        'folder': {
                            f'{prefix}Y88_INTRADAYS_XLR': {
                                'hold': False if phase == 'BENCH' else True,
                                'case': ['Interfaces']
                            }
                        }
                    }
                }
            })

        return controlm_tasks

    def _generate_controlm_start_tasks(self, config: Y88TemplateConfig, phase: str) -> List[Dict[str, Any]]:
        """Generate ControlM START tasks."""
        controlm_tasks = []

        prefix = 'BDCP_OSTART_${controlm_prefix_BENCH}' if phase == 'BENCH' else 'PDCP_OSTART_P'

        # Core applications START
        if config.template_type in [Y88TemplateType.LOANIQ_CORE, Y88TemplateType.LOANIQ_FULL]:
            controlm_tasks.append({
                'XLR_task_controlm': {
                    'START LOANIQ': {
                        'type_group': 'SequentialGroup',
                        'folder': {
                            f'{prefix}Y88_XLR': {
                                'hold': False if phase == 'BENCH' else True,
                                'case': ['Scripts', 'SDK', 'App']
                            }
                        }
                    }
                }
            })

        # Interfaces START
        if config.template_type in [Y88TemplateType.LOANIQ_INTERFACES, Y88TemplateType.LOANIQ_FULL]:
            controlm_tasks.append({
                'XLR_task_controlm': {
                    'START Interfaces': {
                        'type_group': 'SequentialGroup',
                        'folder': {
                            f'{prefix}Y88_INTRADAYS_XLR': {
                                'hold': False if phase == 'BENCH' else True,
                                'case': ['Interfaces']
                            }
                        }
                    }
                }
            })

        return controlm_tasks

    def get_predefined_templates(self) -> Dict[str, Y88TemplateConfig]:
        """Get predefined Y88 template configurations."""
        return {
            'y88_basic': Y88TemplateConfig(
                template_type=Y88TemplateType.BASIC,
                project_name='BASIC_PROJECT',
                iua='NXY88',
                phases=['DEV', 'UAT', 'PRODUCTION'],
                interfaces=[]
            ),
            'y88_loaniq_core': Y88TemplateConfig(
                template_type=Y88TemplateType.LOANIQ_CORE,
                project_name='LOANIQ_CORE',
                iua='NXY88',
                phases=['DEV', 'UAT', 'BENCH', 'PRODUCTION'],
                interfaces=[]
            ),
            'y88_loaniq_interfaces': Y88TemplateConfig(
                template_type=Y88TemplateType.LOANIQ_INTERFACES,
                project_name='LOANIQ_INTERFACES',
                iua='NXY88',
                phases=['DEV', 'UAT', 'BENCH', 'PRODUCTION'],
                interfaces=[
                    Y88InterfaceType.SUMMIT,
                    Y88InterfaceType.SUMMIT_COF,
                    Y88InterfaceType.TOGE,
                    Y88InterfaceType.DICTIONNAIRE
                ]
            ),
            'y88_loaniq_full': Y88TemplateConfig(
                template_type=Y88TemplateType.LOANIQ_FULL,
                project_name='LOANIQ_COMPLETE',
                iua='NXY88',
                phases=['DEV', 'UAT', 'BENCH', 'PRODUCTION'],
                interfaces=[
                    Y88InterfaceType.SUMMIT,
                    Y88InterfaceType.SUMMIT_COF,
                    Y88InterfaceType.TOGE,
                    Y88InterfaceType.TOGE_ACK,
                    Y88InterfaceType.NON_LOAN_US,
                    Y88InterfaceType.MOTOR,
                    Y88InterfaceType.ROAR,
                    Y88InterfaceType.ROAR_ACK,
                    Y88InterfaceType.DICTIONNAIRE
                ]
            )
        }

    def export_template(self, template: Dict[str, Any], output_path: str) -> bool:
        """Export template to YAML file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(template, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            self.logger.info(f"✅ Template exported to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export template: {e}")
            return False

    def create_custom_template(self,
                             project_name: str,
                             iua: str,
                             phases: List[str],
                             interfaces: List[str],
                             enable_jenkins: bool = True,
                             enable_controlm: bool = True) -> Dict[str, Any]:
        """Create custom Y88 template with user-specified configuration."""
        # Convert interface strings to enum types
        interface_types = []
        for interface_str in interfaces:
            try:
                interface_type = Y88InterfaceType(interface_str.lower())
                interface_types.append(interface_type)
            except ValueError:
                self.logger.warning(f"Unknown interface type: {interface_str}")

        # Determine template type based on configuration
        has_core = any(pkg in ['app', 'scripts', 'sdk'] for pkg in [project_name.lower()])
        has_interfaces = len(interface_types) > 0

        if has_core and has_interfaces:
            template_type = Y88TemplateType.LOANIQ_FULL
        elif has_interfaces:
            template_type = Y88TemplateType.LOANIQ_INTERFACES
        elif has_core:
            template_type = Y88TemplateType.LOANIQ_CORE
        else:
            template_type = Y88TemplateType.CUSTOM

        config = Y88TemplateConfig(
            template_type=template_type,
            project_name=project_name,
            iua=iua,
            phases=phases,
            interfaces=interface_types,
            enable_jenkins=enable_jenkins,
            enable_controlm=enable_controlm
        )

        return self.generate_template(config)