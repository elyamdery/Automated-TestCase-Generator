"""
Conversation package for Test Case Generator.

This package provides functionality for multi-turn AI conversations
to refine test cases interactively.
"""

from conversation.conversation_manager import ConversationManager
from conversation.conversation_ui import ConversationUI

__all__ = ['ConversationManager', 'ConversationUI']
