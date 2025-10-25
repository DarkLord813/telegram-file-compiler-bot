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
    
    def get_main_keyboard(self):
        """Create the main inline keyboard"""
        keyboard = [
            [InlineKeyboardButton("📦 Create Archive", callback_data="show_archive_options")],
            [InlineKeyboardButton("📋 List Files", callback_data="list_files")],
            [InlineKeyboardButton("🗑️ Clear All", callback_data="clear_files")],
            [InlineKeyboardButton("🔧 Extract Archives", callback_data="show_extract_options")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="show_help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_archive_format_keyboard(self):
        """Create keyboard for archive format selection"""
        supported_formats = archive_manager.ArchiveManager.get_supported_formats()
        keyboard = []
        
        for format_key, format_desc in supported_formats.items():
            keyboard.append([InlineKeyboardButton(
                f"📦 {format_key.upper()} - {format_desc}", 
                callback_data=f"create_{format_key}"
            )])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_extract_keyboard(self):
        """Create keyboard for extraction options"""
        keyboard = [
            [InlineKeyboardButton("📁 Extract All Archives", callback_data="extract_all")],
            [InlineKeyboardButton("📋 List Extractable Files", callback_data="list_extractable")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_confirm_keyboard(self, action, format_type=None):
        """Create confirmation keyboard"""
        if action == "create_archive":
            keyboard = [
                [
                    InlineKeyboardButton("✅ Create", callback_data=f"confirm_{format_type}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_creation")
                ]
            ]
        elif action == "extract_all":
            keyboard = [
                [
                    InlineKeyboardButton("✅ Extract All", callback_data="confirm_extract_all"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_extraction")
                ]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_back_keyboard(self):
        """Create back to main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("⬅️ Back to Main", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user_id = update.effective_user.id
        self.initialize_user_session(user_id)
        
        welcome_message = """
🤖 **Advanced File Compiler Bot**

I can compile files into various archive formats AND extract archives like APK, ZIP, 7z, etc!

**Features:**
• 📦 Create ZIP, 7Z, TAR, TAR.GZ archives
• 📁 Extract APK, ZIP, 7Z, TAR files
• 🖼️ Handle documents, images, videos
• 🔒 Secure temporary file handling

Use the buttons below to manage your files!
        """
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown',
            reply_markup=self.get_main_keyboard()
        )
    
    def initialize_user_session(self, user_id: int):
        """Initialize or reinitialize user session"""
        user_temp_dir = os.path.join(config.TEMP_DIR, f"user_{user_id}")
        utils.ensure_directory(user_temp_dir)
        
        self.user_sessions[user_id] = {
            'files': [],
            'temp_dir': user_temp_dir,
            'waiting_confirmation': None,
            'extracted_files': []
        }
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Initialize session if not exists
        if user_id not in self.user_sessions:
            self.initialize_user_session(user_id)
        
        if data == "show_archive_options":
            await self.handle_show_archive_options(query)
        elif data.startswith("create_"):
            format_type = data.replace("create_", "")
            await self.handle_create_archive(query, format_type)
        elif data == "show_extract_options":
            await self.handle_show_extract_options(query)
        elif data == "extract_all":
            await self.handle_extract_all(query)
        elif data == "list_extractable":
            await self.handle_list_extractable(query)
        elif data == "list_files":
            await self.handle_list_files(query)
        elif data == "clear_files":
            await self.handle_clear_files(query)
        elif data == "show_help":
            await self.handle_show_help(query)
        elif data.startswith("confirm_"):
            if data.startswith("confirm_extract"):
                await self.handle_confirm_extraction(query, data.replace("confirm_", ""))
            else:
                await self.handle_confirm_creation(query, data.replace("confirm_", ""))
        elif data in ["cancel_creation", "cancel_extraction"]:
            await self.handle_cancel_operation(query)
        elif data == "back_to_main":
            await self.handle_back_to_main(query)
    
    async def handle_show_archive_options(self, query):
        """Show available archive formats"""
        supported_formats = archive_manager.ArchiveManager.get_supported_formats()
        formats_text = "\n".join([f"• **{key.upper()}** - {desc}" for key, desc in supported_formats.items()])
        
        message = f"""
📦 **Available Archive Formats**

{formats_text}

Choose a format to create your archive:
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_archive_format_keyboard()
        )
    
    async def handle_show_extract_options(self, query):
        """Show extraction options"""
        user_id = query.from_user.id
        archive_files = [f for f in self.user_sessions[user_id]['files'] 
                        if archive_manager.ArchiveManager.can_extract_archive(f['name'])]
        
        message = f"""
📁 **Archive Extraction**

Found **{len(archive_files)}** extractable archive file(s) in your storage.

You can:
• Extract all supported archives at once
• View list of extractable files
• Archives will be extracted and added to your file list
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_extract_keyboard()
        )
    
    async def handle_create_archive(self, query, format_type):
        """Handle archive creation request"""
        user_id = query.from_user.id
        files = self.user_sessions[user_id]['files']
        
        if not files:
            await query.edit_message_text(
                "❌ No files received yet! Please send some files first.",
                reply_markup=self.get_back_keyboard()
            )
            return
        
        # Store the format type for confirmation
        self.user_sessions[user_id]['waiting_confirmation'] = f"create_{format_type}"
        
        file_list = "\n".join([f"• {f['name']}" for f in files])
        total_size = sum(f['size'] for f in files)
        message = f"""
📦 **Create {format_type.upper()} Archive**

**Files to include ({len(files)}):**
{file_list}

**Archive size:** {utils.format_file_size(total_size)}

Are you sure you want to create the {format_type.upper()} archive?
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_confirm_keyboard("create_archive", format_type)
        )
    
    async def handle_extract_all(self, query):
        """Handle extract all archives request"""
        user_id = query.from_user.id
        archive_files = [f for f in self.user_sessions[user_id]['files'] 
                        if archive_manager.ArchiveManager.can_extract_archive(f['name'])]
        
        if not archive_files:
            await query.edit_message_text(
                "❌ No extractable archives found!\n\nSupported formats: APK, ZIP, 7Z, TAR, TAR.GZ",
                reply_markup=self.get_back_keyboard()
            )
            return
        
        archive_list = "\n".join([f"• {f['name']}" for f in archive_files])
        message = f"""
📁 **Extract All Archives**

**Archives to extract ({len(archive_files)}):**
{archive_list}

All files from these archives will be extracted and added to your file list.

Continue?
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_confirm_keyboard("extract_all")
        )
    
    async def handle_list_extractable(self, query):
        """List extractable archive files"""
        user_id = query.from_user.id
        archive_files = [f for f in self.user_sessions[user_id]['files'] 
                        if archive_manager.ArchiveManager.can_extract_archive(f['name'])]
        
        if not archive_files:
            message = "📭 No extractable archives found.\n\nSend me APK, ZIP, 7Z, or TAR files to extract them!"
        else:
            archive_list = "\n".join([f"• {f['name']} ({utils.format_file_size(f['size'])})" for f in archive_files])
            message = f"""
📋 **Extractable Archives** ({len(archive_files)} files)

{archive_list}

Use "Extract All Archives" to extract all of these at once!
            """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_extract_keyboard()
        )
    
    async def handle_confirm_creation(self, query, format_type):
        """Handle confirmed archive creation"""
        user_id = query.from_user.id
        user_session = self.user_sessions[user_id]
        
        await query.edit_message_text(f"⏳ Creating {format_type.upper()} archive... Please wait.")
        
        try:
            archive_path = await self.create_archive(user_id, format_type)
            
            if archive_path:
                # Send the archive file
                with open(archive_path, 'rb') as archive_file:
                    await query.message.reply_document(
                        document=archive_file,
                        filename=f"compiled_files.{format_type}",
                        caption=f"✅ Your {format_type.upper()} archive is ready!",
                        reply_markup=self.get_main_keyboard()
                    )
                
                # Clean up the archive file
                os.remove(archive_path)
                
                # Clear waiting confirmation
                user_session['waiting_confirmation'] = None
                
            else:
                await query.edit_message_text(
                    "❌ Failed to create archive. Please try again.",
                    reply_markup=self.get_main_keyboard()
                )
                
        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            await query.edit_message_text(
                "❌ Error creating archive. Please try again.",
                reply_markup=self.get_main_keyboard()
            )
    
    async def handle_confirm_extraction(self, query, action):
        """Handle confirmed archive extraction"""
        user_id = query.from_user.id
        user_session = self.user_sessions[user_id]
        
        await query.edit_message_text("⏳ Extracting archives... Please wait.")
        
        try:
            extracted_count = await self.extract_all_archives(user_id)
            
            if extracted_count > 0:
                total_files = len(user_session['files'])
                await query.edit_message_text(
                    f"✅ Successfully extracted {extracted_count} archive(s)!\n\n"
                    f"📊 Total files now: {total_files}",
                    reply_markup=self.get_main_keyboard()
                )
            else:
                await query.edit_message_text(
                    "❌ No files were extracted. Please check if you have valid archive files.",
                    reply_markup=self.get_main_keyboard()
                )
                
        except Exception as e:
            logger.error(f"Error extracting archives: {e}")
            await query.edit_message_text(
                "❌ Error extracting archives. Please try again.",
                reply_markup=self.get_main_keyboard()
            )
    
    async def handle_cancel_operation(self, query):
        """Cancel any pending operation"""
        user_id = query.from_user.id
        self.user_sessions[user_id]['waiting_confirmation'] = None
        
        await query.edit_message_text(
            "Operation cancelled.",
            reply_markup=self.get_main_keyboard()
        )
    
    async def create_archive(self, user_id: int, format_type: str) -> str:
        """Create archive from user's files"""
        user_session = self.user_sessions[user_id]
        files = user_session['files']
        temp_dir = user_session['temp_dir']
        
        if not files:
            return None
        
        archive_name = f"compiled_files_{user_id}_{len(files)}files.{format_type}"
        archive_path = os.path.join(temp_dir, archive_name)
        
        success = await archive_manager.ArchiveManager.compile_archive(files, archive_path, format_type)
        return archive_path if success else None
    
    async def extract_all_archives(self, user_id: int) -> int:
        """Extract all supported archives for a user"""
        user_session = self.user_sessions[user_id]
        files = user_session['files']
        temp_dir = user_session['temp_dir']
        
        extractable_files = [f for f in files if archive_manager.ArchiveManager.can_extract_archive(f['name'])]
        total_extracted = 0
        
        for archive_file in extractable_files:
            try:
                # Create extraction directory
                extract_dir = os.path.join(temp_dir, f"extracted_{os.path.splitext(archive_file['name'])[0]}")
                utils.ensure_directory(extract_dir)
                
                # Extract archive
                extracted_files = await archive_manager.ArchiveManager.extract_archive(archive_file['path'], extract_dir)
                
                # Add extracted files to user's file list
                for extracted_file in extracted_files:
                    # Check file limit
                    if len(user_session['files']) >= config.MAX_FILES_PER_USER:
                        break
                    
                    user_session['files'].append({
                        'name': extracted_file['name'],
                        'path': extracted_file['path'],
                        'size': extracted_file['size']
                    })
                    total_extracted += 1
                
            except Exception as e:
                logger.error(f"Error extracting {archive_file['name']}: {e}")
                continue
        
        return total_extracted

    async def handle_list_files(self, query):
        """List all stored files"""
        user_id = query.from_user.id
        files = self.user_sessions[user_id]['files']
        
        if not files:
            message = "📭 No files received yet.\n\nSend me some files to get started!"
        else:
            file_list = "\n".join([f"• {f['name']} ({utils.format_file_size(f['size'])})" for f in files])
            total_size = sum(f['size'] for f in files)
            message = f"""
📋 **Your Files** ({len(files)} files, {utils.format_file_size(total_size)} total)

{file_list}

Ready to create an archive?
            """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_main_keyboard()
        )
    
    async def handle_clear_files(self, query):
        """Clear all stored files"""
        user_id = query.from_user.id
        
        # Clean up temporary files
        if user_id in self.user_sessions:
            temp_dir = self.user_sessions[user_id]['temp_dir']
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
        
        # Reinitialize session
        self.initialize_user_session(user_id)
        
        await query.edit_message_text(
            "✅ All files cleared!",
            reply_markup=self.get_main_keyboard()
        )
    
    async def handle_show_help(self, query):
        """Show help information"""
        help_message = f"""
🤖 **File Compilation Bot - Help**

**How to use:**
1. Send me files (documents, images, etc.)
2. Use the buttons to manage your files
3. Create ZIP or 7Z archives
4. Download your compiled archive!

**Supported file types:**
• Documents (PDF, DOC, TXT, etc.)
• Images (JPG, PNG, etc.)
• Videos (MP4, AVI, etc.)
• Other file types

**Archive Support:**
• Create: ZIP, 7Z, TAR, TAR.GZ
• Extract: APK, ZIP, 7Z, TAR, TAR.GZ

**Limits:**
• Max file size: {utils.format_file_size(config.MAX_FILE_SIZE)}
• Max files per user: {config.MAX_FILES_PER_USER}

**Commands:**
/start - Restart the bot and show main menu
        """
        
        await query.edit_message_text(
            help_message,
            parse_mode='Markdown',
            reply_markup=self.get_back_keyboard()
        )
    
    async def handle_back_to_main(self, query):
        """Return to main menu"""
        user_id = query.from_user.id
        files_count = len(self.user_sessions[user_id]['files'])
        
        message = f"""
🤖 **File Compilation Bot**

📊 **Status:** {files_count} file(s) stored

Use the buttons below to manage your files!
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.get_main_keyboard()
        )
    
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming files."""
        user_id = update.effective_user.id
        
        # Initialize session if not exists
        if user_id not in self.user_sessions:
            self.initialize_user_session(user_id)
        
        user_session = self.user_sessions[user_id]
        
        # Check file limit
        if len(user_session['files']) >= config.MAX_FILES_PER_USER:
            await update.message.reply_text(
                f"❌ Maximum file limit reached ({config.MAX_FILES_PER_USER} files). "
                "Please create an archive or clear some files.",
                reply_markup=self.get_main_keyboard()
            )
            return
        
        # Get the file
        file_obj = None
        file_name = None
        file_size = 0
        
        if update.message.document:
            file_obj = await update.message.document.get_file()
            file_name = utils.safe_filename(update.message.document.file_name or "document")
            file_size = update.message.document.file_size or 0
        elif update.message.photo:
            file_obj = await update.message.photo[-1].get_file()
            file_name = f"photo_{len(user_session['files']) + 1}.jpg"
            file_size = file_obj.file_size or 0
        elif update.message.video:
            file_obj = await update.message.video.get_file()
            file_name = utils.safe_filename(update.message.video.file_name or f"video_{len(user_session['files']) + 1}.mp4")
            file_size = update.message.video.file_size or 0
        elif update.message.audio:
            file_obj = await update.message.audio.get_file()
            file_name = utils.safe_filename(update.message.audio.file_name or f"audio_{len(user_session['files']) + 1}.mp3")
            file_size = update.message.audio.file_size or 0
        else:
            await update.message.reply_text(
                "❌ Unsupported file type.",
                reply_markup=self.get_main_keyboard()
            )
            return
        
        # Check file size
        if file_size > config.MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ File too large. Maximum size is {utils.format_file_size(config.MAX_FILE_SIZE)}",
                reply_markup=self.get_main_keyboard()
            )
            return
        
        # Download file
        temp_dir = user_session['temp_dir']
        file_path = os.path.join(temp_dir, file_name)
        
        # Ensure unique filename
        counter = 1
        original_name = file_name
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_name)
            file_name = f"{name}_{counter}{ext}"
            file_path = os.path.join(temp_dir, file_name)
            counter += 1
        
        try:
            await file_obj.download_to_drive(file_path)
            
            # Get actual file size
            actual_size = os.path.getsize(file_path)
            
            # Store file info
            user_session['files'].append({
                'name': file_name,
                'path': file_path,
                'size': actual_size
            })
            
            files_count = len(user_session['files'])
            file_type_icon = "📁"
            if archive_manager.ArchiveManager.is_archive_file(file_name):
                file_type_icon = "📦"
            
            message = (
                f"{file_type_icon} File '{file_name}' received! ({utils.format_file_size(actual_size)})\n\n"
                f"📊 Total files: {files_count}/{config.MAX_FILES_PER_USER}"
            )
            
            if archive_manager.ArchiveManager.can_extract_archive(file_name):
                message += "\n\n🔓 This appears to be an archive file! You can extract it using the extraction menu."
            
            await update.message.reply_text(
                message,
                reply_markup=self.get_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await update.message.reply_text(
                "❌ Error downloading file. Please try again.",
                reply_markup=self.get_main_keyboard()
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Send error message to user
        if update and update.effective_user:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text="❌ An error occurred. Please try again.",
                    reply_markup=self.get_main_keyboard()
                )
            except Exception:
                pass

    def run(self):
        """Run the bot in polling mode (for development)"""
        from telegram.ext import Application
        
        # Create application
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.handle_file))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        print("✅ Bot is running successfully in POLLING mode!")
        application.run_polling(drop_pending_updates=True)

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
            webhook_url=webhook_url,
            secret_token='WEBHOOK_SECRET'
        )
        print("✅ Bot is running successfully with webhooks!")
