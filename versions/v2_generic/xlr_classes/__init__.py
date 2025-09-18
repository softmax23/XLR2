"""
XLR Classes Module

This module contains all the specialized classes for creating XebiaLabs Release (XLR) templates
that orchestrate complex deployment pipelines across multiple environments.

Classes:
    XLRControlm: Control-M batch job scheduling integration
    XLRGeneric: Base XLR operations and template management
    XLRDynamicPhase: Dynamic phase creation and management
    XLRSun: ServiceNow (SUN) approval workflow integration
    XLRTaskScript: Custom script task generation and management

The classes work together through multiple inheritance to provide comprehensive
deployment automation including:
- Multi-environment deployments (DEV, UAT, BENCH, PRODUCTION)
- Approval workflows for production environments
- Batch job scheduling coordination
- Build system integration (Jenkins)
- Deployment tool integration (XL Deploy)
- Email notifications and reporting

Author: Generated for generic application deployment
Version: 2.0 (Generic - Modular)
"""

from .xlr_generic import XLRGeneric
from .xlr_controlm import XLRControlm
from .xlr_dynamic_phase import XLRDynamicPhase
from .xlr_sun import XLRSun
from .xlr_task_script import XLRTaskScript

__all__ = [
    'XLRGeneric',
    'XLRControlm',
    'XLRDynamicPhase',
    'XLRSun',
    'XLRTaskScript'
]

__version__ = '2.0.0'
__author__ = 'Generated for Generic Application Deployment'