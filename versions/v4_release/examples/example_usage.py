"""
Example Usage of Enhanced XLR Template Creator for XL Release 22.x
================================================================

This example demonstrates how to use the enhanced XLR template creator
with the modern API client optimized for XL Release version 22.x.
"""

import logging
from pathlib import Path
from xlr_api_client import create_basic_auth_client, create_token_auth_client, XLRAPIException
from DYNAMIC_template_enhanced import EnhancedXLRCreateTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_auth():
    """Example using basic authentication."""
    try:
        # Create API client with basic authentication
        api_client = create_basic_auth_client(
            base_url="https://your-xlr-server.com",
            username="your_username",
            password="your_password",
            verify_ssl=False,  # Set to True in production
            timeout=60,
            max_retries=3
        )

        # Test connection
        if api_client.health_check():
            logger.info("Successfully connected to XL Release server")

            # Get server info
            server_info = api_client.get_server_info()
            logger.info(f"XL Release version: {server_info.get('version', 'Unknown')}")
        else:
            logger.error("Failed to connect to XL Release server")
            return

        # Load YAML configuration
        yaml_config = {
            'general_info': {
                'name_release': 'Example_Template_v1.0',
                'phases': ['DEV', 'UAT', 'PRODUCTION'],
                'xlr_folder': 'Applications/Examples',
                'iua': 'EX001',
                'template_package_mode': 'string',
                'phase_mode': 'multi_list'
            },
            'template_liste_package': {
                'example_package': {
                    'package_build_name': 'EXAMPLE-V<version>',
                    'mode': 'CHECK_XLD'
                }
            }
        }

        # Create enhanced template creator
        with EnhancedXLRCreateTemplate(yaml_config, api_client) as template_creator:
            logger.info("Creating template with enhanced API client")

            # Create phases
            for phase in yaml_config['general_info']['phases']:
                template_url = template_creator.create_phase_with_fallback(phase)
                logger.info(f"Created phase: {phase}")

            logger.info(f"Template created successfully: {template_url}")

    except XLRAPIException as e:
        logger.error(f"XL Release API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def example_token_auth():
    """Example using token authentication (recommended for XL Release 22.x)."""
    try:
        # Create API client with token authentication
        api_client = create_token_auth_client(
            base_url="https://your-xlr-server.com",
            token="your_personal_access_token",  # Use Personal Access Token from XL Release
            verify_ssl=True,
            timeout=60
        )

        # Test connection
        if not api_client.health_check():
            logger.error("Failed to connect with token authentication")
            return

        logger.info("Successfully authenticated with Personal Access Token")

        # Search for existing templates
        search_results = api_client.search("title:Example*", entity_type="template")
        logger.info(f"Found {len(search_results.get('entities', []))} existing templates")

        # List templates with pagination
        templates = api_client.list_templates(page=0, results_per_page=10)
        logger.info(f"Total templates in system: {templates.get('total', 0)}")

    except XLRAPIException as e:
        logger.error(f"Token authentication failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def example_search_and_manage():
    """Example of search and template management capabilities."""
    try:
        api_client = create_basic_auth_client(
            base_url="https://your-xlr-server.com",
            username="admin",
            password="admin"
        )

        # Search for templates by title
        templates = api_client.find_templates_by_title("Example_Template")
        logger.info(f"Found {len(templates)} templates matching 'Example_Template'")

        for template in templates:
            logger.info(f"Template: {template['title']} (ID: {template['id']})")

        # Search for folders
        folder = api_client.find_folder_by_path("Applications/Examples")
        if folder:
            logger.info(f"Found folder: {folder['title']} (ID: {folder['id']})")
        else:
            logger.info("Folder not found")

        # Get template details
        if templates:
            template_id = templates[0]['id']
            template_details = api_client.get_template(template_id)
            logger.info(f"Template details: {template_details['title']}")

            # Get template variables
            variables = api_client.get_variables(template_id)
            logger.info(f"Template has {len(variables)} variables")

    except XLRAPIException as e:
        logger.error(f"Search operation failed: {e}")


def example_error_handling():
    """Example of comprehensive error handling."""
    try:
        # Create client with invalid credentials
        api_client = create_basic_auth_client(
            base_url="https://invalid-server.com",
            username="invalid",
            password="invalid"
        )

        # This will fail and demonstrate error handling
        api_client.get_server_info()

    except XLRAPIException as e:
        logger.error(f"API Exception - Status Code: {e.status_code}")
        logger.error(f"API Exception - Message: {e}")
        logger.error(f"API Exception - Response: {e.response}")
    except ConnectionError as e:
        logger.error(f"Connection Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")


def example_with_yaml_file():
    """Example using actual YAML file."""
    import yaml

    try:
        # Load configuration from YAML file
        yaml_file = Path("template.yaml")
        if not yaml_file.exists():
            logger.error("template.yaml not found")
            return

        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)

        # Create API client
        api_client = create_basic_auth_client(
            base_url="https://your-xlr-server.com",
            username="admin",
            password="admin"
        )

        # Create template with configuration from file
        with EnhancedXLRCreateTemplate(config, api_client) as creator:
            for phase in config['general_info']['phases']:
                template_url = creator.create_phase_with_fallback(phase)

            logger.info(f"Template created from YAML: {template_url}")

    except Exception as e:
        logger.error(f"YAML processing error: {e}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("XL Release 22.x Enhanced Template Creator Examples")
    logger.info("=" * 60)

    # Run examples
    logger.info("\n1. Basic Authentication Example:")
    example_basic_auth()

    logger.info("\n2. Token Authentication Example:")
    example_token_auth()

    logger.info("\n3. Search and Management Example:")
    example_search_and_manage()

    logger.info("\n4. Error Handling Example:")
    example_error_handling()

    logger.info("\n5. YAML File Example:")
    example_with_yaml_file()

    logger.info("\nAll examples completed!")