#!/usr/bin/env python3
"""
Telegram File Compiler Bot - Main Entry Point (Render Optimized)
"""

import logging
import os
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
        
        # Create and run the bot
        print("🚀 Starting Telegram File Compiler Bot on Render...")
        print("📦 Supports: ZIP, 7Z, TAR, TAR.GZ compilation")
        print("📁 Supports: APK, ZIP, 7Z, TAR extraction")
        print("🌐 Webhook ready for production")
        
        # Check if we're in production (Render sets RENDER env var)
        if os.environ.get('RENDER'):
            print("🏭 Running in Render production environment")
            bot.run_webhook()
        else:
            print("🔧 Running in development mode (polling)")
            bot.run()
        
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        print(f"❌ Error: {e}")
        print("💡 Make sure you've set the BOT_TOKEN environment variable in Render")

if __name__ == "__main__":
    main()
