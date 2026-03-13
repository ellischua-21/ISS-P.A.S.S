import tkinter as tk
from tkinter import ttk, messagebox
import threading

from batch_logic import batch_change_password, is_valid_password
from discovery import discover_devices, get_local_ip
import config


class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.resizable(config.RESIZABLE_WIDTH, config.RESIZABLE_HEIGHT)

        # Device management variables
        self.ip_vars = []
        self.discovered_ips = []

        # Loading animation variables
        self.loading = False
        self.loading_texts = config.LOADING_TEXTS
        self.loading_index = 0

        # Password visibility toggles
        self.current_password_visible = False
        self.new_password_visible = False
        self.confirm_password_visible = False

        self.setup_styles()
        self.build_ui()
        self.refresh_devices()

    #--------------- UI SETUP METHODS -----------------

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("TLabel", font=config.LABEL_FONT)
        self.style.configure("TButton", font=config.BUTTON_FONT)
        self.style.configure("TLabelframe.Label", font=config.LABELED_FRAME_FONT)

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="both", expand=True)

        self.build_device_frame(top_frame)
        self.build_credentials_frame(top_frame)
        self.build_log_frame(main_frame)

    def build_device_frame(self, parent):
        device_frame = tk.LabelFrame(
            parent,
            text="Detected Devices",
            font=config.LABELED_FRAME_FONT,
            bd=3,
            relief="solid",
            padx=5,
            pady=5
        )
        device_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)
        device_frame.config(width=260)
        device_frame.pack_propagate(False)

        device_frame.grid_columnconfigure(0, weight=1)
        device_frame.grid_columnconfigure(1, weight=0)
        device_frame.grid_rowconfigure(2, weight=1)

        self.device_count_label = ttk.Label(device_frame, text="Device Count: 0")
        self.device_count_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))

        search_frame = ttk.Frame(device_frame)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_device_list)

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Consolas", 12), width=16)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        canvas_frame = ttk.Frame(device_frame)
        canvas_frame.grid(row=2, column=0, sticky="nsew")

        self.device_canvas = tk.Canvas(
            canvas_frame,
            height=300,
            width=210,
            highlightthickness=0
        )
        self.device_scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.device_canvas.yview
        )
        self.device_list_frame = ttk.Frame(self.device_canvas)

        self.device_list_frame.bind(
            "<Configure>",
            lambda e: self.device_canvas.configure(
                scrollregion=self.device_canvas.bbox("all")
            )
        )

        self.device_canvas.create_window((0, 0), window=self.device_list_frame, anchor="nw")
        self.device_canvas.configure(yscrollcommand=self.device_scrollbar.set)

        def _on_mousewheel(event):
            self.device_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.device_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.device_canvas.pack(side="left", fill="both", expand=True)
        self.device_scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(device_frame)
        button_frame.grid(row=2, column=1, sticky="n", padx=5, pady=5)

        self.refresh_button = ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_devices
        )
        self.refresh_button.pack(fill="x", pady=(0, 2))

        self.select_all_button = ttk.Button(
            button_frame,
            text="Select All",
            command=self.select_all
        )
        self.select_all_button.pack(fill="x", pady=2)

        self.deselect_all_button = ttk.Button(
            button_frame,
            text="Deselect All",
            command=self.deselect_all
        )
        self.deselect_all_button.pack(fill="x", pady=(2, 0))

    #--------------- CREDENTIALS FRAME -----------------

    def build_credentials_frame(self, parent):
        cred_frame = tk.LabelFrame(
            parent,
            text="Credentials",
            font=config.LABELED_FRAME_FONT,
            bd=3,
            relief="solid",
            padx=10,
            pady=10
        )
        cred_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)
        cred_frame.config(width=400)
        cred_frame.pack_propagate(False)

        cred_frame.grid_columnconfigure(0, weight=1)
        cred_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(cred_frame, text="Username").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.username_entry = ttk.Entry(cred_frame, font=config.ENTRY_FONT, width=21)
        self.username_entry.insert(0, "admin")
        self.username_entry.grid(row=0, column=1, sticky="w", padx=5, pady=8)

        ttk.Label(cred_frame, text="Current Password").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        current_pass_frame = ttk.Frame(cred_frame)
        current_pass_frame.grid(row=1, column=1, padx=5, pady=8, sticky="w")

        self.current_pass_entry = ttk.Entry(
            current_pass_frame,
            font=config.ENTRY_FONT,
            width=21,
            show="*"
        )
        self.current_pass_entry.pack(side="left")

        self.current_eye_button = ttk.Button(
            current_pass_frame,
            text="👁",
            width=3,
            command=self.toggle_current_password
        )
        self.current_eye_button.pack(side="left", padx=(5, 0))

        ttk.Label(cred_frame, text="New Password").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        new_pass_frame = ttk.Frame(cred_frame)
        new_pass_frame.grid(row=2, column=1, padx=5, pady=8, sticky="w")

        self.new_pass_entry = ttk.Entry(
            new_pass_frame,
            font=config.ENTRY_FONT,
            width=21,
            show="*"
        )
        self.new_pass_entry.pack(side="left")

        self.new_eye_button = ttk.Button(
            new_pass_frame,
            text="👁",
            width=3,
            command=self.toggle_new_password
        )
        self.new_eye_button.pack(side="left", padx=(5, 0))

        ttk.Label(cred_frame, text="Confirm Password").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        confirm_pass_frame = ttk.Frame(cred_frame)
        confirm_pass_frame.grid(row=3, column=1, padx=5, pady=8, sticky="w")

        self.confirm_pass_entry = ttk.Entry(
            confirm_pass_frame,
            font=config.ENTRY_FONT,
            width=21,
            show="*"
        )
        self.confirm_pass_entry.pack(side="left")

        self.confirm_eye_button = ttk.Button(
            confirm_pass_frame,
            text="👁",
            width=3,
            command=self.toggle_confirm_password
        )
        self.confirm_eye_button.pack(side="left", padx=(5, 0))

        self.start_button = ttk.Button(
            cred_frame,
            text="START",
            command=self.start_update
        )
        self.start_button.grid(row=8, column=0, columnspan=2, pady=50)

        self.progress_label = ttk.Label(cred_frame, text="Progress: 0 / 0")
        self.progress_label.grid(row=9, column=0, columnspan=2, pady=5)

        self.loading_label = ttk.Label(cred_frame, text="")
        self.loading_label.grid(row=10, column=0, columnspan=2, pady=5)

    #--------------- LOG FRAME -----------------

    def build_log_frame(self, parent):
        log_frame = tk.LabelFrame(
            parent,
            text="Results Log",
            font=config.LABELED_FRAME_FONT,
            bd=3,
            relief="solid",
            padx=10,
            pady=10
        )
        log_frame.pack(fill="x", expand=False, pady=(10, 0))

        self.log_box = tk.Text(
            log_frame,
            height=12,
            font=config.LOG_FONT,
            state="disabled",
            bg="white",
            fg="black"
        )
        self.log_box.pack(fill="x", expand=False)

    #--------------- PASSWORD VISIBILITY -----------------

    def toggle_current_password(self):
        self.current_password_visible = not self.current_password_visible
        if self.current_password_visible:
            self.current_pass_entry.config(show="")
            self.current_eye_button.config(text="X")
        else:
            self.current_pass_entry.config(show="*")
            self.current_eye_button.config(text="👁")

    def toggle_new_password(self):
        self.new_password_visible = not self.new_password_visible
        if self.new_password_visible:
            self.new_pass_entry.config(show="")
            self.new_eye_button.config(text="X")
        else:
            self.new_pass_entry.config(show="*")
            self.new_eye_button.config(text="👁")

    def toggle_confirm_password(self):
        self.confirm_password_visible = not self.confirm_password_visible
        if self.confirm_password_visible:
            self.confirm_pass_entry.config(show="")
            self.confirm_eye_button.config(text="X")
        else:
            self.confirm_pass_entry.config(show="*")
            self.confirm_eye_button.config(text="👁")

    #--------------- SELECT/DESELECT -----------------

    def select_all(self):
        for _, var in self.ip_vars:
            var.set(True)

    def deselect_all(self):
        for _, var in self.ip_vars:
            var.set(False)

    #--------------- RESULTS LOG METHODS -----------------

    def animate_loading(self):
        if self.loading:
            self.loading_label.config(
                text=self.loading_texts[self.loading_index % len(self.loading_texts)]
            )
            self.loading_index += 1
            self.root.after(400, self.animate_loading)
        else:
            self.loading_label.config(text="")

    def append_log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete(1.0, tk.END)
        self.log_box.config(state="disabled")

    #--------------- DEVICE LIST -----------------

    def populate_device_list(self, ips):
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        self.ip_vars.clear()

        if not ips:
            empty_label = ttk.Label(self.device_list_frame, text="No Hikvision devices found.")
            empty_label.pack(anchor="w", pady=10)
            self.device_count_label.config(text="Device Count: 0")
            return

        for ip in ips:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(
                self.device_list_frame,
                text=ip,
                variable=var,
                font=config.DEVICE_FONT,
                anchor="w",
                padx=5,
                pady=12,
                indicatoron=True,
                borderwidth=2,
                highlightthickness=1
            )
            chk.pack(anchor="w", fill="x")
            self.ip_vars.append((ip, var))

        self.device_count_label.config(text=f"Device Count: {len(ips)}")

    def filter_device_list(self, *args):
        query = self.search_var.get().strip().lower()

        if not query:
            filtered_ips = self.discovered_ips
        else:
            filtered_ips = [ip for ip in self.discovered_ips if query in ip.lower()]

        self.populate_device_list(filtered_ips)

    #--------------- DISCOVERY WORKFLOW METHODS -----------------

    def run_discovery(self):
        try:
            print("Detected local IP:", get_local_ip())
            devices = discover_devices()
            self.root.after(0, lambda: self.finish_discovery(devices))
        except Exception as e:
            self.root.after(0, lambda: self.finish_discovery([], str(e)))

    def finish_discovery(self, devices, error_message=None):
        self.discovered_ips = devices
        self.filter_device_list()

        if error_message:
            self.append_log(f"Discovery error: {error_message}")
        else:
            self.append_log(f"Discovery complete. {len(devices)} Hikvision device(s) found.")

        self.refresh_button.config(state="normal")
        self.select_all_button.config(state="normal")
        self.deselect_all_button.config(state="normal")

    def refresh_devices(self):
        self.refresh_button.config(state="disabled")
        self.select_all_button.config(state="disabled")
        self.deselect_all_button.config(state="disabled")

        self.clear_log()
        self.append_log("Scanning current subnet for Hikvision devices...")
        self.device_count_label.config(text="Device Count: Scanning...")

        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        scanning_label = ttk.Label(self.device_list_frame, text="Scanning devices...")
        scanning_label.pack(anchor="w", pady=10)

        thread = threading.Thread(target=self.run_discovery, daemon=True)
        thread.start()

    #--------------- PASSWORD UPDATE WORKFLOW METHODS -----------------

    def run_batch_process(self, selected_ips, username, current_pass, new_pass):
        results = batch_change_password(
            ip_list=selected_ips,
            username=username,
            current_password=current_pass,
            new_password=new_pass
        )
        self.root.after(0, lambda: self.finish_update(results, selected_ips))

    def finish_update(self, results, selected_ips):
        self.log_box.config(state="normal")
        for r in results:
            self.log_box.insert(tk.END, r["message"] + "\n")
        self.log_box.config(state="disabled")

        self.progress_label.config(text=f"Progress: {len(results)} / {len(selected_ips)}")
        self.loading = False
        self.start_button.config(state="normal")

    def start_update(self):
        selected_ips = [ip for ip, var in self.ip_vars if var.get()]
        if not selected_ips:
            messagebox.showerror("Error", "No devices selected.")
            return

        username = self.username_entry.get().strip()
        current_pass = self.current_pass_entry.get()
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()

        if not username or not current_pass or not new_pass or not confirm_pass:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Password Error", "New password and confirm password do not match.")
            return

        valid, msg = is_valid_password(new_pass)
        if not valid:
            messagebox.showerror("Password Error", msg)
            return

        self.clear_log()
        self.progress_label.config(text=f"Progress: 0 / {len(selected_ips)}")

        self.loading = True
        self.loading_index = 0
        self.animate_loading()
        self.start_button.config(state="disabled")

        thread = threading.Thread(
            target=self.run_batch_process,
            args=(selected_ips, username, current_pass, new_pass),
            daemon=True
        )
        thread.start()