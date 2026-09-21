"""
Dating Agent - Multi-platform dating app orchestrator

This package provides tools to aggregate, filter, and match profiles
from multiple dating platforms (Tinder, Hinge, Match).
"""

__version__ = "0.1.0"

from .profile_aggregator import profile_aggregator
from .profile_store import profile_store
from .auth_handlers import HingeAuth, TinderAuth

__all__ = [
    "profile_aggregator",
    "profile_store",
    "HingeAuth",
    "TinderAuth",
]
