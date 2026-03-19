import tkinter as tk
from tkinter import ttk
import config


class GUIHelpers:
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

    def select_all(self):
        for ip, var in self.ip_vars:
            var.set(True)
            self.checked_ips.add(ip)
        self.update_selected_count()

    def deselect_all(self):
        for ip, var in self.ip_vars:
            var.set(False)
            self.checked_ips.discard(ip)
        self.update_selected_count()

    def on_checkbox_toggled(self, ip, var):
        if var.get():
            self.checked_ips.add(ip)
        else:
            self.checked_ips.discard(ip)
        self.update_selected_count()

    def clear_ip_selection(self, ip):
        """Remove an IP from the selected set and uncheck it if currently visible."""
        self.checked_ips.discard(ip)
        for other_ip, other_var in self.ip_vars:
            if other_ip == ip:
                other_var.set(False)
                break
        self.update_selected_count()

    def update_selected_count(self):
        selected_count = len(self.checked_ips)
        self.selected_count_label.config(text=f"Selected devices: {selected_count}")

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

    def populate_device_list(self, ips, checked_ips=None):
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        self.ip_vars.clear()

        if not ips:
            empty_label = ttk.Label(self.device_list_frame, text="No devices found.")
            empty_label.pack(anchor="w", pady=10)
            self.device_count_label.config(text="Device Count: 0")
            self.selected_count_label.config(text=f"Selected devices: {len(self.checked_ips)}")
            return

        # Keep track of selections even when the list is filtered
        if checked_ips:
            self.checked_ips.update(checked_ips)

        for ip in ips:
            var = tk.BooleanVar(value=(ip in self.checked_ips))
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
                highlightthickness=1,
                command=lambda ip=ip, var=var: self.on_checkbox_toggled(ip, var)
            )
            chk.pack(anchor="w", fill="x")
            chk.bind("<MouseWheel>", lambda e: self.device_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            self.ip_vars.append((ip, var))

        self.device_count_label.config(text=f"Device Count: {len(ips)}")
        self.update_selected_count()

    def filter_device_list(self, *args):
        query = self.search_var.get().strip().lower()

        # Collect currently checked IPs before repopulating
        checked_ips = {ip for ip, var in self.ip_vars if var.get()}

        if not query:
            filtered_ips = self.discovered_ips
        else:
            filtered_ips = [ip for ip in self.discovered_ips if query in ip.lower()]

        self.populate_device_list(filtered_ips, checked_ips)

        # Scroll to top when searching
        if query:
            self.device_canvas.yview_moveto(0.0)