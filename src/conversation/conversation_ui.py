"""
Conversation UI for Test Case Generator.

This module provides a UI for multi-turn AI conversations
to refine test cases interactively.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Optional, Any, Callable
import datetime

from conversation.conversation_manager import ConversationManager

class ConversationUI:
    """
    UI for multi-turn AI conversations.
    
    This class provides a UI for:
    - Displaying conversation history
    - Sending messages to refine test cases
    - Viewing and accepting refinements
    """
    
    def __init__(self, parent, conversation_manager: ConversationManager, callback: Callable = None):
        """
        Initialize the conversation UI.
        
        Args:
            parent: Parent tkinter widget
            conversation_manager: Conversation manager instance
            callback: Optional callback function to call when a test case is updated
        """
        self.parent = parent
        self.conversation_manager = conversation_manager
        self.callback = callback
        
        # Create a top-level window for the conversation
        self.window = tk.Toplevel(parent)
        self.window.title("Test Case Refinement Chat")
        self.window.geometry("800x600")
        self.window.minsize(600, 400)
        
        # Set icon and configure window
        self.window.iconbitmap(default="resources/icon.ico") if os.path.exists("resources/icon.ico") else None
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create variables
        self.current_conversation_id = None
        self.current_test_case = None
        
        # Create widgets
        self._create_widgets()
        
        # Hide the window initially
        self.window.withdraw()
    
    def _create_widgets(self):
        """Create the UI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split into conversation and test case panels
        panel_frame = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        panel_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Conversation panel (left)
        conversation_frame = ttk.Frame(panel_frame)
        panel_frame.add(conversation_frame, weight=3)
        
        # Test case panel (right)
        test_case_frame = ttk.Frame(panel_frame)
        panel_frame.add(test_case_frame, weight=2)
        
        # Conversation history
        history_frame = ttk.LabelFrame(conversation_frame, text="Conversation", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat history text area
        self.chat_history = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            state=tk.DISABLED
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        
        # Message input
        input_frame = ttk.Frame(conversation_frame)
        input_frame.pack(fill=tk.X)
        
        self.message_input = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            height=3
        )
        self.message_input.pack(fill=tk.X, expand=True, side=tk.LEFT)
        
        # Bind Enter key to send message
        self.message_input.bind("<Return>", self._on_enter_pressed)
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self._send_message,
            style="Accent.TButton"
        )
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Quick refinement buttons
        refinement_frame = ttk.LabelFrame(conversation_frame, text="Quick Refinements", padding="10")
        refinement_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create a grid of refinement buttons
        refinements = [
            ("Add Edge Cases", self._add_edge_cases),
            ("Improve Steps", self._improve_steps),
            ("Add Performance Tests", self._add_performance_tests),
            ("Focus on Security", self._focus_on_security)
        ]
        
        for i, (text, command) in enumerate(refinements):
            ttk.Button(
                refinement_frame,
                text=text,
                command=command
            ).grid(row=i//2, column=i%2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Configure grid columns
        refinement_frame.columnconfigure(0, weight=1)
        refinement_frame.columnconfigure(1, weight=1)
        
        # Test case display
        test_case_label_frame = ttk.LabelFrame(test_case_frame, text="Current Test Case", padding="10")
        test_case_label_frame.pack(fill=tk.BOTH, expand=True)
        
        # Test case text area
        self.test_case_text = scrolledtext.ScrolledText(
            test_case_label_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            state=tk.DISABLED
        )
        self.test_case_text.pack(fill=tk.BOTH, expand=True)
        
        # Accept changes button
        self.accept_button = ttk.Button(
            test_case_frame,
            text="Accept Changes",
            command=self._accept_changes,
            state=tk.DISABLED
        )
        self.accept_button.pack(side=tk.RIGHT, pady=(10, 0))
        
        # Compare with original button
        self.compare_button = ttk.Button(
            test_case_frame,
            text="Compare with Original",
            command=self._compare_with_original,
            state=tk.DISABLED
        )
        self.compare_button.pack(side=tk.LEFT, pady=(10, 0))
    
    def show(self, test_case_id: str, test_case: Dict):
        """
        Show the conversation UI for a test case.
        
        Args:
            test_case_id: ID of the test case
            test_case: The test case dictionary
        """
        # Check if there's an existing conversation for this test case
        conversations = self.conversation_manager.list_conversations(test_case_id)
        
        if conversations:
            # Use the most recent active conversation
            active_conversations = [c for c in conversations if c.get('status') == 'active']
            if active_conversations:
                conversation_id = active_conversations[0].get('id')
                self.current_conversation_id = conversation_id
                self.current_test_case = self.conversation_manager.get_current_test_case(conversation_id)
            else:
                # Start a new conversation
                self.current_conversation_id = self.conversation_manager.start_conversation(test_case_id, test_case)
                self.current_test_case = test_case
        else:
            # Start a new conversation
            self.current_conversation_id = self.conversation_manager.start_conversation(test_case_id, test_case)
            self.current_test_case = test_case
        
        # Update the UI
        self._update_chat_history()
        self._update_test_case_display()
        
        # Enable buttons
        self.accept_button.config(state=tk.NORMAL)
        self.compare_button.config(state=tk.NORMAL)
        
        # Show the window
        self.window.deiconify()
        self.window.lift()
        
        # Focus on the message input
        self.message_input.focus_set()
    
    def _update_chat_history(self):
        """Update the chat history display."""
        if not self.current_conversation_id:
            return
        
        # Get the conversation history
        messages = self.conversation_manager.get_conversation_history(self.current_conversation_id)
        
        # Clear the chat history
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete(1.0, tk.END)
        
        # Add messages to the chat history
        for message in messages:
            role = message.get('role')
            content = message.get('content', '')
            
            # Skip system messages
            if role == 'system':
                continue
            
            # Format based on role
            if role == 'user':
                self.chat_history.insert(tk.END, "You: ", "user")
                self.chat_history.insert(tk.END, content + "\n\n", "user_message")
            elif role == 'assistant':
                self.chat_history.insert(tk.END, "Assistant: ", "assistant")
                self.chat_history.insert(tk.END, content + "\n\n", "assistant_message")
        
        # Configure tags
        self.chat_history.tag_configure("user", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")
        self.chat_history.tag_configure("user_message", font=("Segoe UI", 10), foreground="#2c3e50")
        self.chat_history.tag_configure("assistant", font=("Segoe UI", 10, "bold"), foreground="#27ae60")
        self.chat_history.tag_configure("assistant_message", font=("Segoe UI", 10), foreground="#27ae60")
        
        # Disable editing
        self.chat_history.config(state=tk.DISABLED)
        
        # Scroll to the bottom
        self.chat_history.see(tk.END)
    
    def _update_test_case_display(self):
        """Update the test case display."""
        if not self.current_test_case:
            return
        
        # Clear the test case text
        self.test_case_text.config(state=tk.NORMAL)
        self.test_case_text.delete(1.0, tk.END)
        
        # Format the test case as JSON
        test_case_json = json.dumps(self.current_test_case, indent=2)
        
        # Add to the text area
        self.test_case_text.insert(tk.END, test_case_json)
        
        # Disable editing
        self.test_case_text.config(state=tk.DISABLED)
    
    def _send_message(self):
        """Send a message to the conversation."""
        if not self.current_conversation_id:
            return
        
        # Get the message
        message = self.message_input.get(1.0, tk.END).strip()
        if not message:
            return
        
        # Clear the message input
        self.message_input.delete(1.0, tk.END)
        
        # Add the message to the conversation
        self.conversation_manager.add_user_message(self.current_conversation_id, message)
        
        # Update the UI
        self._update_chat_history()
        
        # Process the message and generate a response
        self._process_message(message)
    
    def _process_message(self, message: str):
        """
        Process a user message and generate a response.
        
        Args:
            message: The user message
        """
        # In a real implementation, this would call the LLM to generate a response
        # For now, we'll use a simple rule-based approach
        
        # Check for common refinement requests
        if "edge case" in message.lower():
            self._add_edge_cases()
        elif "improve step" in message.lower() or "better step" in message.lower():
            self._improve_steps()
        elif "performance" in message.lower():
            self._add_performance_tests()
        elif "security" in message.lower():
            self._focus_on_security()
        else:
            # Generic response
            response = "I understand you want to refine the test case. Would you like me to add edge cases, improve the steps, add performance tests, or focus on security aspects?"
            self.conversation_manager.add_assistant_message(self.current_conversation_id, response)
            self._update_chat_history()
    
    def _add_edge_cases(self):
        """Add edge cases to the test case."""
        if not self.current_conversation_id or not self.current_test_case:
            return
        
        # Define some edge cases based on the test case
        edge_cases = [
            {
                "step": "Test with maximum allowed input values",
                "expected": "System handles maximum values correctly"
            },
            {
                "step": "Test with minimum allowed input values",
                "expected": "System handles minimum values correctly"
            },
            {
                "step": "Test with invalid input format",
                "expected": "System displays appropriate error message"
            }
        ]
        
        # Apply the refinement
        updated_test_case, assistant_message = self.conversation_manager.apply_refinement(
            self.current_conversation_id,
            'add_edge_cases',
            {'edge_cases': edge_cases}
        )
        
        # Update the current test case
        self.current_test_case = updated_test_case
        
        # Update the UI
        self._update_chat_history()
        self._update_test_case_display()
    
    def _improve_steps(self):
        """Improve the steps in the test case."""
        if not self.current_conversation_id or not self.current_test_case:
            return
        
        # Improve the first few steps if they exist
        improved_steps = {}
        steps = self.current_test_case.get('steps', [])
        
        if len(steps) > 0:
            improved_steps['0'] = f"Precisely {steps[0]} with detailed parameters"
        
        if len(steps) > 1:
            improved_steps['1'] = f"Carefully {steps[1]} following best practices"
        
        # Apply the refinement
        updated_test_case, assistant_message = self.conversation_manager.apply_refinement(
            self.current_conversation_id,
            'improve_steps',
            {'improved_steps': improved_steps}
        )
        
        # Update the current test case
        self.current_test_case = updated_test_case
        
        # Update the UI
        self._update_chat_history()
        self._update_test_case_display()
    
    def _add_performance_tests(self):
        """Add performance testing scenarios to the test case."""
        if not self.current_conversation_id or not self.current_test_case:
            return
        
        # Define some performance scenarios
        scenarios = [
            {
                "step": "Measure response time under normal load",
                "expected": "Response time is under 2 seconds"
            },
            {
                "step": "Measure response time under heavy load (100 concurrent users)",
                "expected": "Response time is under 5 seconds"
            },
            {
                "step": "Monitor memory usage during operation",
                "expected": "Memory usage remains stable and below 500MB"
            }
        ]
        
        # Apply the refinement
        updated_test_case, assistant_message = self.conversation_manager.apply_refinement(
            self.current_conversation_id,
            'add_performance_scenarios',
            {'scenarios': scenarios}
        )
        
        # Update the current test case
        self.current_test_case = updated_test_case
        
        # Update the UI
        self._update_chat_history()
        self._update_test_case_display()
    
    def _focus_on_security(self):
        """Add security testing aspects to the test case."""
        if not self.current_conversation_id or not self.current_test_case:
            return
        
        # Define some security aspects
        security_aspects = [
            {
                "step": "Test with SQL injection attempts in input fields",
                "expected": "System sanitizes inputs and prevents SQL injection"
            },
            {
                "step": "Test with cross-site scripting (XSS) attempts",
                "expected": "System escapes special characters and prevents XSS"
            },
            {
                "step": "Verify authentication and authorization controls",
                "expected": "Unauthorized users cannot access restricted functionality"
            }
        ]
        
        # Apply the refinement
        updated_test_case, assistant_message = self.conversation_manager.apply_refinement(
            self.current_conversation_id,
            'focus_on_security',
            {'security_aspects': security_aspects}
        )
        
        # Update the current test case
        self.current_test_case = updated_test_case
        
        # Update the UI
        self._update_chat_history()
        self._update_test_case_display()
    
    def _accept_changes(self):
        """Accept the changes to the test case."""
        if not self.current_conversation_id or not self.current_test_case:
            return
        
        # Close the conversation
        self.conversation_manager.close_conversation(self.current_conversation_id)
        
        # Call the callback with the updated test case
        if self.callback:
            self.callback(self.current_test_case)
        
        # Close the window
        self.window.withdraw()
    
    def _compare_with_original(self):
        """Compare the current test case with the original."""
        if not self.current_conversation_id:
            return
        
        # Get the original test case
        original_test_case = self.conversation_manager.get_original_test_case(self.current_conversation_id)
        if not original_test_case:
            messagebox.showerror("Error", "Original test case not found.")
            return
        
        # Create a comparison window
        comparison_window = tk.Toplevel(self.window)
        comparison_window.title("Test Case Comparison")
        comparison_window.geometry("1000x600")
        comparison_window.minsize(800, 400)
        
        # Create a frame with padding
        frame = ttk.Frame(comparison_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Split into original and current panels
        panel = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        panel.pack(fill=tk.BOTH, expand=True)
        
        # Original test case panel
        original_frame = ttk.LabelFrame(panel, text="Original Test Case", padding="10")
        panel.add(original_frame, weight=1)
        
        # Current test case panel
        current_frame = ttk.LabelFrame(panel, text="Current Test Case", padding="10")
        panel.add(current_frame, weight=1)
        
        # Original test case text
        original_text = scrolledtext.ScrolledText(
            original_frame,
            wrap=tk.WORD,
            font=("Courier New", 10)
        )
        original_text.pack(fill=tk.BOTH, expand=True)
        
        # Current test case text
        current_text = scrolledtext.ScrolledText(
            current_frame,
            wrap=tk.WORD,
            font=("Courier New", 10)
        )
        current_text.pack(fill=tk.BOTH, expand=True)
        
        # Format the test cases as JSON
        original_json = json.dumps(original_test_case, indent=2)
        current_json = json.dumps(self.current_test_case, indent=2)
        
        # Add to the text areas
        original_text.insert(tk.END, original_json)
        current_text.insert(tk.END, current_json)
        
        # Disable editing
        original_text.config(state=tk.DISABLED)
        current_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            frame,
            text="Close",
            command=comparison_window.destroy
        ).pack(side=tk.RIGHT, pady=(10, 0))
    
    def _on_enter_pressed(self, event):
        """Handle Enter key press in the message input."""
        # Send the message if Enter is pressed without Shift
        if not event.state & 0x1:  # Shift not pressed
            self._send_message()
            return "break"  # Prevent the newline from being added
    
    def _on_close(self):
        """Handle window close event."""
        # Hide the window instead of destroying it
        self.window.withdraw()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Conversation UI Example")
    root.geometry("200x100")
    
    conversation_manager = ConversationManager()
    
    def on_test_case_updated(test_case):
        print(f"Test case updated: {test_case}")
    
    conversation_ui = ConversationUI(root, conversation_manager, on_test_case_updated)
    
    # Button to show the conversation UI
    ttk.Button(
        root,
        text="Show Conversation",
        command=lambda: conversation_ui.show(
            "TEST-001",
            {
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
        )
    ).pack(padx=20, pady=20)
    
    root.mainloop()
