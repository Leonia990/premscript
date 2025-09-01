import pygame
import pygame.gfxdraw
import time
import math
from datetime import datetime

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Discord Auto-Poster with ImGui-style Interface")

# Colors
BACKGROUND = (30, 30, 40)
PANEL = (45, 45, 55)
ACCENT = (88, 101, 242)
BUTTON = (78, 93, 240)
BUTTON_HOVER = (98, 113, 255)
BUTTON_DELETE = (200, 70, 70)
BUTTON_DELETE_HOVER = (220, 90, 90)
TEXT = (220, 220, 220)
TEXT_INPUT = (60, 60, 70)
SUCCESS = (87, 242, 135)
ERROR = (242, 87, 87)
WARNING = (242, 202, 87)
INFO = (87, 172, 242)

# Fonts
font_large = pygame.font.SysFont("Arial", 28)
font_medium = pygame.font.SysFont("Arial", 20)
font_small = pygame.font.SysFont("Arial", 16)

# App state
class Channel:
    def __init__(self, channel_id="", user_id="", webhook_url="", message="", interval=3600):
        self.channel_id = channel_id
        self.user_id = user_id
        self.webhook_url = webhook_url
        self.message = message
        self.interval = interval
        self.last_posted = "Never"

channels = []
logs = []
bot_token = "your_bot_token_here"
selected_channel_index = -1
editing_field = None
input_text = ""
status_message = "Welcome to Discord Auto-Poster"
status_color = INFO
last_update = time.time()
next_post_time = time.time() + 3600
auto_posting = False

# Add a default channel
channels.append(Channel())

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
        status_color = ERROR
        last_update = time.time()
        logs.append(("ERROR", status_message))
        return False
        
    if not channel.message:
        status_message = f"Error: No message configured for channel {channel_index+1}"
        status_color = ERROR
        last_update = time.time()
        logs.append(("ERROR", status_message))
        return False
    
    # Simulate sending message
    status_message = f"Message sent to channel {channel_index+1} at {current_time}"
    status_color = SUCCESS
    last_update = time.time()
    channel.last_posted = current_time
    logs.append(("SUCCESS", status_message))
    return True

# Draw a rounded rectangle
def draw_rounded_rect(surface, rect, color, corner_radius):
    """Draw a rectangle with rounded corners"""
    x, y, width, height = rect
    if width < 2 * corner_radius:
        corner_radius = width // 2
    if height < 2 * corner_radius:
        corner_radius = height // 2
    
    # Draw the main rectangle
    pygame.draw.rect(surface, color, (x + corner_radius, y, width - 2 * corner_radius, height))
    pygame.draw.rect(surface, color, (x, y + corner_radius, width, height - 2 * corner_radius))
    
    # Draw the four corner circles
    pygame.draw.circle(surface, color, (x + corner_radius, y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + width - corner_radius, y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + corner_radius, y + height - corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + width - corner_radius, y + height - corner_radius), corner_radius)

# Draw a button
def draw_button(text, rect, hover=False, color=BUTTON, hover_color=BUTTON_HOVER):
    btn_color = hover_color if hover else color
    draw_rounded_rect(screen, rect, btn_color, 5)
    text_surf = font_medium.render(text, True, TEXT)
    text_rect = text_surf.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
    screen.blit(text_surf, text_rect)

