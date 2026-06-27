import os
import shutil
import psutil
import ctypes
import subprocess
import sys
import customtkinter as ctk

# --- Version Info ---
APP_NAME = "WinSysCare"
VERSION = "v1.0.0"
DEVELOPER = "Developed by Ahmed Rabea"

class AdvancedOptimizer:
    def __init__(self):
        self.junk_paths = {
            "User Temp": os.environ.get('TEMP'),
            "Windows Temp": r'C:\Windows\Temp',
            "Prefetch": r'C:\Windows\Prefetch',
            "Windows Update Cache": r'C:\Windows\SoftwareDistribution\Download',
            "Windows Logs": r'C:\Windows\Logs',
            "Crash Reports": os.path.join(os.environ.get('LOCALAPPDATA'), 'CrashDumps')
        }

    def clean_all_junk(self):
        total_files = 0
        total_size = 0
        for name, path in self.junk_paths.items():
            if path and os.path.exists(path):
                try:
                    for filename in os.listdir(path):
                        file_path = os.path.join(path, filename)
                        try:
                            size = os.path.getsize(file_path)
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                            total_files += 1
                            total_size += size
                        except: continue
                except: continue
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1 | 2 | 4)
        except: pass
        return total_files, round(total_size / (1024 * 1024), 2)

    def delete_inactive_profiles(self):
        try:
            current_user = os.getlogin()
            ps_script = f"""
            $CurrentUser = '{current_user}'
            Get-CimInstance -Class Win32_UserProfile | Where-Object {{ 
                (!$_.Special) -and 
                ($_.LocalPath -notlike "*$CurrentUser*") -and 
                ($_.LocalPath -notlike "*Administrator*") -and
                ($_.LocalPath -notlike "*Public*")
            }} | Remove-CimInstance
            """
            process = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, shell=True)
            if process.returncode == 0:
                return True, "All inactive profiles have been removed successfully."
            else:
                return False, f"System Error: {process.stderr}"
        except Exception as e:
            return False, str(e)

    def run_sfc_scan(self):
        try:
            subprocess.Popen(['cmd.exe', '/c', f'title {APP_NAME} - System Scan & sfc /scannow & pause'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
        except: return False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("900x550")
        ctk.set_appearance_mode("dark")
        
        self.optimizer = AdvancedOptimizer()

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo & Version
        self.logo_label = ctk.CTkLabel(self.sidebar, text=APP_NAME, font=("Segoe UI", 26, "bold"), text_color="#3498db")
        self.logo_label.pack(pady=(30, 5))
        self.ver_label = ctk.CTkLabel(self.sidebar, text=VERSION, font=("Segoe UI", 12), text_color="gray")
        self.ver_label.pack(pady=(0, 20))

        # Sidebar Buttons
        self.create_sidebar_button("Dashboard", self.show_dashboard)
        self.create_sidebar_button("Deep Cleaner", self.show_cleaner)
        self.create_sidebar_button("User Profiles", self.show_profiles_manager)
        self.create_sidebar_button("System Repair", self.show_repair)

        # Developer Credit (Bottom of Sidebar)
        self.dev_label = ctk.CTkLabel(self.sidebar, text=DEVELOPER, font=("Segoe UI", 11, "italic"), text_color="#555")
        self.dev_label.pack(side="bottom", pady=20)

        # Main Area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=30, pady=20, sticky="nsew")

        self.show_dashboard()

    def create_sidebar_button(self, text, command):
        # تم إزالة padx من هنا لإصلاح الخطأ
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, 
                            height=40, font=("Segoe UI", 14), 
                            fg_color="transparent", hover_color="#2c3e50", anchor="w")
        btn.pack(pady=5, padx=15, fill="x") # وضع الـ padx هنا بدلاً من تعريف الزر

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="System Performance", font=("Segoe UI", 24, "bold")).pack(pady=20, anchor="w")
        
        self.cpu_lbl = ctk.CTkLabel(self.main_frame, text="CPU Usage: 0%", font=("Segoe UI", 14))
        self.cpu_lbl.pack(anchor="w", padx=20)
        self.cpu_bar = ctk.CTkProgressBar(self.main_frame, progress_color="#3498db")
        self.cpu_bar.pack(pady=(5, 20), fill="x", padx=20)

        self.ram_lbl = ctk.CTkLabel(self.main_frame, text="RAM Usage: 0%", font=("Segoe UI", 14))
        self.ram_lbl.pack(anchor="w", padx=20)
        self.ram_bar = ctk.CTkProgressBar(self.main_frame, progress_color="#2ecc71")
        self.ram_bar.pack(pady=(5, 20), fill="x", padx=20)
        
        self.update_stats()

    def update_stats(self):
        if hasattr(self, 'cpu_bar'):
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.cpu_lbl.configure(text=f"CPU Usage: {cpu}%")
                self.cpu_bar.set(cpu/100)
                self.ram_lbl.configure(text=f"RAM Usage: {ram}%")
                self.ram_bar.set(ram/100)
                self.after(1000, self.update_stats)
            except: pass

    def show_cleaner(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Deep System Cleaner", font=("Segoe UI", 24, "bold")).pack(pady=20, anchor="w")
        ctk.CTkLabel(self.main_frame, text="Cleans Temporary files, Update cache, and Logs.", font=("Segoe UI", 14)).pack(pady=5, anchor="w")
        
        self.btn_clean = ctk.CTkButton(self.main_frame, text="Run Deep Clean", 
                                       command=self.execute_clean, fg_color="#e67e22", hover_color="#d35400", height=45)
        self.btn_clean.pack(pady=30)
        self.res_lbl = ctk.CTkLabel(self.main_frame, text="", font=("Segoe UI", 14))
        self.res_lbl.pack()

    def execute_clean(self):
        self.btn_clean.configure(state="disabled", text="Cleaning...")
        self.update()
        files, size = self.optimizer.clean_all_junk()
        self.res_lbl.configure(text=f"Successfully cleaned {files} items!\nTotal Space Freed: {size} MB", text_color="#2ecc71")
        self.btn_clean.configure(state="normal", text="Run Deep Clean")

    def show_profiles_manager(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="User Profiles Manager", font=("Segoe UI", 24, "bold")).pack(pady=20, anchor="w")
        
        warn_box = ctk.CTkFrame(self.main_frame, fg_color="#3e1a1a", border_width=1, border_color="#c0392b")
        warn_box.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(warn_box, text="DANGER ZONE", text_color="#e74c3c", font=("Segoe UI", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(warn_box, text="This will permanently delete all inactive Domain/Local profiles.\nAdministrator and Your Current Session will be skipped.", 
                     text_color="white", font=("Segoe UI", 13)).pack(pady=(0, 15))

        self.btn_profile = ctk.CTkButton(self.main_frame, text="Delete All Inactive Profiles", 
                                        fg_color="#c0392b", hover_color="#a93226", height=45,
                                        command=self.execute_profile_clean)
        self.btn_profile.pack(pady=30)
        self.profile_res = ctk.CTkLabel(self.main_frame, text="", font=("Segoe UI", 14))
        self.profile_res.pack()

    def execute_profile_clean(self):
        self.btn_profile.configure(state="disabled", text="Processing Users...")
        self.update()
        success, msg = self.optimizer.delete_inactive_profiles()
        self.profile_res.configure(text=msg, text_color="#2ecc71" if success else "#e74c3c")
        self.btn_profile.configure(state="normal", text="Delete All Inactive Profiles")

    def show_repair(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="System Repair Tools", font=("Segoe UI", 24, "bold")).pack(pady=20, anchor="w")
        ctk.CTkLabel(self.main_frame, text="Use these tools to fix corrupted Windows files.", font=("Segoe UI", 14)).pack(pady=5, anchor="w")

        ctk.CTkButton(self.main_frame, text="Run SFC System Scan", 
                      command=self.optimizer.run_sfc_scan, height=40, fg_color="#2980b9").pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()