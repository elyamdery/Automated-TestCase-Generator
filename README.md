# Automated Manual Test Case Generator

## Overview

This project develops an AI-powered system that automatically generates professional manual test cases from Software Requirements Specifications (SRS). The system leverages existing test cases to learn format, style, and language patterns, then applies this learning to generate new test cases for functionalities outlined in new SRS documents.

### Key Features

- Automatic parsing of SRS documents in various formats (.docx, .pdf, text)
- Learning from existing test cases (CSV format)
- Test case generation tailored to specific platform types and versions
- Structured output in CSV format compatible with TFS/Azure DevOps
- User-friendly interface for configuration and operation
- Secure local processing with no data transmission
- Enhanced SRS analysis for technical documents
- Platform-aware test generation with specialized terminology
- Template-based writing style matching existing test cases

### New Feature: Enhanced SRS Analysis and Test Case Generation

The latest update includes significant improvements to the SRS analysis and test case generation capabilities:

1. **Improved SRS Document Analysis**:
   - Better extraction of requirements from technical documents
   - Enhanced detection of platform-specific requirements
   - Improved parsing of requirement details (features, actions, inputs)

2. **Platform-Aware Test Generation**:
   - Test cases are now generated with awareness of both platform information and SRS content
   - Platform-specific terminology is incorporated into test steps
   - Requirements are prioritized based on relevance to the selected platform

3. **Template-Based Writing Style**:
   - Test cases now follow the writing style of existing tests
   - Consistent formatting of steps and expected results
   - Adoption of domain-specific terminology from existing tests

## AI Agent Architecture

### Central Intelligence Component

The AI agent serves as the central "brain" that coordinates all aspects of the test generation process. It consists of:

1. **Knowledge Integration Layer**
   - Combines domain-specific knowledge about platform types
   - Maintains context awareness across different system versions
   - Builds cumulative understanding of test case patterns and requirements

2. **Decision Engine**
   - Determines which requirements need test coverage
   - Selects appropriate test patterns based on requirement type
   - Prioritizes test case generation based on complexity and criticality

3. **Orchestration System**
   - Coordinates the flow between input processing, analysis, and output generation
   - Manages API interactions with the LLM provider
   - Handles recovery from failures and unexpected inputs

### Agent Integration Strategy

The agent is implemented using a modular architecture with these key components:

1. **Agent Core** (`src/agent/core.py`)
   - Central controller that maintains state and context
   - Implements the primary decision-making logic
   - Manages the prompt engineering process

2. **Knowledge Repository** (`src/agent/knowledge/`)
   - Stores learned patterns from existing test cases
   - Contains machine-specific information and constraints
   - Maintains version-specific variations and requirements

3. **Agent Memory** (`src/agent/memory/`)
   - Implements short and long-term memory mechanisms
   - Tracks session context during generation
   - Stores feedback for continuous improvement

4. **Reasoning Module** (`src/agent/reasoning/`)
   - Implements advanced logic for test case selection and generation
   - Handles edge cases and conflicts in requirements
   - Ensures consistency across generated test cases

### LLM Integration

The agent leverages Large Language Models through:

1. **Dynamic Prompt Construction**
   - Builds context-aware prompts incorporating:
     - Specific requirement details
     - Machine type and version context
     - Few-shot examples matching the current task
     - Style and format guidelines learned from existing tests

2. **Chain-of-Thought Approach**
   - Breaking complex test generation into logical steps:
     1. Requirement understanding
     2. Test condition identification
     3. Test step formulation
     4. Expected result prediction

3. **Iterative Refinement**
   - Using multiple LLM calls to progressively improve output quality
   - Initial draft → validation → refinement → final output

## Technology Stack

### Core Technologies

- **Python 3.8+**: Primary development language
- **Pandas**: Data manipulation for CSV processing
- **Document Processing**:
  - python-docx for .docx files
  - PyPDF2 for PDF parsing
- **UI Framework**:
  - Tkinter for the graphical user interface
- **Language Model Integration**:
  - Support for various language models
  - Configurable for offline operation

### Development Tools

- **Version Control**: Git with GitHub
- **Testing**: unittest for component testing
- **Code Quality**: Modular architecture with clear separation of concerns

