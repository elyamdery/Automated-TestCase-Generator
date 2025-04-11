"""
Test script for the updated mock agent.
"""

from mock_agent import MockTestGenerationAgent

def main():
    """Test the mock agent with the Easy Demo SRS document."""
    # Create the agent
    agent = MockTestGenerationAgent()
    
    # Read the SRS document
    print("Reading SRS document...")
    srs_data = agent.read_srs('data/easy_demo_srs.txt')
    
    # Print platform info
    print(f"\nPlatform info: {srs_data['platform_info']}")
    
    # Print requirements
    print(f"\nNumber of requirements: {len(srs_data['requirements'])}")
    print("\nFirst 3 requirements:")
    for i, req in enumerate(srs_data['requirements'][:3]):
        print(f"\nRequirement {i+1}:")
        for key, value in req.items():
            if key == 'description':
                print(f"  {key}: {value[:50]}...")  # Truncate long descriptions
            else:
                print(f"  {key}: {value}")
    
    # Generate test cases
    print("\nGenerating test cases...")
    platform_type = srs_data['platform_info']['type'] or 'E'  # Default to 'E' for Easy Demo
    version = srs_data['platform_info']['version'] or '2.0'  # Default to version 2.0
    
    # Mock patterns (normally learned from existing test cases)
    patterns = {
        'steps_per_requirement': 4,
        'common_steps': ['Navigate to screen', 'Enter data', 'Click button'],
        'common_expected': ['Screen loads', 'Data accepted', 'Action completes'],
        'step_format': '{action} {object}',
        'expected_format': '{object} {result}'
    }
    
    # Generate test cases
    test_cases = agent.generate_test_cases(
        srs_data['requirements'][:5],  # Use first 5 requirements
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

if __name__ == "__main__":
    main()
