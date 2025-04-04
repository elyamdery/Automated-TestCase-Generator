"""
Test Case Generator UI Application

A simple, minimalist GUI for the automated test case generation system.
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
    GUI Application for Test Case Generation
    """

    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Test Case Generator - Automated Manual Test Writing")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Set background color and title bar icon
        self.root.configure(background='#f0f0f0')

        # Try to set a nice icon for the window
        try:
            self.root.iconbitmap(default="resources/icon.ico")
        except:
            # If icon not found, try to create a simple icon using a canvas
            try:
                icon = tk.PhotoImage(data="""R0lGODlhEAAQAIABAAAAAP///yH5BAEKAAEALAAAAAAQABAAAAIjjI+py+0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2UQAAOw==""")
                self.root.iconphoto(True, icon)
            except:
                pass  # If all fails, use default icon

        # Load environment variables
        load_dotenv()

        # Set up variables
        self.srs_path = tk.StringVar()
        self.tests_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.path.join("output", "generated_tests.csv"))
        self.machine_type = tk.StringVar(value="A")
        self.version = tk.StringVar(value="1.0")
        self.progress_text = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0.0)

        # Set up the UI
        self._create_ui()

        # Agent instance (will be created when needed)
        self.agent = None

        # Flag for running process
        self.is_running = False

    def _create_ui(self):
        """Create the user interface."""
        # Main frame with padding and background
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Set a nice background color for the main frame
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")

        # Title and subtitle
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            title_frame,
            text="Test Case Generator",
            font=("Segoe UI", 20, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ttk.Label(
            title_frame,
            text="Generate professional test cases from SRS documents",
            font=("Segoe UI", 12),
            foreground="#7f8c8d"
        )
        subtitle_label.pack()

        # Input frame with better styling
        input_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # Add a description label
        ttk.Label(
            input_frame,
            text="Select the SRS document and existing test cases to use as input",
            font=("Segoe UI", 9),
            foreground="#7f8c8d"
        ).pack(anchor=tk.W, pady=(0, 10))

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

        # Existing tests file selection
        tests_frame = ttk.Frame(input_frame)
        tests_frame.pack(fill=tk.X, pady=5)

        ttk.Label(tests_frame, text="Existing Tests:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(tests_frame, textvariable=self.tests_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            tests_frame,
            text="Browse...",
            command=self._browse_tests
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Configuration frame with better styling
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))

        # Add a description label
        ttk.Label(
            config_frame,
            text="Configure the platform type, version, and output settings",
            font=("Segoe UI", 9),
            foreground="#7f8c8d"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Machine type selection
        machine_frame = ttk.Frame(config_frame)
        machine_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            machine_frame,
            text="Knowledge Center:",
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 15))

        # Create a better-looking radio button frame with a border
        radio_frame = ttk.LabelFrame(machine_frame, text="Select Platform Type")
        radio_frame.pack(side=tk.LEFT, padx=(0, 15), fill=tk.X, expand=True)

        # Add radio buttons in a grid layout
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

        # Add help button
        help_button = ttk.Button(
            machine_frame,
            text="?",
            width=2,
            command=self._show_platform_help
        )
        help_button.pack(side=tk.LEFT)

        # Version selection
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            version_frame,
            text="Version:",
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 15))

        # Create a better-looking version selection frame
        version_select_frame = ttk.LabelFrame(version_frame, text="Select Platform Version")
        version_select_frame.pack(side=tk.LEFT, padx=(0, 15), fill=tk.X, expand=True)

        # Add combobox in a nicer layout
        version_combo = ttk.Combobox(
            version_select_frame,
            textvariable=self.version,
            values=["1.0", "2.0", "3.0"],
            width=15
        )
        version_combo.grid(row=0, column=0, padx=15, pady=5, sticky=tk.W)

        # Add help button
        help_button = ttk.Button(
            version_frame,
            text="?",
            width=2,
            command=self._show_version_help
        )
        help_button.pack(side=tk.LEFT)

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

        # Progress frame with better styling
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="15")
        progress_frame.pack(fill=tk.X, pady=(0, 15))

        # Add a description label
        ttk.Label(
            progress_frame,
            text="Current progress of the test case generation process",
            font=("Segoe UI", 9),
            foreground="#7f8c8d"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Progress bar with improved styling
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_value,
            maximum=100,
            style="Accent.Horizontal.TProgressbar",
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=10)

        # Progress text with better font
        progress_label = ttk.Label(
            progress_frame,
            textvariable=self.progress_text,
            font=("Segoe UI", 10),
            foreground="#2c3e50"
        )
        progress_label.pack(fill=tk.X, pady=5)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Create a frame with a nice background for buttons
        button_bg_frame = ttk.Frame(button_frame, padding="10")
        button_bg_frame.pack(fill=tk.X, pady=10)

        # Help button with icon-like appearance
        help_button = ttk.Button(
            button_bg_frame,
            text="Help & Info",
            command=self._show_help,
            width=15
        )
        help_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Spacer frame to push buttons to the sides
        spacer = ttk.Frame(button_bg_frame)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Cancel button with improved styling
        self.cancel_button = ttk.Button(
            button_bg_frame,
            text="Cancel",
            command=self._cancel,
            state=tk.DISABLED,
            width=15
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Generate button with improved styling
        self.generate_button = ttk.Button(
            button_bg_frame,
            text="Generate Test Cases",
            command=self._generate_tests,
            style="Accent.TButton",
            width=25
        )
        self.generate_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(fill=tk.X)

        # Apply styles
        self._apply_styles()

    def _apply_styles(self):
        """Apply custom styles to the UI."""
        style = ttk.Style()

        # Configure the theme - use 'vista' on Windows for better button appearance
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")

        # Configure colors and fonts
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TRadiobutton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TLabelframe", font=("Segoe UI", 10))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")

        # Fix button text display issues
        style.configure("TButton", padding=6)

        # Accent button style with better visibility
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=8,
            background="#3498db",
            foreground="#ffffff"
        )

        # Progress bar style
        style.configure("Accent.Horizontal.TProgressbar", background="#2ecc71")

        # Try to make buttons more visible with map configuration
        style.map('TButton',
            foreground=[('pressed', '#333333'), ('active', '#000000')],
            background=[('pressed', '#d8d8d8'), ('active', '#ececec')]
        )

        style.map('Accent.TButton',
            foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
            background=[('pressed', '#2980b9'), ('active', '#3498db')]
        )

    def _browse_srs(self):
        """Browse for SRS document."""
        file_path = filedialog.askopenfilename(
            title="Select SRS Document",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.srs_path.set(file_path)

    def _browse_tests(self):
        """Browse for existing test cases."""
        file_path = filedialog.askopenfilename(
            title="Select Existing Test Cases",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.tests_path.set(file_path)

    def _browse_output(self):
        """Browse for output file location."""
        file_path = filedialog.asksaveasfilename(
            title="Save Generated Test Cases",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.output_path.set(file_path)

    def _generate_tests(self):
        """Generate test cases."""
        # Validate inputs
        if not self._validate_inputs():
            return

        # Disable generate button and enable cancel button
        self.generate_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.is_running = True

        # Start generation in a separate thread
        threading.Thread(target=self._run_generation, daemon=True).start()

    def _validate_inputs(self):
        """Validate user inputs."""
        # Check SRS path
        if not self.srs_path.get():
            messagebox.showerror("Error", "Please select an SRS document.")
            return False

        if not os.path.exists(self.srs_path.get()):
            messagebox.showerror("Error", "SRS document not found.")
            return False

        # Check tests path
        if not self.tests_path.get():
            messagebox.showerror("Error", "Please select existing test cases.")
            return False

        if not os.path.exists(self.tests_path.get()):
            messagebox.showerror("Error", "Existing test cases file not found.")
            return False

        # Check output path
        output_dir = os.path.dirname(self.output_path.get())
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {str(e)}")
                return False

        return True

    def _run_generation(self):
        """Run the test case generation process."""
        try:
            # Update progress
            self._update_progress(0, "Initializing...")

            # Create configuration
            config = {
                'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
                'openai_api_key': os.getenv('OPENAI_API_KEY', 'dummy_key'),
                'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', 'dummy_key'),
                'output_dir': os.path.dirname(self.output_path.get())
            }

            # Create the agent
            self._update_progress(10, "Creating agent...")
            self.agent = TestGenerationAgent(config)

            # Process the SRS
            self._update_progress(20, "Processing SRS document...")
            requirements = self.agent.process_srs(self.srs_path.get())

            # Learn from existing tests
            self._update_progress(40, "Learning from existing tests...")
            self.agent.learn_from_existing_tests(self.tests_path.get())

            # Generate test cases
            self._update_progress(60, "Generating test cases...")
            test_cases = self.agent.generate_test_cases(
                requirements,
                self.machine_type.get(),
                self.version.get()
            )

            # Output to CSV
            self._update_progress(80, "Writing test cases to CSV...")
            self.agent.output_to_csv(test_cases, self.output_path.get())

            # Complete
            self._update_progress(100, "Test case generation complete!")

            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Generated {len(test_cases)} test cases successfully!\n\nOutput file: {self.output_path.get()}"
            ))

        except Exception as e:
            logger.error(f"Error during test generation: {str(e)}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self._update_progress(0, "Error occurred")

        finally:
            # Re-enable generate button and disable cancel button
            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
            self.is_running = False

    def _update_progress(self, value, text):
        """Update the progress bar and text."""
        self.root.after(0, lambda: self.progress_value.set(value))
        self.root.after(0, lambda: self.progress_text.set(text))

    def _cancel(self):
        """Cancel the generation process."""
        if not self.is_running:
            return

        # Set flag to stop the process
        self.is_running = False

        # Update UI
        self._update_progress(0, "Cancelled")
        self.generate_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

        messagebox.showinfo("Cancelled", "Test case generation was cancelled.")

    def _show_help(self):
        """Show help information."""
        help_text = """
        Test Case Generator Help

        This application generates test cases from SRS documents based on existing test cases.

        How to use:
        1. Select an SRS document (Word, PDF, or text file)
        2. Select existing test cases (CSV file)
        3. Choose your platform type (A, B, or Z)
        4. Select the platform version
        5. Specify the output file location
        6. Click 'Generate Test Cases'

        For more information, please refer to the documentation.
        """

        messagebox.showinfo("Help", help_text)

    def _show_platform_help(self):
        """Show help about platform types."""
        platform_help = """
        Platform Type Information

        Select the appropriate platform type for your test cases:

        • Platform A: Used for standard configurations
          - Features: Basic authentication, standard UI
          - Naming convention: A_[TestID]_[Version]

        • Platform B: Used for enhanced configurations
          - Features: Advanced authentication, enhanced UI
          - Naming convention: B_[TestID]_[Version]

        • Platform Z: Used for specialized configurations
          - Features: Specialized security, custom UI
          - Naming convention: Z_[TestID]_[Version]

        The platform type affects the generated test cases and their features.
        """

        messagebox.showinfo("Platform Types", platform_help)

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


def main():
    """Run the application."""
    # Create the root window
    root = tk.Tk()

    # Set application icon
    try:
        root.iconbitmap("resources/icon.ico")
    except:
        pass  # Icon not found, use default

    # Create the application
    app = TestGeneratorApp(root)

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