# Draw a text input field
def draw_input_field(text, rect, active=False):
    color = ACCENT if active else TEXT_INPUT
    draw_rounded_rect(screen, rect, color, 5)
    draw_rounded_rect(screen, (rect[0]+1, rect[1]+1, rect[2]-2, rect[3]-2), PANEL, 5)
    
    # Render text with ellipsis if too long
    text_surf = font_medium.render(text, True, TEXT)
    if text_surf.get_width() > rect[2] - 20:
        # Truncate text with ellipsis
        while text and text_surf.get_width() > rect[2] - 20:
            text = text[:-1]
            text_surf = font_medium.render(text + "...", True, TEXT)
        text += "..."
    
    text_rect = text_surf.get_rect(midleft=(rect[0] + 10, rect[1] + rect[3] // 2))
    screen.blit(text_surf, text_rect)
    
    # Draw cursor if active
    if active and int(time.time() * 2) % 2 == 0:
        cursor_x = text_rect.right + 2 if text else rect[0] + 10
        pygame.draw.line(screen, TEXT, (cursor_x, rect[1] + 10), (cursor_x, rect[1] + rect[3] - 10), 2)

# Draw a panel
def draw_panel(rect):
    draw_rounded_rect(screen, rect, PANEL, 10)

# Draw text
def draw_text(text, pos, color=TEXT, font=font_medium):
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, pos)

# Draw bot settings panel
def draw_bot_settings():
    global editing_field, input_text, bot_token
    
    draw_panel((20, 20, 960, 100))
    draw_text("Bot Settings", (30, 30), font=font_large)
    
    draw_text("Bot Token:", (40, 70))
    token_rect = pygame.Rect(150, 65, 700, 40)
    draw_input_field(bot_token, token_rect, editing_field == "token")
    
    # Handle clicks on input fields
    if pygame.mouse.get_pressed()[0]:
        if token_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = "token"
            input_text = bot_token
        elif not token_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = None

# Draw channel list panel
def draw_channel_list():
    global selected_channel_index
    
    draw_panel((20, 140, 300, 400))
    draw_text("Channels", (30, 150), font=font_large)
    
    # Draw channel buttons
    for i in range(len(channels)):
        rect = pygame.Rect(30, 190 + i*50, 260, 40)
        hover = rect.collidepoint(pygame.mouse.get_pos())
        color = ACCENT if i == selected_channel_index else BUTTON
        draw_button(f"Channel {i+1}", rect, hover, color)
        
        if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            selected_channel_index = i
            editing_field = None
    
    # Draw add channel button
    add_rect = pygame.Rect(30, 190 + len(channels)*50, 125, 40)
    hover = add_rect.collidepoint(pygame.mouse.get_pos())
    draw_button("Add Channel", add_rect, hover)
    
    if hover and pygame.mouse.get_pressed()[0]:
        channels.append(Channel())
        selected_channel_index = len(channels) - 1
        editing_field = None
    
    # Draw delete channel button
    if selected_channel_index >= 0:
        delete_rect = pygame.Rect(165, 190 + len(channels)*50, 125, 40)
        hover = delete_rect.collidepoint(pygame.mouse.get_pos())
        draw_button("Delete", delete_rect, hover, BUTTON_DELETE, BUTTON_DELETE_HOVER)
        
        if hover and pygame.mouse.get_pressed()[0]:
            if len(channels) > 1:
                channels.pop(selected_channel_index)
                selected_channel_index = min(selected_channel_index, len(channels) - 1)
            else:
                status_message = "Cannot delete the only channel"
                status_color = WARNING
                logs.append(("WARNING", status_message))

# Draw channel editor panel
def draw_channel_editor():
    global editing_field, input_text, selected_channel_index
    
    if selected_channel_index < 0:
        return
        
    channel = channels[selected_channel_index]
    
    draw_panel((340, 140, 640, 400))
    draw_text(f"Channel {selected_channel_index+1} Settings", (350, 150), font=font_large)
    
    y_pos = 190
    # Channel ID
    draw_text("Channel ID:", (360, y_pos))
    channel_id_rect = pygame.Rect(500, y_pos-5, 460, 40)
    draw_input_field(channel.channel_id, channel_id_rect, editing_field == "channel_id")
    y_pos += 50
    
    # User ID
    draw_text("User ID:", (360, y_pos))
    user_id_rect = pygame.Rect(500, y_pos-5, 460, 40)
    draw_input_field(channel.user_id, user_id_rect, editing_field == "user_id")
    y_pos += 50
    
    # Webhook URL
    draw_text("Webhook URL:", (360, y_pos))
    webhook_rect = pygame.Rect(500, y_pos-5, 460, 40)
    draw_input_field(channel.webhook_url, webhook_rect, editing_field == "webhook")
    y_pos += 50
    
    # Message
    draw_text("Message:", (360, y_pos))
    message_rect = pygame.Rect(500, y_pos-5, 460, 40)
    draw_input_field(channel.message, message_rect, editing_field == "message")
    y_pos += 50
    
    # Interval
    draw_text("Interval (seconds):", (360, y_pos))
    interval_rect = pygame.Rect(500, y_pos-5, 460, 40)
    draw_input_field(str(channel.interval), interval_rect, editing_field == "interval")
    y_pos += 50
    
    # Last posted
    draw_text(f"Last Posted: {channel.last_posted}", (360, y_pos))
    
    # Handle clicks on input fields
    if pygame.mouse.get_pressed()[0]:
        if channel_id_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = "channel_id"
            input_text = channel.channel_id
        elif user_id_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = "user_id"
            input_text = channel.user_id
        elif webhook_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = "webhook"
            input_text = channel.webhook_url
        elif message_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = "message"
            input_text = channel.message
        elif interval_rect.collidepoint(pygame.mouse.get_pos()):
            editing_field = "interval"
            input_text = str(channel.interval)
        elif not any([channel_id_rect.collidepoint(pygame.mouse.get_pos()),
                     user_id_rect.collidepoint(pygame.mouse.get_pos()),
                     webhook_rect.collidepoint(pygame.mouse.get_pos()),
                     message_rect.collidepoint(pygame.mouse.get_pos()),
                     interval_rect.collidepoint(pygame.mouse.get_pos())]):
            editing_field = None
    
    # Draw test button
    test_rect = pygame.Rect(360, y_pos+40, 280, 40)
    hover = test_rect.collidepoint(pygame.mouse.get_pos())
    draw_button("Test Post Now", test_rect, hover)
    
    if hover and pygame.mouse.get_pressed()[0]:
        send_message(selected_channel_index)

# Draw status panel
def draw_status_panel():
    global auto_posting, next_post_time
    
    draw_panel((20, 560, 960, 120))
    draw_text("Status & Controls", (30, 570), font=font_large)
    
    # Draw status message
    draw_text(status_message, (40, 610), color=status_color)
    
    # Draw last update time
    elapsed = time.time() - last_update
    time_text = f"Last update: {int(elapsed)} seconds ago"
    draw_text(time_text, (40, 640), color=TEXT)
    
    # Draw auto-post toggle
    toggle_rect = pygame.Rect(700, 610, 130, 40)
    hover = toggle_rect.collidepoint(pygame.mouse.get_pos())
    btn_text = "Disable" if auto_posting else "Enable"
    btn_color = SUCCESS if auto_posting else WARNING
    btn_hover = (SUCCESS[0]-20, SUCCESS[1]-20, SUCCESS[2]-20) if auto_posting else (WARNING[0]-20, WARNING[1]-20, WARNING[2]-20)
    draw_button(btn_text, toggle_rect, hover, btn_color, btn_hover)
    
    if hover and pygame.mouse.get_pressed()[0]:
        auto_posting = not auto_posting
        status_message = "Auto-posting " + ("enabled" if auto_posting else "disabled")
        status_color = SUCCESS if auto_posting else WARNING
        logs.append(("INFO", status_message))
    
    # Draw next post time
    if auto_posting:
        next_post = max(0, next_post_time - time.time())
        next_text = f"Next post in: {int(next_post)} seconds"
        draw_text(next_text, (700, 650), color=INFO)

# Draw logs panel
def draw_logs_panel():
    draw_panel((340, 560, 340, 120))
    draw_text("Logs", (350, 570), font=font_large)
    
    # Show last 3 logs
    for i, log in enumerate(logs[-3:]):
        log_type, message = log
        color = INFO
        if log_type == "ERROR":
            color = ERROR
        elif log_type == "SUCCESS":
            color = SUCCESS
        elif log_type == "WARNING":
            color = WARNING
            
        draw_text(f"{log_type}: {message}", (350, 600 + i*20), color=color, font=font_small)

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if editing_field:
                if event.key == pygame.K_RETURN:
                    # Save changes
                    if selected_channel_index >= 0:
                        channel = channels[selected_channel_index]
                        if editing_field == "channel_id":
                            channel.channel_id = input_text
                        elif editing_field == "user_id":
                            channel.user_id = input_text
                        elif editing_field == "webhook":
                            channel.webhook_url = input_text
                        elif editing_field == "message":
                            channel.message = input_text
                        elif editing_field == "interval":
                            try:
                                channel.interval = int(input_text)
                            except ValueError:
                                pass
                        elif editing_field == "token":
                            bot_token = input_text
                    editing_field = None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    # Only allow numbers for interval field
                    if editing_field == "interval":
                        if event.unicode.isdigit():
                            input_text += event.unicode
                    else:
                        input_text += event.unicode
    
    # Update input text for active field
    if editing_field == "token":
        bot_token = input_text
    elif selected_channel_index >= 0:
        channel = channels[selected_channel_index]
        if editing_field == "channel_id":
            channel.channel_id = input_text
        elif editing_field == "user_id":
            channel.user_id = input_text
        elif editing_field == "webhook":
            channel.webhook_url = input_text
        elif editing_field == "message":
            channel.message = input_text
        elif editing_field == "interval":
            if input_text.isdigit() or input_text == "":
                channel.interval = input_text
    
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
    
    # Clear screen
    screen.fill(BACKGROUND)
    
    # Draw UI elements
    draw_bot_settings()
    draw_channel_list()
    draw_channel_editor()
    draw_status_panel()
    draw_logs_panel()
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()