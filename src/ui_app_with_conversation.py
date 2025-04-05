"""
Test Case Generator UI Application with Conversation Link

A simple, minimalist GUI for the automated test case generation system
with integrated AI conversation capabilities.
"""

import os
import sys
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dotenv import load_dotenv

# Import the agent
from agent.core.agent import TestGenerationAgent

# Import the conversation link
from ui_conversation_link import ConversationLink

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ui_app.log')
    ]
)
logger = logging.getLogger(__name__)

class TestGeneratorApp:
    """
    Test Generator Application with Conversation Link
    
    A GUI application for generating test cases from SRS documents
    and refining them through AI conversation.
    """
    
    def __init__(self, root):
        """
        Initialize the application.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Test Case Generator")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set icon if available
        if os.path.exists("resources/icon.ico"):
            self.root.iconbitmap("resources/icon.ico")
        
        # Load environment variables
        load_dotenv()
        
        # Create variables
        self.srs_path = tk.StringVar()
        self.tests_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.machine_type = tk.StringVar(value="A")
        self.version = tk.StringVar(value="1.0")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Create the agent
        self.agent = TestGenerationAgent()
        
        # Create the UI
        self._create_ui()
        
        # Create the conversation link
        self.conversation_link = ConversationLink(self.root)
        
        # Place the conversation link button in the output frame
        self.conversation_link.place_button(
            x=10, y=10, 
            anchor=tk.NW
        )
        
        # Set the update callback
        self.conversation_link.set_update_callback(self._on_test_cases_updated)
        
        # Initially disable the conversation button
        self.conversation_link.launch_button.config(state=tk.DISABLED)
        
        # Log initialization
        logger.info("Application initialized")
    
    def _create_ui(self):
        """Create the user interface."""
        # Create styles
        self._create_styles()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input files section
        input_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add a button to open the data directory
        data_dir_frame = ttk.Frame(input_frame)
        data_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(data_dir_frame, text="Can't find your files?").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            data_dir_frame,
            text="Open Data Directory",
            command=self._open_data_directory
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # SRS file selection
        srs_frame = ttk.Frame(input_frame)
        srs_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(srs_frame, text="SRS Document:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(srs_frame, textvariable=self.srs_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            srs_frame, 
            text="Browse...", 
            command=self._browse_srs
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Existing tests selection
        tests_frame = ttk.Frame(input_frame)
        tests_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(tests_frame, text="Existing Tests:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(tests_frame, textvariable=self.tests_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            tests_frame, 
            text="Browse...", 
            command=self._browse_tests
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Platform type selection
        platform_frame = ttk.Frame(config_frame)
        platform_frame.pack(fill=tk.X, pady=5)
        
        platform_label_frame = ttk.Frame(platform_frame)
        platform_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(platform_label_frame, text="Select Platform Type:").pack(side=tk.LEFT)
        ttk.Button(
            platform_label_frame, 
            text="?", 
            width=2,
            command=self._show_platform_help
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Radio buttons for platform type
        radio_frame = ttk.Frame(platform_frame)
        radio_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            radio_frame, 
            text="Platform A", 
            variable=self.machine_type, 
            value="A"
        ).grid(row=0, column=0, padx=15, pady=5, sticky=tk.W)
        
        ttk.Radiobutton(
            radio_frame, 
            text="Platform B", 
            variable=self.machine_type, 
            value="B"
        ).grid(row=0, column=1, padx=15, pady=5, sticky=tk.W)
        
        ttk.Radiobutton(
            radio_frame, 
            text="Platform Z", 
            variable=self.machine_type, 
            value="Z"
        ).grid(row=0, column=2, padx=15, pady=5, sticky=tk.W)
        
        # Version selection
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=5)
        
        version_label_frame = ttk.Frame(version_frame)
        version_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(version_label_frame, text="Select Platform Version:").pack(side=tk.LEFT)
        ttk.Button(
            version_label_frame, 
            text="?", 
            width=2,
            command=self._show_version_help
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Dropdown for version
        ttk.Combobox(
            version_frame, 
            textvariable=self.version,
            values=["1.0", "2.0", "3.0"],
            width=10
        ).pack(side=tk.LEFT)
        
        # Output file selection
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output File:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            output_frame, 
            text="Browse...", 
            command=self._browse_output
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            mode="determinate",
            length=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status label
        ttk.Label(
            progress_frame, 
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic")
        ).pack(anchor=tk.W)
        
        # Button section
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Help button
        ttk.Button(
            button_frame, 
            text="Help & Info",
            command=self._show_help
        ).pack(side=tk.LEFT)
        
        # Spacer
        ttk.Frame(button_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Generate button
        self.generate_button = ttk.Button(
            button_frame, 
            text="Generate Test Cases",
            command=self._generate_test_cases,
            style="Accent.TButton"
        )
        self.generate_button.pack(side=tk.RIGHT)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Output text area
        self.output_text = tk.Text(
            output_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            state=tk.DISABLED
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for output text
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
    
    def _create_styles(self):
        """Create custom styles for the UI."""
        style = ttk.Style()
        
        # Use the 'vista' theme on Windows for better button appearance
        if os.name == 'nt':
            style.theme_use('vista')
        
        # Create an accent button style
        style.configure(
            "Accent.TButton",
            background="#0078D7",
            foreground="white",
            padding=(10, 5)
        )
        
        # Configure other styles
        style.configure(
            "TButton",
            padding=(8, 4)
        )
        
        style.configure(
            "TLabel",
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 10, "bold")
        )
    
    def _browse_srs(self):
        """Browse for SRS document."""
        # Start in the data directory if it exists
        initial_dir = os.path.abspath("data") if os.path.exists("data") else os.getcwd()
        
        # Show a message to help the user
        messagebox.showinfo(
            "File Selection", 
            f"Looking for files in: {initial_dir}\n\nIf you don't see your files, please check this directory."
        )
        
        file_path = filedialog.askopenfilename(
            title="Select SRS Document",
            initialdir=initial_dir,
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf")
            ]
        )
        if file_path:
            self.srs_path.set(file_path)
    
    def _browse_tests(self):
        """Browse for existing test cases."""
        # Start in the data directory if it exists
        initial_dir = os.path.abspath("data") if os.path.exists("data") else os.getcwd()
        
        # Show a message to help the user
        messagebox.showinfo(
            "File Selection", 
            f"Looking for files in: {initial_dir}\n\nIf you don't see your files, please check this directory."
        )
        
        file_path = filedialog.askopenfilename(
            title="Select Existing Test Cases",
            initialdir=initial_dir,
            filetypes=[
                ("All Files", "*.*"),
                ("CSV Files", "*.csv")
            ]
        )
        if file_path:
            self.tests_path.set(file_path)
    
    def _browse_output(self):
        """Browse for output file location."""
        # Start in the output directory if it exists
        initial_dir = os.path.abspath("output") if os.path.exists("output") else os.getcwd()
        
        file_path = filedialog.asksaveasfilename(
            title="Save Generated Test Cases",
            initialdir=initial_dir,
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def _open_data_directory(self):
        """Open the data directory in the file explorer."""
        # Create the data directory if it doesn't exist
        data_dir = os.path.abspath("data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            
            # Create a README file in the data directory
            readme_path = os.path.join(data_dir, "README.txt")
            with open(readme_path, "w") as f:
                f.write("""
                DATA DIRECTORY
                
                This directory is for storing input files for the Test Case Generator:
                
                1. SRS Documents (*.txt, *.docx, *.pdf)
                2. Existing Test Cases (*.csv)
                
                Place your files in this directory to make them easily accessible from the application.
                """)
        
        # Open the directory in the file explorer
        try:
            if os.name == 'nt':  # Windows
                os.startfile(data_dir)
            elif os.name == 'posix':  # macOS, Linux
                import subprocess
                subprocess.Popen(['open', data_dir] if sys.platform == 'darwin' else ['xdg-open', data_dir])
            else:
                messagebox.showinfo("Open Directory", f"Data directory is located at:\n{data_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open data directory: {str(e)}")
    
    def _show_platform_help(self):
        """Show help about platform types."""
        platform_help = """
        Platform Type Information
        
        Select the appropriate platform type for your test cases:
        
        • Platform A
          - Standard configuration
          - Basic feature set
          - Used for general testing
        
        • Platform B
          - Enhanced configuration
          - Extended feature set
          - Used for specialized testing
        
        • Platform Z
          - Advanced configuration
          - Complete feature set
          - Used for comprehensive testing
        
        The platform type affects which features are tested and how test cases are structured.
        """
        
        messagebox.showinfo("Platform Type Information", platform_help)
    
    def _show_version_help(self):
        """Show help about versions."""
        version_help = """
        Version Information
        
        Select the appropriate version for your platform:
        
        • Version 1.0: Base version
          - Features: Core functionality
          - File naming: [PlatformType]_[TestID]_1.0
        
        • Version 2.0: Enhanced version
          - Features: Advanced functionality, improved security
          - File naming: [PlatformType]_[TestID]_2.0
        
        • Version 3.0: Latest version
          - Features: Complete functionality set, maximum security
          - File naming: [PlatformType]_[TestID]_3.0
        
        The version affects which features are tested in the generated test cases.
        """
        
        messagebox.showinfo("Version Information", version_help)
    
    def _show_help(self):
        """Show help and information."""
        help_text = """
        Test Case Generator Help
        
        This application generates test cases from SRS documents based on existing test cases.
        
        Steps to use:
        
        1. Select an SRS document (DOCX, PDF, or TXT)
        2. Select existing test cases (CSV)
        3. Choose the platform type and version
        4. Specify the output file location
        5. Click "Generate Test Cases"
        
        After generation, you can use the AI Assistant to refine the test cases through conversation.
        
        For more information, please refer to the user manual.
        """
        
        messagebox.showinfo("Help & Information", help_text)
    
    def _generate_test_cases(self):
        """Generate test cases."""
        # Validate inputs
        if not self._validate_inputs():
            return
        
        # Disable the generate button
        self.generate_button.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_var.set(0.0)
        self.status_var.set("Initializing...")
        
        # Clear output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # Get inputs
        srs_path = self.srs_path.get()
        tests_path = self.tests_path.get()
        output_path = self.output_path.get()
        machine_type = self.machine_type.get()
        version = self.version.get()
        
        # Start generation in a separate thread
        threading.Thread(
            target=self._run_generation,
            args=(srs_path, tests_path, output_path, machine_type, version),
            daemon=True
        ).start()
    
    def _run_generation(self, srs_path, tests_path, output_path, machine_type, version):
        """
        Run the test case generation process.
        
        Args:
            srs_path: Path to the SRS document
            tests_path: Path to the existing test cases
            output_path: Path to save the generated test cases
            machine_type: Machine type (A, B, Z)
            version: Version (1.0, 2.0, 3.0)
        """
        try:
            # Update status
            self._update_status("Reading SRS document...", 0.1)
            
            # Read SRS document
            srs_data = self.agent.read_srs(srs_path)
            
            # Update status
            self._update_status("Reading existing test cases...", 0.2)
            
            # Read existing test cases
            existing_tests = self.agent.read_existing_tests(tests_path)
            
            # Update status
            self._update_status("Analyzing requirements...", 0.3)
            
            # Analyze requirements
            requirements = self.agent.analyze_requirements(srs_data)
            
            # Update status
            self._update_status("Learning test patterns...", 0.4)
            
            # Learn test patterns
            patterns = self.agent.learn_patterns(existing_tests)
            
            # Update status
            self._update_status("Generating test cases...", 0.5)
            
            # Generate test cases
            test_cases = self.agent.generate_test_cases(
                requirements,
                patterns,
                machine_type,
                version
            )
            
            # Update status
            self._update_status("Formatting output...", 0.8)
            
            # Format output
            output_data = self.agent.format_output(test_cases)
            
            # Update status
            self._update_status("Saving test cases...", 0.9)
            
            # Save test cases
            self.agent.save_test_cases(output_data, output_path)
            
            # Update status
            self._update_status("Test cases generated successfully!", 1.0)
            
            # Update output text
            self._update_output(f"Generated {len(test_cases)} test cases for {machine_type} version {version}.\n\nSaved to: {output_path}")
            
            # Update the conversation link with the generated test cases
            self.root.after(0, lambda: self._update_conversation_link(test_cases, srs_data, machine_type, version))
            
        except Exception as e:
            # Log the error
            logger.error(f"Error generating test cases: {str(e)}", exc_info=True)
            
            # Update status
            self._update_status(f"Error: {str(e)}", 0.0)
            
            # Show error message
            messagebox.showerror("Error", f"An error occurred while generating test cases:\n\n{str(e)}")
        
        finally:
            # Re-enable the generate button
            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
    
    def _update_conversation_link(self, test_cases, srs_data, machine_type, version):
        """
        Update the conversation link with the generated test cases.
        
        Args:
            test_cases: List of generated test cases
            srs_data: SRS data
            machine_type: Machine type
            version: Version
        """
        # Set the test cases
        self.conversation_link.set_test_cases(test_cases)
        
        # Set the SRS data
        self.conversation_link.set_srs_data(srs_data)
        
        # Set the platform info
        self.conversation_link.set_platform_info(machine_type, version)
        
        # Enable the conversation button
        self.conversation_link.launch_button.config(state=tk.NORMAL)
    
    def _on_test_cases_updated(self, updated_test_cases):
        """
        Handle updated test cases from the conversation.
        
        Args:
            updated_test_cases: List of updated test cases
        """
        # Update the output text
        self._update_output(f"Test cases updated through conversation.\n\nTotal test cases: {len(updated_test_cases)}")
        
        # TODO: Save the updated test cases if needed
    
    def _update_status(self, status, progress):
        """
        Update the status and progress.
        
        Args:
            status: Status message
            progress: Progress value (0.0 to 1.0)
        """
        # Update in the main thread
        self.root.after(0, lambda: self._update_status_ui(status, progress))
    
    def _update_status_ui(self, status, progress):
        """
        Update the status and progress in the UI.
        
        Args:
            status: Status message
            progress: Progress value (0.0 to 1.0)
        """
        self.status_var.set(status)
        self.progress_var.set(progress * 100)
    
    def _update_output(self, text):
        """
        Update the output text.
        
        Args:
            text: Text to display
        """
        # Update in the main thread
        self.root.after(0, lambda: self._update_output_ui(text))
    
    def _update_output_ui(self, text):
        """
        Update the output text in the UI.
        
        Args:
            text: Text to display
        """
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
    
    def _validate_inputs(self):
        """
        Validate user inputs.
        
        Returns:
            True if inputs are valid, False otherwise
        """
        # Check SRS path
        srs_path = self.srs_path.get()
        if not srs_path:
            messagebox.showerror("Error", "Please select an SRS document.")
            return False
        
        if not os.path.exists(srs_path):
            messagebox.showerror("Error", f"SRS document not found: {srs_path}")
            return False
        
        # Check tests path
        tests_path = self.tests_path.get()
        if not tests_path:
            messagebox.showerror("Error", "Please select existing test cases.")
            return False
        
        if not os.path.exists(tests_path):
            messagebox.showerror("Error", f"Existing test cases not found: {tests_path}")
            return False
        
        # Check output path
        output_path = self.output_path.get()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file location.")
            return False
        
        # Check if output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {str(e)}")
                return False
        
        return True


def main():
    """Run the application."""
    # Create the root window
    root = tk.Tk()
    
    # Create the application
    app = TestGeneratorApp(root)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
