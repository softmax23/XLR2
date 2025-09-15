"""
Example usage of the restructured XLR Dynamic Template modules.

This example demonstrates how to use the new modular structure
and maintain compatibility with template.yaml configuration.
"""

import logging
from pathlib import Path

# Import the new modular classes
from src.core import (
    XLRGeneric,
    XLRControlm,
    XLRDynamicPhase,
    XLRSun,
    XLRTaskScript
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def load_template_config(template_path: str) -> dict:
    """Load template configuration from YAML file."""
    import yaml

    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load template config: {e}")
        return {}

def main():
    """Main example function."""
    # Load template configuration
    template_config = load_template_config('src/templates/template.yaml')

    if not template_config:
        logging.error("Failed to load template configuration")
        return

    # Initialize core components
    xlr_generic = XLRGeneric()
    xlr_controlm = XLRControlm()
    xlr_dynamic_phase = XLRDynamicPhase()
    xlr_sun = XLRSun()
    xlr_task_script = XLRTaskScript()

    # Setup connections (example configuration)
    xlr_api_config = {
        'url': 'https://your-xlr-server/api/v1/',
        'username': 'your-username',
        'password': 'your-password'
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
        url_api_controlm='https://your-controlm-server/api/',
        ctm_prod='PROD_CTM',
        ctm_bench='BENCH_CTM'
    )

    # Setup ServiceNow configuration
    xlr_sun.setup_sun_configuration(
        sun_approver=template_config.get('general_info', {}).get('SUN_approuver', 'default@company.com')
    )

    # Example: Create a template using the new structure
    try:
        # Set parameters from template config
        xlr_generic.parameters = template_config

        # Create template
        dict_template, template_id = xlr_generic.create_template()

        logging.info(f"Template created successfully: {template_id}")

        # Process phases from template configuration
        phases = template_config.get('general_info', {}).get('phases', [])

        for phase in phases:
            logging.info(f"Processing phase: {phase}")

            # Process phase-specific tasks
            xlr_generic.parameter_phase_task(phase)

            # Add Control-M tasks if needed
            if template_config.get('controlm_integration'):
                xlr_controlm.script_jython_date_for_controlm(phase)

            # Add ServiceNow integration if needed
            if template_config.get('servicenow_integration'):
                change_details = {
                    'short_description': f'Deployment for {phase}',
                    'description': f'Automated deployment in {phase} environment',
                    'category': 'Software',
                    'priority': '3'
                }
                xlr_sun.create_sun_change_request(phase, change_details)

        logging.info("Template creation completed successfully")

    except Exception as e:
        logging.error(f"Error creating template: {e}")

def backward_compatibility_example():
    """
    Example showing backward compatibility with old all_class.py structure.

    This function demonstrates how existing code can be minimally updated
    to use the new modular structure.
    """

    # Old way (commented out):
    # from all_class import XLRGeneric
    # xlr_generic = XLRGeneric()

    # New way:
    from src.core.xlr_generic import XLRGeneric
    xlr_generic = XLRGeneric()

    # The rest of the code remains largely the same
    # xlr_generic.CreateTemplate()  # Old method name
    # xlr_generic.create_template()  # New improved method name

    logging.info("Backward compatibility maintained with minimal changes")

if __name__ == "__main__":
    main()
    backward_compatibility_example()