## Project Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/automated-test-generator.git
   cd automated-test-generator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python src/ui_app.py
   ```

   Or use the batch file:
   ```
   src/run_ui.bat
   ```

## Implementation Roadmap

### Phase 1: Input Data Acquisition & Preparation

1. **SRS Input Processing**
   - Develop parsers for various document formats
   - Extract individual requirements
   - Identify requirement metadata

2. **Existing Test Case Analysis**
   - Parse CSV test case files
   - Extract structural patterns and linguistic style
   - Build knowledge base of existing tests

3. **Machine/Version Context Handling**
   - Implement detection for target machine types
   - Define version context extraction

### Phase 2: Core Processing Engine Development

1. **SRS Analysis Module**
   - Implement requirement extraction
   - Develop NLP-based semantic understanding
   - Create machine-specific filtering

2. **Test Pattern Learning**
   - Analyze test structure and linguistic patterns
   - Create searchable test case index
   - Implement clustering for similar test types

3. **LLM Integration**
   - Set up API connections
   - Develop prompt engineering strategies
   - Implement few-shot learning with examples

4. **Test Case Generation**
   - Create generation pipeline
   - Implement post-processing and validation
   - Add machine/version specialization

### Phase 3: Output Generation

1. **CSV Formatting**
   - Map generated tests to target format
   - Implement validation checks
   - Create robust file output handling

### Phase 4: User Interface

1. **Graphical User Interface**
   - Develop intuitive UI for configuration
   - Implement file selection dialogs
   - Create progress tracking and status updates

2. **User Experience**
   - Design clear workflow for users
   - Provide helpful guidance and tooltips
   - Implement error handling and recovery

### Phase 5: Security and Integration

1. **Security Features**
   - Implement local processing options
   - Ensure no sensitive data is transmitted
   - Create secure configuration options

2. **Platform Integration**
   - Support for different platform types
   - Version-specific test generation
   - Customizable naming conventions

## Getting Started with Agent Development

1. **Agent Core Implementation**
   ```bash
   # Create the agent module structure
   mkdir -p src/agent/{core,knowledge,memory,reasoning}
   touch src/agent/__init__.py
   touch src/agent/{core,knowledge,memory,reasoning}/__init__.py
   ```

2. **Implement the basic agent core**
   ```python
   # src/agent/core.py - Basic structure
   class TestGenerationAgent:
       def __init__(self, config):
           self.config = config
           self.knowledge_base = self._initialize_knowledge()
           self.memory = self._initialize_memory()
           self.reasoning = self._initialize_reasoning()

       def process_srs(self, srs_document):
           # Process SRS and identify requirements
           pass

       def learn_from_existing_tests(self, test_cases):
           # Extract patterns from existing tests
           pass

       def generate_test_cases(self, requirements, machine_type, version):
           # Core test generation logic
           pass
   ```

3. **Knowledge base implementation**
   ```python
   # src/agent/knowledge/base.py - Example structure
   class KnowledgeRepository:
       def __init__(self):
           self.test_patterns = {}
           self.machine_contexts = {
               'X': {},
               'Y': {},
               'Z': {}
           }

       def add_test_pattern(self, pattern, metadata):
           # Store learned patterns
           pass

       def get_relevant_patterns(self, requirement, machine_type, version):
           # Retrieve appropriate patterns
           pass
   ```

## Usage

### Basic Operation

1. Launch the application:
   ```bash
   python src/ui_app.py
   ```

2. Using the UI:
   - Select your SRS document (DOCX, PDF, or text file)
   - Select your existing test cases CSV file
   - Choose your platform type and version
   - Specify the output file location
   - Click "Generate Test Cases"

3. Review output:
   - Generated test cases will be available in the specified output file
   - The CSV file is compatible with TFS/Azure DevOps import

### Command Line Usage

For automation or batch processing, you can also use the command line interface:

```bash
python src/main.py --srs path/to/srs.docx --tests path/to/existing_tests.csv --platform-type A --version 1.0 --output output/generated_tests.csv
```

## Security and Privacy Considerations

- All processing happens locally on your machine
- No data is transmitted externally by default (demo mode uses mock responses)
- No sensitive information is stored persistently
- Configurable to run entirely offline for sensitive environments

For more information, see the [Security and Integration Guide](src/SECURITY_AND_INTEGRATION_GUIDE.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.