"""
Core Agent Implementation for Automated Test Case Generation.

This module contains the main TestGenerationAgent class that orchestrates
the entire test generation process.
"""

import logging
import os
import re
import pandas as pd
from typing import Dict, List, Optional, Any

# Import shared steps manager
from ..input.shared_steps import SharedStepsManager

# Import from other agent modules
from ..knowledge.base import KnowledgeRepository
from ..memory.context import AgentMemory
from ..reasoning.engine import ReasoningEngine
from ..input.document_parser import get_parser_for_file
from ..input.csv_parser import TestCaseParser

# Setup logging
logger = logging.getLogger(__name__)

class TestGenerationAgent:
    """
    Main agent class responsible for test case generation.

    This agent coordinates all aspects of the process:
    - SRS document processing
    - Existing test case analysis
    - LLM-powered test generation
    - Machine/version specific adaptations
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the test generation agent.

        Args:
            config: Configuration dictionary with LLM settings, paths, etc.
        """
        self.config = config
        logger.info("Initializing Test Generation Agent")

        # Initialize core components
        self.knowledge_base = self._initialize_knowledge()
        self.memory = self._initialize_memory()
        self.reasoning = self._initialize_reasoning()

        # Initialize shared steps manager
        shared_steps_dir = config.get('shared_steps_dir')
        self.shared_steps = SharedStepsManager(shared_steps_dir)

        # LLM client setup (will be initialized later)
        self.llm_client = None

        logger.info("Agent initialization complete")

    def _initialize_knowledge(self) -> KnowledgeRepository:
        """Initialize the knowledge repository."""
        logger.debug("Initializing knowledge repository")
        return KnowledgeRepository()

    def _initialize_memory(self) -> AgentMemory:
        """Initialize the agent memory system."""
        logger.debug("Initializing agent memory")
        return AgentMemory()

    def _initialize_reasoning(self) -> ReasoningEngine:
        """Initialize the reasoning engine."""
        logger.debug("Initializing reasoning engine")
        return ReasoningEngine()

    def setup_llm_client(self):
        """Set up the LLM client based on configuration."""
        provider = self.config.get("llm_provider", "openai")

        if provider == "openai":
            from openai import OpenAI
            self.llm_client = OpenAI(api_key=self.config.get("openai_api_key"))
        elif provider == "anthropic":
            from anthropic import Anthropic
            self.llm_client = Anthropic(api_key=self.config.get("anthropic_api_key"))
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        logger.info(f"LLM client set up for provider: {provider}")

    def process_srs(self, srs_path: str) -> List[Dict]:
        """
        Process an SRS document to extract requirements.

        Args:
            srs_path: Path to the SRS document

        Returns:
            List of extracted requirements
        """
        logger.info(f"Processing SRS document: {srs_path}")

        # Check if file exists
        if not os.path.exists(srs_path):
            logger.error(f"SRS file not found: {srs_path}")
            raise FileNotFoundError(f"SRS file not found: {srs_path}")

        # Get appropriate parser based on file extension
        parser = get_parser_for_file(srs_path)

        # Parse the document
        try:
            requirements = parser.parse(srs_path)
            logger.info(f"Extracted {len(requirements)} requirements from SRS")

            # Store in memory for context
            self.memory.store_requirements(requirements)

            # Set machine context in memory if available in requirements
            machine_info = self._extract_machine_info_from_requirements(requirements)
            if machine_info.get('machine_type') and machine_info.get('version'):
                self.memory.set_machine_context(
                    machine_info['machine_type'],
                    machine_info['version']
                )

            return requirements

        except Exception as e:
            logger.error(f"Error processing SRS document: {str(e)}")
            raise

    def _extract_machine_info_from_requirements(self, requirements: List[Dict]) -> Dict:
        """
        Extract machine type and version information from requirements if available.

        Args:
            requirements: List of requirement dictionaries

        Returns:
            Dictionary with machine_type and version if found
        """
        machine_info = {}

        # Look for machine type indicators in requirements
        machine_types = ['X', 'Y', 'Z']
        type_counts = {t: 0 for t in machine_types}

        for req in requirements:
            description = req.get('description', '').lower()

            # Check for machine type mentions
            for m_type in machine_types:
                if f"machine {m_type}" in description or f"type {m_type}" in description or f"Machine {m_type}" in description:
                    type_counts[m_type] += 1

            # Check for version mentions
            version_match = re.search(r'version\s+([\d\.]+)', description)
            if version_match and 'version' not in machine_info:
                machine_info['version'] = version_match.group(1)

        # Set machine type to the most frequently mentioned one
        if type_counts:
            most_common_type = max(type_counts.items(), key=lambda x: x[1])
            if most_common_type[1] > 0:  # Only if it was mentioned at least once
                machine_info['machine_type'] = most_common_type[0]

        return machine_info

    def learn_from_existing_tests(self, tests_path: str):
        """
        Analyze existing test cases to learn patterns.

        Args:
            tests_path: Path to CSV file with existing tests
        """
        logger.info(f"Learning from existing tests: {tests_path}")

        # Check if file exists
        if not os.path.exists(tests_path):
            logger.error(f"Test cases file not found: {tests_path}")
            raise FileNotFoundError(f"Test cases file not found: {tests_path}")

        # Parse the CSV file
        try:
            # Create parser
            parser = TestCaseParser()

            # Parse CSV
            test_df = parser.parse(tests_path)

            # Analyze structure
            structure = parser.analyze_structure(test_df)
            key_columns = structure['key_columns']

            # Analyze linguistic style
            style = parser.analyze_linguistic_style(test_df, key_columns)

            # Extract patterns
            patterns = parser.extract_patterns(test_df, key_columns)

            # Store patterns in knowledge base
            for pattern in patterns:
                # Add pattern to knowledge base
                self.knowledge_base.add_test_pattern(
                    pattern=pattern,
                    metadata={
                        'source': tests_path,
                        'linguistic_style': style
                    }
                )

                # Add examples to knowledge base for few-shot learning
                for example in pattern.get('examples', []):
                    # Determine tags for the example
                    tags = []

                    # Add machine type and version tags if available
                    machine_type = self.memory.short_term.get('current_machine')
                    version = self.memory.short_term.get('current_version')

                    if machine_type:
                        tags.append(machine_type)
                    if version:
                        tags.append(version)

                    # Add test type tags
                    for test_type in pattern.get('test_types', []):
                        tags.append(test_type)

                    # Add example to knowledge base
                    self.knowledge_base.add_example(example, tags)

            logger.info(f"Learned from {len(test_df)} test cases, extracted {len(patterns)} patterns")

        except Exception as e:
            logger.error(f"Error learning from test cases: {str(e)}")
            raise

        logger.info("Test pattern learning complete")

    def generate_test_cases(self,
                          requirements: List[Dict],
                          machine_type: str,
                          version: str) -> List[Dict]:
        """
        Generate test cases for the provided requirements.

        Args:
            requirements: List of requirement dictionaries
            machine_type: Target machine type (X, Y, Z)
            version: Target version

        Returns:
            List of generated test cases
        """
        logger.info(f"Generating test cases for {len(requirements)} requirements")
        logger.info(f"Target: Machine type {machine_type}, Version {version}")

        # Store machine type and version in memory for context
        self.memory.set_machine_context(machine_type, version)

        # Ensure LLM client is ready
        if not self.llm_client:
            self.setup_llm_client()

        generated_tests = []

        # Process each requirement
        for req in requirements:
            # Get relevant patterns from knowledge base
            patterns = self.knowledge_base.get_relevant_patterns(
                req, machine_type, version
            )

            # Use reasoning engine to plan test cases
            test_plan = self.reasoning.plan_test_cases(req, patterns)

            # Generate test cases using LLM
            for plan in test_plan:
                test_case = self._generate_single_test(req, plan, machine_type, version)
                generated_tests.append(test_case)

        logger.info(f"Generated {len(generated_tests)} test cases")
        return generated_tests

    def _generate_single_test(self,
                            requirement: Dict,
                            test_plan: Dict,
                            machine_type: str,
                            version: str) -> Dict:
        """
        Generate a single test case using the LLM.

        Args:
            requirement: The requirement to test
            test_plan: Plan for the test case
            machine_type: Target machine type
            version: Target version

        Returns:
            Generated test case
        """
        # Construct prompt with context
        prompt = self._build_test_generation_prompt(
            requirement, test_plan, machine_type, version
        )

        # Call LLM
        response = self._call_llm(prompt)

        # Parse response into structured test case
        test_case = self._parse_llm_response(response)

        # Add requirement ID to the test case
        test_case['requirement_id'] = requirement.get('id', 'Unknown')

        # Add machine type and version information
        test_case['machine_type'] = machine_type
        test_case['version'] = version

        # Add test type from the test plan
        test_case['test_type'] = test_plan.get('type', 'functional')

        return test_case

    def _build_test_generation_prompt(self,
                                     requirement: Dict,
                                     test_plan: Dict,
                                     machine_type: str,
                                     version: str) -> str:
        """Build the prompt for test case generation."""
        # This would be a sophisticated prompt engineering implementation
        # Would include few-shot examples from knowledge base

        # Placeholder implementation
        prompt = f"""
        Generate a detailed test case for the following requirement:

        Requirement ID: {requirement.get('id', 'Unknown')}
        Description: {requirement.get('description', '')}

        The test case should be for machine type {machine_type}, version {version}.

        Please format the test case with:
        1. Preconditions
        2. Test steps (numbered)
        3. Expected results for each step
        """

        # Add examples from knowledge base
        examples = self.knowledge_base.get_examples(requirement, machine_type, version)
        if examples:
            prompt += "\n\nHere are similar test cases for reference:\n\n"
            for example in examples:
                prompt += f"{example}\n\n"

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        # Implementation would depend on the LLM provider
        if not self.llm_client:
            self.setup_llm_client()

        # Get the provider from config
        provider = self.config.get("llm_provider", "openai")

        # Check if we're in demo mode (no API key)
        if self.config.get("openai_api_key") == "dummy_key" or self.config.get("anthropic_api_key") == "dummy_key":
            logger.info("Running in demo mode with mock LLM responses")
            return self._generate_mock_response(prompt)

        try:
            if provider == "openai":
                # Call OpenAI API
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",  # Use GPT-4 for better reasoning
                    messages=[
                        {"role": "system", "content": "You are an expert test engineer who specializes in writing detailed, professional manual test cases."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content

            elif provider == "anthropic":
                # Call Anthropic API
                response = self.llm_client.messages.create(
                    model="claude-2",
                    max_tokens=2000,
                    system="You are an expert test engineer who specializes in writing detailed, professional manual test cases.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text

            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        except Exception as e:
            logger.error(f"Error calling LLM API: {str(e)}")
            # Return a placeholder response for now
            return self._generate_mock_response(prompt)

    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response for demo purposes."""
        logger.info("Generating mock LLM response")

        # Extract requirement ID from prompt if available
        req_id_match = re.search(r'Requirement ID: ([\w-]+)', prompt)
        req_id = req_id_match.group(1) if req_id_match else "REQ-XXX"

        # Extract requirement description if available
        desc_match = re.search(r'Description: ([^\n]+)', prompt)
        description = desc_match.group(1) if desc_match else f"Requirement for {req_id}"

        # Extract machine type and version if available
        machine_match = re.search(r'machine type ([XYZ])', prompt)
        machine_type = machine_match.group(1) if machine_match else "X"

        version_match = re.search(r'version ([\d\.]+)', prompt)
        version = version_match.group(1) if version_match else "1.0"

        # Extract test type if available
        test_type_match = re.search(r'type: ([\w_]+)', prompt)
        test_type = test_type_match.group(1) if test_type_match else "happy_path"

        # Generate steps based on requirement ID and test type
        steps = []
        expected_results = []

        # Basic preconditions for all tests
        preconditions = f"""- System is operational
        - User has appropriate permissions
        - Machine type {machine_type} version {version} is available"""

        # Add specific preconditions based on requirement ID
        if "authentication" in description.lower() or "login" in description.lower():
            preconditions += "\n        - User credentials are available"

        if "database" in description.lower() or "data" in description.lower():
            preconditions += "\n        - Database connection is established"

        # Generate steps based on requirement ID and test type
        if test_type == "happy_path":
            # Basic happy path test

            # Determine if we should include a shared step
            # For login-related requirements, include the login shared step
            if "login" in description.lower() or "authentication" in description.lower():
                steps = [
                    "SHARED_STEP: SS-00001",  # Login shared step
                    f"Navigate to the section related to {req_id}",
                    f"Configure the test parameters for {machine_type} version {version}",
                    f"Execute the primary function described in {req_id}",
                    f"Verify the results match the expected outcome"
                ]

                expected_results = [
                    "Login successful",  # Single result for the shared step
                    "Navigation completes without errors",
                    "Test parameters are accepted",
                    "Function executes without errors",
                    "Results match the expected values for the requirement"
                ]
            else:
                steps = [
                    f"Launch the application for testing {req_id}",
                    f"Navigate to the section related to {req_id}",
                    f"Configure the test parameters for {machine_type} version {version}",
                    f"Execute the primary function described in {req_id}",
                    f"Verify the results match the expected outcome"
                ]

                expected_results = [
                    "Application launches successfully",
                    "Navigation completes without errors",
                    "Test parameters are accepted",
                    "Function executes without errors",
                    "Results match the expected values for the requirement"
                ]

        elif test_type == "boundary_conditions":
            # Boundary condition test
            steps = [
                f"Launch the application for testing {req_id}",
                f"Navigate to the section related to {req_id}",
                f"Configure the test with minimum allowed values",
                f"Execute the function and verify behavior",
                f"Reconfigure with maximum allowed values",
                f"Execute again and verify behavior"
            ]

            expected_results = [
                "Application launches successfully",
                "Navigation completes without errors",
                "Minimum values are accepted",
                "Function handles minimum values correctly",
                "Maximum values are accepted",
                "Function handles maximum values correctly"
            ]

        elif test_type == "error_cases":
            # Error handling test

            # For system status or monitoring requirements, include the status verification shared step
            if "status" in description.lower() or "monitoring" in description.lower() or "health" in description.lower():
                steps = [
                    "SHARED_STEP: SS-00002",  # System status verification
                    f"Navigate to the section related to {req_id}",
                    f"Attempt to execute with invalid input data",
                    f"Verify error handling behavior",
                    f"Attempt to execute with missing required data",
                    f"Verify error handling behavior"
                ]

                expected_results = [
                    "System status verified",  # Single result for the shared step
                    "Navigation completes without errors",
                    "System detects invalid input",
                    "Appropriate error message is displayed",
                    "System detects missing data",
                    "Appropriate error message is displayed"
                ]
            else:
                steps = [
                    f"Launch the application for testing {req_id}",
                    f"Navigate to the section related to {req_id}",
                    f"Attempt to execute with invalid input data",
                    f"Verify error handling behavior",
                    f"Attempt to execute with missing required data",
                    f"Verify error handling behavior"
                ]

                expected_results = [
                    "Application launches successfully",
                    "Navigation completes without errors",
                    "System detects invalid input",
                    "Appropriate error message is displayed",
                    "System detects missing data",
                    "Appropriate error message is displayed"
                ]

        else:
            # Default test case
            steps = [
                f"Launch the application for testing {req_id}",
                f"Navigate to the appropriate section",
                f"Execute the test function",
                f"Verify the results",
                f"Log the test outcome"
            ]

            expected_results = [
                "Application launches successfully",
                "Navigation completes without errors",
                "Function executes without errors",
                "Results are as expected",
                "Test outcome is logged successfully"
            ]

        # Format the steps and expected results
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        results_text = "\n".join([f"{i+1}. {result}" for i, result in enumerate(expected_results)])

        # Generate the complete response
        return f"""
        PRECONDITIONS:
{preconditions}

        STEPS:
{steps_text}

        EXPECTED RESULTS:
{results_text}
        """


    def _parse_llm_response(self, response: str) -> Dict:
        """Parse the LLM response into a structured test case."""
        logger.debug("Parsing LLM response into structured test case")

        # Get machine type and version from memory if available
        machine_type = self.memory.short_term.get('current_machine')
        version = self.memory.short_term.get('current_version')

        # Initialize the test case structure
        test_case = {
            "id": f"Generated-{self._generate_test_id(machine_type, version)}",
            "preconditions": "",
            "steps": [],
            "expected_results": []
        }

        try:
            # Look for preconditions section
            preconditions_match = re.search(
                r'(?i)(?:PRECONDITIONS?|PRE-CONDITIONS?|PREREQUISITES?)\s*:?\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)',
                response
            )
            if preconditions_match:
                test_case["preconditions"] = preconditions_match.group(1).strip()

            # Look for steps section
            steps = []
            steps_match = re.findall(
                r'(?i)(?:^|\n)\s*(\d+)\s*\.\s*([^\n]+)',
                response
            )
            if steps_match:
                for _, step_text in steps_match:
                    steps.append(step_text.strip())
                test_case["steps"] = steps

            # Look for expected results section
            results = []
            results_section = re.search(
                r'(?i)(?:EXPECTED RESULTS?|EXPECTED OUTCOMES?|EXPECTED BEHAVIOR)\s*:?\s*(.*?)(?:\n\s*$|\Z)',
                response,
                re.DOTALL
            )
            if results_section:
                results_text = results_section.group(1)
                # Try to find numbered results
                results_match = re.findall(
                    r'(?i)(?:^|\n)\s*(\d+)\s*\.\s*([^\n]+)',
                    results_text
                )
                if results_match:
                    for _, result_text in results_match:
                        results.append(result_text.strip())
                else:
                    # If no numbered results, split by newlines
                    results = [line.strip() for line in results_text.split('\n') if line.strip()]

                test_case["expected_results"] = results

            # If we couldn't parse steps or results, use a fallback approach
            if not test_case["steps"] or not test_case["expected_results"]:
                logger.warning("Using fallback parsing for LLM response")

                # Split the response into sections
                sections = re.split(r'\n\s*\n', response)

                for section in sections:
                    section_lower = section.lower()

                    # Check if this section contains steps
                    if "step" in section_lower and not test_case["steps"]:
                        steps = []
                        step_lines = [line.strip() for line in section.split('\n') if line.strip()]
                        for line in step_lines:
                            if re.match(r'^\d+\.', line):
                                steps.append(re.sub(r'^\d+\.\s*', '', line))
                        if steps:
                            test_case["steps"] = steps

                    # Check if this section contains expected results
                    elif ("expected" in section_lower or "result" in section_lower) and not test_case["expected_results"]:
                        results = []
                        result_lines = [line.strip() for line in section.split('\n') if line.strip()]
                        for line in result_lines:
                            if re.match(r'^\d+\.', line):
                                results.append(re.sub(r'^\d+\.\s*', '', line))
                            elif not line.lower().startswith("expected"):
                                results.append(line)
                        if results:
                            test_case["expected_results"] = results

            # Ensure we have the same number of expected results as steps
            if len(test_case["steps"]) > len(test_case["expected_results"]):
                # Pad with generic expected results
                for i in range(len(test_case["expected_results"]), len(test_case["steps"])):
                    test_case["expected_results"].append(f"Action completes successfully")

            logger.debug(f"Parsed test case with {len(test_case['steps'])} steps and {len(test_case['expected_results'])} expected results")
            return test_case

        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            # Return a basic structure if parsing fails
            return {
                "id": f"Generated-{self._generate_test_id(machine_type, version)}",
                "preconditions": "System is in operational state",
                "steps": ["Step 1: Perform the required action"],
                "expected_results": ["Action completes successfully"]
            }

    def _generate_test_id(self, machine_type: str = None, version: str = None) -> str:
        """Generate a unique test ID."""
        import uuid
        import time

        # Use timestamp and partial UUID for uniqueness
        timestamp = int(time.time())
        short_uuid = str(uuid.uuid4())[:8]

        # If machine type and version are provided, include them in the ID
        if machine_type and version:
            # Replace dots in version with underscores
            version_str = version.replace('.', '_')
            return f"{machine_type}_{timestamp}_{short_uuid}_{version_str}"
        else:
            return f"{timestamp}-{short_uuid}"

    def output_to_csv(self, test_cases: List[Dict], output_path: str):
        """
        Write generated test cases to CSV file in TFS format.

        Args:
            test_cases: List of test case dictionaries
            output_path: Path for output CSV file
        """
        logger.info(f"Writing {len(test_cases)} test cases to {output_path}")

        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Create a list to hold the TFS formatted rows
            tfs_rows = []

            # Process each test case
            for test_idx, test_case in enumerate(test_cases):
                # Extract test case information
                test_id = test_case.get('id', f'TC-{test_idx+1}')
                title = f"Test for {test_case.get('requirement_id', 'Unknown Requirement')}"

                # Add the test case header row
                tfs_rows.append({
                    'ID': test_id,
                    'Work Item type': 'Test case',
                    'Title': title,
                    'Test Step': '',
                    'Step Action': '',
                    'Step expected': ''
                })

                # Add preconditions as a note if present
                if test_case.get('preconditions'):
                    tfs_rows.append({
                        'ID': '',
                        'Work Item type': '',
                        'Title': '',
                        'Test Step': '',
                        'Step Action': f"PRECONDITIONS: {test_case['preconditions']}",
                        'Step expected': ''
                    })

                # Add each step with its action and expected result
                step_idx = 0
                for i, (step, expected) in enumerate(zip(
                    test_case.get('steps', []),
                    test_case.get('expected_results', [])
                )):
                    # Check if this is a reference to a shared step
                    if step.startswith('SHARED_STEP:'):
                        # Extract shared step ID
                        shared_step_id = step.replace('SHARED_STEP:', '').strip()

                        # Add shared step reference
                        step_idx += 1
                        tfs_rows.append({
                            'ID': '',
                            'Work Item type': '',
                            'Title': '',
                            'Test Step': step_idx,
                            'Step Action': f"Shared action {shared_step_id}",
                            'Step expected': expected
                        })
                    else:
                        # Regular step
                        step_idx += 1
                        tfs_rows.append({
                            'ID': '',
                            'Work Item type': '',
                            'Title': '',
                            'Test Step': step_idx,
                            'Step Action': step,
                            'Step expected': expected
                        })

            # Convert to DataFrame
            df = pd.DataFrame(tfs_rows)

            # Write to CSV
            df.to_csv(output_path, index=False)

            logger.info(f"Successfully wrote {len(test_cases)} test cases to {output_path} in TFS format")

        except Exception as e:
            logger.error(f"Error writing test cases to CSV: {str(e)}")
            raise

        logger.info("Test cases successfully written to CSV")