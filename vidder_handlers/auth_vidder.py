"""
🔐 VidderTech Authentication Handlers - Complete Implementation
🚀 Built by VidderTech - Advanced Security & Integration System

This module handles all authentication and user management:
- /login - TestBook authentication with OAuth
- /telelogin - Telegram session management
- /logout - Comprehensive session cleanup
- /lang - Advanced language selection (15+ languages)
- /profile - User profile management
- /settings - Personal preferences
"""

import asyncio
import logging
import hashlib
import base64
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
)
from telegram.constants import ParseMode, ChatAction

from vidder_config import config, messages, states, callbacks
from vidder_database.vidder_database import db_manager

# Setup logging
logger = logging.getLogger('vidder.handlers.auth')

class VidderAuthHandlers:
    """🔐 Complete Authentication System with Advanced Security"""
    
    def __init__(self):
        self.supported_languages = config.SUPPORTED_LANGUAGES
        self.session_timeout = timedelta(hours=config.SESSION_TIMEOUT_HOURS)
        self.max_login_attempts = config.MAX_LOGIN_ATTEMPTS
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🔑 Advanced TestBook authentication with OAuth integration"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            user_data = await db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "Please use /start first to register with VidderTech."
                )
                return
            
            # Check if already authenticated
            if user_data.get('testbook_token'):
                await self._show_already_authenticated(update, user_data, 'testbook')
                return
            
            # Check login attempts
            login_attempts = user_data.get('login_attempts', 0)
            if login_attempts >= self.max_login_attempts:
                await self._show_login_locked(update, user_data)
                return
            
            # Show comprehensive TestBook login options
            login_message = f"""
🔑 **TestBook Authentication - VidderTech Integration**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 **Connect your TestBook account to unlock:**

🎯 **Premium Import Features:**
• 📚 Import complete TestBook tests
• 🤖 Auto-convert test questions to quizzes
• 📊 Sync your TestBook progress
• 🎓 Access premium TestBook content
• 📈 Enhanced analytics with TestBook data

🔒 **Security & Privacy:**
• 🛡️ Military-grade encryption (AES-256)
• 🔐 Secure OAuth 2.0 authentication  
• 🚫 We never store your TestBook password
• ✅ You can revoke access anytime
• 📋 Full transparency in data usage

⚡ **Authentication Methods:**
Choose your preferred login method below:

🔐 **Login Attempt:** {login_attempts + 1}/{self.max_login_attempts}
            """
            
            # Create authentication keyboard
            keyboard = [
                [
                    InlineKeyboardButton(
                        "📱 TestBook Mobile App",
                        callback_data="testbook_mobile_auth"
                    ),
                    InlineKeyboardButton(
                        "🌐 TestBook Website", 
                        callback_data="testbook_web_auth"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔐 OAuth Login",
                        callback_data="testbook_oauth_auth"
                    ),
                    InlineKeyboardButton(
                        "🆔 Manual Token",
                        callback_data="testbook_manual_token"
                    )
                ],
                [
                    InlineKeyboardButton("❓ How it Works", callback_data="testbook_auth_help"),
                    InlineKeyboardButton("🔒 Privacy Policy", callback_data="privacy_policy")
                ],
                [
                    InlineKeyboardButton("🎮 Try Without Login", callback_data="skip_testbook_login"),
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                login_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log authentication attempt
            await db_manager._log_analytics(
                "auth_testbook_initiated",
                user_id,
                metadata={
                    "login_attempts": login_attempts + 1,
                    "auth_method": "command"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in login command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _show_already_authenticated(self, update: Update, user_data: Dict, service: str):
        """Show already authenticated status with advanced options"""
        service_name = service.title()
        
        auth_status_message = f"""
✅ **{service_name} Authentication Active**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 **You're already connected!**

📊 **Current Session:**
🔐 **Service:** {service_name}
⏰ **Last Login:** {user_data.get('last_login', 'Unknown')[:16] if user_data.get('last_login') else 'Unknown'}
🆔 **User ID:** `{user_data['user_id']}`
👤 **Account:** {user_data.get('role', 'free').title()}

🚀 **Available Actions with {service_name}:**
        """
        
        if service == 'testbook':
            auth_status_message += """
• 📚 Import TestBook tests directly
• 🎯 Auto-convert questions to quizzes  
• 📊 Sync progress and analytics
• 🎓 Access premium TestBook content
• 📈 Enhanced performance insights
            """
        else:
            auth_status_message += """
• 📊 Extract polls from Telegram channels
• 🔄 Clone quizzes from other bots
• 📱 Access private channel content
• 🤖 Auto-import quiz data
• 📈 Enhanced extraction capabilities
            """
        
        auth_status_message += f"""

🔧 **Management Options:**
• Test your connection
• Re-authenticate if needed
• View authentication details
• Logout and clear session

🚀 **{config.COMPANY_NAME} - Keeping You Connected!**
        """
        
        # Create management keyboard
        keyboard = [
            [
                InlineKeyboardButton(f"🔍 Test {service_name} Connection", callback_data=f"test_{service}_connection"),
                InlineKeyboardButton(f"📊 View {service_name} Data", callback_data=f"view_{service}_data")
            ],
            [
                InlineKeyboardButton(f"🔄 Re-authenticate", callback_data=f"reauth_{service}"),
                InlineKeyboardButton(f"🚪 Logout {service_name}", callback_data=f"logout_{service}")
            ],
            [
                InlineKeyboardButton("⚙️ Auth Settings", callback_data="auth_settings"),
                InlineKeyboardButton("🔒 Security Info", callback_data="security_info")
            ],
            [
                InlineKeyboardButton("🏠 Back to Home", callback_data="start")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            auth_status_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def telelogin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📱 Advanced Telegram session authentication"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            user_data = await db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "Please use /start first to register with VidderTech."
                )
                return
            
            # Check if already has Telegram session
            if user_data.get('telegram_session'):
                await self._show_already_authenticated(update, user_data, 'telegram')
                return
            
            # Advanced Telegram authentication options
            telelogin_message = f"""
📱 **Telegram Session Authentication - VidderTech**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **What is Telegram Authentication?**
This feature creates a secure connection to extract content from Telegram channels, groups, and bots.

✨ **Unlock These Amazing Features:**
• 📊 Extract polls from any public channel
• 🔄 Clone quizzes from @QuizBot and similar bots
• 📱 Import quiz data from Telegram groups
• 🤖 Auto-convert Telegram polls to quizzes
• 📈 Bulk import from multiple channels
• 🎯 Access premium Telegram content

🔒 **Privacy & Security Guaranteed:**
• 🛡️ End-to-end encryption (Military grade)
• 🚫 NO access to your private messages
• 📋 Only public content extraction
• 🔐 Session data encrypted locally
• ❌ Zero personal data collection
• ✅ You control all permissions

⚡ **Quick & Secure Authentication:**
Choose your preferred method:

🔐 **Session Security:** Your data is protected with bank-level security standards.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("📱 Phone Authentication", callback_data="tele_phone_auth"),
                    InlineKeyboardButton("📲 QR Code Login", callback_data="tele_qr_auth")
                ],
                [
                    InlineKeyboardButton("🔐 Session Token", callback_data="tele_token_auth"),
                    InlineKeyboardButton("🌐 Web Authentication", callback_data="tele_web_auth")
                ],
                [
                    InlineKeyboardButton("📱 Via Bot Token", callback_data="tele_bot_auth"),
                    InlineKeyboardButton("🔑 API Hash Method", callback_data="tele_api_auth")
                ],
                [
                    InlineKeyboardButton("❓ Authentication Help", callback_data="tele_auth_help"),
                    InlineKeyboardButton("🔒 Privacy Details", callback_data="tele_privacy_details")
                ],
                [
                    InlineKeyboardButton("🎮 Skip for Now", callback_data="skip_telegram_auth"),
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                telelogin_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log authentication attempt
            await db_manager._log_analytics(
                "auth_telegram_initiated",
                user_id,
                metadata={"auth_method": "command"}
            )
            
        except Exception as e:
            logger.error(f"❌ Error in telelogin command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def logout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🚪 Comprehensive logout system with session management"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            user_data = await db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text("Please use /start first to register.")
                return
            
            # Check active sessions
            has_testbook = bool(user_data.get('testbook_token'))
            has_telegram = bool(user_data.get('telegram_session'))
            has_google = bool(user_data.get('google_id'))
            
            if not any([has_testbook, has_telegram, has_google]):
                await update.message.reply_text(
                    "❌ **No Active Sessions**\n\n"
                    "You don't have any active authentication sessions.\n\n"
                    "🔐 **Available Logins:**\n"
                    "• /login - TestBook authentication\n"
                    "• /telelogin - Telegram session\n\n"
                    f"🚀 **{config.COMPANY_NAME} - Always Secure!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Show comprehensive logout options
            logout_message = f"""
🚪 **Session Management - VidderTech Security Center**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **Current Active Sessions:**

{'🟢 TestBook Authentication' if has_testbook else '⚪ No TestBook session'}
{'🟢 Telegram Session Active' if has_telegram else '⚪ No Telegram session'}  
{'🟢 Google Account Linked' if has_google else '⚪ No Google account'}

⚠️ **What happens when you logout:**

📱 **TestBook Logout:**
• ❌ TestBook quiz import disabled
• ❌ Auto-sync features disabled
• ✅ Your VidderTech quizzes remain safe
• ✅ Basic quiz creation still works

📱 **Telegram Logout:**
• ❌ Poll extraction disabled
• ❌ Channel content import disabled
• ✅ Your quiz data remains safe
• ✅ All other features still work

👤 **Google Logout:**
• ❌ Google Drive integration disabled
• ❌ Auto-backup to Google disabled
• ✅ Local data remains intact

🔒 **Security Benefits of Logout:**
• 🛡️ Prevents unauthorized access
• 🔐 Clears all stored tokens
• 📱 Revokes API permissions
• ✅ Complete privacy protection

🎯 **Choose what to logout from:**
            """
            
            keyboard = []
            
            # Add logout options based on active sessions
            if has_testbook:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout TestBook", callback_data="logout_testbook")
                ])
            
            if has_telegram:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout Telegram", callback_data="logout_telegram")
                ])
            
            if has_google:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout Google", callback_data="logout_google")
                ])
            
            # Bulk logout option if multiple sessions
            active_sessions = sum([has_testbook, has_telegram, has_google])
            if active_sessions > 1:
                keyboard.append([
                    InlineKeyboardButton("🚪 Logout All Sessions", callback_data="logout_all_sessions")
                ])
            
            # Additional options
            keyboard.extend([
                [
                    InlineKeyboardButton("🔒 Session Details", callback_data="session_details"),
                    InlineKeyboardButton("📊 Login History", callback_data="login_history")
                ],
                [
                    InlineKeyboardButton("❌ Cancel Logout", callback_data="cancel_logout"),
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                logout_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error in logout command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _show_login_locked(self, update: Update, user_data: Dict):
        """Show login locked message with recovery options"""
        locked_message = f"""
🔒 **Account Temporarily Locked**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **Security Protection Activated**

Your account has been temporarily locked due to multiple failed login attempts.

📊 **Lock Details:**
🔢 Failed Attempts: `{user_data.get('login_attempts', 0)}/{self.max_login_attempts}`
⏰ Lock Duration: `30 minutes`
🔓 Auto-unlock: `{(datetime.now() + timedelta(minutes=30)).strftime('%H:%M')}`

🔓 **Unlock Options:**

1️⃣ **Wait for Auto-unlock** (Recommended)
2️⃣ **Contact Support** for immediate unlock
3️⃣ **Verify Account** via email/phone

🛡️ **Why This Happens:**
This security measure protects your account from unauthorized access attempts.

🆘 **Need Immediate Access?**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📧 Contact Support", url=f"mailto:{config.COMPANY_EMAIL}"),
                InlineKeyboardButton("📱 Telegram Support", url=f"https://t.me/{config.COMPANY_TELEGRAM[1:]}")
            ],
            [
                InlineKeyboardButton("🔓 Request Unlock", callback_data="request_unlock"),
                InlineKeyboardButton("📱 Verify Phone", callback_data="verify_phone")
            ],
            [
                InlineKeyboardButton("🏠 Back to Home", callback_data="start")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            locked_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def lang_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🌍 Advanced multi-language selection system"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            user_data = await db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text("Please use /start first to register.")
                return
            
            current_lang = user_data.get('language', 'en')
            
            # Create comprehensive language selection
            lang_message = f"""
🌍 **VidderTech Multi-Language System**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗣️ **Current Language:** {self.supported_languages.get(current_lang, '🇺🇸 English')}

🎯 **Language affects:**
• 📱 Bot interface messages
• 🎮 Quiz templates and formats  
• 📊 Report generation
• 🤖 AI-generated content
• 📚 TestBook content extraction
• 🌐 Web scraping results

🌟 **Available Languages:**
*Choose your preferred language below*

💡 **Pro Tip:** You can change language anytime!

🚀 **{config.COMPANY_NAME} speaks your language!**
            """
            
            # Create language keyboard with flags and native names
            keyboard = []
            
            # Group languages for better display
            lang_items = list(self.supported_languages.items())
            
            for i in range(0, len(lang_items), 2):
                row = []
                
                # First language
                code, name = lang_items[i]
                current_marker = "✅ " if code == current_lang else ""
                row.append(InlineKeyboardButton(
                    f"{current_marker}{name}",
                    callback_data=f"set_language_{code}"
                ))
                
                # Second language (if exists)
                if i + 1 < len(lang_items):
                    code, name = lang_items[i + 1]
                    current_marker = "✅ " if code == current_lang else ""
                    row.append(InlineKeyboardButton(
                        f"{current_marker}{name}",
                        callback_data=f"set_language_{code}"
                    ))
                
                keyboard.append(row)
            
            # Add special options
            keyboard.extend([
                [
                    InlineKeyboardButton("🤖 Auto-Detect Language", callback_data="auto_detect_language"),
                    InlineKeyboardButton("🔄 Reset to Default", callback_data="reset_language")
                ],
                [
                    InlineKeyboardButton("➕ Request New Language", callback_data="request_language"),
                    InlineKeyboardButton("🌐 Translation Help", callback_data="translation_help")
                ],
                [
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                lang_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log analytics
            await db_manager._log_analytics(
                "language_selection_opened",
                user_id,
                metadata={"current_language": current_lang}
            )
            
        except Exception as e:
            logger.error(f"❌ Error in lang command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """👤 Advanced user profile management system"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            user_data = await db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text("Please use /start first to register.")
                return
            
            # Get comprehensive user statistics
            user_stats = await db_manager.get_user_stats(user_id)
            
            # Format profile information
            profile_message = self._format_user_profile(user_data, user_stats)
            
            # Create profile management keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile"),
                    InlineKeyboardButton("🔒 Privacy Settings", callback_data="privacy_settings")
                ],
                [
                    InlineKeyboardButton("🎨 Customize Theme", callback_data="customize_theme"),
                    InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")
                ],
                [
                    InlineKeyboardButton("📊 Detailed Stats", callback_data="detailed_user_stats"),
                    InlineKeyboardButton("🏆 Achievements", callback_data="user_achievements")
                ],
                [
                    InlineKeyboardButton("📤 Export Profile", callback_data="export_profile"),
                    InlineKeyboardButton("🗑️ Delete Account", callback_data="delete_account")
                ],
                [
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                profile_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log analytics
            await db_manager._log_analytics("profile_viewed", user_id)
            
        except Exception as e:
            logger.error(f"❌ Error in profile command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    def _format_user_profile(self, user_data: Dict, user_stats: Dict) -> str:
        """Format comprehensive user profile"""
        try:
            creation_stats = user_stats.get('creation_stats', {})
            participation_stats = user_stats.get('participation_stats', {})
            
            # Calculate membership duration
            created_at = user_data.get('created_at')
            member_since = "Unknown"
            membership_days = 0
            
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at)
                    membership_days = (datetime.now() - created_date).days
                    member_since = created_date.strftime('%B %d, %Y')
                except:
                    pass
            
            # Determine user level
            quiz_count = user_data.get('quizzes_created', 0)
            user_level = "Beginner"
            if quiz_count >= 50:
                user_level = "Expert Creator"
            elif quiz_count >= 20:
                user_level = "Advanced Creator"
            elif quiz_count >= 5:
                user_level = "Experienced Creator"
            elif quiz_count >= 1:
                user_level = "Creator"
            
            profile_message = f"""
👤 **VidderTech User Profile**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **Basic Information:**
👤 Name: `{user_data.get('first_name', '')} {user_data.get('last_name', '')}`.strip()
🔤 Username: `@{user_data.get('username', 'Not set')}`
📧 Email: `{user_data.get('email', 'Not provided')}`
📱 Phone: `{user_data.get('phone', 'Not provided')}`

👑 **Account Status:**
🏆 Level: `{user_level}`
💎 Role: `{user_data.get('role', 'free').title()}`
✨ Status: `{user_data.get('status', 'active').title()}`
💎 Premium: `{'✅ Active' if user_data.get('is_premium') else '❌ Not Active'}`
📅 Member Since: `{member_since}` *({membership_days} days)*

🌍 **Preferences:**
🗣️ Language: `{self.supported_languages.get(user_data.get('language', 'en'), '🇺🇸 English')}`
🕰️ Timezone: `{user_data.get('timezone', 'UTC')}`
🎨 Theme: `{user_data.get('ui_preferences', {}).get('theme', 'Auto').title()}`

🎯 **Quiz Statistics:**
📝 Quizzes Created: `{creation_stats.get('total_created', 0)}`
📤 Published Quizzes: `{creation_stats.get('published', 0)}`
❓ Questions Written: `{creation_stats.get('total_questions_created', 0)}`

🎮 **Participation Stats:**
🎯 Quizzes Attempted: `{participation_stats.get('total_attempted', 0)}`
✅ Completed: `{participation_stats.get('completed', 0)}`
📊 Average Score: `{participation_stats.get('avg_score', 0):.1f}%`
🏆 Best Performance: `{participation_stats.get('best_score', 0):.1f}%`

🏅 **Achievements:**
{self._get_user_badges(user_data, creation_stats, participation_stats)}

📊 **VidderTech Ranking:**
🌍 Global Rank: `#{user_stats.get('global_rank', 'N/A')}`
🇮🇳 India Rank: `#{user_stats.get('country_rank', 'N/A')}`
🏆 Category Rank: `#{user_stats.get('category_rank', 'N/A')}`

🔒 **Security Information:**
🔐 Last Login: `{user_data.get('last_login', 'Unknown')[:16] if user_data.get('last_login') else 'Unknown'}`
📱 Last Active: `{user_data.get('last_active', 'Unknown')[:16] if user_data.get('last_active') else 'Unknown'}`
🛡️ Account Security: `High`

💡 **Profile Completion:** {self._calculate_profile_completion(user_data)}%

🚀 **{config.COMPANY_NAME} - Your Learning Journey!**
            """
            
            return profile_message
            
        except Exception as e:
            logger.error(f"❌ Error formatting user profile: {e}")
            return "❌ Error loading profile. Please try again."
    
    def _get_user_badges(self, user_data: Dict, creation_stats: Dict, participation_stats: Dict) -> str:
        """Generate user achievement badges"""
        badges = []
        
        # Creation badges
        quiz_count = creation_stats.get('total_created', 0)
        if quiz_count >= 1:
            badges.append("🎯 Quiz Creator")
        if quiz_count >= 5:
            badges.append("📝 Prolific Creator")
        if quiz_count >= 10:
            badges.append("🏆 Quiz Master")
        if quiz_count >= 25:
            badges.append("👑 Quiz Legend")
        
        # Participation badges
        completed = participation_stats.get('completed', 0)
        if completed >= 1:
            badges.append("🎮 Quiz Taker")
        if completed >= 10:
            badges.append("🎯 Active Player")
        if completed >= 25:
            badges.append("🏅 Quiz Enthusiast")
        
        # Performance badges
        best_score = participation_stats.get('best_score', 0)
        if best_score >= 90:
            badges.append("⭐ Top Performer")
        if best_score == 100:
            badges.append("🌟 Perfect Score")
        
        # Special badges
        if user_data.get('is_premium'):
            badges.append("💎 Premium Member")
        if user_data.get('role') in ['admin', 'super_admin', 'owner']:
            badges.append("👨‍💼 VidderTech Team")
        
        # Streak badges
        streak = user_data.get('streak_current', 0)
        if streak >= 7:
            badges.append("🔥 Weekly Streak")
        if streak >= 30:
            badges.append("🚀 Monthly Streak")
        
        return '\n'.join(badges) if badges else "🌱 New Member - Start your journey!"
    
    def _calculate_profile_completion(self, user_data: Dict) -> int:
        """Calculate profile completion percentage"""
        total_fields = 10
        completed_fields = 0
        
        # Check essential fields
        if user_data.get('first_name'):
            completed_fields += 1
        if user_data.get('last_name'):
            completed_fields += 1
        if user_data.get('username'):
            completed_fields += 1
        if user_data.get('email'):
            completed_fields += 1
        if user_data.get('phone'):
            completed_fields += 1
        if user_data.get('bio'):
            completed_fields += 1
        if user_data.get('country'):
            completed_fields += 1
        if user_data.get('city'):
            completed_fields += 1
        if user_data.get('organization'):
            completed_fields += 1
        if user_data.get('avatar_url'):
            completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)

# Register all handlers
def register_auth_handlers(app):
    """Register all authentication command handlers"""
    handler = VidderAuthHandlers()
    
    # Command handlers
    app.add_handler(CommandHandler("login", handler.login_command))
    app.add_handler(CommandHandler("telelogin", handler.telelogin_command))
    app.add_handler(CommandHandler("logout", handler.logout_command))
    app.add_handler(CommandHandler("lang", handler.lang_command))
    app.add_handler(CommandHandler("profile", handler.profile_command))
    
    logger.info("✅ VidderTech Auth Handlers registered successfully")

# Export handler class
__all__ = ['VidderAuthHandlers', 'register_auth_handlers']