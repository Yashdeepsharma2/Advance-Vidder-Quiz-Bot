"""
Main bot file for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import asyncio
import logging
import sys
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import (
    Application, ApplicationBuilder, ContextTypes, 
    CommandHandler, MessageHandler, CallbackQueryHandler,
    PollHandler, InlineQueryHandler, filters
)
from telegram.constants import ParseMode

# Import configuration and database
from config import config, Messages
from database.database import db_manager
from database.models import Analytics

# Import all handlers
from handlers.basic_commands import register_basic_handlers
from handlers.auth_commands import register_auth_handlers  
from handlers.quiz_commands import register_quiz_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VidderQuizBot:
    """Main bot class"""
    
    def __init__(self):
        self.app = None
        self.start_time = datetime.now()
    
    async def initialize(self):
        """Initialize the bot"""
        try:
            # Validate configuration
            if not config.TELEGRAM_BOT_TOKEN:
                raise ValueError("TELEGRAM_BOT_TOKEN is not set")
            
            # Initialize database
            logger.info("Initializing database...")
            db_manager.init_database()
            
            # Create application
            logger.info("Creating Telegram application...")
            self.app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
            
            # Set up bot commands
            await self.setup_bot_commands()
            
            # Register handlers
            self.register_handlers()
            
            # Set up error handler
            self.app.add_error_handler(self.error_handler)
            
            logger.info("Bot initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def setup_bot_commands(self):
        """Setup bot commands menu"""
        commands = [
            BotCommand("start", "🚀 Start the bot and show main menu"),
            BotCommand("help", "📋 Get help with bot commands"),
            BotCommand("features", "✨ Show all bot features"),
            BotCommand("create", "🎯 Create a new quiz"),
            BotCommand("myquizzes", "📊 View your created quizzes"),
            BotCommand("stats", "📈 View bot statistics"),
            BotCommand("info", "ℹ️ About VidderTech and bot info"),
            BotCommand("login", "🔐 Login to TestBook for quiz import"),
            BotCommand("telelogin", "📱 Login to Telegram for poll extraction"),
            BotCommand("logout", "🚪 Logout from authenticated services"),
            BotCommand("lang", "🌐 Select language for quizzes"),
            BotCommand("done", "✅ Finish creating current quiz"),
            BotCommand("cancel", "❌ Cancel current quiz creation"),
            BotCommand("del", "🗑️ Delete a quiz by ID"),
            BotCommand("edit", "✏️ Edit an existing quiz"),
            BotCommand("assignment", "📝 Create assignment for students"),
            BotCommand("extract", "📊 Extract questions from polls/channels"),
            BotCommand("quiz", "🔄 Clone quiz from other bots"),
            BotCommand("pause", "⏸️ Pause current quiz"),
            BotCommand("resume", "▶️ Resume paused quiz"),
            BotCommand("stop", "⏹️ Stop current quiz"),
            BotCommand("fast", "⚡ Speed up quiz questions"),
            BotCommand("slow", "🐌 Slow down quiz questions"),
            BotCommand("normal", "➡️ Reset quiz to normal speed"),
            BotCommand("addfilter", "➕ Add words to filter list"),
            BotCommand("removefilter", "➖ Remove words from filter list"),
            BotCommand("listfilters", "📋 Show all filter words"),
            BotCommand("clearfilters", "🗑️ Clear all filter words"),
            BotCommand("add", "👥 Add user to paid quiz access"),
            BotCommand("rem", "👥 Remove user from paid quiz access"),
            BotCommand("post", "📢 Broadcast message (Admin only)"),
            BotCommand("ban", "🚫 Ban user from bot (Admin only)")
        ]
        
        try:
            await self.app.bot.set_my_commands(commands)
            logger.info("Bot commands set successfully!")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    def register_handlers(self):
        """Register all command handlers"""
        logger.info("Registering handlers...")
        
        # Register handler modules
        register_basic_handlers(self.app)
        register_auth_handlers(self.app)
        register_quiz_handlers(self.app)
        
        # Register additional handlers
        self.app.add_handler(CommandHandler("edit", self.edit_command))
        self.app.add_handler(CommandHandler("assignment", self.assignment_command))
        self.app.add_handler(CommandHandler("submit", self.submit_command))
        self.app.add_handler(CommandHandler("extract", self.extract_command))
        self.app.add_handler(CommandHandler("quiz", self.quiz_clone_command))
        
        # Quiz control commands
        self.app.add_handler(CommandHandler("pause", self.pause_command))
        self.app.add_handler(CommandHandler("resume", self.resume_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("fast", self.fast_command))
        self.app.add_handler(CommandHandler("slow", self.slow_command))
        self.app.add_handler(CommandHandler("normal", self.normal_command))
        
        # Filter commands
        self.app.add_handler(CommandHandler("addfilter", self.add_filter_command))
        self.app.add_handler(CommandHandler("removefilter", self.remove_filter_command))
        self.app.add_handler(CommandHandler("listfilters", self.list_filters_command))
        self.app.add_handler(CommandHandler("clearfilters", self.clear_filters_command))
        
        # User management commands
        self.app.add_handler(CommandHandler("add", self.add_user_command))
        self.app.add_handler(CommandHandler("rem", self.remove_user_command))
        self.app.add_handler(CommandHandler("remall", self.remove_all_users_command))
        
        # Admin commands
        self.app.add_handler(CommandHandler("post", self.broadcast_command))
        self.app.add_handler(CommandHandler("stopcast", self.stop_broadcast_command))
        self.app.add_handler(CommandHandler("ban", self.ban_command))
        
        # Special handlers
        self.app.add_handler(PollHandler(self.poll_handler))
        self.app.add_handler(InlineQueryHandler(self.inline_query_handler))
        
        logger.info("All handlers registered successfully!")
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Log error analytics if update is available
        if isinstance(update, Update) and update.effective_user:
            try:
                analytics = Analytics(
                    analytics_id=db_manager.generate_id("analytics_"),
                    event_type="bot_error",
                    user_id=update.effective_user.id,
                    metadata={
                        "error": str(context.error),
                        "update_type": type(update).__name__
                    }
                )
                await db_manager.log_analytics(analytics)
            except Exception as e:
                logger.error(f"Failed to log error analytics: {e}")
        
        # Send error message to user if possible
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An unexpected error occurred. Our team has been notified. Please try again later.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")
    
    async def log_command_usage(self, update: Update, command: str):
        """Log command usage for analytics"""
        try:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="command_usage",
                user_id=user_id,
                metadata={
                    "command": command,
                    "chat_id": chat_id,
                    "chat_type": update.effective_chat.type
                }
            )
            await db_manager.log_analytics(analytics)
        except Exception as e:
            logger.error(f"Failed to log command usage: {e}")
    
    # Placeholder command handlers (to be implemented in separate modules)
    async def edit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /edit command"""
        await self.log_command_usage(update, "edit")
        await update.message.reply_text(
            "✏️ **Quiz Edit Feature**\n\n"
            "🚧 This feature is under development.\n"
            "Soon you'll be able to edit your quizzes with advanced options!\n\n"
            "🔄 Use /myquizzes to see your existing quizzes.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def assignment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /assignment command"""
        await self.log_command_usage(update, "assignment")
        await update.message.reply_text(
            "📝 **Assignment Management**\n\n"
            "🚧 Assignment feature is coming soon!\n"
            "You'll be able to:\n"
            "• Create assignments for students\n"
            "• Track submissions\n"
            "• Generate performance reports\n\n"
            "🎯 Use /create to create regular quizzes for now.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def submit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /submit command"""
        await self.log_command_usage(update, "submit")
        await update.message.reply_text(
            "📤 **Assignment Submission**\n\n"
            "🚧 Submission feature is under development.\n"
            "Students will be able to submit their assignment work here.\n\n"
            "⏳ Coming soon with full tracking and analytics!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def extract_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /extract command"""
        await self.log_command_usage(update, "extract")
        await update.message.reply_text(
            "📊 **Poll & Content Extraction**\n\n"
            "🚧 Advanced extraction features coming soon!\n"
            "Extract questions from:\n"
            "• Telegram polls and channels\n"
            "• TestBook tests\n"
            "• PDF documents\n"
            "• Web articles\n\n"
            "🔧 Basic extraction is available via quiz creation.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def quiz_clone_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quiz command"""
        await self.log_command_usage(update, "quiz")
        await update.message.reply_text(
            "🔄 **Quiz Cloning**\n\n"
            "🚧 Quiz cloning feature is in development!\n"
            "Soon you'll be able to:\n"
            "• Clone from @quizbot\n"
            "• Import from other quiz bots\n"
            "• Bulk import from channels\n\n"
            "📝 Use /create to make original quizzes now.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Quiz control command placeholders
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command"""
        await self.log_command_usage(update, "pause")
        await update.message.reply_text("⏸️ Quiz pause feature - Coming soon!")
    
    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command"""
        await self.log_command_usage(update, "resume")
        await update.message.reply_text("▶️ Quiz resume feature - Coming soon!")
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        await self.log_command_usage(update, "stop")
        await update.message.reply_text("⏹️ Quiz stop feature - Coming soon!")
    
    async def fast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fast command"""
        await self.log_command_usage(update, "fast")
        await update.message.reply_text("⚡ Fast quiz mode - Coming soon!")
    
    async def slow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /slow command"""
        await self.log_command_usage(update, "slow")
        await update.message.reply_text("🐌 Slow quiz mode - Coming soon!")
    
    async def normal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /normal command"""
        await self.log_command_usage(update, "normal")
        await update.message.reply_text("➡️ Normal quiz speed - Coming soon!")
    
    # Filter command placeholders
    async def add_filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addfilter command"""
        await self.log_command_usage(update, "addfilter")
        await update.message.reply_text("➕ Add filter feature - Coming soon!")
    
    async def remove_filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removefilter command"""
        await self.log_command_usage(update, "removefilter")
        await update.message.reply_text("➖ Remove filter feature - Coming soon!")
    
    async def list_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listfilters command"""
        await self.log_command_usage(update, "listfilters")
        await update.message.reply_text("📋 List filters feature - Coming soon!")
    
    async def clear_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clearfilters command"""
        await self.log_command_usage(update, "clearfilters")
        await update.message.reply_text("🗑️ Clear filters feature - Coming soon!")
    
    # User management command placeholders
    async def add_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command"""
        await self.log_command_usage(update, "add")
        await update.message.reply_text("👥 Add user to paid quiz - Coming soon!")
    
    async def remove_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rem command"""
        await self.log_command_usage(update, "rem")
        await update.message.reply_text("👥 Remove user from paid quiz - Coming soon!")
    
    async def remove_all_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remall command"""
        await self.log_command_usage(update, "remall")
        await update.message.reply_text("👥 Remove all users from paid quiz - Coming soon!")
    
    # Admin command placeholders
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /post command"""
        await self.log_command_usage(update, "post")
        user_id = update.effective_user.id
        
        # Check admin permissions
        if user_id not in config.ADMIN_IDS and user_id != config.OWNER_ID:
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        await update.message.reply_text("📢 Broadcast feature - Coming soon!")
    
    async def stop_broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stopcast command"""
        await self.log_command_usage(update, "stopcast")
        user_id = update.effective_user.id
        
        if user_id not in config.ADMIN_IDS and user_id != config.OWNER_ID:
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        await update.message.reply_text("⏹️ Stop broadcast feature - Coming soon!")
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ban command"""
        await self.log_command_usage(update, "ban")
        user_id = update.effective_user.id
        
        if user_id not in config.ADMIN_IDS and user_id != config.OWNER_ID:
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        await update.message.reply_text("🚫 Ban user feature - Coming soon!")
    
    # Special handlers
    async def poll_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle poll updates"""
        logger.info("Poll received - processing...")
        # Poll processing logic will be implemented later
    
    async def inline_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline queries"""
        logger.info("Inline query received - processing...")
        # Inline query logic will be implemented later
    
    async def run(self):
        """Run the bot"""
        try:
            logger.info(f"🚀 Starting {config.BRAND_NAME} Quiz Bot v{config.BOT_VERSION}")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"Bot Username: {config.BOT_USERNAME}")
            logger.info(f"Admin IDs: {config.ADMIN_IDS}")
            logger.info(f"Owner ID: {config.OWNER_ID}")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Initialize bot
            await self.initialize()
            
            # Start polling
            logger.info("🔄 Starting polling...")
            await self.app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}")
            raise
        finally:
            logger.info("🔄 Cleaning up...")
            if self.app:
                await self.app.shutdown()

async def main():
    """Main function"""
    bot = VidderQuizBot()
    await bot.run()

if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required!")
            sys.exit(1)
        
        # Run bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)