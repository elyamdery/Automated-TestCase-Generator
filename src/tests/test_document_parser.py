"""
Tests for the document parser module.
"""

import unittest
import os
import tempfile
from agent.input.document_parser import DocumentParser, TextParser, get_parser_for_file

class TestDocumentParser(unittest.TestCase):
    """Test cases for the document parser."""
    
    def test_text_parser(self):
        """Test parsing a text file with requirements."""
        # Create a temporary text file with sample requirements
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("""
            REQ-001: The system shall allow users to log in with username and password.
            
            REQ-002: The system shall display an error message for invalid login attempts.
            
            The system must maintain a log of all login attempts. This is a critical security feature.
            """)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = TextParser()
            requirements = parser.parse(temp_file)
            
            # Verify the results
            self.assertEqual(len(requirements), 3)
            self.assertEqual(requirements[0]['id'], 'REQ-001')
            self.assertEqual(requirements[1]['id'], 'REQ-002')
            self.assertTrue('critical' in requirements[2]['tags'])
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_get_parser_for_file(self):
        """Test getting the appropriate parser for different file types."""
        # Test with different file extensions
        docx_parser = get_parser_for_file('test.docx')
        pdf_parser = get_parser_for_file('test.pdf')
        text_parser = get_parser_for_file('test.txt')
        
        # Verify the parser types
        self.assertEqual(docx_parser.__class__.__name__, 'DocxParser')
        self.assertEqual(pdf_parser.__class__.__name__, 'PdfParser')
        self.assertEqual(text_parser.__class__.__name__, 'TextParser')
    
    def test_extract_tags(self):
        """Test extracting tags from requirement text."""
        parser = DocumentParser()
        
        # Test with different texts
        critical_text = "This is a critical requirement for security."
        ui_text = "The user interface must display a confirmation dialog."
        
        # Extract tags
        critical_tags = parser._extract_tags(critical_text)
        ui_tags = parser._extract_tags(ui_text)
        
        # Verify the tags
        self.assertTrue('critical' in critical_tags)
        self.assertTrue('security' in critical_tags)
        self.assertTrue('ui' in ui_tags)

if __name__ == '__main__':
    unittest.main()
