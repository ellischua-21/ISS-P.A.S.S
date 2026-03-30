# Import necessary modules
import tkinter as tk
from login import LoginWindow

# Main entry point
if __name__ == "__main__":
    # Create the main Tkinter root window
    root = tk.Tk()
    # Initialize the login window
    login = LoginWindow(root)
    # Start the Tkinter event loop
    root.mainloop()