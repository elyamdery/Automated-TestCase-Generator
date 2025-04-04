"""
Tests for the CSV parser module.
"""

import unittest
import os
import tempfile
import pandas as pd
from agent.input.csv_parser import TestCaseParser

class TestCsvParser(unittest.TestCase):
    """Test cases for the CSV parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file with sample test cases
        self.test_data = pd.DataFrame({
            'Test ID': ['TC-001', 'TC-002', 'TC-003'],
            'Requirement ID': ['REQ-001', 'REQ-001', 'REQ-002'],
            'Preconditions': [
                'System is operational',
                'User is logged in',
                'Database is accessible'
            ],
            'Test Steps': [
                '1. Navigate to login page\n2. Enter valid credentials\n3. Click login button',
                '1. Navigate to login page\n2. Enter invalid credentials\n3. Click login button',
                '1. Open user profile\n2. Click edit button\n3. Update user information\n4. Save changes'
            ],
            'Expected Results': [
                '1. Login page is displayed\n2. Credentials are accepted\n3. User is logged in successfully',
                '1. Login page is displayed\n2. Credentials are entered\n3. Error message is displayed',
                '1. Profile page opens\n2. Edit mode is activated\n3. Information is updated\n4. Changes are saved'
            ]
        })
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            self.test_data.to_csv(f, index=False)
            self.temp_file = f.name
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up
        os.unlink(self.temp_file)
    
    def test_parse_csv(self):
        """Test parsing a CSV file with test cases."""
        # Parse the file
        parser = TestCaseParser()
        df = parser.parse(self.temp_file)
        
        # Verify the results
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['Test ID', 'Requirement ID', 'Preconditions', 'Test Steps', 'Expected Results'])
    
    def test_analyze_structure(self):
        """Test analyzing the structure of test cases."""
        # Parse and analyze
        parser = TestCaseParser()
        df = parser.parse(self.temp_file)
        structure = parser.analyze_structure(df)
        
        # Verify the structure analysis
        self.assertEqual(structure['test_case_count'], 3)
        self.assertTrue('key_columns' in structure)
        self.assertTrue('test_id' in structure['key_columns'])
        self.assertTrue('steps' in structure['key_columns'])
        self.assertTrue('expected_results' in structure['key_columns'])
    
    def test_analyze_linguistic_style(self):
        """Test analyzing the linguistic style of test cases."""
        # Parse and analyze
        parser = TestCaseParser()
        df = parser.parse(self.temp_file)
        structure = parser.analyze_structure(df)
        style = parser.analyze_linguistic_style(df, structure['key_columns'])
        
        # Verify the style analysis
        self.assertTrue('common_verbs' in style)
        self.assertTrue('average_step_length' in style)
        self.assertTrue(style['average_step_length'] > 0)
    
    def test_extract_patterns(self):
        """Test extracting patterns from test cases."""
        # Parse and extract patterns
        parser = TestCaseParser()
        df = parser.parse(self.temp_file)
        structure = parser.analyze_structure(df)
        patterns = parser.extract_patterns(df, structure['key_columns'])
        
        # Verify the patterns
        self.assertTrue(len(patterns) > 0)
        self.assertTrue('requirement_id' in patterns[0])
        self.assertTrue('test_count' in patterns[0])
        self.assertTrue('examples' in patterns[0])
        
        # Check that we have examples
        self.assertTrue(len(patterns[0]['examples']) > 0)

if __name__ == '__main__':
    unittest.main()
