import os
import tempfile
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from .config import Config
from .utils import format_file_size, safe_filename, cleanup_old_files
from .archive_manager import ArchiveManager

logger = logging.getLogger(__name__)

class FileCompilationBot:
    def __init__(self):
        self.user_sessions = {}
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        cleanup_old_files(Config.TEMP_DIR)
    
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
        supported_formats = ArchiveManager.get_supported_formats()
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
        user_temp_dir = os.path.join(Config.TEMP_DIR, f"user_{user_id}")
        os.makedirs(user_temp_dir, exist_ok=True)
        
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
        supported_formats = ArchiveManager.get_supported_formats()
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
                        if ArchiveManager.can_extract_archive(f['name'])]
        
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

**Archive size:** {format_file_size(total_size)}

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
                        if ArchiveManager.can_extract_archive(f['name'])]
        
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
                        if ArchiveManager.can_extract_archive(f['name'])]
        
        if not archive_files:
            message = "📭 No extractable archives found.\n\nSend me APK, ZIP, 7Z, or TAR files to extract them!"
        else:
            archive_list = "\n".join([f"• {f['name']} ({format_file_size(f['size'])})" for f in archive_files])
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
        
        success = await ArchiveManager.compile_archive(files, archive_path, format_type)
        return archive_path if success else None
    
    async def extract_all_archives(self, user_id: int) -> int:
        """Extract all supported archives for a user"""
        user_session = self.user_sessions[user_id]
        files = user_session['files']
        temp_dir = user_session['temp_dir']
        
        extractable_files = [f for f in files if ArchiveManager.can_extract_archive(f['name'])]
        total_extracted = 0
        
        for archive_file in extractable_files:
            try:
                # Create extraction directory
                extract_dir = os.path.join(temp_dir, f"extracted_{os.path.splitext(archive_file['name'])[0]}")
                os.makedirs(extract_dir, exist_ok=True)
                
                # Extract archive
                extracted_files = await ArchiveManager.extract_archive(archive_file['path'], extract_dir)
                
                # Add extracted files to user's file list
                for extracted_file in extracted_files:
                    # Check file limit
                    if len(user_session['files']) >= Config.MAX_FILES_PER_USER:
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

    # ... (keep the existing handle_list_files, handle_clear_files, handle_show_help, handle_back_to_main methods)

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming files."""
        user_id = update.effective_user.id
        
        # Initialize session if not exists
        if user_id not in self.user_sessions:
            self.initialize_user_session(user_id)
        
        user_session = self.user_sessions[user_id]
        
        # Check file limit
        if len(user_session['files']) >= Config.MAX_FILES_PER_USER:
            await update.message.reply_text(
                f"❌ Maximum file limit reached ({Config.MAX_FILES_PER_USER} files). "
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
            file_name = safe_filename(update.message.document.file_name or "document")
            file_size = update.message.document.file_size or 0
        elif update.message.photo:
            file_obj = await update.message.photo[-1].get_file()
            file_name = f"photo_{len(user_session['files']) + 1}.jpg"
            file_size = file_obj.file_size or 0
        elif update.message.video:
            file_obj = await update.message.video.get_file()
            file_name = safe_filename(update.message.video.file_name or f"video_{len(user_session['files']) + 1}.mp4")
            file_size = update.message.video.file_size or 0
        elif update.message.audio:
            file_obj = await update.message.audio.get_file()
            file_name = safe_filename(update.message.audio.file_name or f"audio_{len(user_session['files']) + 1}.mp3")
            file_size = update.message.audio.file_size or 0
        else:
            await update.message.reply_text(
                "❌ Unsupported file type.",
                reply_markup=self.get_main_keyboard()
            )
            return
        
        # Check file size
        if file_size > Config.MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ File too large. Maximum size is {format_file_size(Config.MAX_FILE_SIZE)}",
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
            if ArchiveManager.is_archive_file(file_name):
                file_type_icon = "📦"
            
            message = (
                f"{file_type_icon} File '{file_name}' received! ({format_file_size(actual_size)})\n\n"
                f"📊 Total files: {files_count}/{Config.MAX_FILES_PER_USER}"
            )
            
            if ArchiveManager.can_extract_archive(file_name):
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
