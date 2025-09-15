"""
XLR Dynamic Template Package

This package provides a comprehensive solution for creating and managing
dynamic XLR (XebiaLabs Release) templates with support for:

- Dynamic template creation and configuration
- Multi-phase deployment automation
- Control-M job integration
- ServiceNow ticket management
- Jenkins CI/CD integration
- XL Deploy automation

Main modules:
- core: Core functionality for XLR operations
- api: API client for external integrations
- templates: Template management utilities
- config: Configuration handling
"""

from .core import (
    XLRGeneric,
    XLRControlm,
    XLRDynamicPhase,
    XLRSun,
    XLRTaskScript
)

__version__ = "2.0.0"
__author__ = "XLR Automation Team"

__all__ = [
    'XLRGeneric',
    'XLRControlm',
    'XLRDynamicPhase',
    'XLRSun',
    'XLRTaskScript'
]