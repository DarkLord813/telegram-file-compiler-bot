#!/usr/bin/env python3
"""
Telegram File Compiler Bot - Main Entry Point
"""

import logging
from bot import FileCompilationBot
import config
import utils

def main():
    """Main function to start the bot"""
    try:
        # Validate configuration
        config.validate_config()
        
        # Setup logging
        utils.setup_logging(config.LOG_LEVEL)
        
        # Create bot instance
        bot = FileCompilationBot()
        
        # Create application
        from telegram.ext import Application
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, bot.handle_file))
        application.add_handler(CallbackQueryHandler(bot.handle_callback))
        application.add_error_handler(bot.error_handler)
        
        # Start the bot
        print("🤖 Telegram File Compiler Bot is starting...")
        print("📦 Supports: ZIP, 7Z, TAR, TAR.GZ compilation")
        print("📁 Supports: APK, ZIP, 7Z, TAR extraction")
        print("🚀 Press Ctrl+C to stop the bot")
        
        application.run_polling()
        
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        print(f"Error: {e}")
        print("Please check your configuration in config.py")

if __name__ == "__main__":
    main()
