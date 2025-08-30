import customtkinter as ctk
import psutil
import platform
import socket
from datetime import datetime
import threading
import time
from tkinter import messagebox

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SystemInfoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("System Information Dashboard")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Sidebar title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="System Dashboard", 
                                      font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Sidebar buttons
        self.system_button = ctk.CTkButton(self.sidebar_frame, text="System Info", 
                                          command=self.show_system_info)
        self.system_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.disk_button = ctk.CTkButton(self.sidebar_frame, text="Disk Info", 
                                        command=self.show_disk_info)
        self.disk_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.process_button = ctk.CTkButton(self.sidebar_frame, text="Process Manager", 
                                           command=self.show_process_manager)
        self.process_button.grid(row=3, column=0, padx=20, pady=10)
        
        # Appearance mode option menu
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, 
                                                            values=["Light", "Dark", "System"],
                                                            command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        # Scaling option menu
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, 
                                                    values=["80%", "90%", "100%", "110%", "120%"],
                                                    command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        # Set default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")
        
        # Create main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Title label for main content
        self.title_label = ctk.CTkLabel(self.main_frame, text="System Information", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Create content frame
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize data
        self.process_list = []
        self.update_thread = None
        self.stop_thread = False
        
        # Show system info by default
        self.show_system_info()
        
        # Start update thread
        self.start_update_thread()
    
    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_system_info(self):
        self.clear_content_frame()
        self.title_label.configure(text="System Information")
        
        # Get system information
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        # Create system info frame
        sys_info_frame = ctk.CTkFrame(self.content_frame)
        sys_info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        sys_info_frame.grid_columnconfigure(1, weight=1)
        
        # System information labels
        info_labels = [
            ("System", uname.system),
            ("Node Name", uname.node),
            ("Release", uname.release),
            ("Version", uname.version),
            ("Machine", uname.machine),
            ("Processor", uname.processor),
            ("Boot Time", boot_time.strftime("%Y-%m-%d %H:%M:%S")),
            ("IP Address", socket.gethostbyname(socket.gethostname()))
        ]
        
        for i, (label, value) in enumerate(info_labels):
            ctk.CTkLabel(sys_info_frame, text=f"{label}:", font=ctk.CTkFont(weight="bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5)
            ctk.CTkLabel(sys_info_frame, text=value).grid(
                row=i, column=1, sticky="w", padx=10, pady=5)
        
        # CPU usage frame
        cpu_frame = ctk.CTkFrame(self.content_frame)
        cpu_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        cpu_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(cpu_frame, text="CPU Usage:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        self.cpu_usage_label = ctk.CTkLabel(cpu_frame, text="0%")
        self.cpu_usage_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # CPU usage progress bar
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame)
        self.cpu_progress.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.cpu_progress.set(0)
        
        # Memory usage frame
        mem_frame = ctk.CTkFrame(self.content_frame)
        mem_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        mem_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(mem_frame, text="Memory Usage:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        self.mem_usage_label = ctk.CTkLabel(mem_frame, text="0%")
        self.mem_usage_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Memory usage progress bar
        self.mem_progress = ctk.CTkProgressBar(mem_frame)
        self.mem_progress.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.mem_progress.set(0)
        
        # Memory details
        mem = psutil.virtual_memory()
        mem_details = [
            ("Total", f"{mem.total / (1024**3):.2f} GB"),
            ("Available", f"{mem.available / (1024**3):.2f} GB"),
            ("Used", f"{mem.used / (1024**3):.2f} GB")
        ]
        
        for i, (label, value) in enumerate(mem_details):
            ctk.CTkLabel(mem_frame, text=f"{label}:", font=ctk.CTkFont(weight="bold")).grid(
                row=i+2, column=0, sticky="w", padx=10, pady=2)
            ctk.CTkLabel(mem_frame, text=value).grid(
                row=i+2, column=1, sticky="w", padx=10, pady=2)
    
    def show_disk_info(self):
        self.clear_content_frame()
        self.title_label.configure(text="Disk Information")
        
        # Get disk information
        disk_partitions = psutil.disk_partitions()
        
        # Create disk info frame
        disk_info_frame = ctk.CTkFrame(self.content_frame)
        disk_info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        disk_info_frame.grid_columnconfigure(1, weight=1)
        
        # Disk information labels
        row = 0
        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Device label
                ctk.CTkLabel(disk_info_frame, text=f"Device: {partition.device}", 
                            font=ctk.CTkFont(weight="bold")).grid(
                    row=row, column=0, sticky="w", padx=10, pady=(10, 2))
                row += 1
                
                # Mount point
                ctk.CTkLabel(disk_info_frame, text="Mountpoint:").grid(
                    row=row, column=0, sticky="w", padx=10, pady=2)
                ctk.CTkLabel(disk_info_frame, text=partition.mountpoint).grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1
                
                # File system type
                ctk.CTkLabel(disk_info_frame, text="File System:").grid(
                    row=row, column=0, sticky="w", padx=10, pady=2)
                ctk.CTkLabel(disk_info_frame, text=partition.fstype).grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1
                
                # Total size
                ctk.CTkLabel(disk_info_frame, text="Total Size:").grid(
                    row=row, column=0, sticky="w", padx=10, pady=2)
                ctk.CTkLabel(disk_info_frame, text=f"{usage.total / (1024**3):.2f} GB").grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1
                
                # Used space
                ctk.CTkLabel(disk_info_frame, text="Used Space:").grid(
                    row=row, column=0, sticky="w", padx=10, pady=2)
                ctk.CTkLabel(disk_info_frame, text=f"{usage.used / (1024**3):.2f} GB").grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1
                
                # Free space
                ctk.CTkLabel(disk_info_frame, text="Free Space:").grid(
                    row=row, column=0, sticky="w", padx=10, pady=2)
                ctk.CTkLabel(disk_info_frame, text=f"{usage.free / (1024**3):.2f} GB").grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1
                
                # Usage percentage
                ctk.CTkLabel(disk_info_frame, text="Usage:").grid(
                    row=row, column=0, sticky="w", padx=10, pady=2)
                usage_percent = ctk.CTkLabel(disk_info_frame, text=f"{usage.percent}%")
                usage_percent.grid(row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1
                
                # Usage progress bar
                progress = ctk.CTkProgressBar(disk_info_frame)
                progress.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 10))
                progress.set(usage.percent / 100)
                row += 1
                
                # Separator
                separator = ctk.CTkFrame(disk_info_frame, height=2, fg_color="gray")
                separator.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
                row += 1
                
            except PermissionError:
                # Skip disks that require special permissions
                continue
    
    def show_process_manager(self):
        self.clear_content_frame()
        self.title_label.configure(text="Process Manager")
        
        # Create process manager frame
        process_frame = ctk.CTkFrame(self.content_frame)
        process_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        process_frame.grid_columnconfigure(0, weight=1)
        process_frame.grid_rowconfigure(1, weight=1)
        
        # Search frame
        search_frame = ctk.CTkFrame(process_frame)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_processes)
        
        # Refresh button
        refresh_button = ctk.CTkButton(search_frame, text="Refresh", command=self.refresh_processes)
        refresh_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Process list frame
        list_frame = ctk.CTkFrame(process_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Create process list with headers
        headers = ["PID", "Name", "CPU %", "Memory %", "Status", "Actions"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(list_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Create scrollable frame for processes
        self.process_list_frame = ctk.CTkScrollableFrame(list_frame)
        self.process_list_frame.grid(row=1, column=0, columnspan=len(headers), sticky="nsew", padx=5, pady=5)
        self.process_list_frame.grid_columnconfigure(1, weight=1)
        
        # Populate process list
        self.refresh_processes()
    
    def refresh_processes(self):
        # Clear existing process list
        for widget in self.process_list_frame.winfo_children():
            widget.destroy()
        
        # Get process list
        self.process_list = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                self.process_list.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage (descending)
        self.process_list.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        # Display processes
        self.display_processes()
    
    def display_processes(self):
        # Filter processes based on search term
        search_term = self.search_entry.get().lower()
        filtered_processes = self.process_list
        if search_term:
            filtered_processes = [p for p in self.process_list if search_term in p['name'].lower()]
        
        # Display processes
        for i, proc in enumerate(filtered_processes):
            # PID
            pid_label = ctk.CTkLabel(self.process_list_frame, text=str(proc['pid']))
            pid_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            # Name
            name_label = ctk.CTkLabel(self.process_list_frame, text=proc['name'])
            name_label.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            
            # CPU %
            cpu_label = ctk.CTkLabel(self.process_list_frame, text=f"{proc['cpu_percent'] or 0:.1f}%")
            cpu_label.grid(row=i, column=2, padx=5, pady=2, sticky="w")
            
            # Memory %
            mem_label = ctk.CTkLabel(self.process_list_frame, text=f"{proc['memory_percent'] or 0:.1f}%")
            mem_label.grid(row=i, column=3, padx=5, pady=2, sticky="w")
            
            # Status
            status_label = ctk.CTkLabel(self.process_list_frame, text=proc['status'])
            status_label.grid(row=i, column=4, padx=5, pady=2, sticky="w")
            
            # End process button
            end_button = ctk.CTkButton(self.process_list_frame, text="End Process", 
                                      width=80, command=lambda pid=proc['pid']: self.end_process(pid))
            end_button.grid(row=i, column=5, padx=5, pady=2)
    
    def filter_processes(self, event):
        self.display_processes()
    
    def end_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            messagebox.showinfo("Success", f"Process {pid} terminated successfully")
            self.refresh_processes()
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", f"Process {pid} does not exist")
        except psutil.AccessDenied:
            messagebox.showerror("Error", f"Access denied to terminate process {pid}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to terminate process {pid}: {str(e)}")
    
    def update_system_info(self):
        # Update CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_usage_label.configure(text=f"{cpu_percent}%")
        self.cpu_progress.set(cpu_percent / 100)
        
        # Update memory usage
        mem = psutil.virtual_memory()
        self.mem_usage_label.configure(text=f"{mem.percent}%")
        self.mem_progress.set(mem.percent / 100)
    
    def start_update_thread(self):
        def update_loop():
            while not self.stop_thread:
                try:
                    self.update_system_info()
                    time.sleep(2)
                except:
                    break
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def on_closing(self):
        self.stop_thread = True
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        self.destroy()

if __name__ == "__main__":
    app = SystemInfoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()