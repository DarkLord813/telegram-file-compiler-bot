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
    port = int(os.environ.get('PORT', 10000))
    
    if not bot_token:
        print("❌ ERROR: BOT_TOKEN environment variable is required!")
        return
    
    # Auto-detect WEBHOOK_URL from Render environment
    webhook_url = os.environ.get('WEBHOOK_URL')
    if not webhook_url:
        # Try different Render environment variables
        render_service_url = os.environ.get('RENDER_SERVICE_URL')
        render_external_url = os.environ.get('RENDER_EXTERNAL_URL')
        render_app_name = os.environ.get('RENDER_APP_NAME')
        
        if render_service_url:
            webhook_url = render_service_url
        elif render_external_url:
            webhook_url = render_external_url
        elif render_app_name:
            webhook_url = f"https://{render_app_name}.onrender.com"
        else:
            # Last resort - try to get from Render's default environment
            service_name = os.environ.get('RENDER_SERVICE_NAME')
            if service_name:
                webhook_url = f"https://{service_name}.onrender.com"
            else:
                print("⚠️  WEBHOOK_URL not set, trying to use Render's default URL...")
                # Use a default pattern - this might work for most Render deployments
                webhook_url = f"https://{os.environ.get('RENDER_SERVICE_ID', 'your-app')}.onrender.com"
    
    print(f"🚀 Starting File Compilation Bot...")
    print(f"📊 Webhook URL: {webhook_url}")
    print(f"🔑 Bot Token: {bot_token[:10]}..." if bot_token else "❌ No Bot Token!")
    print(f"🌐 Port: {port}")
    
    try:
        # Create and run bot
        bot = FileCompilationBot()
        
        # Run in webhook mode for production
        bot.run_webhook(
            webhook_url=webhook_url,
            port=port
        )
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
