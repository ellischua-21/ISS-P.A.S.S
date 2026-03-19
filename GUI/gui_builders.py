import tkinter as tk
from tkinter import ttk
import config


class GUIBuilders:
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
        device_frame.grid_rowconfigure(3, weight=1)

        self.device_count_label = ttk.Label(device_frame, text="Device Count: 0")
        self.device_count_label.grid(row=0, column=0, sticky="w", padx=5, pady=(0, 5))

        self.selected_count_label = ttk.Label(device_frame, text="Selected devices: 0")
        self.selected_count_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))

        search_frame = ttk.Frame(device_frame)
        search_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_device_list)

        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("mono", 12),
            width=16
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        canvas_frame = ttk.Frame(device_frame)
        canvas_frame.grid(row=3, column=0, sticky="nsew")

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
        button_frame.grid(row=3, column=1, sticky="n", padx=5, pady=5)

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
        self.username_entry = ttk.Entry(
            cred_frame, 
            font=config.ENTRY_FONT, 
            width=21
        )

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
        self.start_button.grid(row=9, column=0, columnspan=2, pady=45)

        self.check_button = ttk.Button(
            cred_frame,
            text="CHECK",
            command=self.check_selected_devices
        )
        self.check_button.grid(row=10, column=0, columnspan=2, pady=5)

        self.progress_label = ttk.Label(cred_frame, text="Progress: 0 / 0")
        self.progress_label.grid(row=11, column=0, columnspan=2, pady=45)

        self.loading_label = ttk.Label(cred_frame, text="")
        self.loading_label.grid(row=12 , column=0, columnspan=2, pady=5)

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