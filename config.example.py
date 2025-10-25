
## 4. `config.example.py`
```python
"""
Configuration file for Telegram File Compiler Bot
Copy this file to config.py and update with your values
"""

# Bot Token from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Optional: Admin user IDs (for special features)
ADMIN_IDS = [123456789]

# Optional: Maximum file size in bytes (default: 50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Optional: Maximum files per user
MAX_FILES_PER_USER = 20

# Optional: Temporary directory path
TEMP_DIR = "temp"

# Optional: Logging level
LOG_LEVEL = "INFO"
