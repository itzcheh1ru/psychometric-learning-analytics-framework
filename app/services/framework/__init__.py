"""
app/services/framework/__init__.py

Service package for the Framework Integration layer.

Exports:
- COMPONENT_REGISTRY: metadata for all four analytical components
- FrameworkStatusService, framework_status_service
- FRAMEWORK_SPECIFICATION

Status: Prototype – all components are in data collection / development stage.
        No combined model, no overall AI risk score, no cross-component results.
"""

from app.services.framework.registry import COMPONENT_REGISTRY, FRAMEWORK_SPECIFICATION
from app.services.framework.status_service import (
    FrameworkStatusService,
    framework_status_service,
)

__all__ = [
    "COMPONENT_REGISTRY",
    "FRAMEWORK_SPECIFICATION",
    "FrameworkStatusService",
    "framework_status_service",
]
