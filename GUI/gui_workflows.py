from tkinter import ttk, messagebox
import threading

from batch_logic import batch_change_password, is_valid_password
from discovery import discover_devices, get_local_ip


class GUIWorkflows:
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
            self.log_box.insert("end", r["message"] + "\n")
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