import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

import config
import utils
import archive_manager

logger = logging.getLogger(__name__)

class FileCompilationBot:
    def __init__(self):
        self.user_sessions = {}
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        utils.ensure_directory(config.TEMP_DIR)
        utils.cleanup_old_files(config.TEMP_DIR)
    
    # ... (keep all your existing methods exactly as they were)
    # ... (all the handle_ methods, keyboard methods, etc.)
    # ... (just make sure none of them call config.validate_config())

    def run_webhook(self, webhook_url=None, port=10000):
        """Run the bot in webhook mode (for production on Render)"""
        from telegram.ext import Application
        
        # Create application
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.handle_file))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_error_handler(self.error_handler)
        
        # Set webhook
        if webhook_url:
            application.bot.set_webhook(webhook_url)
            print(f"✅ Webhook set to: {webhook_url}")
        
        # Start webhook
        print("🚀 Starting bot in WEBHOOK mode...")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=config.BOT_TOKEN,
            webhook_url=webhook_url
        )
