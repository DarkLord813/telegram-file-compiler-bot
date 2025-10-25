import os

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'your_bot_token_here')

# File handling configuration
MAX_FILE_SIZE = 8 * 1024 * 1024 * 1024  # 8GB
MAX_FILES_PER_USER = 100
TEMP_DIR = "temp_files"

# Webhook configuration (for production)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your_webhook_secret_here')

# Archive configuration
SUPPORTED_ARCHIVE_FORMATS = {
    'zip': 'ZIP Archive',
    '7z': '7-Zip Archive', 
    'tar': 'TAR Archive',
    'tar.gz': 'GZipped TAR'
}

EXTRACTABLE_ARCHIVES = {
    'apk', 'zip', '7z', 'tar', 'tar.gz', 'gz'
}
