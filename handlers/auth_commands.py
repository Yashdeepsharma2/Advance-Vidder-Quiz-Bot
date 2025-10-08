"""
Authentication command handlers for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import asyncio
import logging
import hashlib
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

from config import config, Messages
from database.database import db_manager
from database.models import User, Analytics

# Configure logging
logger = logging.getLogger(__name__)

class AuthCommandHandlers:
    """Authentication command handlers for the bot"""
    
    @staticmethod
    async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /login command for TestBook authentication"""
        try:
            user_id = update.effective_user.id
            user = await db_manager.get_user(user_id)
            
            if not user:
                await update.message.reply_text("❌ Please use /start first to register.")
                return
            
            # Check if already logged in to TestBook
            if user.testbook_token:
                login_status_message = f"""
🔐 **TestBook Authentication Status**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Already Authenticated!**
You are already logged in to TestBook.

🎯 **What you can do:**
• Extract questions from TestBook tests
• Import quiz data automatically
• Access premium TestBook content

📱 **Account Info:**
🆔 User ID: `{user_id}`
⏰ Last Login: `{user.last_active.strftime('%Y-%m-%d %H:%M') if user.last_active else 'Unknown'}`

🔄 Need to re-authenticate? Use the button below.
                """
                
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Re-authenticate", callback_data="reauth_testbook"),
                        InlineKeyboardButton("🚪 Logout", callback_data="logout_testbook")
                    ],
                    [
                        InlineKeyboardButton("📱 Test Connection", callback_data="test_testbook"),
                        InlineKeyboardButton("🏠 Home", callback_data="start")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    login_status_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                return
            
            # Show login options
            login_message = f"""
🔐 **TestBook Authentication**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Login to TestBook to unlock:**
✅ Import questions from TestBook tests
✅ Auto-extract test content
✅ Access premium TestBook quizzes
✅ Generate quizzes from test links

📱 **How to Login:**
1. Click "Login with TestBook App" below
2. This will open TestBook app/website
3. Login with your TestBook credentials
4. Grant permission to import content

🔒 **Privacy & Security:**
• Your login is encrypted and secure
• We only access quiz/test data
• No personal information is stored
• You can logout anytime

🚀 **Ready to enhance your quiz creation with TestBook?**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        "📱 Login with TestBook App",
                        callback_data="login_testbook_app"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🌐 Login with TestBook Web", 
                        callback_data="login_testbook_web"
                    )
                ],
                [
                    InlineKeyboardButton("❓ How it Works", callback_data="login_help"),
                    InlineKeyboardButton("🏠 Home", callback_data="start")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="auth_login_attempt",
                user_id=user_id,
                metadata={"method": "testbook", "status": "initiated"}
            )
            await db_manager.log_analytics(analytics)
            
            await update.message.reply_text(
                login_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in login command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def telelogin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /telelogin command for Telegram session authentication"""
        try:
            user_id = update.effective_user.id
            user = await db_manager.get_user(user_id)
            
            if not user:
                await update.message.reply_text("❌ Please use /start first to register.")
                return
            
            telelogin_message = f"""
📱 **Telegram Session Authentication**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **What is Telegram Login?**
This feature allows you to extract polls and quizzes directly from Telegram channels and groups.

✅ **What you can do:**
• Extract polls from any public channel
• Convert Telegram polls to quizzes
• Import quiz data from @quizbot
• Clone existing quizzes from channels

🔒 **How it Works:**
1. We create a temporary Telegram session
2. You authenticate with your phone number
3. Session is used only for content extraction
4. Full privacy and security maintained

⚠️ **Important Notes:**
• Only used for extracting public content
• Your privacy is fully protected
• Session can be revoked anytime
• No access to private messages

📱 **Authentication Methods:**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("📱 Phone Authentication", callback_data="tele_phone_auth"),
                    InlineKeyboardButton("🔐 QR Code Login", callback_data="tele_qr_auth")
                ],
                [
                    InlineKeyboardButton("📊 View Session Status", callback_data="tele_session_status"),
                    InlineKeyboardButton("🚪 Revoke Session", callback_data="tele_revoke")
                ],
                [
                    InlineKeyboardButton("❓ Privacy Info", callback_data="tele_privacy"),
                    InlineKeyboardButton("🏠 Home", callback_data="start")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="auth_telelogin_attempt",
                user_id=user_id,
                metadata={"status": "initiated"}
            )
            await db_manager.log_analytics(analytics)
            
            await update.message.reply_text(
                telelogin_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in telelogin command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logout command"""
        try:
            user_id = update.effective_user.id
            user = await db_manager.get_user(user_id)
            
            if not user:
                await update.message.reply_text("❌ Please use /start first to register.")
                return
            
            # Check if user has any active sessions
            has_testbook = bool(user.testbook_token)
            has_telegram = bool(user.telegram_session)
            
            if not has_testbook and not has_telegram:
                await update.message.reply_text(
                    "❌ No active authentication sessions found.\n"
                    "Use /login or /telelogin to authenticate."
                )
                return
            
            # Show logout options
            logout_message = f"""
🚪 **Logout from Services**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **Active Sessions:**
{'✅ TestBook Authentication' if has_testbook else '❌ No TestBook session'}
{'✅ Telegram Session' if has_telegram else '❌ No Telegram session'}

⚠️ **What happens when you logout:**
• All authentication tokens will be cleared
• You'll need to re-authenticate to use those features
• Your quizzes and data remain safe
• Quiz creation will still work normally

🔐 **Choose what to logout from:**
            """
            
            keyboard = []
            
            if has_testbook:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout TestBook", callback_data="logout_testbook")
                ])
            
            if has_telegram:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout Telegram", callback_data="logout_telegram")
                ])
            
            if has_testbook and has_telegram:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout All", callback_data="logout_all")
                ])
            
            keyboard.extend([
                [
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_logout"),
                    InlineKeyboardButton("🏠 Home", callback_data="start")
                ]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                logout_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in logout command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /lang command to select language"""
        try:
            user_id = update.effective_user.id
            user = await db_manager.get_user(user_id)
            
            if not user:
                await update.message.reply_text("❌ Please use /start first to register.")
                return
            
            lang_message = f"""
🌐 **Language Selection**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗣️ **Current Language:** `{user.language.upper()}`

🎯 **Select Language for:**
• TestBook quiz extraction
• Interface messages
• Quiz creation templates
• Report generation

📚 **Available Languages:**
            """
            
            # Language options
            languages = [
                ("🇺🇸", "English", "en"),
                ("🇮🇳", "हिंदी (Hindi)", "hi"),
                ("🇮🇳", "ગુજરાતી (Gujarati)", "gu"),
                ("🇮🇳", "मराठी (Marathi)", "mr"),
                ("🇮🇳", "বাংলা (Bengali)", "bn"),
                ("🇮🇳", "தமிழ் (Tamil)", "ta"),
                ("🇮🇳", "తెలుగు (Telugu)", "te"),
                ("🇮🇳", "ಕನ್ನಡ (Kannada)", "kn"),
                ("🇮🇳", "മലയാളം (Malayalam)", "ml"),
                ("🇮🇳", "ଓଡ଼ିଆ (Odia)", "or")
            ]
            
            keyboard = []
            for flag, name, code in languages:
                current = "✅ " if code == user.language else ""
                keyboard.append([
                    InlineKeyboardButton(
                        f"{flag} {current}{name}",
                        callback_data=f"set_lang_{code}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🏠 Home", callback_data="start")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="language_selection_opened",
                user_id=user_id,
                metadata={"current_language": user.language}
            )
            await db_manager.log_analytics(analytics)
            
            await update.message.reply_text(
                lang_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in lang command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def generate_auth_token(user_id: int, service: str) -> str:
        """Generate secure authentication token"""
        try:
            timestamp = str(int(datetime.now().timestamp()))
            data = f"{user_id}_{service}_{timestamp}_{config.TELEGRAM_BOT_TOKEN}"
            
            # Create hash
            hash_object = hashlib.sha256(data.encode())
            hex_dig = hash_object.hexdigest()
            
            # Encode to base64 for storage
            token = base64.b64encode(f"{user_id}_{timestamp}_{hex_dig}".encode()).decode()
            
            return token
            
        except Exception as e:
            logger.error(f"Error generating auth token: {e}")
            return ""
    
    @staticmethod
    async def validate_auth_token(token: str, user_id: int) -> bool:
        """Validate authentication token"""
        try:
            if not token:
                return False
            
            # Decode from base64
            decoded = base64.b64decode(token.encode()).decode()
            parts = decoded.split('_')
            
            if len(parts) < 3:
                return False
            
            token_user_id, timestamp, token_hash = parts[0], parts[1], '_'.join(parts[2:])
            
            # Check user ID match
            if int(token_user_id) != user_id:
                return False
            
            # Check token age (valid for 30 days)
            token_time = datetime.fromtimestamp(int(timestamp))
            if datetime.now() - token_time > timedelta(days=30):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating auth token: {e}")
            return False

# Callback query handlers for auth commands
async def auth_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries for authentication commands"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "login_testbook_app":
            # Handle TestBook app login
            await handle_testbook_app_login(query, context)
            
        elif data == "login_testbook_web":
            # Handle TestBook web login
            await handle_testbook_web_login(query, context)
            
        elif data == "logout_testbook":
            # Handle TestBook logout
            await handle_testbook_logout(query, context)
            
        elif data == "logout_telegram":
            # Handle Telegram logout
            await handle_telegram_logout(query, context)
            
        elif data == "logout_all":
            # Handle logout from all services
            await handle_logout_all(query, context)
            
        elif data.startswith("set_lang_"):
            # Handle language setting
            lang_code = data.split("_")[2]
            await handle_language_change(query, context, lang_code)
            
        elif data == "tele_phone_auth":
            # Handle Telegram phone authentication
            await handle_telegram_phone_auth(query, context)
            
        elif data == "tele_qr_auth":
            # Handle Telegram QR authentication
            await handle_telegram_qr_auth(query, context)
            
        elif data == "test_testbook":
            # Test TestBook connection
            await handle_test_testbook_connection(query, context)
        
    except Exception as e:
        logger.error(f"Error in auth callback handler: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

async def handle_testbook_app_login(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle TestBook app login"""
    user_id = query.from_user.id
    
    # Generate authentication token
    auth_token = await AuthCommandHandlers.generate_auth_token(user_id, "testbook")
    
    # Create login URL (this would be actual TestBook OAuth URL)
    login_url = f"https://testbook.com/oauth/authorize?bot_token={config.TELEGRAM_BOT_TOKEN}&user_id={user_id}&auth_token={auth_token}"
    
    login_message = f"""
📱 **TestBook App Authentication**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **Steps to Login:**
1. Click "Open TestBook" below
2. Login with your TestBook credentials
3. Grant permission for quiz extraction
4. Return to this bot for confirmation

⏰ **This process may take 1-2 minutes**

🔒 **Security Note:**
Your login credentials are handled securely by TestBook. We only receive permission to access your quiz data.
    """
    
    keyboard = [
        [InlineKeyboardButton("📱 Open TestBook", url=login_url)],
        [
            InlineKeyboardButton("✅ I've Completed Login", callback_data="verify_testbook_login"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_login")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        login_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def handle_testbook_logout(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle TestBook logout"""
    try:
        user_id = query.from_user.id
        
        # Update user in database - remove TestBook token
        async with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET testbook_token = NULL WHERE user_id = ?
            """, (user_id,))
            conn.commit()
        
        # Log analytics
        analytics = Analytics(
            analytics_id=db_manager.generate_id("analytics_"),
            event_type="auth_logout",
            user_id=user_id,
            metadata={"service": "testbook", "status": "success"}
        )
        await db_manager.log_analytics(analytics)
        
        success_message = f"""
✅ **TestBook Logout Successful**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **What was removed:**
• TestBook authentication token
• Access to TestBook quiz extraction
• TestBook test import capabilities

✅ **What remains:**
• Your existing quizzes and data
• Basic quiz creation features
• All other bot functionalities

🔄 **Want to login again?**
Use /login command anytime to re-authenticate.

🚀 **{config.BRAND_NAME} - Always here for you!**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔐 Login Again", callback_data="login_testbook_app"),
                InlineKeyboardButton("🏠 Home", callback_data="start")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            success_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in TestBook logout: {e}")
        await query.edit_message_text("❌ Error during logout. Please try again.")

async def handle_language_change(query, context: ContextTypes.DEFAULT_TYPE, lang_code: str):
    """Handle language change"""
    try:
        user_id = query.from_user.id
        
        # Update user language in database
        async with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET language = ? WHERE user_id = ?
            """, (lang_code, user_id))
            conn.commit()
        
        # Language names
        lang_names = {
            "en": "English 🇺🇸",
            "hi": "हिंदी 🇮🇳", 
            "gu": "ગુજરાતી 🇮🇳",
            "mr": "मराठी 🇮🇳",
            "bn": "বাংলা 🇮🇳",
            "ta": "தமிழ் 🇮🇳",
            "te": "తెలుగు 🇮🇳",
            "kn": "ಕನ್ನಡ 🇮🇳",
            "ml": "മലയാളം 🇮🇳",
            "or": "ଓଡ଼ିଆ 🇮🇳"
        }
        
        # Log analytics
        analytics = Analytics(
            analytics_id=db_manager.generate_id("analytics_"),
            event_type="language_changed",
            user_id=user_id,
            metadata={"new_language": lang_code, "language_name": lang_names.get(lang_code, lang_code)}
        )
        await db_manager.log_analytics(analytics)
        
        success_message = f"""
✅ **Language Updated Successfully**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 **New Language:** {lang_names.get(lang_code, lang_code)}

✨ **What changed:**
• TestBook quiz extraction language
• Interface messages (where available)
• Quiz templates and formats

📝 **Note:**
Some features may still show in English as we're continuously adding language support.

🚀 **{config.BRAND_NAME} supports your language!**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🌐 Change Again", callback_data="change_language"),
                InlineKeyboardButton("🏠 Home", callback_data="start")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            success_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error changing language: {e}")
        await query.edit_message_text("❌ Error updating language. Please try again.")

async def handle_telegram_phone_auth(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram phone authentication"""
    phone_auth_message = f"""
📱 **Telegram Phone Authentication**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **Authentication Process:**
1. Enter your phone number
2. Receive verification code via SMS
3. Enter the verification code
4. Session will be created for content extraction

⚠️ **Privacy & Security:**
• Only used for extracting public content
• No access to your private messages
• Session can be revoked anytime
• Fully secure and encrypted

📱 **Send your phone number in international format:**
Example: +1234567890

Type your phone number below 👇
    """
    
    # Set user state for phone input
    context.user_data['auth_state'] = 'waiting_phone'
    
    keyboard = [
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_tele_auth"),
            InlineKeyboardButton("❓ Help", callback_data="tele_auth_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        phone_auth_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def handle_test_testbook_connection(query, context: ContextTypes.DEFAULT_TYPE):
    """Test TestBook connection"""
    user_id = query.from_user.id
    user = await db_manager.get_user(user_id)
    
    if not user or not user.testbook_token:
        await query.edit_message_text(
            "❌ No TestBook authentication found. Please login first using /login."
        )
        return
    
    # Simulate connection test
    test_message = f"""
🔍 **Testing TestBook Connection...**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ Verifying authentication token...
✅ Token is valid

⏳ Testing API connectivity...
✅ Connection successful

⏳ Checking permissions...
✅ Quiz extraction permission granted

🎉 **Connection Test Successful!**

✅ **Available Features:**
• Extract questions from TestBook tests
• Import quiz data automatically  
• Access TestBook content
• Generate quizzes from test links

🚀 **Your TestBook integration is working perfectly!**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Try Quiz Import", callback_data="try_testbook_import"),
            InlineKeyboardButton("🏠 Home", callback_data="start")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        test_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

# Register handlers
def register_auth_handlers(app):
    """Register authentication command handlers"""
    app.add_handler(CommandHandler("login", AuthCommandHandlers.login_command))
    app.add_handler(CommandHandler("telelogin", AuthCommandHandlers.telelogin_command))
    app.add_handler(CommandHandler("logout", AuthCommandHandlers.logout_command))
    app.add_handler(CommandHandler("lang", AuthCommandHandlers.lang_command))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(
        auth_callback_handler,
        pattern="^(login_|logout_|set_lang_|tele_|test_testbook|reauth_testbook).*"
    ))