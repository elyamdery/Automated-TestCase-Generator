# Test Case Generator UI

A simple, minimalist GUI application for generating test cases from SRS documents.

## Features

- Clean, user-friendly interface
- Support for multiple document formats (DOCX, PDF, TXT)
- Knowledge center selection (A, B, Z)
- Version selection
- Progress tracking
- TFS-compatible output format

## Usage

1. **Select SRS Document**: Choose the Software Requirements Specification document (DOCX, PDF, or TXT format)
2. **Select Existing Tests**: Choose a CSV file containing existing test cases to learn from
3. **Configure Settings**:
   - Select the knowledge center (A, B, or Z)
   - Choose the version
   - Specify the output file location
4. **Generate Test Cases**: Click the "Generate Test Cases" button to start the process

## Security Considerations

This application is designed with security in mind:

1. **No Data Transmission**: All processing happens locally on your machine
2. **No External APIs**: When using the demo mode (default), no data is sent to external APIs
3. **Classified Information**: The application does not store or transmit any classified information
4. **File Handling**: Only processes the files you explicitly select

## Requirements

- Python 3.8 or higher
- Required packages:
  - tkinter (usually included with Python)
  - pandas
  - python-docx (for DOCX processing)
  - PyPDF2 (for PDF processing)

## Running the Application

Double-click the `run_ui.bat` file or run:

```
python ui_app.py
```

## Troubleshooting

If you encounter any issues:

1. Check the `ui_app.log` file for detailed error messages
2. Ensure all required packages are installed
3. Verify that the input files exist and are in the correct format
