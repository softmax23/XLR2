"""
Enhanced XLR Template Creation Script with Modern API Client
==========================================================

This enhanced version of DYNAMIC_template.py uses the new XLRAPIClient
for improved reliability, error handling, and API best practices.

Key improvements:
- Modern API client with retry logic and proper error handling
- Better authentication methods (Basic Auth, Tokens, OAuth2)
- Proper use of XL Release REST API endpoints
- Enhanced logging and debugging capabilities
- Pagination support for large datasets
- Search capabilities for finding resources
- Full identifier support following XL Release conventions
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

from ..api.xlr_api_client import XLRAPIClient, XLRAPIException
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


class EnhancedXLRCreateTemplate(XLRGeneric, XLRSun, XLRTaskScript, XLRControlm, XLRDynamicPhase):
    """
    Enhanced XLR Template Creation and Management Class with Modern API Client.

    This class extends the original functionality with:
    - Robust API client with retry logic
    - Better error handling and logging
    - Modern authentication methods
    - Improved resource management
    - Search and pagination capabilities
    """

    CONFIG_FILE_PATH = '_conf/xlr_create_template_change.ini'

    def __init__(self, parameters: Dict[str, Any], api_client: XLRAPIClient = None):
        """
        Initialize the enhanced XLR template creator.

        Args:
            parameters: YAML configuration parameters
            api_client: Optional pre-configured API client
        """
        self._validate_parameters(parameters)
        self._load_configuration()
        self.parameters = parameters
        self._setup_logging()
        self._initialize_variables()

        # Initialize API client
        self.api_client = api_client or self._create_api_client()

        # Setup template
        self._setup_template()

    def _create_api_client(self) -> XLRAPIClient:
        """
        Create and configure the XL Release API client.

        Returns:
            Configured XLRAPIClient instance
        """
        try:
            # Get configuration from loaded settings
            base_url = getattr(self, 'url_api_xlr', '').rstrip('/')
            username = getattr(self, 'ops_username_api', '')
            password = getattr(self, 'ops_password_api', '')

            if not base_url:
                raise ValueError("XL Release API URL not found in configuration")

            # Create client with retry logic and proper timeouts
            api_client = create_basic_auth_client(
                base_url=base_url,
                username=username,
                password=password,
                verify_ssl=False,  # Maintaining compatibility with original
                timeout=60,  # Increased timeout for template operations
                max_retries=3
            )

            # Perform health check
            if not api_client.health_check():
                self.logger_error.error("XL Release server health check failed")
                raise ConnectionError("Cannot connect to XL Release server")

            self.logger_detail.info(f"Connected to XL Release at {base_url}")
            return api_client

        except Exception as e:
            self.logger_error.error(f"Failed to create API client: {e}")
            raise

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
        self.template_id = None
        self.folder_id = None

    def _setup_template(self) -> None:
        """Setup and initialize the XLR template."""
        try:
            check_yaml_file(self)
            self._clear_screen()

            self.logger_cr.info("")
            self.logger_cr.info("BEGIN ENHANCED TEMPLATE CREATION")
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
        """Initialize core template components using enhanced API client."""
        try:
            # Find or create folder
            self._find_or_create_xlr_folder()

            # Delete existing template if needed
            self._delete_existing_template()

            # Create new template
            self._create_new_template()

            # Setup template variables and phases
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

        except XLRAPIException as e:
            self.logger_error.error(f"API error during template initialization: {e}")
            raise
        except Exception as e:
            self.logger_error.error(f"Unexpected error during template initialization: {e}")
            raise

    def _find_or_create_xlr_folder(self) -> None:
        """Find or create the XLR folder using search API."""
        folder_path = self.parameters['general_info']['xlr_folder']

        try:
            # Try to find existing folder
            folder = self.api_client.find_folder_by_path(folder_path)

            if folder:
                self.folder_id = folder['id']
                self.logger_detail.info(f"Found existing folder: {folder_path}")
            else:
                # Create folder if it doesn't exist
                # Note: Folder creation might require additional API endpoints
                # depending on your XL Release version
                self.logger_detail.warning(f"Folder not found: {folder_path}")
                # For now, we'll use a default folder or create it through the parent class
                super().find_xlr_folder()  # Fallback to original implementation

        except XLRAPIException as e:
            self.logger_error.error(f"Error finding/creating folder {folder_path}: {e}")
            # Fallback to original implementation
            super().find_xlr_folder()

    def _delete_existing_template(self) -> None:
        """Delete existing template with the same name using search API."""
        template_name = self.parameters['general_info']['name_release']

        try:
            # Search for existing templates with the same name
            existing_templates = self.api_client.find_templates_by_title(template_name)

            for template in existing_templates:
                template_id = template['id']
                self.logger_detail.info(f"Deleting existing template: {template_name} (ID: {template_id})")

                try:
                    self.api_client.delete_template(template_id)
                    self.logger_cr.info(f"Successfully deleted template: {template_name}")
                except XLRAPIException as e:
                    if e.status_code == 404:
                        self.logger_detail.info(f"Template already deleted: {template_name}")
                    else:
                        self.logger_error.error(f"Error deleting template {template_name}: {e}")

        except XLRAPIException as e:
            self.logger_error.error(f"Error searching for existing templates: {e}")
            # Fallback to original implementation
            super().delete_template()

    def _create_new_template(self) -> None:
        """Create a new template using the enhanced API client."""
        template_name = self.parameters['general_info']['name_release']

        try:
            # Prepare template data according to XL Release API structure
            template_data = {
                'id': None,
                'type': 'xlrelease.Release',
                'title': template_name,
                'status': 'TEMPLATE',
                'description': f'Template created for {template_name}',
                'scheduledStartDate': None,
                'dueDate': None,
                'owner': getattr(self, 'ops_username_api', 'admin'),
                'tags': [],
                'variables': [],
                'phases': [],
                'teams': []
            }

            # Add folder reference if available
            if hasattr(self, 'folder_id') and self.folder_id:
                template_data['folderId'] = self.folder_id

            # Create template
            response = self.api_client.create_template(template_data)

            if 'id' in response:
                self.template_id = response['id']
                self.XLR_template_id = self.template_id
                self.template_url = f"{self.api_client.base_url}/templates/{self.template_id}"

                # Update dict_template structure
                self.dict_template = {
                    'template': {
                        'xlr_id': self.template_id,
                        'xlr_folder': self.folder_id
                    }
                }

                self.logger_cr.info(f"Successfully created template: {template_name}")
                self.logger_detail.info(f"Template ID: {self.template_id}")
                self.logger_detail.info(f"Template URL: {self.template_url}")
            else:
                raise XLRAPIException("Template creation failed - no ID returned")

        except XLRAPIException as e:
            self.logger_error.error(f"Error creating template {template_name}: {e}")
            raise
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating template: {e}")
            raise

    def _create_template_variables(self) -> None:
        """Create standard template variables using the enhanced API client."""
        if not self.template_id:
            self.logger_error.error("Cannot create variables - template ID not set")
            return

        variables_config = [
            ('ops_username_api', 'StringVariable', getattr(self, 'ops_username_api', '')),
            ('ops_password_api', 'PasswordStringVariable', getattr(self, 'ops_password_api', '')),
            ('email_owner_release', 'StringVariable', ''),
            ('xlr_list_phase_selection', 'StringVariable', ''),
            ('IUA', 'StringVariable', self.parameters['general_info'].get('iua', ''))
        ]

        for var_name, var_type, var_value in variables_config:
            try:
                variable_data = {
                    'key': var_name,
                    'type': f'xlrelease.{var_type}',
                    'label': var_name,
                    'description': '',
                    'value': var_value,
                    'requiresValue': False,
                    'showOnReleaseStart': False,
                    'multiline': False
                }

                self.api_client.create_variable(self.template_id, variable_data)
                self.logger_detail.info(f"Created variable: {var_name}")

            except XLRAPIException as e:
                self.logger_error.error(f"Error creating variable {var_name}: {e}")
                # Continue with other variables

    def enhanced_create_phase(self, phase: str) -> str:
        """
        Enhanced phase creation using the modern API client.

        Args:
            phase: The phase name to create

        Returns:
            The template URL after phase creation
        """
        if not self.template_id:
            raise ValueError("Template ID not set - cannot create phases")

        try:
            self.logger_detail.info(f"Creating enhanced phase: {phase}")

            # Prepare phase data
            phase_data = {
                'type': 'xlrelease.Phase',
                'title': phase,
                'description': f'Phase {phase} created by enhanced template creator',
                'status': 'PLANNED',
                'color': self._get_phase_color(phase),
                'tasks': []
            }

            # Create phase using API client
            response = self.api_client.create_phase(self.template_id, phase_data)

            if 'id' in response:
                phase_id = response['id']

                # Update internal structure
                if phase not in self.dict_template:
                    self.dict_template[phase] = {}
                self.dict_template[phase]['xlr_id_phase'] = phase_id

                self.logger_cr.info(f"Successfully created phase: {phase}")
                self.logger_detail.info(f"Phase ID: {phase_id}")

                # Add phase-specific tasks based on type
                if phase in ['BUILD', 'DEV', 'UAT']:
                    self._create_development_phase_enhanced(phase, phase_id)
                elif phase in ['BENCH', 'PRODUCTION']:
                    self._create_production_phase_enhanced(phase, phase_id)

                return self.template_url

            else:
                raise XLRAPIException(f"Phase creation failed for {phase} - no ID returned")

        except XLRAPIException as e:
            self.logger_error.error(f"Error creating phase {phase}: {e}")
            raise
        except Exception as e:
            self.logger_error.error(f"Unexpected error creating phase {phase}: {e}")
            raise

    def _get_phase_color(self, phase: str) -> str:
        """Get appropriate color for phase based on type."""
        colors = {
            'BUILD': '#3498db',    # Blue
            'DEV': '#2ecc71',      # Green
            'UAT': '#f39c12',      # Orange
            'BENCH': '#e74c3c',    # Red
            'PRODUCTION': '#9b59b6' # Purple
        }
        return colors.get(phase, '#34495e')  # Default grey

    def _create_development_phase_enhanced(self, phase: str, phase_id: str) -> None:
        """Create development phase with enhanced API calls."""
        try:
            # Create validation gate task
            gate_task_data = {
                'type': 'xlrelease.GateTask',
                'title': f'Validation_{phase}_template',
                'description': f'Validation gate for {phase} phase',
                'conditions': [
                    {
                        'title': f'Validation_{phase}_template OK',
                        'type': 'xlrelease.GateCondition'
                    }
                ]
            }

            self.api_client.create_task(phase_id, gate_task_data)
            self.logger_detail.info(f"Created validation gate for {phase}")

            # Add more tasks as needed...
            # This would replace the original parameter_phase_task() call

        except XLRAPIException as e:
            self.logger_error.error(f"Error creating development phase tasks for {phase}: {e}")

    def _create_production_phase_enhanced(self, phase: str, phase_id: str) -> None:
        """Create production phase with enhanced API calls."""
        try:
            # Create SNOW validation gate
            snow_gate_data = {
                'type': 'xlrelease.GateTask',
                'title': f'Validation creation SNOW ${{{phase}.sun.id}}',
                'description': f'SNOW validation gate for {phase}',
                'conditions': [
                    {
                        'title': f'SNOW creation validated for {phase}',
                        'type': 'xlrelease.GateCondition'
                    }
                ]
            }

            self.api_client.create_task(phase_id, snow_gate_data)
            self.logger_detail.info(f"Created SNOW validation gate for {phase}")

            # Add more production-specific tasks...

        except XLRAPIException as e:
            self.logger_error.error(f"Error creating production phase tasks for {phase}: {e}")

    def create_phase_with_fallback(self, phase: str) -> str:
        """
        Create phase with fallback to original implementation.

        This method tries the enhanced API first, then falls back to the original
        implementation if needed for compatibility.
        """
        try:
            # Try enhanced implementation first
            return self.enhanced_create_phase(phase)
        except Exception as e:
            self.logger_error.error(f"Enhanced phase creation failed for {phase}: {e}")
            self.logger_detail.info(f"Falling back to original implementation for {phase}")

            # Fallback to original implementation
            return super().createphase(phase)

    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'api_client') and self.api_client:
            self.api_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # Inherit all other methods from parent classes
    # This ensures backward compatibility while adding enhanced functionality

    def define_variable_type_template_DYNAMIC(self) -> None:
        """
        Define dynamic template variables (inherited from parent with enhancements).
        """
        # Call parent implementation
        super().define_variable_type_template_DYNAMIC()

    def dynamic_phase_dynamic(self) -> str:
        """
        Create and configure the dynamic phase (inherited from parent with enhancements).
        """
        # Call parent implementation
        return super().dynamic_phase_dynamic()


def main() -> None:
    """
    Enhanced main entry point for the XLR Template Creation script.
    """
    parser = argparse.ArgumentParser(
        description='Enhanced XLR template creator with modern API client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python DYNAMIC_template_enhanced.py --infile template.yaml

The YAML file should contain the template configuration including:
- general_info: Basic template information
- template_liste_package: Package definitions
- Phases: Phase-specific configurations

Enhanced features:
- Robust API client with retry logic
- Modern authentication methods
- Better error handling and logging
- Search and pagination support
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

        # Create and process template using context manager
        with EnhancedXLRCreateTemplate(parameters) as template_creator:
            logger.info("Starting enhanced template creation")

            for phase in parameters['general_info']['phases']:
                template_url = template_creator.create_phase_with_fallback(phase)

            # Log completion
            logger.info("---------------------------")
            logger.info("ENHANCED TEMPLATE CREATION COMPLETED SUCCESSFULLY")
            logger.info("---------------------------")
            logger.info(f"Release Name: {parameters['general_info']['name_release']}")
            logger.info(f"Template URL: {template_url}")

    except KeyError as e:
        print(f'Missing required configuration key: {e}')
        sys.exit(12)
    except XLRAPIException as e:
        print(f'XL Release API error: {e}')
        sys.exit(13)
    except Exception as e:
        print(f'Error during template creation: {e}')
        sys.exit(14)


if __name__ == "__main__":
    main()