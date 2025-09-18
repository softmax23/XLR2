"""
YAML file validation utilities for XLR template creation
"""
import yaml
import sys

def check_yaml_file(template_instance):
    """
    Validate YAML configuration file for XLR template creation.

    Args:
        template_instance: XLRCreateTemplate instance with parameters to validate

    Performs basic validation of required YAML structure and logs results.
    """
    try:
        parameters = template_instance.parameters

        # Basic validation
        required_sections = ['general_info', 'template_liste_package']
        for section in required_sections:
            if section not in parameters:
                template_instance.logger_error.error(f"Missing required section: {section}")
                sys.exit(1)

        # Validate general_info
        general_info = parameters['general_info']
        required_fields = ['name_release', 'phases']
        for field in required_fields:
            if field not in general_info:
                template_instance.logger_error.error(f"Missing required field in general_info: {field}")
                sys.exit(1)

        template_instance.logger_cr.info("YAML file validation: PASSED")

    except Exception as e:
        template_instance.logger_error.error(f"YAML validation error: {e}")
        sys.exit(1)