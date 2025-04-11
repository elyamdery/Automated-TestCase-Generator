"""
Mock Test Generation Agent for demonstration purposes.

This module provides a mock implementation of the TestGenerationAgent
for use in the UI demonstration.
"""

import os
import re
import csv
import random
import logging
from typing import Dict, List, Any

# Setup logging
logger = logging.getLogger(__name__)

class MockTestGenerationAgent:
    """
    Mock Test Generation Agent for demonstration purposes.

    This class provides mock implementations of the methods
    needed by the UI for demonstration purposes.
    """

    def __init__(self, config=None):
        """
        Initialize the mock agent.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        logger.info("Mock Test Generation Agent initialized")

    def read_srs(self, srs_path: str) -> Dict:
        """
        Read an SRS document.

        Args:
            srs_path: Path to the SRS document

        Returns:
            Dictionary containing SRS data
        """
        logger.info(f"Reading SRS document: {srs_path}")

        # Read the SRS document with error handling for different encodings
        srs_content = ""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(srs_path, 'r', encoding=encoding) as f:
                    srs_content = f.read()
                logger.info(f"Successfully read SRS document with {encoding} encoding")
                break
            except UnicodeDecodeError:
                logger.warning(f"Failed to read SRS document with {encoding} encoding")
                continue

        if not srs_content:
            logger.error("Failed to read SRS document with any encoding")
            raise ValueError("Could not read SRS document with any supported encoding")

        # Extract requirements
        requirements = self._extract_requirements(srs_content)

        # Return SRS data
        return {
            'content': srs_content,
            'requirements': requirements,
            'platform_info': self._extract_platform_info(srs_content)
        }

    def read_existing_tests(self, tests_path: str) -> List[Dict]:
        """
        Read existing test cases and extract writing style and patterns.

        Args:
            tests_path: Path to the existing test cases

        Returns:
            List of test case dictionaries with enhanced metadata
        """
        logger.info(f"Reading existing test cases: {tests_path}")

        # Read the CSV file with error handling for different encodings
        existing_tests = []
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        success = False
        reader = None

        for encoding in encodings:
            try:
                with open(tests_path, 'r', newline='', encoding=encoding) as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    current_test_case = None
                    success = True
                    logger.info(f"Successfully read CSV file with {encoding} encoding")

                    # Process the CSV file
                    rows = list(reader)  # Read all rows into memory

                    for row in rows:
                        if len(row) > 0 and row[0]:  # New test case
                            if current_test_case:
                                existing_tests.append(current_test_case)

                            # Create a new test case with enhanced metadata
                            current_test_case = {
                                'id': row[0],
                                'type': row[1] if len(row) > 1 else 'Test case',
                                'title': row[2] if len(row) > 2 else '',
                                'requirement_id': '',  # Will extract from title or other fields
                                'platform_type': '',    # Will extract from title or other fields
                                'version': '',         # Will extract from title or other fields
                                'steps': [],
                                'expected_results': [],
                                'writing_style': {}    # Will be populated later
                            }

                            # Try to extract requirement ID, platform type, and version from the row
                            # Look for REQ-XXX pattern in any field
                            for field in row:
                                req_match = re.search(r'REQ-\d+', field)
                                if req_match:
                                    current_test_case['requirement_id'] = req_match.group(0)
                                    break

                            # Look for platform type (single letter) in specific positions
                            if len(row) > 2 and len(row[2]) == 1 and row[2].isalpha():
                                current_test_case['platform_type'] = row[2].upper()

                            # Look for version (X.Y format) in specific positions
                            for field in row:
                                version_match = re.search(r'\d+\.\d+', field)
                                if version_match:
                                    current_test_case['version'] = version_match.group(0)
                                    break

                        elif len(row) > 3 and row[3] and current_test_case:  # Test step
                            step_num = row[3]
                            step_action = row[4] if len(row) > 4 else ''
                            step_expected = row[5] if len(row) > 5 else ''

                            if step_action:  # Only add non-empty steps
                                current_test_case['steps'].append(step_action)
                                current_test_case['expected_results'].append(step_expected)

                    # Add the last test case
                    if current_test_case:
                        existing_tests.append(current_test_case)

                    # Extract writing style and patterns from the test cases
                    self._extract_writing_style(existing_tests)
                    break

            except UnicodeDecodeError:
                logger.warning(f"Failed to read CSV file with {encoding} encoding")
                continue
            except Exception as e:
                logger.error(f"Error processing CSV: {str(e)}")
                # Fallback to mock data
                existing_tests = self._get_mock_test_cases()
                # Extract writing style from mock test cases
                self._extract_writing_style(existing_tests)
        else:
            logger.error("Failed to read CSV file with any encoding")
            # Fallback to mock data
            existing_tests = self._get_mock_test_cases()
            # Extract writing style from mock test cases
            self._extract_writing_style(existing_tests)

        return existing_tests

    def analyze_requirements(self, srs_data: Dict) -> List[Dict]:
        """
        Analyze requirements from SRS data.

        Args:
            srs_data: SRS data dictionary

        Returns:
            List of requirement dictionaries
        """
        logger.info("Analyzing requirements")

        # Get platform information
        platform_info = srs_data.get('platform_info', {})

        # Analyze requirements in the context of the platform
        if platform_info.get('type') or platform_info.get('name'):
            return self.analyze_platform_requirements(srs_data['requirements'], platform_info)
        else:
            # Return the requirements from the SRS data without platform-specific analysis
            return srs_data['requirements']

    def analyze_platform_requirements(self, requirements: List[Dict], platform_info: Dict) -> List[Dict]:
        """
        Analyze requirements in the context of a specific platform.

        This method enhances requirements with platform-specific information
        and identifies which requirements are relevant to the platform.

        Args:
            requirements: List of requirement dictionaries
            platform_info: Platform information dictionary

        Returns:
            List of enhanced requirement dictionaries
        """
        platform_type = platform_info.get('type')
        platform_name = platform_info.get('name')
        platform_version = platform_info.get('version')

        logger.info(f"Analyzing requirements for platform {platform_name or platform_type} version {platform_version}")

        # Enhanced requirements list
        enhanced_requirements = []

        # Platform-specific keywords to look for in requirements
        platform_keywords = []
        if platform_type:
            platform_keywords.append(f"Platform {platform_type}")
            platform_keywords.append(f"Machine Type {platform_type}")
            platform_keywords.append(f"Type {platform_type}")
        if platform_name:
            platform_keywords.append(platform_name)
            # Add variations of the platform name
            name_parts = platform_name.split()
            if len(name_parts) > 1:
                platform_keywords.extend(name_parts)

        # Version-specific keywords
        version_keywords = []
        if platform_version:
            version_keywords.append(f"Version {platform_version}")
            version_keywords.append(f"v{platform_version}")
            # Extract major version (e.g., 2.0 -> 2)
            if '.' in platform_version:
                major_version = platform_version.split('.')[0]
                version_keywords.append(f"Version {major_version}")
                version_keywords.append(f"v{major_version}")

        # Process each requirement
        for req in requirements:
            # Create a copy of the requirement to enhance
            enhanced_req = req.copy()

            # Check if this requirement is platform-specific
            is_platform_specific = False
            for keyword in platform_keywords:
                if keyword.lower() in req.get('description', '').lower():
                    is_platform_specific = True
                    break

            # Check if this requirement is version-specific
            is_version_specific = False
            for keyword in version_keywords:
                if keyword.lower() in req.get('description', '').lower():
                    is_version_specific = True
                    break

            # Add platform-specific flags to the requirement
            enhanced_req['platform_specific'] = is_platform_specific
            enhanced_req['version_specific'] = is_version_specific
            enhanced_req['platform_type'] = platform_type
            enhanced_req['platform_name'] = platform_name
            enhanced_req['platform_version'] = platform_version

            # Add relevance score based on how well the requirement matches the platform
            relevance_score = 1.0  # Base relevance
            if is_platform_specific:
                relevance_score += 0.5  # Boost for platform-specific requirements
            if is_version_specific:
                relevance_score += 0.3  # Boost for version-specific requirements
            if req.get('technical', False):
                relevance_score += 0.2  # Boost for technical requirements

            enhanced_req['relevance_score'] = relevance_score

            # Add the enhanced requirement to the list
            enhanced_requirements.append(enhanced_req)

        # Sort requirements by relevance score (most relevant first)
        enhanced_requirements.sort(key=lambda r: r.get('relevance_score', 0), reverse=True)

        return enhanced_requirements

    def learn_patterns(self, existing_tests: List[Dict]) -> Dict:
        """
        Learn patterns from existing test cases.

        Args:
            existing_tests: List of existing test case dictionaries

        Returns:
            Dictionary of learned patterns
        """
        logger.info("Learning patterns from existing test cases")

        # Calculate average steps per test case
        total_steps = sum(len(tc.get('steps', [])) for tc in existing_tests)
        avg_steps = total_steps / len(existing_tests) if existing_tests else 3

        # Extract common step patterns
        common_steps = []
        for tc in existing_tests:
            for step in tc.get('steps', []):
                # Simplify step by removing specific details
                simplified_step = re.sub(r'\\b(the|a|an)\\b', '{article}', step, flags=re.IGNORECASE)
                simplified_step = re.sub(r'\\d+', '{number}', simplified_step)
                simplified_step = re.sub(r'\"[^\"]+\"', '{value}', simplified_step)

                if simplified_step not in common_steps:
                    common_steps.append(simplified_step)

        # Extract common expected result patterns
        common_expected = []
        for tc in existing_tests:
            for expected in tc.get('expected_results', []):
                # Simplify expected result by removing specific details
                simplified_expected = re.sub(r'\\b(the|a|an)\\b', '{article}', expected, flags=re.IGNORECASE)
                simplified_expected = re.sub(r'\\d+', '{number}', simplified_expected)
                simplified_expected = re.sub(r'\"[^\"]+\"', '{value}', simplified_expected)

                if simplified_expected not in common_expected:
                    common_expected.append(simplified_expected)

        # Extract writing style patterns
        writing_style = self._extract_global_writing_style(existing_tests)

        # Extract platform-specific patterns
        platform_patterns = self._extract_platform_patterns(existing_tests)

        # Return learned patterns with enhanced information
        return {
            'steps_per_requirement': round(avg_steps),
            'common_steps': common_steps[:10],  # Limit to 10 common steps
            'common_expected': common_expected[:10],  # Limit to 10 common expected results
            'step_format': writing_style.get('step_format', '{action} {object}'),
            'expected_format': writing_style.get('expected_format', '{object} {result}'),
            'writing_style': writing_style,
            'platform_patterns': platform_patterns
        }

    def generate_test_cases(self,
                           requirements: List[Dict],
                           patterns: Dict,
                           machine_type: str,
                           version: str) -> List[Dict]:
        """
        Generate test cases.

        Args:
            requirements: List of requirement dictionaries
            patterns: Dictionary of learned patterns
            machine_type: Machine type (A, B, Z, E for Easy Demo)
            version: Version (1.0, 2.0, 3.0)

        Returns:
            List of generated test case dictionaries
        """
        logger.info(f"Generating test cases for {machine_type} version {version}")

        # Generate test cases
        test_cases = []

        # Determine if this is the Easy Demo platform
        is_easy_demo = machine_type == 'E'
        platform_display_name = "Easy Demo" if is_easy_demo else f"Platform {machine_type}"

        # Create appropriate shared steps based on platform type
        shared_steps_id = f"{machine_type}_{version.replace('.', '_')}_SHARED_001"

        # Define shared steps based on platform type
        if is_easy_demo:
            shared_steps = {
                'id': shared_steps_id,
                'type': 'Shared steps',
                'title': f"Common Setup for {platform_display_name} v{version}",
                'steps': [
                    f"Power on the {platform_display_name} system and wait for boot sequence to complete",
                    "Log in with authorized technician credentials",
                    "Verify system status indicators show normal operation",
                    "Navigate to the main control panel"
                ],
                'expected_results': [
                    "System powers on and completes boot sequence without errors",
                    "Login is successful with appropriate authorization level",
                    "All system status indicators show green/normal status",
                    "Main control panel is displayed with all expected controls"
                ],
                'platform_type': machine_type,
                'version': version
            }
        else:
            # Standard shared steps for other platforms
            shared_steps = {
                'id': shared_steps_id,
                'type': 'Shared steps',
                'title': f"Common Setup for {platform_display_name} v{version}",
                'steps': [
                    f"Ensure the system is running {machine_type} version {version}",
                    "Verify user has appropriate permissions",
                    "Navigate to the main dashboard"
                ],
                'expected_results': [
                    "System is running the correct version",
                    "User permissions are confirmed",
                    "Main dashboard is displayed"
                ],
                'platform_type': machine_type,
                'version': version
            }

        test_cases.append(shared_steps)

        # Generate regular test cases
        for i, req in enumerate(requirements):
            # Generate a test case ID
            test_id = f"{machine_type}_{version.replace('.', '_')}_{i+1:03d}"

            # Generate a test case title
            # For technical requirements, create more specific titles
            is_technical = req.get('technical', False)
            if is_technical and is_easy_demo:
                title = f"Verify {req.get('feature', 'Feature')} {req.get('action', 'Action')} functionality"
            else:
                title = f"Test {req.get('feature', 'Feature')} - {req.get('action', 'Action')}"

            # Generate steps and expected results
            steps = []
            expected_results = []

            # Add preconditions
            if is_easy_demo:
                preconditions = f"{platform_display_name} system v{version} is powered on and operational. Technician is logged in with appropriate credentials."
            else:
                preconditions = f"System is running {machine_type} version {version}. User has appropriate permissions."

            # Number of steps for this test case - technical tests often have more steps
            base_steps = patterns.get('steps_per_requirement', 3)
            num_steps = base_steps + (2 if is_technical else 0)

            # Decide if we should use shared steps
            use_shared_steps = random.choice([True, False]) if i > 0 else False

            # Generate steps and expected results
            if use_shared_steps:
                # First step is a shared step
                steps.append(f"SHARED_STEP:{shared_steps_id}")
                expected_results.append("All shared steps complete successfully")

                # Adjust the number of remaining steps
                num_steps -= 1

            # Get writing style information from patterns
            writing_style = patterns.get('writing_style', {})
            platform_patterns = patterns.get('platform_patterns', {})

            # Get platform-specific patterns if available
            platform_specific_patterns = platform_patterns.get(machine_type, {})
            platform_terminology = platform_specific_patterns.get('terminology', {}).get('common_terms', [])

            # Generate the remaining steps based on requirement type
            if is_technical and is_easy_demo:
                # Technical test case steps for Easy Demo platform
                tech_steps = self._generate_technical_steps(req, num_steps, platform_display_name, writing_style, platform_terminology)
                steps.extend(tech_steps['steps'])
                expected_results.extend(tech_steps['expected_results'])
            else:
                # Standard test case steps with writing style applied
                for j in range(num_steps):
                    if j == 0:
                        # First step: Navigate to feature
                        if is_easy_demo:
                            # Apply writing style to step
                            if writing_style.get('step_starts_with_verb', True):
                                if writing_style.get('step_uses_articles', True):
                                    steps.append(f"Navigate to the {req.get('feature', 'Feature')} section in the control panel")
                                else:
                                    steps.append(f"Navigate to {req.get('feature', 'Feature')} section in control panel")
                            else:
                                steps.append(f"The {req.get('feature', 'Feature')} section in the control panel is navigated to")

                            # Apply writing style to expected result
                            if writing_style.get('expected_starts_with_object', True):
                                if writing_style.get('expected_uses_passive', True):
                                    expected_results.append(f"The {req.get('feature', 'Feature')} interface is displayed with all controls accessible")
                                else:
                                    expected_results.append(f"The {req.get('feature', 'Feature')} interface displays with all controls accessible")
                            else:
                                expected_results.append(f"All controls for the {req.get('feature', 'Feature')} interface are accessible")
                        else:
                            # Apply writing style to step
                            if writing_style.get('step_starts_with_verb', True):
                                if writing_style.get('step_uses_articles', True):
                                    steps.append(f"Navigate to the {req.get('feature', 'Feature')} screen")
                                else:
                                    steps.append(f"Navigate to {req.get('feature', 'Feature')} screen")
                            else:
                                steps.append(f"The {req.get('feature', 'Feature')} screen is navigated to")

                            # Apply writing style to expected result
                            if writing_style.get('expected_starts_with_object', True):
                                if writing_style.get('expected_uses_passive', True):
                                    expected_results.append(f"The {req.get('feature', 'Feature')} screen is loaded successfully")
                                else:
                                    expected_results.append(f"The {req.get('feature', 'Feature')} screen loads successfully")
                            else:
                                expected_results.append(f"Successfully loaded the {req.get('feature', 'Feature')} screen")
                    elif j == 1:
                        # Second step: Enter input
                        if is_easy_demo:
                            # Apply writing style to step
                            if writing_style.get('step_starts_with_verb', True):
                                if writing_style.get('step_uses_articles', True):
                                    steps.append(f"Configure the {req.get('input', 'Input')} according to test specifications")
                                else:
                                    steps.append(f"Configure {req.get('input', 'Input')} according to test specifications")
                            else:
                                steps.append(f"The {req.get('input', 'Input')} is configured according to test specifications")

                            # Apply writing style to expected result
                            if writing_style.get('expected_starts_with_object', True):
                                if writing_style.get('expected_uses_passive', True):
                                    expected_results.append(f"The {req.get('input', 'Input')} configuration is applied successfully")
                                else:
                                    expected_results.append(f"The {req.get('input', 'Input')} configuration applies successfully")
                            else:
                                expected_results.append(f"Successfully applied the {req.get('input', 'Input')} configuration")
                        else:
                            # Apply writing style to step
                            if writing_style.get('step_starts_with_verb', True):
                                if writing_style.get('step_uses_articles', True):
                                    steps.append(f"Enter the valid {req.get('input', 'Input')} data")
                                else:
                                    steps.append(f"Enter valid {req.get('input', 'Input')} data")
                            else:
                                steps.append(f"Valid {req.get('input', 'Input')} data is entered")

                            # Apply writing style to expected result
                            if writing_style.get('expected_starts_with_object', True):
                                if writing_style.get('expected_uses_passive', True):
                                    expected_results.append(f"The {req.get('input', 'Input')} data is accepted")
                                else:
                                    expected_results.append(f"The {req.get('input', 'Input')} data accepts")
                            else:
                                expected_results.append(f"Accepted the {req.get('input', 'Input')} data")
                    elif j == num_steps - 1:
                        # Last step: Perform action
                        if is_easy_demo:
                            # Apply writing style to step
                            if writing_style.get('step_starts_with_verb', True):
                                if writing_style.get('step_uses_articles', True):
                                    steps.append(f"Activate the {req.get('action', 'Action')} function and monitor system response")
                                else:
                                    steps.append(f"Activate {req.get('action', 'Action')} function and monitor system response")
                            else:
                                steps.append(f"The {req.get('action', 'Action')} function is activated and system response is monitored")

                            # Apply writing style to expected result
                            if writing_style.get('expected_starts_with_object', True):
                                if writing_style.get('expected_uses_passive', True):
                                    expected_results.append(f"The {req.get('action', 'Action')} function is executed correctly and system responds as expected")
                                else:
                                    expected_results.append(f"The {req.get('action', 'Action')} function executes correctly and system responds as expected")
                            else:
                                expected_results.append(f"Correctly executed the {req.get('action', 'Action')} function with expected system response")
                        else:
                            # Apply writing style to step
                            if writing_style.get('step_starts_with_verb', True):
                                if writing_style.get('step_uses_articles', True):
                                    steps.append(f"Click the {req.get('action', 'Action')} button")
                                else:
                                    steps.append(f"Click {req.get('action', 'Action')} button")
                            else:
                                steps.append(f"The {req.get('action', 'Action')} button is clicked")

                            # Apply writing style to expected result
                            if writing_style.get('expected_starts_with_object', True):
                                if writing_style.get('expected_uses_passive', True):
                                    expected_results.append(f"The {req.get('action', 'Action')} is completed successfully")
                                else:
                                    expected_results.append(f"The {req.get('action', 'Action')} completes successfully")
                            else:
                                expected_results.append(f"Successfully completed the {req.get('action', 'Action')}")
                    else:
                        # Middle steps: Random actions with platform-specific terminology
                        # Use common verbs from writing style if available
                        if writing_style.get('common_verbs'):
                            action_verbs = writing_style.get('common_verbs')
                        else:
                            if is_easy_demo:
                                action_verbs = ['Calibrate', 'Measure', 'Verify', 'Adjust', 'Monitor', 'Initialize', 'Configure']
                            else:
                                action_verbs = ['Select', 'Configure', 'Verify', 'Adjust', 'Check']

                        # Use platform-specific terminology if available
                        if platform_terminology:
                            # Filter for nouns that could be objects
                            objects = [term for term in platform_terminology if not self._is_verb(term)]
                            if not objects:  # Fallback if no suitable objects found
                                if is_easy_demo:
                                    objects = ['parameters', 'settings', 'sensor readings', 'system values', 'diagnostic data', 'control signals']
                                else:
                                    objects = ['settings', 'options', 'parameters', 'values', 'fields']
                        else:
                            if is_easy_demo:
                                objects = ['parameters', 'settings', 'sensor readings', 'system values', 'diagnostic data', 'control signals']
                            else:
                                objects = ['settings', 'options', 'parameters', 'values', 'fields']

                        action = random.choice(action_verbs)
                        obj = random.choice(objects)

                        # Apply writing style to step
                        if writing_style.get('step_starts_with_verb', True):
                            if writing_style.get('step_uses_articles', True):
                                steps.append(f"{action} the {obj} for {req.get('feature', 'Feature')}")
                            else:
                                steps.append(f"{action} {obj} for {req.get('feature', 'Feature')}")
                        else:
                            steps.append(f"The {obj} for {req.get('feature', 'Feature')} are {action.lower()}ed")

                        # Apply writing style to expected result
                        if writing_style.get('expected_starts_with_object', True):
                            if writing_style.get('expected_uses_passive', True):
                                expected_results.append(f"The {obj} are {action.lower()}ed correctly")
                            else:
                                expected_results.append(f"The {obj} {action.lower()} correctly")
                        else:
                            # Use common result phrases if available
                            if writing_style.get('common_result_phrases'):
                                result_phrase = random.choice(writing_style.get('common_result_phrases'))
                                expected_results.append(f"{action.capitalize()}ed the {obj} {result_phrase}")
                            else:
                                expected_results.append(f"Correctly {action.lower()}ed the {obj}")

            # Create the test case
            test_case = {
                'id': test_id,
                'type': 'Test case',
                'title': title,
                'preconditions': preconditions,
                'steps': steps,
                'expected_results': expected_results,
                'requirement_id': req.get('id', ''),
                'platform_type': machine_type,
                'version': version
            }

            # Add the test case to the list
            test_cases.append(test_case)

        return test_cases

    def format_output(self, test_cases: List[Dict]) -> List[List[str]]:
        """
        Format test cases for output.

        Args:
            test_cases: List of test case dictionaries

        Returns:
            List of CSV rows
        """
        logger.info("Formatting output")

        # Format test cases for CSV output
        output_rows = []

        # Add header row
        output_rows.append(['ID', 'Work Item type', 'Title', 'Test Step', 'Step Action', 'Step expected'])

        # Add test cases
        for tc in test_cases:
            # Add test case header row
            output_rows.append([
                tc.get('id', ''),
                tc.get('type', 'Test case'),
                tc.get('title', ''),
                '',
                '',
                ''
            ])

            # Add preconditions if present
            if tc.get('preconditions'):
                output_rows.append([
                    '',
                    '',
                    '',
                    '',
                    f"PRECONDITIONS: {tc.get('preconditions')}",
                    ''
                ])

            # Add steps
            for i, (step, expected) in enumerate(zip(tc.get('steps', []), tc.get('expected_results', []))):
                # Check if this is a shared step
                if step.startswith('SHARED_STEP:'):
                    shared_step_id = step.replace('SHARED_STEP:', '').strip()
                    output_rows.append([
                        '',
                        '',
                        '',
                        str(i + 1),
                        f"Shared action {shared_step_id}",
                        expected
                    ])
                else:
                    output_rows.append([
                        '',
                        '',
                        '',
                        str(i + 1),
                        step,
                        expected
                    ])

        return output_rows

    def save_test_cases(self, output_data: List[List[str]], output_path: str):
        """
        Save test cases to a file.

        Args:
            output_data: List of CSV rows
            output_path: Path to save the test cases
        """
        logger.info(f"Saving test cases to {output_path}")

        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Write the CSV file with error handling
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in output_data:
                    writer.writerow(row)
        except Exception as e:
            logger.error(f"Error writing CSV file: {str(e)}")
            # Try with a different encoding
            with open(output_path, 'w', newline='', encoding='cp1252') as f:
                writer = csv.writer(f)
                for row in output_data:
                    writer.writerow(row)

    def _extract_requirements(self, srs_content: str) -> List[Dict]:
        """
        Extract requirements from SRS content.

        Args:
            srs_content: SRS document content

        Returns:
            List of requirement dictionaries
        """
        # Enhanced parsing of requirements from the SRS content
        requirements = []

        # Look for REQ-XXX patterns with improved regex to handle technical documents
        req_pattern = re.compile(r'REQ-\\d+:?\\s*(.*?)\\s*(?=REQ-\\d+:|$|\\n\\s*\\n)', re.DOTALL)
        matches = req_pattern.findall(srs_content)

        # If no matches, try alternative patterns that might be used in technical documents
        if not matches:
            # Try to find requirements with different formats (e.g., "Requirement 1.2.3:")
            alt_pattern = re.compile(r'(?:Requirement|REQ)\\s+(?:\\d+\\.?)+:?\\s*(.*?)\\s*(?=(?:Requirement|REQ)\\s+(?:\\d+\\.?)+:|$|\\n\\s*\\n)', re.DOTALL)
            matches = alt_pattern.findall(srs_content)

        # If still no matches, create some mock requirements
        if not matches:
            # Create mock requirements based on common software features
            # Include more technical features for the Easy Demo platform
            features = ['Login', 'Configuration', 'Dashboard', 'Diagnostics', 'Settings', 'Calibration', 'Reports',
                       'Data Export', 'System Monitoring', 'User Management', 'Device Control', 'Sensor Readings']
            actions = ['initialize', 'configure', 'monitor', 'analyze', 'export', 'import', 'validate',
                      'calibrate', 'measure', 'control', 'adjust', 'optimize']
            inputs = ['parameters', 'configuration', 'sensor data', 'measurement values', 'system status',
                     'diagnostic information', 'calibration values', 'control signals']

            # Generate 5-10 mock requirements
            num_reqs = random.randint(5, 10)

            for i in range(num_reqs):
                feature = random.choice(features)
                action = random.choice(actions)
                input_type = random.choice(inputs)

                requirements.append({
                    'id': f'REQ-{i+1:03d}',
                    'feature': feature,
                    'action': action,
                    'input': input_type,
                    'description': f'The system shall allow users to {action} {feature} using {input_type}.',
                    'technical': True
                })
        else:
            # Process the matched requirements with improved parsing for technical content
            for i, req_text in enumerate(matches):
                # Extract requirement ID from the original text if possible
                req_id_match = re.search(r'REQ-(\\d+)', srs_content)
                req_id = f'REQ-{req_id_match.group(1)}' if req_id_match else f'REQ-{i+1:03d}'

                # Extract feature, action, and input from the requirement text with better handling
                # of technical terminology
                words = req_text.split()

                # Try to identify the main feature (usually a noun after "shall")
                feature_match = re.search(r'shall\\s+(?:be\\s+able\\s+to\\s+)?([a-z]+)\\s', req_text.lower())
                feature = feature_match.group(1) if feature_match else (words[2] if len(words) > 2 else 'Feature')

                # Try to identify the main action (usually a verb after the feature)
                action_match = re.search(r'shall\\s+(?:be\\s+able\\s+to\\s+)?[a-z]+\\s+([a-z]+)', req_text.lower())
                action = action_match.group(1) if action_match else (words[3] if len(words) > 3 else 'action')

                # Try to identify the input or object (usually follows the action)
                input_match = re.search(r'shall\\s+(?:be\\s+able\\s+to\\s+)?[a-z]+\\s+[a-z]+\\s+([a-z\\s]+)\\s+(?:to|for|with|using)', req_text.lower())
                input_type = input_match.group(1) if input_match else (words[5] if len(words) > 5 else 'input')

                # Check if this is a technical requirement
                technical_terms = ['calibrate', 'measure', 'sensor', 'diagnostic', 'parameter', 'configuration',
                                 'initialize', 'monitor', 'control', 'signal', 'data', 'value', 'system']
                is_technical = any(term in req_text.lower() for term in technical_terms)

                requirements.append({
                    'id': req_id,
                    'feature': feature.strip(),
                    'action': action.strip(),
                    'input': input_type.strip(),
                    'description': req_text.strip(),
                    'technical': is_technical
                })

        return requirements

    def _extract_platform_info(self, srs_content: str) -> Dict:
        """
        Extract platform information from SRS content.

        Args:
            srs_content: SRS document content

        Returns:
            Dictionary containing platform information
        """
        # Look for platform type and version in the SRS content
        platform_type = None
        version = None
        platform_name = None

        # Look for "Platform Type X" or similar
        platform_match = re.search(r'Platform\s+Type\s+([A-Z])', srs_content)
        if platform_match:
            platform_type = platform_match.group(1)

        # Look for "Easy Demo" platform
        easy_demo_match = re.search(r'Easy\s+Demo', srs_content, re.IGNORECASE)
        if easy_demo_match:
            platform_type = 'E'  # Assign 'E' for Easy Demo platform
            platform_name = 'Easy Demo'

        # Look for other platform names
        platform_name_match = re.search(r'(?:Platform|System)\s+(?:Type\s+)?([A-Za-z\s]+)(?:,|\n|\r)', srs_content)
        if platform_name_match and not platform_name:
            extracted_name = platform_name_match.group(1).strip()
            if extracted_name not in ['A', 'B', 'Z', 'X', 'Y']:
                platform_name = extracted_name

        # Look for "Version X.Y" or similar
        version_match = re.search(r'Version\s+(\d+\.\d+)', srs_content)
        if version_match:
            version = version_match.group(1)

        # If no version found, try alternative formats
        if not version:
            alt_version_match = re.search(r'[Vv](?:\.|ersion)\s*(\d+(?:\.\d+)?)', srs_content)
            if alt_version_match:
                version = alt_version_match.group(1)
                # Add .0 if only major version is specified
                if '.' not in version:
                    version = f"{version}.0"

        return {
            'type': platform_type,
            'version': version,
            'name': platform_name
        }

    def _generate_technical_steps(self, req: Dict, num_steps: int, platform_name: str, writing_style: Dict = None, platform_terminology: List[str] = None) -> Dict:
        """
        Generate technical test steps for a requirement.

        Args:
            req: Requirement dictionary
            num_steps: Number of steps to generate
            platform_name: Name of the platform

        Returns:
            Dictionary with steps and expected results
        """
        steps = []
        expected_results = []

        # Extract requirement details
        feature = req.get('feature', 'Feature')
        action = req.get('action', 'Action')
        input_type = req.get('input', 'Input')

        # Get writing style preferences
        if writing_style is None:
            writing_style = {}

        # Use platform-specific terminology if available
        if platform_terminology is None:
            platform_terminology = []

        # Determine step and expected result formats based on writing style
        uses_articles = writing_style.get('step_uses_articles', True)
        starts_with_verb = writing_style.get('step_starts_with_verb', True)
        expected_starts_with_object = writing_style.get('expected_starts_with_object', True)
        expected_uses_passive = writing_style.get('expected_uses_passive', True)

        # Technical test steps are more specific and detailed
        if num_steps >= 1:
            # First step: System preparation
            if starts_with_verb:
                if uses_articles:
                    steps.append(f"Access the {feature} module from the main control panel")
                else:
                    steps.append(f"Access {feature} module from main control panel")
            else:
                steps.append(f"The {feature} module is accessed from the main control panel")

            if expected_starts_with_object:
                if expected_uses_passive:
                    expected_results.append(f"The {feature} module interface is displayed with all controls and indicators visible")
                else:
                    expected_results.append(f"The {feature} module interface displays with all controls and indicators visible")
            else:
                expected_results.append(f"All controls and indicators for the {feature} module interface are visible")

        if num_steps >= 2:
            # Second step: Initial verification
            if starts_with_verb:
                if uses_articles:
                    steps.append(f"Verify the current {feature} status and configuration parameters")
                else:
                    steps.append(f"Verify current {feature} status and configuration parameters")
            else:
                steps.append(f"The current {feature} status and configuration parameters are verified")

            if expected_starts_with_object:
                if expected_uses_passive:
                    expected_results.append(f"All {feature} status indicators are showing normal operation and configuration parameters match expected values")
                else:
                    expected_results.append(f"All {feature} status indicators show normal operation and configuration parameters match expected values")
            else:
                expected_results.append(f"Normal operation is confirmed by all {feature} status indicators and configuration parameters match expected values")

        if num_steps >= 3:
            # Third step: Test setup
            if starts_with_verb:
                if uses_articles:
                    steps.append(f"Configure the {input_type} parameters according to the test specification document")
                else:
                    steps.append(f"Configure {input_type} parameters according to test specification document")
            else:
                steps.append(f"The {input_type} parameters are configured according to the test specification document")

            if expected_starts_with_object:
                if expected_uses_passive:
                    expected_results.append(f"The {input_type} parameters are successfully configured and saved")
                else:
                    expected_results.append(f"The {input_type} parameters configure successfully and save")
            else:
                expected_results.append(f"Successfully configured and saved the {input_type} parameters")

        if num_steps >= 4:
            # Fourth step: Calibration or preparation
            if starts_with_verb:
                if uses_articles:
                    steps.append(f"Perform the system calibration for the {feature} module")
                else:
                    steps.append(f"Perform system calibration for {feature} module")
            else:
                steps.append(f"The system calibration for the {feature} module is performed")

            if expected_starts_with_object:
                if expected_uses_passive:
                    expected_results.append(f"Calibration is completed successfully with all values within acceptable ranges")
                else:
                    expected_results.append(f"Calibration completes successfully with all values within acceptable ranges")
            else:
                expected_results.append(f"Successfully completed calibration with all values within acceptable ranges")

        if num_steps >= 5:
            # Fifth step: Main action
            if starts_with_verb:
                if uses_articles:
                    steps.append(f"Initiate the {action} operation and monitor the system response")
                else:
                    steps.append(f"Initiate {action} operation and monitor system response")
            else:
                steps.append(f"The {action} operation is initiated and the system response is monitored")

            if expected_starts_with_object:
                if expected_uses_passive:
                    expected_results.append(f"The {action} operation is executed without errors and the system responds as expected")
                else:
                    expected_results.append(f"The {action} operation executes without errors and the system responds as expected")
            else:
                expected_results.append(f"Executed the {action} operation without errors and observed expected system response")

        # Add additional steps if needed
        for i in range(5, num_steps):
            # Technical actions and objects
            # Use common verbs from writing style if available
            if writing_style.get('common_verbs'):
                tech_actions = writing_style.get('common_verbs')
            else:
                tech_actions = ['Measure', 'Calibrate', 'Validate', 'Monitor', 'Analyze', 'Record', 'Verify']

            # Use platform-specific terminology if available
            if platform_terminology:
                tech_objects = [term for term in platform_terminology if not self._is_verb(term) and len(term) > 3]
                if not tech_objects:  # Fallback if no suitable objects found
                    tech_objects = ['sensor readings', 'system parameters', 'diagnostic data', 'performance metrics',
                                  'error logs', 'configuration values', 'control signals']
            else:
                tech_objects = ['sensor readings', 'system parameters', 'diagnostic data', 'performance metrics',
                               'error logs', 'configuration values', 'control signals']

            action_verb = random.choice(tech_actions)
            obj = random.choice(tech_objects)

            # Apply writing style to step
            if starts_with_verb:
                if uses_articles:
                    steps.append(f"{action_verb} the {obj} during the {feature} {action} operation")
                else:
                    steps.append(f"{action_verb} {obj} during {feature} {action} operation")
            else:
                steps.append(f"The {obj} are {action_verb.lower()}ed during the {feature} {action} operation")

            # Apply writing style to expected result
            if expected_starts_with_object:
                if expected_uses_passive:
                    expected_results.append(f"The {obj} are within specified operational parameters")
                else:
                    expected_results.append(f"The {obj} fall within specified operational parameters")
            else:
                # Use common result phrases if available
                if writing_style.get('common_result_phrases'):
                    result_phrase = random.choice(writing_style.get('common_result_phrases'))
                    expected_results.append(f"Verified that the {obj} are {result_phrase} within specified operational parameters")
                else:
                    expected_results.append(f"Specified operational parameters are maintained for the {obj}")

        return {
            'steps': steps,
            'expected_results': expected_results
        }

    def _extract_writing_style(self, test_cases: List[Dict]) -> None:
        """
        Extract writing style and patterns from test cases.

        This method analyzes the test cases to identify common patterns,
        terminology, and writing style to use when generating new test cases.

        Args:
            test_cases: List of test case dictionaries
        """
        if not test_cases:
            return

        # Analyze step structure and writing style
        for tc in test_cases:
            writing_style = {}

            # Analyze steps
            if tc.get('steps'):
                steps = tc.get('steps', [])

                # Check for common patterns in steps
                writing_style['step_starts_with_verb'] = all(self._starts_with_verb(step) for step in steps if step)
                writing_style['step_avg_length'] = sum(len(step.split()) for step in steps if step) / len(steps) if steps else 0
                writing_style['step_uses_articles'] = any(re.search(r'\b(the|a|an)\b', step, re.IGNORECASE) for step in steps if step)

                # Extract common verbs used in steps
                verbs = []
                for step in steps:
                    if step:
                        words = step.split()
                        if words and self._is_verb(words[0]):
                            verbs.append(words[0].lower())
                writing_style['common_verbs'] = list(set(verbs))

                # Check for numbering in steps
                writing_style['uses_numbered_steps'] = any(re.match(r'^\d+\.', step) for step in steps if step)

            # Analyze expected results
            if tc.get('expected_results'):
                expected = tc.get('expected_results', [])

                # Check for common patterns in expected results
                writing_style['expected_starts_with_object'] = all(self._starts_with_object(result) for result in expected if result)
                writing_style['expected_avg_length'] = sum(len(result.split()) for result in expected if result) / len(expected) if expected else 0
                writing_style['expected_uses_passive'] = any(re.search(r'\b(is|are|was|were)\b', result, re.IGNORECASE) for result in expected if result)

                # Extract common result phrases
                result_phrases = []
                for result in expected:
                    if result:
                        # Look for phrases like "successfully", "correctly", "as expected"
                        if re.search(r'\b(successfully|correctly|as expected|properly|without error)\b', result, re.IGNORECASE):
                            matches = re.findall(r'\b(successfully|correctly|as expected|properly|without error)\b', result, re.IGNORECASE)
                            result_phrases.extend(matches)
                writing_style['common_result_phrases'] = list(set(result_phrases))

            # Store the writing style in the test case
            tc['writing_style'] = writing_style

    def _starts_with_verb(self, text: str) -> bool:
        """
        Check if a text starts with a verb.

        Args:
            text: Text to check

        Returns:
            True if the text starts with a verb, False otherwise
        """
        if not text:
            return False

        # Common verbs used in test steps
        common_verbs = [
            'verify', 'check', 'ensure', 'confirm', 'validate',
            'click', 'select', 'choose', 'pick',
            'enter', 'input', 'type', 'fill',
            'navigate', 'go', 'browse', 'open',
            'launch', 'start', 'begin', 'initiate',
            'save', 'store', 'record', 'log',
            'generate', 'create', 'make', 'produce',
            'configure', 'set', 'adjust', 'modify',
            'prepare', 'ready', 'setup', 'initialize'
        ]

        first_word = text.split()[0].lower().rstrip(',.:;')
        return first_word in common_verbs or first_word.endswith(('e', 'es', 'ed', 'ing'))

    def _starts_with_object(self, text: str) -> bool:
        """
        Check if a text starts with an object (noun or article).

        Args:
            text: Text to check

        Returns:
            True if the text starts with an object, False otherwise
        """
        if not text:
            return False

        # Common articles and demonstratives
        articles = ['the', 'a', 'an', 'this', 'that', 'these', 'those']

        first_word = text.split()[0].lower().rstrip(',.:;')
        return first_word in articles or not self._is_verb(first_word)

    def _is_verb(self, word: str) -> bool:
        """
        Check if a word is likely a verb.

        Args:
            word: Word to check

        Returns:
            True if the word is likely a verb, False otherwise
        """
        # Common verbs used in test steps
        common_verbs = [
            'verify', 'check', 'ensure', 'confirm', 'validate',
            'click', 'select', 'choose', 'pick',
            'enter', 'input', 'type', 'fill',
            'navigate', 'go', 'browse', 'open',
            'launch', 'start', 'begin', 'initiate',
            'save', 'store', 'record', 'log',
            'generate', 'create', 'make', 'produce',
            'configure', 'set', 'adjust', 'modify',
            'prepare', 'ready', 'setup', 'initialize'
        ]

        word = word.lower().rstrip(',.:;')
        return word in common_verbs or word.endswith(('e', 'es', 'ed', 'ing'))

    def _extract_global_writing_style(self, test_cases: List[Dict]) -> Dict:
        """
        Extract global writing style patterns from all test cases.

        Args:
            test_cases: List of test case dictionaries

        Returns:
            Dictionary of global writing style patterns
        """
        if not test_cases:
            return {}

        # Collect writing style data from all test cases
        all_styles = [tc.get('writing_style', {}) for tc in test_cases if tc.get('writing_style')]
        if not all_styles:
            return {}

        # Determine dominant writing style patterns
        global_style = {}

        # Determine if steps typically start with verbs
        verb_starts = [style.get('step_starts_with_verb', False) for style in all_styles if 'step_starts_with_verb' in style]
        global_style['step_starts_with_verb'] = sum(verb_starts) > len(verb_starts) / 2 if verb_starts else True

        # Determine if steps typically use articles
        uses_articles = [style.get('step_uses_articles', False) for style in all_styles if 'step_uses_articles' in style]
        global_style['step_uses_articles'] = sum(uses_articles) > len(uses_articles) / 2 if uses_articles else True

        # Determine if expected results typically start with objects
        obj_starts = [style.get('expected_starts_with_object', False) for style in all_styles if 'expected_starts_with_object' in style]
        global_style['expected_starts_with_object'] = sum(obj_starts) > len(obj_starts) / 2 if obj_starts else True

        # Determine if expected results typically use passive voice
        uses_passive = [style.get('expected_uses_passive', False) for style in all_styles if 'expected_uses_passive' in style]
        global_style['expected_uses_passive'] = sum(uses_passive) > len(uses_passive) / 2 if uses_passive else True

        # Collect common verbs from all test cases
        all_verbs = []
        for style in all_styles:
            all_verbs.extend(style.get('common_verbs', []))
        global_style['common_verbs'] = list(set(all_verbs))

        # Collect common result phrases from all test cases
        all_phrases = []
        for style in all_styles:
            all_phrases.extend(style.get('common_result_phrases', []))
        global_style['common_result_phrases'] = list(set(all_phrases))

        # Determine step format based on writing style
        if global_style.get('step_starts_with_verb', True):
            if global_style.get('step_uses_articles', True):
                global_style['step_format'] = '{verb} the {object}'
            else:
                global_style['step_format'] = '{verb} {object}'
        else:
            global_style['step_format'] = '{object} {verb}'

        # Determine expected result format based on writing style
        if global_style.get('expected_starts_with_object', True):
            if global_style.get('expected_uses_passive', True):
                global_style['expected_format'] = 'The {object} is {result}'
            else:
                global_style['expected_format'] = '{object} {result}'
        else:
            global_style['expected_format'] = '{result} {object}'

        return global_style

    def _extract_platform_patterns(self, test_cases: List[Dict]) -> Dict:
        """
        Extract platform-specific patterns from test cases.

        Args:
            test_cases: List of test case dictionaries

        Returns:
            Dictionary of platform-specific patterns
        """
        if not test_cases:
            return {}

        # Group test cases by platform type
        platform_groups = {}
        for tc in test_cases:
            platform = tc.get('platform_type')
            if platform:
                if platform not in platform_groups:
                    platform_groups[platform] = []
                platform_groups[platform].append(tc)

        # Extract patterns for each platform
        platform_patterns = {}
        for platform, cases in platform_groups.items():
            # Extract common terminology for this platform
            platform_terms = self._extract_platform_terminology(cases)

            # Extract common step patterns for this platform
            platform_steps = []
            for tc in cases:
                for step in tc.get('steps', []):
                    # Simplify and generalize the step
                    simplified_step = re.sub(r'\b(the|a|an)\b', '{article}', step, flags=re.IGNORECASE)
                    simplified_step = re.sub(r'\d+', '{number}', simplified_step)
                    simplified_step = re.sub(r'"[^"]+"', '{value}', simplified_step)

                    if simplified_step not in platform_steps:
                        platform_steps.append(simplified_step)

            # Store patterns for this platform
            platform_patterns[platform] = {
                'terminology': platform_terms,
                'common_steps': platform_steps[:5]  # Limit to 5 common steps
            }

        return platform_patterns

    def _extract_platform_terminology(self, test_cases: List[Dict]) -> Dict:
        """
        Extract platform-specific terminology from test cases.

        Args:
            test_cases: List of test case dictionaries

        Returns:
            Dictionary of platform-specific terminology
        """
        if not test_cases:
            return {}

        # Extract all words from steps and expected results
        all_words = []
        for tc in test_cases:
            for step in tc.get('steps', []):
                all_words.extend(step.lower().split())
            for expected in tc.get('expected_results', []):
                all_words.extend(expected.lower().split())

        # Count word frequencies
        word_counts = {}
        for word in all_words:
            # Clean the word (remove punctuation)
            word = word.strip(',.;:()"')
            if word and len(word) > 3:  # Ignore short words and empty strings
                if word not in word_counts:
                    word_counts[word] = 0
                word_counts[word] += 1

        # Find common nouns (potential domain-specific terms)
        common_terms = []
        for word, count in word_counts.items():
            if count >= 3 and not self._is_verb(word) and not self._is_common_word(word):
                common_terms.append(word)

        return {
            'common_terms': common_terms[:10]  # Limit to 10 common terms
        }

    def _is_common_word(self, word: str) -> bool:
        """
        Check if a word is a common English word (not domain-specific).

        Args:
            word: Word to check

        Returns:
            True if the word is a common word, False otherwise
        """
        common_words = [
            'this', 'that', 'these', 'those', 'with', 'from', 'into', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'over',
            'should', 'would', 'could', 'must', 'have', 'has', 'had',
            'system', 'user', 'data', 'file', 'page', 'screen', 'button', 'field',
            'value', 'option', 'result', 'process', 'function', 'feature'
        ]

        return word.lower() in common_words

    def _get_mock_test_cases(self) -> List[Dict]:
        """
        Get mock test cases for fallback.

        Returns:
            List of mock test case dictionaries
        """
        return [
            {
                'id': 'TC-001',
                'type': 'Test case',
                'title': 'Test Login Functionality',
                'steps': [
                    'Navigate to login page',
                    'Enter valid credentials',
                    'Click login button'
                ],
                'expected_results': [
                    'Login page loads successfully',
                    'Credentials are accepted',
                    'User is logged in successfully'
                ]
            },
            {
                'id': 'TC-002',
                'type': 'Test case',
                'title': 'Test Registration Process',
                'steps': [
                    'Navigate to registration page',
                    'Enter valid user information',
                    'Accept terms and conditions',
                    'Click register button'
                ],
                'expected_results': [
                    'Registration page loads successfully',
                    'User information is accepted',
                    'Terms and conditions are accepted',
                    'Registration completes successfully'
                ]
            }
        ]
