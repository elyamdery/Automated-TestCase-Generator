"""
Shared Steps Manager for Test Generation Agent.

This module provides functionality to manage and use shared steps
in test case generation.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

# Setup logging
logger = logging.getLogger(__name__)

class SharedStepsManager:
    """
    Manager for shared test steps.
    
    This class provides functionality to:
    - Load shared steps from a repository
    - Create new shared steps
    - Reference shared steps in test cases
    """
    
    def __init__(self, shared_steps_dir: Optional[str] = None):
        """
        Initialize the shared steps manager.
        
        Args:
            shared_steps_dir: Optional directory to load shared steps from
        """
        logger.debug("Initializing Shared Steps Manager")
        
        # Dictionary to store shared steps
        self.shared_steps = {}
        
        # Set the shared steps directory
        self.shared_steps_dir = shared_steps_dir or 'data/shared_steps'
        
        # Load shared steps if directory exists
        if os.path.exists(self.shared_steps_dir):
            self.load_shared_steps()
    
    def load_shared_steps(self):
        """Load shared steps from the repository."""
        logger.info(f"Loading shared steps from {self.shared_steps_dir}")
        
        try:
            # Iterate through files in the directory
            for filename in os.listdir(self.shared_steps_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.shared_steps_dir, filename)
                    
                    with open(file_path, 'r') as f:
                        shared_step = json.load(f)
                        
                        # Add to the dictionary
                        step_id = shared_step.get('id')
                        if step_id:
                            self.shared_steps[step_id] = shared_step
                            logger.debug(f"Loaded shared step: {step_id}")
            
            logger.info(f"Loaded {len(self.shared_steps)} shared steps")
            
        except Exception as e:
            logger.error(f"Error loading shared steps: {str(e)}")
    
    def create_shared_step(self, 
                          title: str, 
                          steps: List[str], 
                          expected_results: List[str],
                          save: bool = True) -> Dict:
        """
        Create a new shared step.
        
        Args:
            title: Title of the shared step
            steps: List of step actions
            expected_results: List of expected results
            save: Whether to save the shared step to disk
            
        Returns:
            The created shared step dictionary
        """
        # Generate a unique ID
        step_id = f"SS-{len(self.shared_steps) + 1:05d}"
        
        # Create the shared step
        shared_step = {
            'id': step_id,
            'title': title,
            'steps': steps,
            'expected_results': expected_results
        }
        
        # Add to the dictionary
        self.shared_steps[step_id] = shared_step
        
        # Save to disk if requested
        if save:
            self._save_shared_step(shared_step)
        
        logger.info(f"Created shared step: {step_id} - {title}")
        return shared_step
    
    def _save_shared_step(self, shared_step: Dict):
        """
        Save a shared step to disk.
        
        Args:
            shared_step: The shared step to save
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.shared_steps_dir, exist_ok=True)
            
            # Save to file
            file_path = os.path.join(self.shared_steps_dir, f"{shared_step['id']}.json")
            with open(file_path, 'w') as f:
                json.dump(shared_step, f, indent=2)
                
            logger.debug(f"Saved shared step to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving shared step: {str(e)}")
    
    def get_shared_step(self, step_id: str) -> Optional[Dict]:
        """
        Get a shared step by ID.
        
        Args:
            step_id: The ID of the shared step
            
        Returns:
            The shared step dictionary or None if not found
        """
        return self.shared_steps.get(step_id)
    
    def find_similar_shared_steps(self, 
                                 keywords: List[str], 
                                 limit: int = 3) -> List[Dict]:
        """
        Find shared steps that match the given keywords.
        
        Args:
            keywords: List of keywords to match
            limit: Maximum number of results to return
            
        Returns:
            List of matching shared steps
        """
        matches = []
        
        # Convert keywords to lowercase for case-insensitive matching
        keywords_lower = [k.lower() for k in keywords]
        
        for step_id, step in self.shared_steps.items():
            # Check if any keyword is in the title
            title_lower = step['title'].lower()
            if any(k in title_lower for k in keywords_lower):
                matches.append(step)
                continue
            
            # Check if any keyword is in the steps
            steps_text = ' '.join(step['steps']).lower()
            if any(k in steps_text for k in keywords_lower):
                matches.append(step)
                continue
        
        # Return up to the limit
        return matches[:limit]
    
    def get_shared_step_reference(self, step_id: str) -> Dict:
        """
        Get a reference to a shared step for inclusion in a test case.
        
        Args:
            step_id: The ID of the shared step
            
        Returns:
            Dictionary with shared step reference information
        """
        shared_step = self.get_shared_step(step_id)
        
        if not shared_step:
            logger.warning(f"Shared step not found: {step_id}")
            return {
                'id': '',
                'work_item_type': '',
                'title': '',
                'test_step': '',
                'step_action': f"SHARED STEP NOT FOUND: {step_id}",
                'step_expected': ''
            }
        
        return {
            'id': step_id,
            'work_item_type': 'Shared steps',
            'title': shared_step['title'],
            'test_step': '',
            'step_action': '',
            'step_expected': ''
        }
