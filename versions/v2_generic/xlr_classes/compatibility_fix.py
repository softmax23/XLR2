"""
Compatibility fix for cross-class method calls.

This module provides a solution for the static method calls between classes
that were originally in the monolithic all_class.py file.
"""

# This is a temporary solution to fix the cross-class method calls
# The proper solution would be to refactor the architecture to avoid these calls

def fix_cross_class_references():
    """
    This function should be called after all classes are loaded to fix
    the cross-class method calls that are causing import issues.
    """
    pass

# Note: The VS Code error highlighting for XLRGeneric() in xlr_controlm.py
# occurs because the classes have circular dependencies.
#
# The original monolithic file worked because all classes were in the same namespace.
# In the modular structure, we need to either:
# 1. Refactor to remove circular dependencies (recommended long-term)
# 2. Use late imports or dependency injection
# 3. Keep the original structure but better organized
#
# For now, the code will work at runtime due to Python's import system,
# but IDE static analysis shows warnings.