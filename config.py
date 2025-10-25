import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the bot"""
    
    # Bot Token (priority: environment variable > config.py)
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # If BOT_TOKEN is not in environment, try to import from config
    if not BOT_TOKEN:
        try:
            from config import BOT_TOKEN as CONFIG_TOKEN
            BOT_TOKEN = CONFIG_TOKEN
        except ImportError:
            pass
    
    # Other settings with defaults
    ADMIN_IDS = getattr(__import__('config', fromlist=['']), 'ADMIN_IDS', [])
    MAX_FILE_SIZE = getattr(__import__('config', fromlist=['']), 'MAX_FILE_SIZE', 50 * 1024 * 1024)
    MAX_FILES_PER_USER = getattr(__import__('config', fromlist=['']), 'MAX_FILES_PER_USER', 20)
    TEMP_DIR = getattr(__import__('config', fromlist=['']), 'TEMP_DIR', 'temp')
    LOG_LEVEL = getattr(__import__('config', fromlist=['']), 'LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required. Please set it in config.py or environment variables.")
        
        if cls.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            raise ValueError("Please update BOT_TOKEN in config.py with your actual bot token")
