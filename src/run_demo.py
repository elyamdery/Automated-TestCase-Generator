"""
Demo script to run the test generation system with sample data.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Import the agent
from agent.core.agent import TestGenerationAgent

def configure_logging():
    """Configure logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('demo.log')
        ]
    )

def main():
    """Run the demo."""
    # Configure logging
    configure_logging()
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run a demo of the test generation system')
    parser.add_argument('--srs', type=str, default='data/sample_srs.txt', help='Path to the SRS document')
    parser.add_argument('--tests', type=str, default='data/sample_tests.csv', help='Path to existing test cases')
    parser.add_argument('--machine-type', type=str, default='X', choices=['X', 'Y', 'Z'], help='Target machine type')
    parser.add_argument('--version', type=str, default='1.0', help='Target version')
    parser.add_argument('--output', type=str, default='output/generated_tests.csv', help='Output file path')
    args = parser.parse_args()

    # Check if files exist
    if not os.path.exists(args.srs):
        logger.error(f"SRS file not found: {args.srs}")
        return 1

    if not os.path.exists(args.tests):
        logger.error(f"Test cases file not found: {args.tests}")
        return 1

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Create configuration
    config = {
        'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
        'openai_api_key': os.getenv('OPENAI_API_KEY', 'dummy_key'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', 'dummy_key'),
        'output_dir': os.path.dirname(args.output)
    }

    # Check if API key is available
    if config['llm_provider'] == 'openai' and not config['openai_api_key']:
        logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        # For demo purposes, we'll continue without making actual API calls

    if config['llm_provider'] == 'anthropic' and not config['anthropic_api_key']:
        logger.warning("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        # For demo purposes, we'll continue without making actual API calls

    try:
        # Create the agent
        logger.info("Initializing the test generation agent")
        agent = TestGenerationAgent(config)

        # Process the SRS
        logger.info(f"Processing SRS document: {args.srs}")
        requirements = agent.process_srs(args.srs)
        logger.info(f"Extracted {len(requirements)} requirements")

        # Learn from existing tests
        logger.info(f"Learning from existing tests: {args.tests}")
        agent.learn_from_existing_tests(args.tests)

        # Generate test cases
        logger.info(f"Generating test cases for machine {args.machine_type} version {args.version}")
        test_cases = agent.generate_test_cases(
            requirements,
            args.machine_type,
            args.version
        )

        # Output to CSV
        logger.info(f"Writing test cases to {args.output}")
        agent.output_to_csv(test_cases, args.output)

        # Print summary
        print("\nTest Generation Demo Summary:")
        print(f"  SRS Document: {args.srs}")
        print(f"  Existing Tests: {args.tests}")
        print(f"  Machine Type: {args.machine_type}")
        print(f"  Version: {args.version}")
        print(f"  Requirements Processed: {len(requirements)}")
        print(f"  Test Cases Generated: {len(test_cases)}")
        print(f"  Output File: {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error during demo: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
