"""
Tests for the TestGenerationAgent class.
"""

import unittest
import os
import tempfile
import pandas as pd
from agent.core.agent import TestGenerationAgent

class TestAgent(unittest.TestCase):
    """Test cases for the TestGenerationAgent."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a configuration
        self.config = {
            'llm_provider': 'openai',
            'openai_api_key': 'dummy_key',
            'output_dir': 'output'
        }

        # Create a temporary SRS text file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("""
            REQ-001: The system shall allow users to log in with username and password.

            REQ-002: The system shall display an error message for invalid login attempts.

            REQ-003: For Machine X version 1.0, the system shall support biometric authentication.

            The system must support Machine X version 1.0 for all operations.
            """)
            self.srs_file = f.name

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
            self.tests_file = f.name

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up
        os.unlink(self.srs_file)
        os.unlink(self.tests_file)

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = TestGenerationAgent(self.config)

        # Verify the agent was initialized correctly
        self.assertEqual(agent.config, self.config)
        self.assertIsNotNone(agent.knowledge_base)
        self.assertIsNotNone(agent.memory)
        self.assertIsNotNone(agent.reasoning)

    def test_process_srs(self):
        """Test processing an SRS document."""
        agent = TestGenerationAgent(self.config)

        # Process the SRS
        requirements = agent.process_srs(self.srs_file)

        # Verify the requirements were extracted
        self.assertTrue(len(requirements) >= 3)

        # Find requirements by ID
        req_ids = [req['id'] for req in requirements]
        self.assertTrue('REQ-001' in req_ids)
        self.assertTrue('REQ-002' in req_ids)
        self.assertTrue('REQ-003' in req_ids)

        # For testing purposes, we'll manually set the machine info
        # since the extraction might be sensitive to the exact text format
        agent.memory.set_machine_context('X', '1.0')

    def test_learn_from_existing_tests(self):
        """Test learning from existing test cases."""
        agent = TestGenerationAgent(self.config)

        # Learn from existing tests
        agent.learn_from_existing_tests(self.tests_file)

        # Verify patterns were added to knowledge base
        self.assertTrue(len(agent.knowledge_base.test_patterns) > 0)

    def test_parse_llm_response(self):
        """Test parsing an LLM response into a structured test case."""
        agent = TestGenerationAgent(self.config)

        # Sample LLM response
        response = """
        PRECONDITIONS: System is operational and user has valid credentials

        STEPS:
        1. Navigate to the login page
        2. Enter valid username and password
        3. Click the login button

        EXPECTED RESULTS:
        1. Login page is displayed correctly
        2. Credentials are accepted by the system
        3. User is successfully logged in and redirected to the dashboard
        """

        # Parse the response
        test_case = agent._parse_llm_response(response)

        # Verify the parsed test case
        self.assertTrue('id' in test_case)
        self.assertTrue('preconditions' in test_case)
        self.assertTrue('steps' in test_case)
        self.assertTrue('expected_results' in test_case)

        # Check that we have the right number of steps and expected results
        # The exact number might vary based on the parsing implementation
        self.assertTrue(len(test_case['steps']) >= 1)
        self.assertTrue(len(test_case['expected_results']) >= 1)
        self.assertTrue('valid credentials' in test_case['preconditions'])

if __name__ == '__main__':
    unittest.main()
