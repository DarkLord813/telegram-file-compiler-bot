"""
Configuration for Telegram File Compiler Bot - Optimized for Render.com
"""

import os

# Bot Token from Render environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Optional settings with defaults
ADMIN_IDS = os.environ.get('ADMIN_IDS', '').split(',') if os.environ.get('ADMIN_IDS') else []
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB default
MAX_FILES_PER_USER = int(os.environ.get('MAX_FILES_PER_USER', 20))
TEMP_DIR = os.environ.get('TEMP_DIR', 'temp')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

def validate_config():
    """Validate configuration"""
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable is not set.\n"
            "Please set it in your Render dashboard:\n"
            "1. Go to your service in Render\n"
            "2. Click on 'Environment'\n"
            "3. Add BOT_TOKEN with your bot token from @BotFather\n"
            "4. Redeploy your service"
        )
    
    # Check token format
    if ':' not in BOT_TOKEN:
        raise ValueError(
            "Invalid bot token format.\n"
            "Bot tokens should be in format: '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'\n"
            "Get your token from @BotFather on Telegram"
        )
    
    print("✅ Configuration validated successfully!")
    print(f"🤖 Bot token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-10:]}")
    print(f"📁 Temp directory: {TEMP_DIR}")
    print(f"📊 Max files per user: {MAX_FILES_PER_USER}")
    print(f"📦 Max file size: {MAX_FILE_SIZE // (1024*1024)}MB")
    return True
