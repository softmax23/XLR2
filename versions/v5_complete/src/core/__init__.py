"""
Core modules for XLR Template Creator V5
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