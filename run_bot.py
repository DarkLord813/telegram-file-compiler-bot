#!/usr/bin/env python3
"""
Telegram File Compiler Bot - Main Entry Point
"""

import logging
from src.bot import FileCompilationBot
from src.config import Config
from src.utils import setup_logging

def main():
    """Main function to start the bot"""
    try:
        # Validate configuration
        Config.validate()
        
        # Setup logging
        setup_logging(Config.LOG_LEVEL)
        
        # Create and run bot
        bot = FileCompilationBot()
        print("🤖 Telegram File Compiler Bot is starting...")
        print("📦 Supports: ZIP, 7Z, TAR, TAR.GZ compilation")
        print("📁 Supports: APK, ZIP, 7Z, TAR extraction")
        print("🚀 Press Ctrl+C to stop the bot")
        
        # Create application and run
        from telegram.ext import Application
        application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, bot.handle_file))
        application.add_handler(CallbackQueryHandler(bot.handle_callback))
        
        # Start the bot
        application.run_polling()
        
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        print(f"Error: {e}")
        print("Please check your configuration in config.py")

if __name__ == "__main__":
    main()
