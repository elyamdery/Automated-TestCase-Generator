"""
Script to generate a simple icon for the application.
"""

import tkinter as tk
import os

def create_icon():
    """Create a simple icon and save it as a .ico file."""
    # Create a root window
    root = tk.Tk()
    root.title("Icon Generator")
    
    # Create a canvas
    canvas = tk.Canvas(root, width=64, height=64, bg="white")
    canvas.pack()
    
    # Draw a simple test case icon
    # Background
    canvas.create_rectangle(4, 4, 60, 60, fill="#3498db", outline="#2980b9", width=2)
    
    # Document lines
    canvas.create_rectangle(12, 12, 52, 52, fill="white", outline="#2980b9", width=1)
    canvas.create_line(16, 20, 48, 20, fill="#7f8c8d", width=1)
    canvas.create_line(16, 28, 48, 28, fill="#7f8c8d", width=1)
    canvas.create_line(16, 36, 48, 36, fill="#7f8c8d", width=1)
    canvas.create_line(16, 44, 48, 44, fill="#7f8c8d", width=1)
    
    # Checkmark
    canvas.create_line(24, 32, 30, 38, fill="#27ae60", width=3)
    canvas.create_line(30, 38, 40, 24, fill="#27ae60", width=3)
    
    # Save as PostScript first (tkinter doesn't directly support saving as .ico)
    ps_file = "resources/icon.ps"
    canvas.postscript(file=ps_file, colormode="color")
    
    print(f"Icon saved as {ps_file}")
    print("You'll need to convert this to .ico format using an external tool.")
    
    # Close the window
    root.after(1000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    # Create the resources directory if it doesn't exist
    os.makedirs("resources", exist_ok=True)
    
    # Create the icon
    create_icon()
