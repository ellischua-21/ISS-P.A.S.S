import tkinter as tk
from tkinter import ttk, messagebox

import config
from GUI.gui_app import PasswordManagerGUI


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("P.A.S.S. Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.password_visible = False

        self.build_ui()

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame,
            text="P.A.S.S. Login",
            font=("Consolas", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        ttk.Label(main_frame, text="Username", font=config.LABEL_FONT).pack(anchor="w")
        self.username_entry = ttk.Entry(main_frame, font=config.ENTRY_FONT)
        self.username_entry.pack(fill="x", pady=(0, 10))
        self.username_entry.focus()

        ttk.Label(main_frame, text="Password", font=config.LABEL_FONT).pack(anchor="w")

        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x", pady=(0, 15))

        self.password_entry = ttk.Entry(password_frame, font=config.ENTRY_FONT, show="*")
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
            text="LOGIN",
            command=self.login
        )
        login_button.pack(pady=10)

    def toggle_password(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.config(show="")
            self.eye_button.config(text="X")
        else:
            self.password_entry.config(show="*")
            self.eye_button.config(text="👁")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if username == config.LOGIN_USERNAME and password == config.LOGIN_PASSWORD:
            self.open_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_main_app(self):
        self.root.destroy()

        main_root = tk.Tk()
        app = PasswordManagerGUI(main_root)
        main_root.mainloop()