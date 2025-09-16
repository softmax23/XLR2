"""
Configuration Loader for XLR Template Creator V5.

This module handles loading and managing configuration from various sources
including config files, environment variables, and default values.
"""

import os
import configparser
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Configuration loader with support for multiple formats and sources."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path or self._find_config_file()
        self.config = {}
        self._load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_paths = [
            'config.yaml',
            'config/config.yaml',
            '_conf/xlr_create_template_change.ini',
            os.path.expanduser('~/.xlr_template_config.yaml')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from file if available
        if self.config_path and os.path.exists(self.config_path):
            self._load_from_file()

        # Load from environment variables
        self._load_from_env()

        # Set defaults
        self._set_defaults()

    def _load_from_file(self) -> None:
        """Load configuration from file."""
        if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
            self._load_yaml_config()
        elif self.config_path.endswith('.ini'):
            self._load_ini_config()

    def _load_yaml_config(self) -> None:
        """Load YAML configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                yaml_config = yaml.safe_load(file)
                if yaml_config:
                    self.config.update(yaml_config)
        except Exception as e:
            print(f"Warning: Could not load YAML config from {self.config_path}: {e}")

    def _load_ini_config(self) -> None:
        """Load INI configuration file (V1 format)."""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)

            # Convert INI to dict
            for section_name in config.sections():
                section = {}
                for key, value in config.items(section_name):
                    section[key] = value
                self.config[section_name] = section

            # Also add items from DEFAULT section at root level
            if 'DEFAULT' in config:
                for key, value in config['DEFAULT'].items():
                    self.config[key] = value

        except Exception as e:
            print(f"Warning: Could not load INI config from {self.config_path}: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'XLR_API_URL': 'url_api_xlr',
            'XLR_USERNAME': 'ops_username_api',
            'XLR_PASSWORD': 'ops_password_api',
            'XLR_BASE_URL': 'xlr_base_url'
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self.config[config_key] = value

    def _set_defaults(self) -> None:
        """Set default configuration values."""
        defaults = {
            'url_api_xlr': 'https://xlr-server/api/v1/',
            'ops_username_api': 'admin',
            'ops_password_api': 'admin',
            'xlr_base_url': 'https://xlr-server/',
            'timeout': 30,
            'verify_ssl': False
        }

        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()

    def __getattr__(self, name: str) -> Any:
        """Allow access to config values as attributes."""
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"'ConfigLoader' object has no attribute '{name}'")