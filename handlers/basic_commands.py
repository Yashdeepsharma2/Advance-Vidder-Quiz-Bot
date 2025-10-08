"""
Basic command handlers for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

from config import config, Messages
from database.database import db_manager
from database.models import User, UserRole, Analytics

# Configure logging
logger = logging.getLogger(__name__)

class BasicCommandHandlers:
    """Basic command handlers for the bot"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            # Create or update user in database
            db_user = await db_manager.get_user(user.id)
            if not db_user:
                new_user = User(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    role=UserRole.USER
                )
                await db_manager.create_user(new_user)
                logger.info(f"New user created: {user.id}")
            else:
                await db_manager.update_user_activity(user.id)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="command_start",
                user_id=user.id,
                metadata={"chat_id": chat_id, "username": user.username}
            )
            await db_manager.log_analytics(analytics)
            
            # Create welcome keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📋 Help", callback_data="help"),
                    InlineKeyboardButton("🚀 Features", callback_data="features")
                ],
                [
                    InlineKeyboardButton("📊 My Quizzes", callback_data="myquizzes"),
                    InlineKeyboardButton("📈 Statistics", callback_data="stats")
                ],
                [
                    InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz"),
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                Messages.WELCOME,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(
                "❌ An error occurred. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            user_id = update.effective_user.id
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="command_help",
                user_id=user_id
            )
            await db_manager.log_analytics(analytics)
            
            # Create help keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🎯 Quiz Commands", callback_data="help_quiz"),
                    InlineKeyboardButton("⚡ Control Commands", callback_data="help_control")
                ],
                [
                    InlineKeyboardButton("🔧 Filter Commands", callback_data="help_filter"),
                    InlineKeyboardButton("👥 User Management", callback_data="help_users")
                ],
                [
                    InlineKeyboardButton("📢 Broadcasting", callback_data="help_broadcast"),
                    InlineKeyboardButton("🔍 Extraction Tools", callback_data="help_extraction")
                ],
                [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                Messages.HELP_MESSAGE,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def features_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /features command"""
        try:
            user_id = update.effective_user.id
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="command_features",
                user_id=user_id
            )
            await db_manager.log_analytics(analytics)
            
            # Create features keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🎯 Try Creating Quiz", callback_data="create_quiz"),
                    InlineKeyboardButton("📊 View Statistics", callback_data="stats")
                ],
                [
                    InlineKeyboardButton("💡 Tutorial Videos", url="https://t.me/VidderTech"),
                    InlineKeyboardButton("📱 Join Channel", url="https://t.me/VidderTech")
                ],
                [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                Messages.FEATURES_MESSAGE,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in features command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            user_id = update.effective_user.id
            user = await db_manager.get_user(user_id)
            
            if not user:
                await update.message.reply_text("❌ User not found. Please use /start first.")
                return
            
            # Get bot statistics
            bot_stats = await db_manager.get_bot_stats()
            user_quizzes = await db_manager.get_user_quizzes(user_id, limit=1000)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="command_stats",
                user_id=user_id
            )
            await db_manager.log_analytics(analytics)
            
            # Create statistics message
            stats_message = f"""
🚀 **{config.BRAND_NAME} Quiz Bot Statistics**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Bot Statistics:**
👥 Total Users: `{bot_stats.total_users:,}`
🔥 Active Today: `{bot_stats.active_users_today:,}`
📝 Total Quizzes: `{bot_stats.total_quizzes:,}`
⚡ Active Quizzes: `{bot_stats.active_quizzes:,}`
❓ Total Questions: `{bot_stats.total_questions:,}`
💬 Total Responses: `{bot_stats.total_responses:,}`

👤 **Your Statistics:**
🎯 Quizzes Created: `{len(user_quizzes)}`
🏆 Total Score: `{user.total_score}`
📅 Member Since: `{user.created_at.strftime('%B %d, %Y') if user.created_at else 'Unknown'}`
⭐ Role: `{user.role.value.title()}`

🚀 **System Status:**
✅ Uptime: **99.99%**
🔄 Last Updated: `{bot_stats.last_updated.strftime('%Y-%m-%d %H:%M:%S') if bot_stats.last_updated else 'Unknown'}`
📱 Version: `{config.BOT_VERSION}`

🏆 **Built with ❤️ by {config.BRAND_NAME}**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 My Quizzes", callback_data="myquizzes"),
                    InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz")
                ],
                [
                    InlineKeyboardButton("🔄 Refresh Stats", callback_data="stats"),
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                stats_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text(Messages.ERROR_DATABASE)
    
    @staticmethod
    async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command"""
        try:
            user_id = update.effective_user.id
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="command_info",
                user_id=user_id
            )
            await db_manager.log_analytics(analytics)
            
            info_message = f"""
🚀 **{config.BRAND_NAME} Quiz Bot Information**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 **About VidderTech:**
VidderTech is a leading technology company specializing in advanced Telegram bot solutions. We create innovative tools that enhance productivity and engagement for communities worldwide.

🤖 **About This Bot:**
The Advance Vidder Quiz Bot is our flagship quiz management solution, designed to provide comprehensive quiz creation, management, and analytics capabilities.

👨‍💻 **Developer Information:**
🏢 Company: VidderTech Solutions
📧 Contact: support@viddertech.com
🌐 Website: https://viddertech.com
📱 Telegram: @VidderTech

🔧 **Technical Specifications:**
⚡ Framework: Python Telegram Bot
🗄️ Database: SQLite with advanced analytics
🚀 Version: {config.BOT_VERSION}
🛡️ Security: Enterprise-grade encryption
📊 Analytics: Real-time performance tracking

🏆 **Features Highlight:**
✅ 99.99% Uptime Guarantee
✅ Advanced Quiz Analytics
✅ Multi-language Support
✅ OCR Text Extraction
✅ Web Scraping Integration
✅ TestBook Integration
✅ Beautiful HTML Reports

💝 **Special Thanks:**
Thank you for using VidderTech solutions! Your feedback helps us improve and create better tools for everyone.

🚀 **Built with ❤️ by VidderTech Team**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🌐 Visit Website", url="https://viddertech.com"),
                    InlineKeyboardButton("📱 Join Channel", url="https://t.me/VidderTech")
                ],
                [
                    InlineKeyboardButton("💬 Support", url="https://t.me/VidderTech"),
                    InlineKeyboardButton("⭐ Rate Us", callback_data="rate_bot")
                ],
                [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                info_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries for basic commands"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            data = query.data
            
            # Route callback queries
            if data == "help":
                await BasicCommandHandlers.help_callback(query, context)
            elif data == "features":
                await BasicCommandHandlers.features_callback(query, context)
            elif data == "stats":
                await BasicCommandHandlers.stats_callback(query, context)
            elif data == "start":
                await BasicCommandHandlers.start_callback(query, context)
            elif data == "rate_bot":
                await BasicCommandHandlers.rate_bot_callback(query, context)
            
        except Exception as e:
            logger.error(f"Error in callback query handler: {e}")
    
    @staticmethod
    async def help_callback(query, context: ContextTypes.DEFAULT_TYPE):
        """Handle help callback"""
        keyboard = [
            [
                InlineKeyboardButton("🎯 Quiz Commands", callback_data="help_quiz"),
                InlineKeyboardButton("⚡ Control Commands", callback_data="help_control")
            ],
            [
                InlineKeyboardButton("🔧 Filter Commands", callback_data="help_filter"),
                InlineKeyboardButton("👥 User Management", callback_data="help_users")
            ],
            [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            Messages.HELP_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def features_callback(query, context: ContextTypes.DEFAULT_TYPE):
        """Handle features callback"""
        keyboard = [
            [
                InlineKeyboardButton("🎯 Try Creating Quiz", callback_data="create_quiz"),
                InlineKeyboardButton("📊 View Statistics", callback_data="stats")
            ],
            [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            Messages.FEATURES_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    
    @staticmethod
    async def stats_callback(query, context: ContextTypes.DEFAULT_TYPE):
        """Handle stats callback"""
        user_id = query.from_user.id
        user = await db_manager.get_user(user_id)
        bot_stats = await db_manager.get_bot_stats()
        user_quizzes = await db_manager.get_user_quizzes(user_id, limit=1000)
        
        stats_message = f"""
🚀 **{config.BRAND_NAME} Quiz Bot Statistics**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Bot Statistics:**
👥 Total Users: `{bot_stats.total_users:,}`
🔥 Active Today: `{bot_stats.active_users_today:,}`
📝 Total Quizzes: `{bot_stats.total_quizzes:,}`
⚡ Active Quizzes: `{bot_stats.active_quizzes:,}`

👤 **Your Statistics:**
🎯 Quizzes Created: `{len(user_quizzes)}`
🏆 Total Score: `{user.total_score if user else 0}`
⭐ Role: `{user.role.value.title() if user else 'User'}`

🏆 **Built with ❤️ by {config.BRAND_NAME}**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 My Quizzes", callback_data="myquizzes"),
                InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz")
            ],
            [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def start_callback(query, context: ContextTypes.DEFAULT_TYPE):
        """Handle start callback"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Help", callback_data="help"),
                InlineKeyboardButton("🚀 Features", callback_data="features")
            ],
            [
                InlineKeyboardButton("📊 My Quizzes", callback_data="myquizzes"),
                InlineKeyboardButton("📈 Statistics", callback_data="stats")
            ],
            [
                InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            Messages.WELCOME,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def rate_bot_callback(query, context: ContextTypes.DEFAULT_TYPE):
        """Handle rate bot callback"""
        rate_message = f"""
⭐ **Rate {config.BRAND_NAME} Quiz Bot**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for using our bot! Your feedback helps us improve.

🌟 **Please rate your experience:**
⭐ 1 Star - Needs improvement
⭐⭐ 2 Stars - Below average
⭐⭐⭐ 3 Stars - Average
⭐⭐⭐⭐ 4 Stars - Good
⭐⭐⭐⭐⭐ 5 Stars - Excellent!

💬 **Share your feedback:**
- What features do you love most?
- What could we improve?
- Any suggestions for new features?

📧 Contact us: @VidderTech
        """
        
        keyboard = [
            [
                InlineKeyboardButton("⭐", callback_data="rate_1"),
                InlineKeyboardButton("⭐⭐", callback_data="rate_2"),
                InlineKeyboardButton("⭐⭐⭐", callback_data="rate_3")
            ],
            [
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_4"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_5")
            ],
            [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            rate_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

# Register handlers
def register_basic_handlers(app):
    """Register basic command handlers"""
    app.add_handler(CommandHandler("start", BasicCommandHandlers.start_command))
    app.add_handler(CommandHandler("help", BasicCommandHandlers.help_command))
    app.add_handler(CommandHandler("features", BasicCommandHandlers.features_command))
    app.add_handler(CommandHandler("stats", BasicCommandHandlers.stats_command))
    app.add_handler(CommandHandler("info", BasicCommandHandlers.info_command))
    app.add_handler(CallbackQueryHandler(BasicCommandHandlers.callback_query_handler, pattern="^(help|features|stats|start|rate_bot|rate_[1-5])$"))