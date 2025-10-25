#!/usr/bin/env python3
"""
Webhook entry point for Render deployment
"""
import os
import logging
from bot import FileCompilationBot

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Main function to start the bot in webhook mode"""
    
    # Get configuration from environment variables
    bot_token = os.environ.get('BOT_TOKEN')
    webhook_url = os.environ.get('WEBHOOK_URL')
    port = int(os.environ.get('PORT', 10000))
    
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required!")
    
    if not webhook_url:
        # Try to construct webhook URL from Render environment
        render_app_name = os.environ.get('RENDER_APP_NAME')
        if render_app_name:
            webhook_url = f"https://{render_app_name}.onrender.com"
        else:
            raise ValueError("WEBHOOK_URL environment variable is required!")
    
    print(f"🚀 Starting File Compilation Bot...")
    print(f"📊 Webhook URL: {webhook_url}")
    print(f"🔑 Bot Token: {bot_token[:10]}...")
    print(f"🌐 Port: {port}")
    
    # Create and run bot
    bot = FileCompilationBot()
    
    # Run in webhook mode for production
    bot.run_webhook(
        webhook_url=webhook_url,
        port=port
    )

if __name__ == '__main__':
    main()
