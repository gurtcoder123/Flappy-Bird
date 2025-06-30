import os

# Game Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics Settings
GRAVITY = 0.5
JUMP_STRENGTH = -9
BIRD_WIDTH = 19
BIRD_HEIGHT = 16

# Obstacle Settings
PILLAR_WIDTH = 50
GAP_SIZE_MIN = 180
GAP_SIZE_MAX = 220
GAP_POSITION_MIN = 180
GAP_POSITION_MAX = 380
OBSTACLE_SPEED = 3
INITIAL_OBSTACLE_SPACING = 400
MINIMUM_OBSTACLE_SPACING = 200

# Background Settings
GROUND_HEIGHT = 100
SKY_HEIGHT = 500
BUILDING_WIDTH = 100
BUILDING_HEIGHT_MIN = 60
BUILDING_HEIGHT_MAX = 180

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 128, 0)
DARK_GREEN = (34, 139, 34)
FOREST_GREEN = (34, 139, 34)
SKY_BLUE = (135, 206, 235)
BRIGHT_GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Email Settings
# Support multiple email providers
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "noreply@jumpybird.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "default_password")

# Auto-detect SMTP settings based on email provider
if EMAIL_ADDRESS.endswith("@gmail.com"):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
elif EMAIL_ADDRESS.endswith("@outlook.com") or EMAIL_ADDRESS.endswith("@hotmail.com"):
    SMTP_SERVER = "smtp-mail.outlook.com"  
    SMTP_PORT = 587
elif EMAIL_ADDRESS.endswith("@yahoo.com"):
    SMTP_SERVER = "smtp.mail.yahoo.com"
    SMTP_PORT = 587
else:
    # Default to Gmail settings, can be overridden with environment variables
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Font Settings
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
