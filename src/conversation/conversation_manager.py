"""
Conversation Manager for Test Case Generator.

This module provides functionality for multi-turn AI conversations
to refine test cases interactively.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Tuple

# Setup logging
logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manager for multi-turn AI conversations.
    
    This class provides functionality to:
    - Start new conversations about test cases
    - Continue existing conversations
    - Track conversation history
    - Apply refinements to test cases based on conversations
    """
    
    def __init__(self, conversation_dir: Optional[str] = None):
        """
        Initialize the conversation manager.
        
        Args:
            conversation_dir: Optional directory to store conversations
        """
        logger.debug("Initializing Conversation Manager")
        
        # Dictionary to store active conversations
        self.active_conversations = {}
        
        # Set the conversation directory
        self.conversation_dir = conversation_dir or os.path.join('data', 'conversations')
        
        # Create the directory if it doesn't exist
        os.makedirs(self.conversation_dir, exist_ok=True)
    
    def start_conversation(self, 
                          test_case_id: str, 
                          test_case: Dict) -> str:
        """
        Start a new conversation about a test case.
        
        Args:
            test_case_id: ID of the test case
            test_case: The test case dictionary
            
        Returns:
            Conversation ID
        """
        # Generate a unique conversation ID
        conversation_id = f"conv_{test_case_id}_{int(datetime.datetime.now().timestamp())}"
        
        # Initialize the conversation
        conversation = {
            'id': conversation_id,
            'test_case_id': test_case_id,
            'original_test_case': test_case,
            'current_test_case': test_case.copy(),
            'messages': [
                {
                    'role': 'system',
                    'content': f"This is a conversation about test case {test_case_id}. The user may want to refine or improve the test case."
                },
                {
                    'role': 'assistant',
                    'content': f"I've generated a test case for {test_case.get('title', 'your requirement')}. Would you like me to refine it in any way? For example, I can add more edge cases, improve the steps, or focus on specific aspects."
                }
            ],
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Add to active conversations
        self.active_conversations[conversation_id] = conversation
        
        # Save the conversation
        self._save_conversation(conversation)
        
        logger.info(f"Started conversation {conversation_id} for test case {test_case_id}")
        
        return conversation_id
    
    def add_user_message(self, 
                        conversation_id: str, 
                        message: str) -> Dict:
        """
        Add a user message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            message: User message
            
        Returns:
            Updated conversation
        """
        # Get the conversation
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            # Try to load from disk
            conversation = self._load_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Add to active conversations
            self.active_conversations[conversation_id] = conversation
        
        # Add the user message
        conversation['messages'].append({
            'role': 'user',
            'content': message
        })
        
        # Update the timestamp
        conversation['updated_at'] = datetime.datetime.now().isoformat()
        
        # Save the conversation
        self._save_conversation(conversation)
        
        logger.debug(f"Added user message to conversation {conversation_id}")
        
        return conversation
    
    def add_assistant_message(self, 
                             conversation_id: str, 
                             message: str,
                             updated_test_case: Optional[Dict] = None) -> Dict:
        """
        Add an assistant message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            message: Assistant message
            updated_test_case: Optional updated test case
            
        Returns:
            Updated conversation
        """
        # Get the conversation
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            # Try to load from disk
            conversation = self._load_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Add to active conversations
            self.active_conversations[conversation_id] = conversation
        
        # Add the assistant message
        conversation['messages'].append({
            'role': 'assistant',
            'content': message
        })
        
        # Update the test case if provided
        if updated_test_case:
            conversation['current_test_case'] = updated_test_case
        
        # Update the timestamp
        conversation['updated_at'] = datetime.datetime.now().isoformat()
        
        # Save the conversation
        self._save_conversation(conversation)
        
        logger.debug(f"Added assistant message to conversation {conversation_id}")
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The conversation dictionary or None if not found
        """
        # Check active conversations
        conversation = self.active_conversations.get(conversation_id)
        if conversation:
            return conversation
        
        # Try to load from disk
        return self._load_conversation(conversation_id)
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Get the message history for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of message dictionaries
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation.get('messages', [])
    
    def get_current_test_case(self, conversation_id: str) -> Optional[Dict]:
        """
        Get the current test case for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The current test case dictionary or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return conversation.get('current_test_case')
    
    def get_original_test_case(self, conversation_id: str) -> Optional[Dict]:
        """
        Get the original test case for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The original test case dictionary or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return conversation.get('original_test_case')
    
    def close_conversation(self, conversation_id: str) -> Dict:
        """
        Close a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The closed conversation
        """
        # Get the conversation
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            # Try to load from disk
            conversation = self._load_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
        
        # Update the status
        conversation['status'] = 'closed'
        conversation['updated_at'] = datetime.datetime.now().isoformat()
        
        # Save the conversation
        self._save_conversation(conversation)
        
        # Remove from active conversations
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
        
        logger.info(f"Closed conversation {conversation_id}")
        
        return conversation
    
    def list_conversations(self, test_case_id: Optional[str] = None) -> List[Dict]:
        """
        List conversations, optionally filtered by test case ID.
        
        Args:
            test_case_id: Optional test case ID to filter by
            
        Returns:
            List of conversation summaries
        """
        conversations = []
        
        # Check the conversation directory
        try:
            for filename in os.listdir(self.conversation_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.conversation_dir, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            conversation = json.load(f)
                            
                            # Filter by test case ID if provided
                            if test_case_id and conversation.get('test_case_id') != test_case_id:
                                continue
                            
                            # Add a summary to the list
                            conversations.append({
                                'id': conversation.get('id'),
                                'test_case_id': conversation.get('test_case_id'),
                                'created_at': conversation.get('created_at'),
                                'updated_at': conversation.get('updated_at'),
                                'status': conversation.get('status'),
                                'message_count': len(conversation.get('messages', []))
                            })
                    except Exception as e:
                        logger.error(f"Error loading conversation from {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
        
        # Sort by updated_at (newest first)
        conversations.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return conversations
    
    def _save_conversation(self, conversation: Dict):
        """
        Save a conversation to disk.
        
        Args:
            conversation: The conversation to save
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.conversation_dir, exist_ok=True)
            
            # Generate filename from conversation ID
            filename = f"{conversation['id']}.json"
            
            # Save to file
            file_path = os.path.join(self.conversation_dir, filename)
            with open(file_path, 'w') as f:
                json.dump(conversation, f, indent=2)
                
            logger.debug(f"Saved conversation to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
    
    def _load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Load a conversation from disk.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The conversation dictionary or None if not found
        """
        try:
            # Generate filename from conversation ID
            filename = f"{conversation_id}.json"
            file_path = os.path.join(self.conversation_dir, filename)
            
            # Check if the file exists
            if not os.path.exists(file_path):
                logger.warning(f"Conversation file not found: {file_path}")
                return None
            
            # Load from file
            with open(file_path, 'r') as f:
                conversation = json.load(f)
                
            logger.debug(f"Loaded conversation from {file_path}")
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
            return None
    
    def apply_refinement(self, 
                        conversation_id: str, 
                        refinement_type: str, 
                        refinement_params: Dict) -> Tuple[Dict, str]:
        """
        Apply a refinement to a test case based on conversation.
        
        Args:
            conversation_id: ID of the conversation
            refinement_type: Type of refinement (e.g., 'add_edge_cases', 'improve_steps')
            refinement_params: Parameters for the refinement
            
        Returns:
            Tuple of (updated test case, assistant message)
        """
        # Get the conversation
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get the current test case
        test_case = conversation.get('current_test_case', {}).copy()
        
        # Apply the refinement based on type
        assistant_message = ""
        
        if refinement_type == 'add_edge_cases':
            # Add edge cases to the test case
            edge_cases = refinement_params.get('edge_cases', [])
            
            # Add edge cases to steps and expected results
            for edge_case in edge_cases:
                test_case['steps'].append(edge_case.get('step', ''))
                test_case['expected_results'].append(edge_case.get('expected', ''))
            
            assistant_message = f"I've added {len(edge_cases)} edge cases to the test case. Would you like me to add more specific scenarios or improve any other aspects?"
        
        elif refinement_type == 'improve_steps':
            # Improve existing steps
            improved_steps = refinement_params.get('improved_steps', {})
            
            # Update the steps
            for step_idx, improved_step in improved_steps.items():
                step_idx = int(step_idx)
                if 0 <= step_idx < len(test_case['steps']):
                    test_case['steps'][step_idx] = improved_step
            
            assistant_message = "I've improved the steps to be more precise and actionable. Is there anything else you'd like me to enhance?"
        
        elif refinement_type == 'add_performance_scenarios':
            # Add performance testing scenarios
            performance_scenarios = refinement_params.get('scenarios', [])
            
            # Add a note about performance testing
            test_case['notes'] = test_case.get('notes', '') + "\nPerformance testing scenarios included."
            
            # Add performance scenarios to steps and expected results
            for scenario in performance_scenarios:
                test_case['steps'].append(scenario.get('step', ''))
                test_case['expected_results'].append(scenario.get('expected', ''))
            
            assistant_message = f"I've added {len(performance_scenarios)} performance testing scenarios. Would you like me to add any other types of scenarios?"
        
        elif refinement_type == 'focus_on_security':
            # Add security testing focus
            security_aspects = refinement_params.get('security_aspects', [])
            
            # Add a note about security testing
            test_case['notes'] = test_case.get('notes', '') + "\nSecurity testing aspects included."
            
            # Add security aspects to steps and expected results
            for aspect in security_aspects:
                test_case['steps'].append(aspect.get('step', ''))
                test_case['expected_results'].append(aspect.get('expected', ''))
            
            assistant_message = f"I've added {len(security_aspects)} security testing aspects to the test case. Would you like me to focus on any specific security concerns?"
        
        else:
            # Unknown refinement type
            raise ValueError(f"Unknown refinement type: {refinement_type}")
        
        # Update the conversation with the refined test case
        self.add_assistant_message(conversation_id, assistant_message, test_case)
        
        return test_case, assistant_message
