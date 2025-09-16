#!/usr/bin/env python3
"""
Configuration loader for XLR v3 modular.
Handles loading and parsing of configuration files.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging


class ConfigLoader:
    """Configuration loader and manager."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to configuration file. If None, will look for config.yaml in project root.
        """
        self.logger = logging.getLogger(__name__)

        if config_path is None:
            # Look for config.yaml in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"

        self.config_path = Path(config_path)
        self._config = None

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
                self.logger.info(f"Configuration loaded from: {self.config_path}")
                return self._config
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            raise

    @property
    def config(self) -> Dict[str, Any]:
        """Get configuration, loading it if not already loaded."""
        if self._config is None:
            self.load_config()
        return self._config

    def get_xlr_config(self) -> Dict[str, str]:
        """
        Get XLR API configuration.

        Returns:
            Dictionary with url, username, password
        """
        xlr_config = self.config.get('xlr_api', {})
        return {
            'url': xlr_config.get('url', ''),
            'username': xlr_config.get('username', ''),
            'password': xlr_config.get('password', '')
        }

    def get_controlm_config(self) -> Dict[str, str]:
        """
        Get Control-M configuration.

        Returns:
            Dictionary with API URL and environment names
        """
        controlm_config = self.config.get('controlm', {})
        return {
            'api_url': controlm_config.get('api_url', ''),
            'production_environment': controlm_config.get('production_environment', 'PROD_CTM'),
            'bench_environment': controlm_config.get('bench_environment', 'BENCH_CTM')
        }

    def get_servicenow_config(self) -> Dict[str, str]:
        """
        Get ServiceNow configuration.

        Returns:
            Dictionary with API URL, username, password
        """
        servicenow_config = self.config.get('servicenow', {})
        return {
            'api_url': servicenow_config.get('api_url', ''),
            'username': servicenow_config.get('username', ''),
            'password': servicenow_config.get('password', '')
        }

    def get_environment_credentials(self, environment: str, service: str) -> Dict[str, str]:
        """
        Get environment-specific credentials.

        Args:
            environment: Environment name (dev, test, prod)
            service: Service name (controlm, xlr)

        Returns:
            Dictionary with username and password
        """
        env_config = self.config.get('environments', {}).get(environment, {})
        service_config = env_config.get(service, {})

        return {
            'username': service_config.get('username', ''),
            'password': service_config.get('password', '')
        }

    def get_security_config(self) -> Dict[str, Any]:
        """
        Get security configuration.

        Returns:
            Dictionary with security settings
        """
        security_config = self.config.get('security', {})
        return {
            'verify_ssl': security_config.get('verify_ssl', False),
            'timeout': security_config.get('timeout', 30),
            'max_retries': security_config.get('max_retries', 3)
        }

    def validate_config(self) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            True if config is valid, False otherwise
        """
        try:
            config = self.config

            # Check required sections
            required_sections = ['xlr_api', 'controlm']
            for section in required_sections:
                if section not in config:
                    self.logger.error(f"Missing required configuration section: {section}")
                    return False

            # Check XLR API config
            xlr_config = config['xlr_api']
            required_xlr_fields = ['url', 'username', 'password']
            for field in required_xlr_fields:
                if not xlr_config.get(field):
                    self.logger.error(f"Missing or empty XLR API field: {field}")
                    return False

            # Check Control-M config
            controlm_config = config['controlm']
            if not controlm_config.get('api_url'):
                self.logger.error("Missing or empty Control-M API URL")
                return False

            self.logger.info("Configuration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return False


def load_config_from_file(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    loader = ConfigLoader(config_path)
    return loader.load_config()


def get_xlr_credentials(config_path: Optional[str] = None) -> Dict[str, str]:
    """
    Convenience function to get XLR credentials.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary with XLR credentials
    """
    loader = ConfigLoader(config_path)
    return loader.get_xlr_config()


def get_controlm_credentials(config_path: Optional[str] = None) -> Dict[str, str]:
    """
    Convenience function to get Control-M credentials.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary with Control-M credentials
    """
    loader = ConfigLoader(config_path)
    return loader.get_controlm_config()