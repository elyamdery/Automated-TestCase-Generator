"""
UI Conversation Link for Test Case Generator.

This module provides a link between the main UI and the conversation UI,
allowing the conversation AI to access knowledge from the main components.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, List, Optional, Any, Callable

from conversation import ConversationManager, ConversationUI

# Setup logging
logger = logging.getLogger(__name__)

class ConversationLink:
    """
    Link between the main UI and the conversation UI.
    
    This class provides functionality to:
    - Launch the conversation UI from the main UI
    - Pass test case data to the conversation UI
    - Update test cases in the main UI based on conversation results
    """
    
    def __init__(self, parent):
        """
        Initialize the conversation link.
        
        Args:
            parent: Parent tkinter widget (main UI)
        """
        self.parent = parent
        
        # Create a conversation manager
        self.conversation_manager = ConversationManager()
        
        # Create a conversation UI (initially hidden)
        self.conversation_ui = ConversationUI(
            parent,
            self.conversation_manager,
            self._on_test_case_updated
        )
        
        # Current test case data
        self.current_test_cases = []
        self.current_srs_data = {}
        self.current_platform_type = ""
        self.current_version = ""
        
        # Create a button to launch the conversation UI
        self.launch_button = ttk.Button(
            parent,
            text="Open AI Assistant",
            command=self._launch_conversation,
            style="Accent.TButton"
        )
    
    def place_button(self, **kwargs):
        """Place the launch button in the parent widget."""
        self.launch_button.place(**kwargs)
    
    def pack_button(self, **kwargs):
        """Pack the launch button in the parent widget."""
        self.launch_button.pack(**kwargs)
    
    def grid_button(self, **kwargs):
        """Grid the launch button in the parent widget."""
        self.launch_button.grid(**kwargs)
    
    def set_test_cases(self, test_cases: List[Dict]):
        """
        Set the current test cases.
        
        Args:
            test_cases: List of test case dictionaries
        """
        self.current_test_cases = test_cases
        
        # Enable the launch button if there are test cases
        if test_cases:
            self.launch_button.config(state=tk.NORMAL)
        else:
            self.launch_button.config(state=tk.DISABLED)
    
    def set_srs_data(self, srs_data: Dict):
        """
        Set the current SRS data.
        
        Args:
            srs_data: SRS data dictionary
        """
        self.current_srs_data = srs_data
    
    def set_platform_info(self, platform_type: str, version: str):
        """
        Set the current platform type and version.
        
        Args:
            platform_type: Platform type (A, B, Z)
            version: Version (1.0, 2.0, 3.0)
        """
        self.current_platform_type = platform_type
        self.current_version = version
    
    def _launch_conversation(self):
        """Launch the conversation UI."""
        if not self.current_test_cases:
            messagebox.showwarning(
                "No Test Cases",
                "No test cases available. Please generate test cases first."
            )
            return
        
        # Create a selection dialog if there are multiple test cases
        if len(self.current_test_cases) > 1:
            self._show_test_case_selection_dialog()
        else:
            # Only one test case, use it directly
            test_case = self.current_test_cases[0]
            self._open_conversation_for_test_case(test_case)
    
    def _show_test_case_selection_dialog(self):
        """Show a dialog to select a test case for conversation."""
        # Create a dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Select Test Case")
        dialog.geometry("600x400")
        dialog.minsize(500, 300)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create a frame with padding
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(
            frame,
            text="Select a test case to discuss with the AI Assistant:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Create a treeview for test cases
        columns = ("id", "title")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("id", text="ID")
        tree.heading("title", text="Title")
        
        tree.column("id", width=100, anchor=tk.W)
        tree.column("title", width=400, anchor=tk.W)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add test cases to the treeview
        for i, test_case in enumerate(self.current_test_cases):
            tree.insert(
                "",
                tk.END,
                values=(
                    test_case.get("id", f"TC-{i+1}"),
                    test_case.get("title", f"Test Case {i+1}")
                ),
                tags=(str(i),)
            )
        
        # Add a preview frame
        preview_frame = ttk.LabelFrame(dialog, text="Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Preview text area
        preview_text = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            font=("Courier New", 9),
            height=10,
            state=tk.DISABLED
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Function to update preview when a test case is selected
        def on_test_case_selected(event):
            # Get the selected item
            selection = tree.selection()
            if not selection:
                return
            
            # Get the test case index
            index = int(tree.item(selection[0], "tags")[0])
            test_case = self.current_test_cases[index]
            
            # Update the preview
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            # Format the test case as JSON
            preview_text.insert(tk.END, json.dumps(test_case, indent=2))
            
            # Disable editing
            preview_text.config(state=tk.DISABLED)
        
        # Bind the selection event
        tree.bind("<<TreeviewSelect>>", on_test_case_selected)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Open button
        def on_open():
            # Get the selected item
            selection = tree.selection()
            if not selection:
                messagebox.showwarning(
                    "No Selection",
                    "Please select a test case."
                )
                return
            
            # Get the test case index
            index = int(tree.item(selection[0], "tags")[0])
            test_case = self.current_test_cases[index]
            
            # Close the dialog
            dialog.destroy()
            
            # Open the conversation for the selected test case
            self._open_conversation_for_test_case(test_case)
        
        ttk.Button(
            button_frame,
            text="Open Conversation",
            command=on_open,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT)
        
        # Create new test case button
        ttk.Button(
            button_frame,
            text="Create New Test Case",
            command=lambda: self._create_new_test_case(dialog)
        ).pack(side=tk.LEFT)
    
    def _create_new_test_case(self, dialog=None):
        """
        Create a new test case through conversation.
        
        Args:
            dialog: Optional dialog to close
        """
        # Close the dialog if provided
        if dialog:
            dialog.destroy()
        
        # Create a basic test case
        test_case = {
            "id": f"{self.current_platform_type}_{int(self.current_version.replace('.', '_'))}_NEW",
            "title": "New Test Case",
            "steps": [],
            "expected_results": []
        }
        
        # Open the conversation for the new test case
        self._open_conversation_for_test_case(test_case, is_new=True)
    
    def _open_conversation_for_test_case(self, test_case: Dict, is_new: bool = False):
        """
        Open the conversation UI for a test case.
        
        Args:
            test_case: The test case dictionary
            is_new: Whether this is a new test case
        """
        # Generate a test case ID if not present
        if "id" not in test_case:
            test_case["id"] = f"{self.current_platform_type}_{int(self.current_version.replace('.', '_'))}_{len(self.current_test_cases) + 1}"
        
        # Show the conversation UI
        self.conversation_ui.show(test_case["id"], test_case)
        
        # Store whether this is a new test case
        self.conversation_ui.is_new_test_case = is_new
    
    def _on_test_case_updated(self, updated_test_case: Dict):
        """
        Handle updated test case from conversation.
        
        Args:
            updated_test_case: The updated test case dictionary
        """
        # Check if this is a new test case
        is_new = getattr(self.conversation_ui, "is_new_test_case", False)
        
        if is_new:
            # Add the new test case to the list
            self.current_test_cases.append(updated_test_case)
            
            # Notify the user
            messagebox.showinfo(
                "Test Case Created",
                f"New test case '{updated_test_case.get('title', 'Untitled')}' has been created."
            )
        else:
            # Find and update the existing test case
            for i, test_case in enumerate(self.current_test_cases):
                if test_case.get("id") == updated_test_case.get("id"):
                    self.current_test_cases[i] = updated_test_case
                    break
            
            # Notify the user
            messagebox.showinfo(
                "Test Case Updated",
                f"Test case '{updated_test_case.get('title', 'Untitled')}' has been updated."
            )
        
        # Call the update callback if defined
        if hasattr(self, "update_callback") and self.update_callback:
            self.update_callback(self.current_test_cases)
    
    def set_update_callback(self, callback: Callable):
        """
        Set a callback function to be called when test cases are updated.
        
        Args:
            callback: Callback function that takes a list of test cases
        """
        self.update_callback = callback
