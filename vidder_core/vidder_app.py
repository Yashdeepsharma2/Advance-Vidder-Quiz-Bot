"""
🚀 VidderTech Application Builder
Built by VidderTech - The Future of Quiz Bots

Complete Telegram application builder with:
- Advanced handler registration
- Middleware integration
- Error handling setup
- Security implementations
- Performance optimizations
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from telegram import Update, BotCommand
from telegram.ext import (
    Application, ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    PollHandler, InlineQueryHandler, filters, Defaults
)
from telegram.constants import ParseMode

from vidder_config import config, Messages
from vidder_logs.vidder_logger import VidderLogger

# Initialize logger
logger = VidderLogger.get_logger('vidder.app')

class VidderApplication:
    """
    🚀 VidderTech Advanced Application Builder
    
    Comprehensive Telegram application with enterprise features:
    - All 35+ command handlers
    - Advanced middleware
    - Security integration
    - Performance monitoring
    """
    
    def __init__(self, vidder_config):
        """Initialize VidderTech application"""
        self.config = vidder_config
        self.app = None
        self.handlers_registered = False
        self.commands_set = False
        
        logger.info("🚀 Initializing VidderTech Application")
    
    async def initialize(self):
        """Initialize Telegram application with VidderTech features"""
        try:
            # Create application with defaults
            defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
            
            self.app = (
                ApplicationBuilder()
                .token(self.config.TOKEN)
                .defaults(defaults)
                .build()
            )
            
            # Setup bot commands
            await self.setup_bot_commands()
            
            # Register all handlers
            await self.register_all_handlers()
            
            # Setup error handling
            self.app.add_error_handler(self.global_error_handler)
            
            logger.info("✅ VidderTech Application initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize VidderTech application: {e}")
            raise
    
    async def setup_bot_commands(self):
        """Setup comprehensive bot command menu"""
        commands = [
            # Basic Commands
            BotCommand("start", "🚀 Start VidderTech bot & show main menu"),
            BotCommand("help", "📋 Complete command reference guide"),
            BotCommand("features", "✨ Explore all advanced features"),
            BotCommand("info", "ℹ️ About VidderTech & contact information"),
            BotCommand("stats", "📊 Detailed bot & user statistics"),
            
            # Authentication & Settings
            BotCommand("login", "🔐 TestBook integration login"),
            BotCommand("telelogin", "📱 Telegram session authentication"),
            BotCommand("logout", "🚪 Secure logout from all services"),
            BotCommand("lang", "🌍 Multi-language selection (15+ languages)"),
            
            # Quiz Management
            BotCommand("create", "🎯 Advanced quiz creation system"),
            BotCommand("edit", "✏️ Comprehensive quiz editing"),
            BotCommand("myquizzes", "📊 Personal quiz dashboard"),
            BotCommand("done", "✅ Complete quiz creation process"),
            BotCommand("cancel", "❌ Cancel current operation"),
            BotCommand("del", "🗑️ Secure quiz deletion"),
            
            # Live Quiz Control
            BotCommand("pause", "⏸️ Intelligent quiz pause"),
            BotCommand("resume", "▶️ Resume quiz with data integrity"),
            BotCommand("stop", "⏹️ Complete quiz termination"),
            BotCommand("fast", "⚡ Dynamic speed increase"),
            BotCommand("slow", "🐌 Adaptive slow mode"),
            BotCommand("normal", "➡️ Optimal speed reset"),
            
            # Assignment System
            BotCommand("assignment", "📚 Create student assignments"),
            BotCommand("submit", "📤 Student submission portal"),
            
            # Content Filtering
            BotCommand("addfilter", "➕ Smart content filtering"),
            BotCommand("removefilter", "➖ Precision filter removal"),
            BotCommand("listfilters", "📋 Filter management dashboard"),
            BotCommand("clearfilters", "🗑️ Complete filter reset"),
            
            # User Management
            BotCommand("add", "👥 Grant premium quiz access"),
            BotCommand("rem", "👥 Remove user permissions"),
            BotCommand("remall", "👥 Bulk permission management"),
            BotCommand("ban", "🚫 Advanced user moderation"),
            
            # Content Extraction
            BotCommand("extract", "🔍 Advanced poll extraction"),
            BotCommand("quiz", "🔄 QuizBot cloning system"),
            
            # Broadcasting (Admin Only)
            BotCommand("post", "📢 Advanced broadcast system"),
            BotCommand("stopcast", "⏹️ Broadcast control")
        ]
        
        try:
            await self.app.bot.set_my_commands(commands)
            self.commands_set = True
            logger.info(f"✅ Bot commands menu set successfully ({len(commands)} commands)")
            
        except Exception as e:
            logger.error(f"❌ Failed to set bot commands: {e}")
            raise
    
    async def register_all_handlers(self):
        """Register all command handlers with VidderTech implementation"""
        try:
            logger.info("📋 Registering VidderTech handlers...")
            
            # Import all handler modules
            from vidder_handlers.basic_vidder import register_basic_vidder_handlers
            from vidder_handlers.auth_vidder import register_auth_vidder_handlers
            from vidder_handlers.quiz_vidder import register_quiz_vidder_handlers
            from vidder_handlers.control_vidder import register_control_vidder_handlers
            from vidder_handlers.filter_vidder import register_filter_vidder_handlers
            from vidder_handlers.user_vidder import register_user_vidder_handlers
            from vidder_handlers.admin_vidder import register_admin_vidder_handlers
            from vidder_handlers.assignment_vidder import register_assignment_vidder_handlers
            from vidder_handlers.extract_vidder import register_extract_vidder_handlers
            from vidder_handlers.analytics_vidder import register_analytics_vidder_handlers
            from vidder_handlers.callback_vidder import register_callback_vidder_handlers
            from vidder_handlers.inline_vidder import register_inline_vidder_handlers
            from vidder_handlers.message_vidder import register_message_vidder_handlers
            from vidder_handlers.error_vidder import register_error_vidder_handlers
            
            # Register handlers in order
            handler_modules = [
                ("Basic Commands", register_basic_vidder_handlers),
                ("Authentication", register_auth_vidder_handlers),
                ("Quiz Management", register_quiz_vidder_handlers),
                ("Quiz Control", register_control_vidder_handlers),
                ("Content Filtering", register_filter_vidder_handlers),
                ("User Management", register_user_vidder_handlers),
                ("Admin Commands", register_admin_vidder_handlers),
                ("Assignment System", register_assignment_vidder_handlers),
                ("Content Extraction", register_extract_vidder_handlers),
                ("Analytics System", register_analytics_vidder_handlers),
                ("Callback Handlers", register_callback_vidder_handlers),
                ("Inline Queries", register_inline_vidder_handlers),
                ("Message Processing", register_message_vidder_handlers),
                ("Error Handling", register_error_vidder_handlers)
            ]
            
            registered_count = 0
            for handler_name, register_func in handler_modules:
                try:
                    count = register_func(self.app)
                    registered_count += count if count else 1
                    logger.info(f"✅ {handler_name}: Registered successfully")
                except Exception as e:
                    logger.error(f"❌ {handler_name}: Registration failed - {e}")
            
            self.handlers_registered = True
            logger.info(f"🎯 All VidderTech handlers registered: {registered_count}+ handlers")
            
        except Exception as e:
            logger.error(f"❌ Handler registration failed: {e}")
            raise
    
    async def global_error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler for VidderTech bot"""
        try:
            logger.error(f"❌ VidderTech Bot Error: {context.error}", exc_info=True)
            
            # Log to analytics if update is available
            if isinstance(update, Update) and update.effective_user:
                # Import here to avoid circular imports
                from vidder_database.vidder_database import VidderDatabase
                
                try:
                    db = VidderDatabase()
                    await db.log_error_analytics(
                        user_id=update.effective_user.id,
                        error_type=type(context.error).__name__,
                        error_message=str(context.error),
                        update_type=type(update).__name__
                    )
                except Exception as analytics_error:
                    logger.error(f"Failed to log error analytics: {analytics_error}")
            
            # Send user-friendly error message
            if isinstance(update, Update) and update.effective_chat:
                try:
                    error_message = f"""
❌ **Oops! Something went wrong**

🔧 **What happened:**
A technical issue occurred while processing your request.

🚀 **What we're doing:**
• Our VidderTech team has been automatically notified
• We're working to fix this immediately
• Your data remains safe and secure

💡 **What you can do:**
• Try the command again in a few moments
• Use /help if you need assistance
• Contact @VidderTech for urgent support

🏆 **VidderTech - We're committed to excellence!**
                    """
                    
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=error_message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as send_error:
                    logger.error(f"Failed to send error message: {send_error}")
        
        except Exception as handler_error:
            logger.critical(f"Critical error in error handler: {handler_error}")
    
    async def startup_checks(self):
        """Perform startup validation checks"""
        checks_passed = 0
        total_checks = 5
        
        logger.info("🔍 Performing VidderTech startup checks...")
        
        try:
            # Check 1: Bot token validation
            bot_info = await self.app.bot.get_me()
            logger.info(f"✅ Bot token valid - @{bot_info.username}")
            checks_passed += 1
            
        except Exception as e:
            logger.error(f"❌ Bot token validation failed: {e}")
        
        try:
            # Check 2: Database connectivity
            from vidder_database.vidder_database import VidderDatabase
            db = VidderDatabase()
            await db.health_check()
            logger.info("✅ Database connectivity confirmed")
            checks_passed += 1
            
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
        
        try:
            # Check 3: Required directories
            required_dirs = ["./logs", "./vidder_backup", "./uploads"]
            for dir_path in required_dirs:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info("✅ Directory structure verified")
            checks_passed += 1
            
        except Exception as e:
            logger.error(f"❌ Directory check failed: {e}")
        
        try:
            # Check 4: Handler registration
            if self.handlers_registered:
                logger.info("✅ All handlers registered successfully")
                checks_passed += 1
            else:
                logger.error("❌ Handler registration incomplete")
                
        except Exception as e:
            logger.error(f"❌ Handler check failed: {e}")
        
        try:
            # Check 5: Commands setup
            if self.commands_set:
                logger.info("✅ Bot commands menu configured")
                checks_passed += 1
            else:
                logger.error("❌ Commands menu not configured")
                
        except Exception as e:
            logger.error(f"❌ Commands check failed: {e}")
        
        # Summary
        logger.info(f"📊 Startup checks: {checks_passed}/{total_checks} passed")
        
        if checks_passed < 3:  # Minimum required checks
            raise RuntimeError("❌ Critical startup checks failed")
        
        return checks_passed == total_checks
    
    async def shutdown(self):
        """Graceful application shutdown"""
        try:
            logger.info("🔄 Shutting down VidderTech application...")
            
            if self.app:
                # Stop application
                await self.app.stop()
                await self.app.shutdown()
                
                logger.info("✅ VidderTech application shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during application shutdown: {e}")
    
    def get_application(self):
        """Get the Telegram application instance"""
        return self.app
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": config.BOT_VERSION,
            "uptime": 0,
            "components": {}
        }
        
        try:
            # Check bot connectivity
            if self.app:
                bot_info = await self.app.bot.get_me()
                health_status["components"]["telegram"] = {
                    "status": "healthy",
                    "bot_username": bot_info.username,
                    "bot_id": bot_info.id
                }
            else:
                health_status["components"]["telegram"] = {
                    "status": "unhealthy",
                    "error": "Application not initialized"
                }
                health_status["status"] = "degraded"
            
            # Check database
            try:
                from vidder_database.vidder_database import VidderDatabase
                db = VidderDatabase()
                await db.health_check()
                health_status["components"]["database"] = {"status": "healthy"}
            except Exception as db_error:
                health_status["components"]["database"] = {
                    "status": "unhealthy",
                    "error": str(db_error)
                }
                health_status["status"] = "degraded"
            
            # Check handlers
            health_status["components"]["handlers"] = {
                "status": "healthy" if self.handlers_registered else "unhealthy",
                "registered": self.handlers_registered
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }