"""
Agent Memory for Test Generation Agent.

This module implements the memory system that maintains context 
during the test generation process.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

class AgentMemory:
    """
    Memory system for the test generation agent.
    
    This class maintains:
    - Short-term memory for the current generation session
    - Long-term memory for recurring patterns
    - Context tracking across multiple interactions
    """
    
    def __init__(self):
        """Initialize the agent memory system."""
        logger.info("Initializing Agent Memory")
        
        # Short-term memory (cleared between sessions)
        self.short_term = {
            'requirements': [],
            'current_machine': None,
            'current_version': None,
            'generation_history': []
        }
        
        # Long-term memory (persists across sessions)
        self.long_term = {
            'feedback_history': [],
            'performance_metrics': {},
            'recurring_patterns': {}
        }
        
        # Session metadata
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.session_start = datetime.now()
        
        logger.info(f"Memory initialized with session ID: {self.session_id}")
    
    def store_requirements(self, requirements: List[Dict]):
        """
        Store requirements in short-term memory.
        
        Args:
            requirements: List of requirement dictionaries
        """
        self.short_term['requirements'] = requirements
        logger.debug(f"Stored {len(requirements)} requirements in memory")
    
    def set_machine_context(self, machine_type: str, version: str):
        """
        Set the current machine context.
        
        Args:
            machine_type: The machine type (X, Y, Z)
            version: The machine version
        """
        self.short_term['current_machine'] = machine_type
        self.short_term['current_version'] = version
        logger.debug(f"Set current machine context to {machine_type} v{version}")
    
    def record_generation(self, requirement_id: str, test_case: Dict):
        """
        Record a generated test case in the generation history.
        
        Args:
            requirement_id: ID of the requirement
            test_case: The generated test case
        """
        self.short_term['generation_history'].append({
            'requirement_id': requirement_id,
            'test_case': test_case,
            'timestamp': datetime.now().isoformat()
        })
        logger.debug(f"Recorded generation for requirement: {requirement_id}")
    
    def record_feedback(self, test_case_id: str, feedback: Dict):
        """
        Record feedback on a generated test case.
        
        Args:
            test_case_id: ID of the test case
            feedback: Feedback information
        """
        feedback_record = {
            'test_case_id': test_case_id,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        
        self.long_term['feedback_history'].append(feedback_record)
        logger.debug(f"Recorded feedback for test case: {test_case_id}")
        
        # Update performance metrics based on feedback
        self._update_performance_metrics(feedback)
    
    def _update_performance_metrics(self, feedback: Dict):
        """
        Update performance metrics based on feedback.
        
        Args:
            feedback: The feedback information
        """
        metrics = self.long_term['performance_metrics']
        
        # Initialize metrics if not present
        if 'total_feedback_count' not in metrics:
            metrics['total_feedback_count'] = 0
            metrics['positive_feedback_count'] = 0
            metrics['approval_rate'] = 0.0
        
        # Update counts
        metrics['total_feedback_count'] += 1
        
        # Check if feedback was positive (approval)
        if feedback.get('approved', False):
            metrics['positive_feedback_count'] += 1
        
        # Recalculate approval rate
        if metrics['total_feedback_count'] > 0:
            metrics['approval_rate'] = (
                metrics['positive_feedback_count'] / metrics['total_feedback_count']
            )
    
    def update_recurring_patterns(self, pattern_key: str, pattern_data: Dict):
        """
        Update recurring patterns in long-term memory.
        
        Args:
            pattern_key: Identifier for the pattern
            pattern_data: Pattern information
        """
        if pattern_key not in self.long_term['recurring_patterns']:
            self.long_term['recurring_patterns'][pattern_key] = {
                'count': 0,
                'data': pattern_data,
                'last_updated': None
            }
        
        # Update pattern information
        pattern = self.long_term['recurring_patterns'][pattern_key]
        pattern['count'] += 1
        pattern['last_updated'] = datetime.now().isoformat()
        
        # Update pattern data if provided
        if pattern_data:
            pattern['data'].update(pattern_data)
        
        logger.debug(f"Updated recurring pattern: {pattern_key} (count: {pattern['count']})")
    
    def get_requirement(self, requirement_id: str) -> Optional[Dict]:
        """
        Get a requirement from memory by ID.
        
        Args:
            requirement_id: The ID of the requirement
            
        Returns:
            The requirement dictionary or None if not found
        """
        for req in self.short_term['requirements']:
            if req.get('id') == requirement_id:
                return req
        return None
    
    def get_generation_history(self, 
                              requirement_id: Optional[str] = None) -> List[Dict]:
        """
        Get the generation history for a requirement.
        
        Args:
            requirement_id: Optional ID to filter by requirement
            
        Returns:
            List of generation history entries
        """
        history = self.short_term['generation_history']
        
        if requirement_id:
            return [
                entry for entry in history 
                if entry['requirement_id'] == requirement_id
            ]
        
        return history
    
    def get_session_stats(self) -> Dict:
        """
        Get statistics for the current session.
        
        Returns:
            Dictionary with session statistics
        """
        history = self.short_term['generation_history']
        requirements = self.short_term['requirements']
        
        # Calculate statistics
        stats = {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'requirements_count': len(requirements),
            'generated_test_cases': len(history),
            'machine_type': self.short_term['current_machine'],
            'version': self.short_term['current_version']
        }
        
        return stats
    
    def clear_short_term_memory(self):
        """Clear the short-term memory for a new session."""
        # Create a new session ID
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.session_start = datetime.now()
        
        # Reset short-term memory
        self.short_term = {
            'requirements': [],
            'current_machine': None,
            'current_version': None,
            'generation_history': []
        }
        
        logger.info(f"Short-term memory cleared, new session: {self.session_id}")
    
    def save_memory_snapshot(self, path: str):
        """
        Save a snapshot of the memory state to a file.
        
        Args:
            path: Path to save the snapshot
        """
        # This would serialize the memory state to a file
        # Implementation would use JSON or pickle
        logger.info(f"Memory snapshot saved to: {path}")
    
    def load_memory_snapshot(self, path: str):
        """
        Load a memory snapshot from a file.
        
        Args:
            path: Path to the snapshot file
        """
        # This would deserialize a memory state from a file
        # Implementation would use JSON or pickle
        logger.info(f"Memory snapshot loaded from: {path}") 