import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer
import time
from datetime import datetime

# Initialize pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 1000, 700
pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Discord Auto-Poster with ImGui")

# Set up ImGui
imgui.create_context()
io = imgui.get_io()
io.display_size = (WIDTH, HEIGHT)
io.ini_file_name = "imgui.ini"

# Set up renderer
renderer = PygameRenderer()

# App state
class Channel:
    def __init__(self, channel_id="", user_id="", webhook_url="", message="", interval=3600):
        self.channel_id = channel_id
        self.user_id = user_id
        self.webhook_url = webhook_url
        self.message = message
        self.interval = interval
        self.last_posted = "Never"

channels = [Channel()]
logs = []
bot_token = "your_bot_token_here"
selected_channel_index = 0
status_message = "Welcome to Discord Auto-Poster"
status_color = (0.2, 0.6, 1.0, 1.0)
last_update = time.time()
next_post_time = time.time() + 3600
auto_posting = False
show_test_popup = False

# Simulated posting function
def send_message(channel_index):
    global status_message, status_color, last_update
    
    if channel_index < 0 or channel_index >= len(channels):
        return False
        
    channel = channels[channel_index]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if channel has required info
    if not channel.channel_id:
        status_message = f"Error: No channel ID configured for channel {channel_index+1}"
        status_color = (1.0, 0.3, 0.3, 1.0)
        last_update = time.time()
        logs.append(("ERROR", status_message))
        return False
        
    if not channel.message:
        status_message = f"Error: No message configured for channel {channel_index+1}"
        status_color = (1.0, 0.3, 0.3, 1.0)
        last_update = time.time()
        logs.append(("ERROR", status_message))
        return False
    
    # Simulate sending message
    status_message = f"Message sent to channel {channel_index+1} at {current_time}"
    status_color = (0.3, 1.0, 0.5, 1.0)
    last_update = time.time()
    channel.last_posted = current_time
    logs.append(("SUCCESS", status_message))
    return True

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            renderer.process_event(event)
    
    # Start new ImGui frame
    imgui.new_frame()
    
    # Handle auto-posting
    if auto_posting and time.time() >= next_post_time:
        # Find the channel with the smallest interval
        min_interval = float('inf')
        next_channel = -1
        
        for i, channel in enumerate(channels):
            if channel.interval and channel.interval < min_interval:
                min_interval = channel.interval
                next_channel = i
        
        if next_channel >= 0:
            send_message(next_channel)
            next_post_time = time.time() + min_interval
    
    # Set up the main window
    imgui.set_next_window_size(WIDTH, HEIGHT)
    imgui.set_next_window_position(0, 0)
    
    # Main window
    imgui.begin("Discord Auto-Poster", 
                flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | 
                      imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE)
    
    # Bot token section
    imgui.text_colored("Bot Token", 0.8, 0.8, 1.0)
    imgui.separator()
    changed, bot_token = imgui.input_text("##bottoken", bot_token, 256)
    imgui.dummy(0, 10)
    
    # Channel list section
    imgui.text_colored("Channels", 0.8, 0.8, 1.0)
    imgui.separator()
    
    # Channel selection buttons
    for i in range(len(channels)):
        if imgui.button(f"Channel {i+1}##channel{i}"):
            selected_channel_index = i
        if i < len(channels) - 1:
            imgui.same_line()
    
    imgui.dummy(0, 5)
    
    # Add/remove channel buttons
    if imgui.button("Add Channel"):
        channels.append(Channel())
        selected_channel_index = len(channels) - 1
    
    imgui.same_line()
    
    if imgui.button("Remove Channel") and len(channels) > 1:
        channels.pop(selected_channel_index)
        selected_channel_index = min(selected_channel_index, len(channels) - 1)
    
    imgui.dummy(0, 10)
    
    # Channel editor section
    if len(channels) > 0:
        channel = channels[selected_channel_index]
        
        imgui.text_colored(f"Channel {selected_channel_index+1} Settings", 0.8, 0.8, 1.0)
        imgui.separator()
        
        # Channel ID
        imgui.text("Channel ID:")
        changed, channel.channel_id = imgui.input_text("##channelid", channel.channel_id, 256)
        
        # User ID
        imgui.text("User ID:")
        changed, channel.user_id = imgui.input_text("##userid", channel.user_id, 256)
        
        # Webhook URL
        imgui.text("Webhook URL:")
        changed, channel.webhook_url = imgui.input_text("##webhook", channel.webhook_url, 256)
        
        # Message
        imgui.text("Message:")
        changed, channel.message = imgui.input_text_multiline("##message", channel.message, 512, 100)
        
        # Interval
        imgui.text("Interval (seconds):")
        changed, channel.interval = imgui.input_int("##interval", channel.interval)
        
        # Last posted
        imgui.text(f"Last Posted: {channel.last_posted}")
        
        # Test button
        if imgui.button("Test Post Now"):
            send_message(selected_channel_index)
    
    imgui.dummy(0, 10)
    
    # Status section
    imgui.text_colored("Status", 0.8, 0.8, 1.0)
    imgui.separator()
    
    # Status message
    imgui.text_colored(status_message, *status_color)
    
    # Last update time
    elapsed = time.time() - last_update
    imgui.text(f"Last update: {int(elapsed)} seconds ago")
    
    # Auto-post toggle
    changed, auto_posting = imgui.checkbox("Auto Posting", auto_posting)
    
    # Next post time
    if auto_posting:
        next_post = max(0, next_post_time - time.time())
        imgui.text(f"Next post in: {int(next_post)} seconds")
    
    imgui.dummy(0, 10)
    
    # Logs section
    imgui.text_colored("Logs", 0.8, 0.8, 1.0)
    imgui.separator()
    
    # Log display
    imgui.begin_child("Logs", 0, 100, True)
    for log_type, message in logs[-10:]:  # Show last 10 logs
        if log_type == "ERROR":
            imgui.text_colored(f"ERROR: {message}", 1.0, 0.3, 0.3)
        elif log_type == "SUCCESS":
            imgui.text_colored(f"SUCCESS: {message}", 0.3, 1.0, 0.5)
        elif log_type == "WARNING":
            imgui.text_colored(f"WARNING: {message}", 1.0, 0.8, 0.3)
        else:
            imgui.text_colored(f"INFO: {message}", 0.2, 0.6, 1.0)
    imgui.end_child()
    
    imgui.end()
    
    # Rendering
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    imgui.render()
    renderer.render(imgui.get_draw_data())
    
    pygame.display.flip()
    clock.tick(60)

# Cleanup
renderer.shutdown()
pygame.quit()