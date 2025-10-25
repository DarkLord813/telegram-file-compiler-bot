"""
Configuration file for Telegram File Compiler Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token from @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', "your_bot_token_here")

# Optional: Admin user IDs (for special features)
ADMIN_IDS = [7475473197, 7713987088]

# Optional: Maximum file size in bytes (default: 50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Optional: Maximum files per user
MAX_FILES_PER_USER = 20

# Optional: Temporary directory path
TEMP_DIR = "temp"

# Optional: Logging level
LOG_LEVEL = "INFO"

def validate_config():
    """Validate configuration"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError("BOT_TOKEN is required. Please set it in config.py or environment variables.")
