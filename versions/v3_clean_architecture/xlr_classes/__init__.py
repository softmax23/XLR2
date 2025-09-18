"""
XLR Classes Module - V3 Clean Architecture

This module contains the enhanced XLR classes using architectural best practices
with proper inheritance hierarchy and no circular dependencies.

Classes:
    XLRBase: Foundation class with shared functionality
    XLRGeneric: Enhanced XLR operations (inherits from XLRBase)
    XLRControlm: Control-M integration (inherits from XLRBase)
    XLRDynamicPhase: Dynamic phase management (inherits from XLRBase)
    XLRSun: ServiceNow workflows (inherits from XLRBase)
    XLRTaskScript: Script generation (inherits from XLRBase)

Architecture Benefits:
- No circular dependencies
- Clean inheritance hierarchy
- Shared functionality in base class
- Specialized functionality in derived classes
- Better maintainability and testability

Author: Generated for generic application deployment
Version: 3.0 (Clean Architecture)
"""

from .xlr_base import XLRBase
from .xlr_generic import XLRGeneric
from .xlr_controlm import XLRControlm
from .xlr_dynamic_phase import XLRDynamicPhase
from .xlr_sun import XLRSun
from .xlr_task_script import XLRTaskScript

__all__ = [
    'XLRBase',
    'XLRGeneric',
    'XLRControlm',
    'XLRDynamicPhase',
    'XLRSun',
    'XLRTaskScript'
]

__version__ = '3.0.0-clean-architecture'
__author__ = 'Generated for Generic Application Deployment'