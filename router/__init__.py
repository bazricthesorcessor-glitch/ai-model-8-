"""
Router module - central service bus for inter-module communication.
Connects Scout, models, query makers, tools, and runtime services.
Does not perform cognitive reasoning.
"""

from .message import Message, Response
from .router import dispatch, send_to_service, register_service

__all__ = [
    "Message",
    "Response",
    "dispatch",
    "send_to_service",
    "register_service",
]
