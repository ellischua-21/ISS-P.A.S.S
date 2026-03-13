import tkinter as tk
from GUI.gui_app import PasswordManagerGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()