"""
Core dynamic template modules for XLR automation.

This package contains the core classes for XLR template and release management:
- XLRGeneric: Core functionality for template operations
- XLRControlm: Control-M integration and job management
- XLRDynamicPhase: Dynamic phase creation and management
- XLRSun: ServiceNow integration and task management
- XLRTaskScript: Script task creation and automation utilities
- XLRRelease: Release creation and management
"""

from .xlr_generic import XLRGeneric, XLRGenericError
from .xlr_controlm import XLRControlm, XLRControlmError
from .xlr_dynamic_phase import XLRDynamicPhase, XLRDynamicPhaseError
from .xlr_sun import XLRSun, XLRSunError
from .xlr_task_script import XLRTaskScript, XLRTaskScriptError
from .xlr_release import XLRRelease, XLRReleaseError

__all__ = [
    'XLRGeneric',
    'XLRGenericError',
    'XLRControlm',
    'XLRControlmError',
    'XLRDynamicPhase',
    'XLRDynamicPhaseError',
    'XLRSun',
    'XLRSunError',
    'XLRTaskScript',
    'XLRTaskScriptError',
    'XLRRelease',
    'XLRReleaseError'
]