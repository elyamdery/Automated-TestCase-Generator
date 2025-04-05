"""
Test script for the conversation feature.
"""

import os
import tkinter as tk
from conversation import ConversationManager, ConversationUI

def main():
    """Run the test script."""
    # Create the root window
    root = tk.Tk()
    root.title("Conversation Feature Test")
    root.geometry("300x200")
    
    # Create a conversation manager
    conversation_manager = ConversationManager()
    
    # Callback function for when a test case is updated
    def on_test_case_updated(test_case):
        print(f"Test case updated: {test_case}")
    
    # Create a conversation UI
    conversation_ui = ConversationUI(root, conversation_manager, on_test_case_updated)
    
    # Sample test case
    test_case = {
        "id": "TEST-001",
        "title": "Test Login Functionality",
        "steps": [
            "Navigate to login page",
            "Enter valid credentials",
            "Click login button"
        ],
        "expected_results": [
            "Login page loads successfully",
            "Credentials are accepted",
            "User is logged in successfully"
        ]
    }
    
    # Button to show the conversation UI
    button = tk.Button(
        root,
        text="Open Conversation",
        command=lambda: conversation_ui.show("TEST-001", test_case)
    )
    button.pack(padx=20, pady=20)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
