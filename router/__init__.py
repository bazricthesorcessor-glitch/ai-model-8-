"""
Router module - central dispatcher for all inter-module communication.
NO LOGIC - only message routing. Brain, Executor, State are called here only.
"""

from .message import Message, Response
from .router import route

__all__ = ["Message", "Response", "route"]
