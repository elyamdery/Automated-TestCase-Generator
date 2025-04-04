"""
Main Entry Point for the Automated Test Case Generation System.

This module provides the command-line interface and orchestrates 
the entire test generation process.
"""

import argparse
import logging
import os
import sys
import json
from typing import Dict
from dotenv import load_dotenv

# Import the agent components
from agent.core.agent import TestGenerationAgent

def configure_logging(verbose: bool = False):
    """Configure the logging system."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_generation.log')
        ]
    )

def load_config(config_path: str = None) -> Dict:
    """
    Load configuration from file and environment variables.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Configuration dictionary
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Default config
    config = {
        'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'output_dir': os.getenv('OUTPUT_DIR', 'output')
    }
    
    # Load config from file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    return config

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate test cases from SRS documents'
    )
    
    parser.add_argument(
        '--srs',
        type=str,
        required=True,
        help='Path to the SRS document'
    )
    
    parser.add_argument(
        '--tests',
        type=str,
        required=True,
        help='Path to existing test cases CSV'
    )
    
    parser.add_argument(
        '--machine-type',
        type=str,
        required=True,
        choices=['X', 'Y', 'Z'],
        help='Target machine type (X, Y, Z)'
    )
    
    parser.add_argument(
        '--version',
        type=str,
        required=True,
        help='Target version'
    )
    
    parser.add_argument(
        '--output-path',
        type=str,
        help='Path for output CSV file'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_args()
    
    # Configure logging
    configure_logging(args.verbose)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Starting Automated Test Case Generation")
    
    # Load configuration
    config = load_config(args.config)
    
    # Create the test generation agent
    agent = TestGenerationAgent(config)
    
    try:
        # Process the SRS document
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
        
        # Determine output path
        output_path = args.output_path
        if not output_path:
            # Create a default output path based on input file and machine type
            srs_name = os.path.splitext(os.path.basename(args.srs))[0]
            output_dir = config.get('output_dir', 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(
                output_dir, 
                f"{srs_name}_{args.machine_type}_v{args.version}.csv"
            )
        
        # Write test cases to CSV
        logger.info(f"Writing test cases to {output_path}")
        agent.output_to_csv(test_cases, output_path)
        
        logger.info("Test case generation completed successfully")
        
        # Print summary to console
        print(f"\nTest Case Generation Summary:")
        print(f"  SRS Document: {args.srs}")
        print(f"  Machine Type: {args.machine_type}")
        print(f"  Version: {args.version}")
        print(f"  Requirements Processed: {len(requirements)}")
        print(f"  Test Cases Generated: {len(test_cases)}")
        print(f"  Output File: {output_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during test generation: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 