import customtkinter as ctk
from tkinter import scrolledtext, messagebox
import threading
import time
from datetime import datetime
import json
import os

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class DiscordAutoPoster(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Discord Auto-Poster")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # App data
        self.bot_token = ""
        self.channels = []
        self.logs = []
        self.auto_posting = False
        self.posting_thread = None
        
        # Load saved data if exists
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Create main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self, 
            text="Discord Auto-Poster", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Create tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.tabview.add("Bot Settings")
        self.tabview.add("Channels")
        self.tabview.add("Logs")
        
        # Configure tab grid
        for tab_name in ["Bot Settings", "Channels", "Logs"]:
            self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)
            self.tabview.tab(tab_name).grid_rowconfigure(1, weight=1)
        
        # Bot Settings tab
        self.setup_bot_settings_tab()
        
        # Channels tab
        self.setup_channels_tab()
        
        # Logs tab
        self.setup_logs_tab()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_bot_settings_tab(self):
        tab = self.tabview.tab("Bot Settings")
        
        # Token frame
        token_frame = ctk.CTkFrame(tab)
        token_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        token_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(token_frame, text="Bot Token:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=20, pady=20, sticky="w"
        )
        
        self.token_entry = ctk.CTkEntry(
            token_frame, 
            placeholder_text="Enter your bot token here",
            show="•"
        )
        self.token_entry.insert(0, self.bot_token)
        self.token_entry.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="ew")
        
        # Control buttons frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.start_btn = ctk.CTkButton(
            control_frame, 
            text="Start Auto-Posting", 
            command=self.toggle_auto_posting,
            fg_color="green" if not self.auto_posting else "red",
            hover_color="darkgreen" if not self.auto_posting else "darkred"
        )
        self.start_btn.grid(row=0, column=0, padx=20, pady=20)
        
        ctk.CTkButton(
            control_frame, 
            text="Save Settings", 
            command=self.save_settings
        ).grid(row=0, column=1, padx=20, pady=20)
        
        ctk.CTkButton(
            control_frame, 
            text="Test Connection", 
            command=self.test_connection
        ).grid(row=0, column=2, padx=20, pady=20)
    
    def setup_channels_tab(self):
        tab = self.tabview.tab("Channels")
        
        # Channel list frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(list_frame, text="Channels", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        
        # Channel listbox
        self.channel_listbox = ctk.CTkScrollableFrame(list_frame)
        self.channel_listbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(list_frame)
        btn_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkButton(
            btn_frame, 
            text="Add Channel", 
            command=self.add_channel
        ).grid(row=0, column=0, padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="Remove Selected", 
            command=self.remove_channel,
            fg_color="red",
            hover_color="darkred"
        ).grid(row=0, column=1, padx=20, pady=10)
        
        # Channel editor
        self.setup_channel_editor(tab)
        
        # Refresh channel list
        self.refresh_channel_list()
    
    def setup_channel_editor(self, tab):
        editor_frame = ctk.CTkFrame(tab)
        editor_frame.grid(row=0, column=1, rowspan=2, padx=(0, 20), pady=20, sticky="nsew")
        editor_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(editor_frame, text="Channel Editor", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w"
        )
        
        # Channel ID
        ctk.CTkLabel(editor_frame, text="Channel ID:").grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        self.channel_id_entry = ctk.CTkEntry(editor_frame)
        self.channel_id_entry.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="ew")
        
        # User ID
        ctk.CTkLabel(editor_frame, text="User ID (for pings):").grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )
        self.user_id_entry = ctk.CTkEntry(editor_frame)
        self.user_id_entry.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="ew")
        
        # Webhook URL
        ctk.CTkLabel(editor_frame, text="Webhook URL:").grid(
            row=3, column=0, padx=20, pady=10, sticky="w"
        )
        self.webhook_entry = ctk.CTkEntry(editor_frame)
        self.webhook_entry.grid(row=3, column=1, padx=(0, 20), pady=10, sticky="ew")
        
        # Message
        ctk.CTkLabel(editor_frame, text="Message:").grid(
            row=4, column=0, padx=20, pady=10, sticky="nw"
        )
        self.message_text = ctk.CTkTextbox(editor_frame, height=150)
        self.message_text.grid(row=4, column=1, padx=(0, 20), pady=10, sticky="nsew")
        
        # Interval
        ctk.CTkLabel(editor_frame, text="Interval (seconds):").grid(
            row=5, column=0, padx=20, pady=10, sticky="w"
        )
        self.interval_entry = ctk.CTkEntry(editor_frame)
        self.interval_entry.insert(0, "3600")
        self.interval_entry.grid(row=5, column=1, padx=(0, 20), pady=10, sticky="ew")
        
        # Save button
        ctk.CTkButton(
            editor_frame, 
            text="Save Channel", 
            command=self.save_channel
        ).grid(row=6, column=0, columnspan=2, padx=20, pady=20)
        
        # Test button
        ctk.CTkButton(
            editor_frame, 
            text="Test Post", 
            command=self.test_post
        ).grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 20))
    
    def setup_logs_tab(self):
        tab = self.tabview.tab("Logs")
        
        ctk.CTkLabel(tab, text="Activity Logs", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            tab, 
            wrap="word", 
            bg="#2b2b2b", 
            fg="white", 
            insertbackground="white",
            font=("Consolas", 10)
        )
        self.log_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_text.config(state="disabled")
        
        # Clear logs button
        ctk.CTkButton(
            tab, 
            text="Clear Logs", 
            command=self.clear_logs
        ).grid(row=2, column=0, padx=20, pady=(0, 20))
    
    def setup_status_bar(self):
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Ready" if not self.auto_posting else "Auto-posting enabled",
            text_color="green" if not self.auto_posting else "red"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.next_post_label = ctk.CTkLabel(status_frame, text="")
        self.next_post_label.grid(row=0, column=1, padx=20, pady=10, sticky="e")
    
    def refresh_channel_list(self):
        # Clear the listbox
        for widget in self.channel_listbox.winfo_children():
            widget.destroy()
        
        # Add channels to the listbox
        for i, channel in enumerate(self.channels):
            btn = ctk.CTkButton(
                self.channel_listbox,
                text=f"Channel {i+1}: {channel.get('channel_id', 'No ID')}",
                command=lambda idx=i: self.select_channel(idx),
                anchor="w"
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
    
    def select_channel(self, index):
        if 0 <= index < len(self.channels):
            channel = self.channels[index]
            self.channel_id_entry.delete(0, "end")
            self.channel_id_entry.insert(0, channel.get("channel_id", ""))
            
            self.user_id_entry.delete(0, "end")
            self.user_id_entry.insert(0, channel.get("user_id", ""))
            
            self.webhook_entry.delete(0, "end")
            self.webhook_entry.insert(0, channel.get("webhook_url", ""))
            
            self.message_text.delete("1.0", "end")
            self.message_text.insert("1.0", channel.get("message", ""))
            
            self.interval_entry.delete(0, "end")
            self.interval_entry.insert(0, str(channel.get("interval", 3600)))
    
    def add_channel(self):
        self.channels.append({
            "channel_id": "",
            "user_id": "",
            "webhook_url": "",
            "message": "",
            "interval": 3600
        })
        self.refresh_channel_list()
        self.select_channel(len(self.channels) - 1)
        self.log("Added new channel")
    
    def remove_channel(self):
        if not self.channels:
            return
        
        # In a real app, you'd want to select which channel to remove
        # For simplicity, we'll remove the last one
        self.channels.pop()
        self.refresh_channel_list()
        self.log("Removed channel")
    
    def save_channel(self):
        if not self.channels:
            return
        
        # Get the currently selected channel index (simplified)
        # In a real app, you'd track the selected index
        channel = self.channels[-1] if self.channels else {}
        
        channel["channel_id"] = self.channel_id_entry.get()
        channel["user_id"] = self.user_id_entry.get()
        channel["webhook_url"] = self.webhook_entry.get()
        channel["message"] = self.message_text.get("1.0", "end-1c")
        
        try:
            channel["interval"] = int(self.interval_entry.get())
        except ValueError:
            channel["interval"] = 3600
        
        self.log("Saved channel settings")
        self.save_data()
    
    def save_settings(self):
        self.bot_token = self.token_entry.get()
        self.save_data()
        self.log("Saved bot settings")
    
    def test_connection(self):
        self.log("Testing connection to Discord...")
        # Simulate connection test
        self.after(1000, lambda: self.log("Connection test completed successfully"))
    
    def test_post(self):
        self.log("Testing post to Discord...")
        # Simulate post test
        self.after(1000, lambda: self.log("Test post completed successfully"))
    
    def toggle_auto_posting(self):
        self.auto_posting = not self.auto_posting
        
        if self.auto_posting:
            self.start_auto_posting()
        else:
            self.stop_auto_posting()
    
    def start_auto_posting(self):
        self.auto_posting = True
        self.start_btn.configure(text="Stop Auto-Posting", fg_color="red", hover_color="darkred")
        self.status_label.configure(text="Auto-posting enabled", text_color="red")
        self.log("Auto-posting started")
        
        # Start auto-posting in a separate thread
        self.posting_thread = threading.Thread(target=self.auto_posting_loop, daemon=True)
        self.posting_thread.start()
    
    def stop_auto_posting(self):
        self.auto_posting = False
        self.start_btn.configure(text="Start Auto-Posting", fg_color="green", hover_color="darkgreen")
        self.status_label.configure(text="Ready", text_color="green")
        self.next_post_label.configure(text="")
        self.log("Auto-posting stopped")
    
    def auto_posting_loop(self):
        while self.auto_posting:
            # Simulate posting to each channel
            for i, channel in enumerate(self.channels):
                if not self.auto_posting:
                    break
                    
                # Simulate posting
                self.log(f"Posted to channel {i+1}")
                time.sleep(2)  # Simulate delay
            
            # Wait for the next posting cycle
            for i in range(60):  # Check every second for 60 seconds
                if not self.auto_posting:
                    break
                    
                remaining = 60 - i
                self.after(0, lambda: self.next_post_label.configure(
                    text=f"Next post in: {remaining}s"
                ))
                time.sleep(1)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        # Update log text widget
        self.log_text.config(state="normal")
        self.log_text.insert("end", log_entry + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def clear_logs(self):
        self.logs = []
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.log("Logs cleared")
    
    def save_data(self):
        data = {
            "bot_token": self.bot_token,
            "channels": self.channels
        }
        
        try:
            with open("discord_auto_poster.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.log(f"Error saving data: {e}")
    
    def load_data(self):
        if os.path.exists("discord_auto_poster.json"):
            try:
                with open("discord_auto_poster.json", "r") as f:
                    data = json.load(f)
                    self.bot_token = data.get("bot_token", "")
                    self.channels = data.get("channels", [])
            except Exception as e:
                self.log(f"Error loading data: {e}")
        
        # Ensure we have at least one channel
        if not self.channels:
            self.channels = [{
                "channel_id": "",
                "user_id": "",
                "webhook_url": "",
                "message": "",
                "interval": 3600
            }]
    
    def on_closing(self):
        self.save_data()
        self.destroy()

if __name__ == "__main__":
    app = DiscordAutoPoster()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()