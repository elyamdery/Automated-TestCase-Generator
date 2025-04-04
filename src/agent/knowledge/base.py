"""
Knowledge Repository for Test Generation Agent.

This module implements the storage and retrieval of test patterns,
machine-specific information, and examples for test generation.
"""

import logging
from typing import Dict, List, Optional, Any

# Setup logging
logger = logging.getLogger(__name__)

class KnowledgeRepository:
    """
    Knowledge repository for storing and retrieving test patterns.
    
    This class maintains:
    - Learned test patterns from existing test cases
    - Machine-specific information and constraints
    - Example test cases for few-shot learning
    """
    
    def __init__(self):
        """Initialize the knowledge repository."""
        logger.info("Initializing Knowledge Repository")
        
        # Storage for learned test patterns
        self.test_patterns = {}
        
        # Machine-specific knowledge
        self.machine_contexts = {
            'X': self._initialize_machine_context('X'),
            'Y': self._initialize_machine_context('Y'),
            'Z': self._initialize_machine_context('Z')
        }
        
        # Example test cases for few-shot learning
        self.examples = []
        
        logger.info("Knowledge Repository initialized")
    
    def _initialize_machine_context(self, machine_type: str) -> Dict:
        """
        Initialize context information for a specific machine type.
        
        Args:
            machine_type: The type of machine (X, Y, Z)
            
        Returns:
            Dictionary with machine-specific context information
        """
        logger.debug(f"Initializing context for machine type: {machine_type}")
        
        # This would contain machine-specific information
        # Features, capabilities, limitations, etc.
        return {
            'features': [],
            'versions': {},
            'specific_actions': [],
            'specific_verifications': []
        }
    
    def add_test_pattern(self, pattern: Dict, metadata: Dict):
        """
        Add a learned test pattern to the repository.
        
        Args:
            pattern: The test pattern structure
            metadata: Additional information about the pattern
        """
        pattern_id = metadata.get('id', f"pattern_{len(self.test_patterns)}")
        logger.debug(f"Adding test pattern: {pattern_id}")
        
        self.test_patterns[pattern_id] = {
            'pattern': pattern,
            'metadata': metadata
        }
    
    def get_relevant_patterns(self, 
                             requirement: Dict, 
                             machine_type: str, 
                             version: str) -> List[Dict]:
        """
        Retrieve patterns relevant to a specific requirement and machine.
        
        Args:
            requirement: The requirement to find patterns for
            machine_type: Target machine type
            version: Target version
            
        Returns:
            List of relevant test patterns
        """
        logger.debug(f"Finding patterns for requirement: {requirement.get('id', 'Unknown')}")
        
        # In a real implementation, this would use NLP similarity
        # or other matching techniques to find relevant patterns
        # For now, return a simple placeholder
        
        return [pattern for pattern in self.test_patterns.values()]
    
    def add_machine_specific_information(self, 
                                        machine_type: str, 
                                        version: str, 
                                        info: Dict):
        """
        Add machine-specific information to the knowledge base.
        
        Args:
            machine_type: The machine type (X, Y, Z)
            version: The version of the machine
            info: Information to add
        """
        if machine_type not in self.machine_contexts:
            logger.warning(f"Adding information for unknown machine type: {machine_type}")
            self.machine_contexts[machine_type] = self._initialize_machine_context(machine_type)
        
        # Add version-specific information if it doesn't exist
        if version not in self.machine_contexts[machine_type]['versions']:
            self.machine_contexts[machine_type]['versions'][version] = {}
        
        # Update with new information
        self.machine_contexts[machine_type]['versions'][version].update(info)
        
        logger.debug(f"Updated information for {machine_type} version {version}")
    
    def add_example(self, example: Dict, tags: List[str]):
        """
        Add an example test case for few-shot learning.
        
        Args:
            example: The example test case
            tags: List of tags for categorization
        """
        example_with_tags = {
            'example': example,
            'tags': tags
        }
        
        self.examples.append(example_with_tags)
        logger.debug(f"Added example with tags: {tags}")
    
    def get_examples(self, 
                    requirement: Dict, 
                    machine_type: str, 
                    version: str,
                    limit: int = 3) -> List[str]:
        """
        Get relevant example test cases for a requirement.
        
        Args:
            requirement: The requirement to find examples for
            machine_type: Target machine type
            version: Target version
            limit: Maximum number of examples to return
            
        Returns:
            List of example test cases as formatted strings
        """
        logger.debug(f"Finding examples for requirement on {machine_type} v{version}")
        
        # Filter examples by machine type and version
        # In a real implementation, this would use more sophisticated
        # matching techniques to find the most relevant examples
        
        filtered_examples = [
            ex for ex in self.examples 
            if machine_type in ex.get('tags', []) and version in ex.get('tags', [])
        ]
        
        # Further filter by similarity to requirement (placeholder implementation)
        # Would use NLP or other techniques in a real implementation
        
        # Convert to formatted strings
        result = []
        for ex in filtered_examples[:limit]:
            # Format the example as a string
            example_text = self._format_example(ex['example'])
            result.append(example_text)
        
        return result
    
    def _format_example(self, example: Dict) -> str:
        """Format an example test case as a string."""
        # This would format the example in a way that's suitable for
        # inclusion in a prompt
        
        # Placeholder implementation
        formatted = f"TEST CASE ID: {example.get('id', 'Unknown')}\n"
        formatted += f"PRECONDITIONS: {example.get('preconditions', '')}\n"
        formatted += "STEPS:\n"
        
        for i, step in enumerate(example.get('steps', []), 1):
            formatted += f"{i}. {step}\n"
        
        formatted += "EXPECTED RESULTS:\n"
        for i, result in enumerate(example.get('expected_results', []), 1):
            formatted += f"{i}. {result}\n"
        
        return formatted
    
    def get_machine_context(self, machine_type: str, version: str) -> Dict:
        """
        Get the context information for a specific machine and version.
        
        Args:
            machine_type: The machine type
            version: The machine version
            
        Returns:
            Dictionary with machine context information
        """
        if machine_type not in self.machine_contexts:
            logger.warning(f"Requested context for unknown machine type: {machine_type}")
            return {}
        
        context = self.machine_contexts[machine_type]
        
        # Add version-specific information if available
        if version in context['versions']:
            version_context = context['versions'][version]
            # Create a new dict with version-specific overrides
            result = {**context, **version_context}
            # Remove the versions key
            if 'versions' in result:
                del result['versions']
            return result
        
        # Return base context without version-specific information
        result = context.copy()
        if 'versions' in result:
            del result['versions']
        return result 