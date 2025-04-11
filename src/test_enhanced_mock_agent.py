"""
Test script for the enhanced mock agent.
"""

import os
from mock_agent import MockTestGenerationAgent

def main():
    """Test the enhanced mock agent with the Easy Demo SRS document."""
    # Create the agent
    agent = MockTestGenerationAgent()
    
    # Read the SRS document
    print("Reading SRS document...")
    srs_data = agent.read_srs('data/easy_demo_srs.txt')
    
    # Print platform info
    print(f"\nPlatform info: {srs_data['platform_info']}")
    
    # Analyze requirements
    print("\nAnalyzing requirements...")
    requirements = agent.analyze_requirements(srs_data)
    
    # Print requirements
    print(f"\nNumber of requirements: {len(requirements)}")
    print("\nFirst 3 requirements:")
    for i, req in enumerate(requirements[:3]):
        print(f"\nRequirement {i+1}:")
        for key, value in req.items():
            if key == 'description':
                print(f"  {key}: {value[:50]}...")  # Truncate long descriptions
            else:
                print(f"  {key}: {value}")
    
    # Read existing test cases
    print("\nReading existing test cases...")
    existing_tests = agent.read_existing_tests('data/sample_tests.csv')
    
    # Learn patterns from existing test cases
    print("\nLearning patterns from existing test cases...")
    patterns = agent.learn_patterns(existing_tests)
    
    # Print learned patterns
    print("\nLearned patterns:")
    print(f"  Steps per requirement: {patterns['steps_per_requirement']}")
    print(f"  Step format: {patterns['step_format']}")
    print(f"  Expected format: {patterns['expected_format']}")
    
    # Print writing style
    print("\nWriting style:")
    for key, value in patterns.get('writing_style', {}).items():
        if isinstance(value, list) and len(value) > 5:
            print(f"  {key}: {value[:5]} (truncated)")
        else:
            print(f"  {key}: {value}")
    
    # Generate test cases
    print("\nGenerating test cases...")
    platform_type = srs_data['platform_info']['type'] or 'E'  # Default to 'E' for Easy Demo
    version = srs_data['platform_info']['version'] or '2.0'  # Default to version 2.0
    
    # Generate test cases
    test_cases = agent.generate_test_cases(
        requirements[:5],  # Use first 5 requirements
        patterns,
        platform_type,
        version
    )
    
    # Print test cases
    print(f"\nGenerated {len(test_cases)} test cases")
    print("\nFirst test case:")
    for key, value in test_cases[0].items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")
    
    print("\nSecond test case:")
    for key, value in test_cases[1].items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")
    
    # Save test cases to CSV
    output_path = 'output/enhanced_test_cases.csv'
    os.makedirs('output', exist_ok=True)
    
    print(f"\nSaving test cases to {output_path}...")
    output_data = agent.format_output(test_cases)
    
    # Write the CSV file
    agent.save_test_cases(output_data, output_path)
    
    print(f"\nTest cases saved to {output_path}")

if __name__ == "__main__":
    main()
