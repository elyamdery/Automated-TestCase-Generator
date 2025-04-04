"""
CSV Parser for Test Cases.

This module provides functionality to parse and analyze existing test cases
from CSV files to learn patterns and structure.
"""

import logging
import csv
import pandas as pd
from typing import Dict, List, Optional, Any
import re

# Setup logging
logger = logging.getLogger(__name__)

class TestCaseParser:
    """
    Parser for test case CSV files.
    
    This class provides functionality to:
    - Parse CSV files containing test cases
    - Extract structure and patterns from existing test cases
    - Analyze linguistic style and common patterns
    """
    
    def __init__(self):
        """Initialize the test case parser."""
        logger.debug("Initializing test case parser")
    
    def parse(self, file_path: str) -> pd.DataFrame:
        """
        Parse a CSV file containing test cases.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataFrame containing the test cases
        """
        logger.info(f"Parsing test case CSV: {file_path}")
        
        try:
            # Read CSV into pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Log basic information about the data
            logger.info(f"Loaded {len(df)} test cases with {len(df.columns)} columns")
            logger.debug(f"Columns: {', '.join(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {str(e)}")
            raise
    
    def analyze_structure(self, df: pd.DataFrame) -> Dict:
        """
        Analyze the structure of test cases.
        
        Args:
            df: DataFrame containing test cases
            
        Returns:
            Dictionary with structural analysis
        """
        logger.info("Analyzing test case structure")
        
        # Identify key columns
        structure = {
            'columns': list(df.columns),
            'key_columns': self._identify_key_columns(df),
            'test_case_count': len(df),
            'average_steps_per_test': self._calculate_average_steps(df)
        }
        
        return structure
    
    def _identify_key_columns(self, df: pd.DataFrame) -> Dict:
        """
        Identify key columns in the test case DataFrame.
        
        Args:
            df: DataFrame containing test cases
            
        Returns:
            Dictionary mapping column roles to column names
        """
        key_columns = {}
        
        # Look for common column names for different roles
        for col in df.columns:
            col_lower = col.lower()
            
            # Test ID column
            if any(term in col_lower for term in ['id', 'test id', 'testid', 'test_id']):
                key_columns['test_id'] = col
            
            # Preconditions column
            elif any(term in col_lower for term in ['precondition', 'pre-condition', 'pre condition']):
                key_columns['preconditions'] = col
            
            # Test steps column
            elif any(term in col_lower for term in ['step', 'test step', 'teststep', 'test_step']):
                key_columns['steps'] = col
            
            # Expected results column
            elif any(term in col_lower for term in ['expected', 'result', 'expected result', 'expectedresult']):
                key_columns['expected_results'] = col
            
            # Requirement mapping column
            elif any(term in col_lower for term in ['req', 'requirement', 'req id', 'reqid']):
                key_columns['requirement_id'] = col
        
        logger.debug(f"Identified key columns: {key_columns}")
        return key_columns
    
    def _calculate_average_steps(self, df: pd.DataFrame) -> float:
        """
        Calculate the average number of steps per test case.
        
        Args:
            df: DataFrame containing test cases
            
        Returns:
            Average number of steps per test case
        """
        # Try to find steps column
        steps_col = None
        for col in df.columns:
            if any(term in col.lower() for term in ['step', 'test step', 'teststep']):
                steps_col = col
                break
        
        if not steps_col:
            logger.warning("Could not identify steps column")
            return 0
        
        # Count steps in each test case
        step_counts = []
        
        for _, row in df.iterrows():
            steps_text = str(row[steps_col])
            
            # Try to count numbered steps (e.g., "1. Step one\n2. Step two")
            step_matches = re.findall(r'^\s*\d+\.', steps_text, re.MULTILINE)
            if step_matches:
                step_counts.append(len(step_matches))
            else:
                # If no numbered steps, count newlines + 1
                step_counts.append(steps_text.count('\n') + 1)
        
        # Calculate average
        if step_counts:
            avg_steps = sum(step_counts) / len(step_counts)
            logger.debug(f"Average steps per test case: {avg_steps:.2f}")
            return avg_steps
        
        return 0
    
    def analyze_linguistic_style(self, df: pd.DataFrame, key_columns: Dict) -> Dict:
        """
        Analyze the linguistic style of test cases.
        
        Args:
            df: DataFrame containing test cases
            key_columns: Dictionary mapping column roles to column names
            
        Returns:
            Dictionary with linguistic style analysis
        """
        logger.info("Analyzing linguistic style of test cases")
        
        style_analysis = {
            'common_verbs': {},
            'average_step_length': 0,
            'tone': 'neutral',
            'formality': 'formal'
        }
        
        # Analyze steps if available
        if 'steps' in key_columns:
            steps_col = key_columns['steps']
            all_steps = []
            
            # Extract individual steps
            for _, row in df.iterrows():
                steps_text = str(row[steps_col])
                
                # Try to split by numbered steps
                step_matches = re.findall(r'^\s*\d+\.\s*(.*?)(?=^\s*\d+\.|\Z)', steps_text, re.MULTILINE | re.DOTALL)
                if step_matches:
                    all_steps.extend([step.strip() for step in step_matches])
                else:
                    # If no numbered steps, split by newlines
                    all_steps.extend([step.strip() for step in steps_text.split('\n') if step.strip()])
            
            # Calculate average step length
            if all_steps:
                style_analysis['average_step_length'] = sum(len(step) for step in all_steps) / len(all_steps)
            
            # Extract common verbs
            verb_counts = {}
            common_verbs = ['verify', 'check', 'ensure', 'click', 'select', 'enter', 'navigate', 'open', 'close', 'save']
            
            for step in all_steps:
                for verb in common_verbs:
                    if re.search(r'\b' + verb + r'\b', step.lower()):
                        verb_counts[verb] = verb_counts.get(verb, 0) + 1
            
            # Sort verbs by frequency
            style_analysis['common_verbs'] = dict(sorted(verb_counts.items(), key=lambda x: x[1], reverse=True))
            
            # Determine tone based on verb usage
            if style_analysis['common_verbs'].get('verify', 0) > style_analysis['common_verbs'].get('check', 0):
                style_analysis['tone'] = 'assertive'
            else:
                style_analysis['tone'] = 'instructive'
        
        logger.debug(f"Linguistic style analysis: {style_analysis}")
        return style_analysis
    
    def extract_patterns(self, df: pd.DataFrame, key_columns: Dict) -> List[Dict]:
        """
        Extract test patterns from existing test cases.
        
        Args:
            df: DataFrame containing test cases
            key_columns: Dictionary mapping column roles to column names
            
        Returns:
            List of extracted patterns
        """
        logger.info("Extracting test patterns from existing test cases")
        
        patterns = []
        
        # Group test cases by requirement if possible
        if 'requirement_id' in key_columns:
            req_col = key_columns['requirement_id']
            req_groups = df.groupby(req_col)
            
            for req_id, group in req_groups:
                if pd.isna(req_id) or not req_id:
                    continue
                
                pattern = {
                    'requirement_id': req_id,
                    'test_count': len(group),
                    'test_types': self._identify_test_types(group, key_columns),
                    'common_preconditions': self._extract_common_preconditions(group, key_columns),
                    'common_steps': self._extract_common_steps(group, key_columns),
                    'examples': self._extract_examples(group, key_columns)
                }
                
                patterns.append(pattern)
        
        # If no requirement grouping possible, extract general patterns
        if not patterns:
            pattern = {
                'requirement_id': 'general',
                'test_count': len(df),
                'test_types': self._identify_test_types(df, key_columns),
                'common_preconditions': self._extract_common_preconditions(df, key_columns),
                'common_steps': self._extract_common_steps(df, key_columns),
                'examples': self._extract_examples(df, key_columns)
            }
            
            patterns.append(pattern)
        
        logger.info(f"Extracted {len(patterns)} test patterns")
        return patterns
    
    def _identify_test_types(self, df: pd.DataFrame, key_columns: Dict) -> List[str]:
        """Identify types of tests in the group."""
        test_types = []
        
        # Look for keywords in steps and expected results
        steps_col = key_columns.get('steps')
        results_col = key_columns.get('expected_results')
        
        if steps_col:
            steps_text = ' '.join(df[steps_col].astype(str))
            
            # Check for happy path tests
            if re.search(r'\b(normal|standard|typical|happy path)\b', steps_text, re.IGNORECASE):
                test_types.append('happy_path')
            
            # Check for boundary tests
            if re.search(r'\b(boundary|limit|maximum|minimum|min|max)\b', steps_text, re.IGNORECASE):
                test_types.append('boundary_conditions')
            
            # Check for error tests
            if re.search(r'\b(error|exception|fail|invalid|negative)\b', steps_text, re.IGNORECASE):
                test_types.append('error_cases')
        
        # If no specific types identified, assume happy path
        if not test_types:
            test_types.append('happy_path')
        
        return test_types
    
    def _extract_common_preconditions(self, df: pd.DataFrame, key_columns: Dict) -> List[str]:
        """Extract common preconditions from test cases."""
        if 'preconditions' not in key_columns:
            return []
        
        preconditions_col = key_columns['preconditions']
        all_preconditions = df[preconditions_col].astype(str).tolist()
        
        # Find common preconditions by frequency
        precondition_counts = {}
        for precondition in all_preconditions:
            if pd.isna(precondition) or not precondition.strip():
                continue
            
            # Split by newlines or semicolons
            for item in re.split(r'[\n;]', precondition):
                item = item.strip()
                if item:
                    precondition_counts[item] = precondition_counts.get(item, 0) + 1
        
        # Return preconditions that appear in at least 30% of test cases
        threshold = 0.3 * len(df)
        common_preconditions = [p for p, count in precondition_counts.items() if count >= threshold]
        
        return common_preconditions
    
    def _extract_common_steps(self, df: pd.DataFrame, key_columns: Dict) -> List[str]:
        """Extract common steps from test cases."""
        if 'steps' not in key_columns:
            return []
        
        steps_col = key_columns['steps']
        all_steps = []
        
        # Extract individual steps
        for _, row in df.iterrows():
            steps_text = str(row[steps_col])
            
            # Try to split by numbered steps
            step_matches = re.findall(r'^\s*\d+\.\s*(.*?)(?=^\s*\d+\.|\Z)', steps_text, re.MULTILINE | re.DOTALL)
            if step_matches:
                all_steps.extend([step.strip() for step in step_matches])
            else:
                # If no numbered steps, split by newlines
                all_steps.extend([step.strip() for step in steps_text.split('\n') if step.strip()])
        
        # Find common steps by frequency
        step_counts = {}
        for step in all_steps:
            if not step.strip():
                continue
            
            # Normalize step by removing specific details
            normalized_step = re.sub(r'\b\d+\b', 'X', step)  # Replace numbers with X
            normalized_step = re.sub(r'"[^"]*"', '"..."', normalized_step)  # Replace quoted text
            
            step_counts[normalized_step] = step_counts.get(normalized_step, 0) + 1
        
        # Return steps that appear multiple times
        threshold = 2
        common_steps = [s for s, count in step_counts.items() if count >= threshold]
        
        return common_steps
    
    def _extract_examples(self, df: pd.DataFrame, key_columns: Dict) -> List[Dict]:
        """Extract representative examples from test cases."""
        examples = []
        
        # Select a few representative examples
        sample_size = min(3, len(df))
        sample_df = df.sample(n=sample_size) if len(df) > sample_size else df
        
        for _, row in sample_df.iterrows():
            example = {}
            
            # Extract key fields
            for role, col in key_columns.items():
                if col in row:
                    example[role] = row[col]
            
            examples.append(example)
        
        return examples
