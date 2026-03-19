from tkinter import ttk, messagebox
import threading

from batch_logic import batch_change_password, is_valid_password
from discovery import discover_devices, get_local_ip


class GUIWorkflows:
    def run_discovery(self):
        try:
            self.append_log(f"Detected local IP: {get_local_ip()}")
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
            self.append_log(f"Scanning complete. {len(devices)} device(s) found.")

        self.refresh_button.config(state="normal")
        self.select_all_button.config(state="normal")
        self.deselect_all_button.config(state="normal")

    def refresh_devices(self):
        self.refresh_button.config(state="disabled")
        self.select_all_button.config(state="disabled")
        self.deselect_all_button.config(state="disabled")

        self.clear_log()
        self.append_log("Scanning current subnet...")
        self.checked_ips.clear()
        self.device_count_label.config(text="Device Count: 0")
        self.selected_count_label.config(text="Selected devices: 0")

        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        scanning_label = ttk.Label(self.device_list_frame, text="Scanning devices...")
        scanning_label.pack(anchor="w", pady=10)

        thread = threading.Thread(target=self.run_discovery, daemon=True)
        thread.start()

    def run_batch_process(self, selected_ips, username, current_pass, new_pass):
        self.processed_count = 0

        def log_result(result):
            self.root.after(0, lambda: self.append_log(result["message"]))
            self.processed_count += 1
            self.root.after(0, lambda: self.progress_label.config(text=f"Progress: {self.processed_count} / {len(selected_ips)}"))
            if result["success"]:
                # Unselect the successful IP (keeps selection state correct even when filtered)
                self.root.after(0, lambda ip=result["ip"]: self.clear_ip_selection(ip))
        results = batch_change_password(
            ip_list=selected_ips,
            username=username,
            current_password=current_pass,
            new_password=new_pass,
            callback=log_result
        )
        self.root.after(0, lambda: self.finish_update(results, selected_ips))

    def finish_update(self, results, selected_ips):
        self.loading = False
        self.start_button.config(state="normal")

    def start_update(self):
        selected_ips = list(self.checked_ips)
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

        if not messagebox.askyesno("Confirm Start", f"Are you sure you want to update passwords for {len(selected_ips)} device(s)?"):
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

    def check_selected_devices(self):
        self.clear_log()
        selected = sorted(self.checked_ips, key=lambda ip: tuple(map(int, ip.split('.'))))
        if not selected:
            self.append_log("No devices selected.")
        else:
            self.append_log("Checked devices:")
            for ip in selected:
                self.append_log(f"  - {ip}")
