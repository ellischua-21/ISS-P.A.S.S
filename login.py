# Import necessary modules
import tkinter as tk
from tkinter import ttk, messagebox

from GUI.gui_app import PasswordManagerGUI
from auth_manager import validate_login, change_password

# Class for the login window
class LoginWindow:
    # Initialize the login window
    def __init__(self, root):
        self.root = root
        self.root.title("P.A.S.S Login")
        self.root.geometry("400x320")
        self.root.resizable(False, False)

        self.password_visible = False

        self.build_ui()

    # Build the user interface
    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame,
            text="P.A.S.S Login",
            font=("Consolas", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        ttk.Label(main_frame, text="Username").pack(anchor="w")
        self.username_entry = ttk.Entry(main_frame, font=("Consolas", 14))
        self.username_entry.pack(fill="x", pady=(0, 10))
        self.username_entry.focus()

        ttk.Label(main_frame, text="Password").pack(anchor="w")

        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x", pady=(0, 15))

        self.password_entry = ttk.Entry(password_frame, font=("Consolas", 14), show="*")
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<Return>", lambda event: self.login())

        self.eye_button = ttk.Button(
            password_frame,
            text="👁",
            width=3,
            command=self.toggle_password
        )
        self.eye_button.pack(side="left", padx=(5, 0))

        login_button = ttk.Button(
            main_frame, 
            text="Login", 
            command=self.login,
            width = 20
        )
        login_button.pack(pady=(10, 15))

        change_pass_button = ttk.Button(
            main_frame,
            text="Change Password",
            command=self.open_change_password_window,
            width = 20
        )
        change_pass_button.pack()

    # Toggle password visibility
    def toggle_password(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.config(show="")
            self.eye_button.config(text="X")
        else:
            self.password_entry.config(show="*")
            self.eye_button.config(text="👁")

    # Handle login attempt
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if validate_login(username, password):
            self.open_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # Open the main application
    def open_main_app(self):
        self.root.destroy()
        main_root = tk.Tk()
        app = PasswordManagerGUI(main_root)
        main_root.mainloop()

    # Open the change password window
    def open_change_password_window(self):
        change_window = tk.Toplevel(self.root)
        change_window.title("Change Password")
        change_window.geometry("400x320")
        change_window.resizable(False, False)

        current_visible = tk.BooleanVar(value=False)
        new_visible = tk.BooleanVar(value=False)
        confirm_visible = tk.BooleanVar(value=False)

        ttk.Label(change_window, text="Current Password").pack(anchor="w", padx=20, pady=(20, 5))
        current_frame = ttk.Frame(change_window)
        current_frame.pack(fill="x", padx=20, pady=(0, 10))

        current_pass_entry = ttk.Entry(current_frame, font=("Consolas", 14), show="*")
        current_pass_entry.pack(side="left", fill="x", expand=True)

        current_eye_button = ttk.Button(current_frame, text="👁", width=3)
        current_eye_button.pack(side="left", padx=(5, 0))

        ttk.Label(change_window, text="New Password").pack(anchor="w", padx=20, pady=(0, 5))
        new_frame = ttk.Frame(change_window)
        new_frame.pack(fill="x", padx=20, pady=(0, 10))

        new_pass_entry = ttk.Entry(new_frame, font=("Consolas", 14), show="*")
        new_pass_entry.pack(side="left", fill="x", expand=True)

        new_eye_button = ttk.Button(new_frame, text="👁", width=3)
        new_eye_button.pack(side="left", padx=(5, 0))

        ttk.Label(change_window, text="Confirm New Password").pack(anchor="w", padx=20, pady=(0, 5))
        confirm_frame = ttk.Frame(change_window)
        confirm_frame.pack(fill="x", padx=20, pady=(0, 15))

        confirm_pass_entry = ttk.Entry(confirm_frame, font=("Consolas", 14), show="*")
        confirm_pass_entry.pack(side="left", fill="x", expand=True)

        confirm_eye_button = ttk.Button(confirm_frame, text="👁", width=3)
        confirm_eye_button.pack(side="left", padx=(5, 0))

        # Toggle visibility function
        def toggle_entry(entry_widget, button_widget, visible_var):
            visible_var.set(not visible_var.get())
            if visible_var.get():
                entry_widget.config(show="")
                button_widget.config(text="X")
            else:
                entry_widget.config(show="*")
                button_widget.config(text="👁")

        current_eye_button.config(
            command=lambda: toggle_entry(current_pass_entry, current_eye_button, current_visible)
        )
        new_eye_button.config(
            command=lambda: toggle_entry(new_pass_entry, new_eye_button, new_visible)
        )
        confirm_eye_button.config(
            command=lambda: toggle_entry(confirm_pass_entry, confirm_eye_button, confirm_visible)
        )

        # Submit change function
        def submit_change():
            current_password = current_pass_entry.get()
            new_password = new_pass_entry.get()
            confirm_password = confirm_pass_entry.get()

            if not current_password or not new_password or not confirm_password:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match.")
                return

            success, msg = change_password(current_password, new_password)

            if success:
                messagebox.showinfo("Success", msg)
                change_window.destroy()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(change_window, text="Save", command=submit_change).pack(pady=10)