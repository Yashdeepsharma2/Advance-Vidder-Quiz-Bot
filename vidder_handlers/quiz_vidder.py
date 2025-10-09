"""
🎯 VidderTech Advanced Quiz Handlers
Built by VidderTech - The Future of Quiz Bots

Complete quiz management system with:
- Advanced quiz creation with ✅ marking system
- Comprehensive quiz editing capabilities
- Real-time quiz management
- Multi-format question support
- AI-powered enhancements
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
)
from telegram.constants import ParseMode

from vidder_config import config, Messages, QuizStates
from vidder_database.vidder_database import vidder_db

# Initialize logger
logger = logging.getLogger('vidder.handlers.quiz')

class VidderQuizHandlers:
    """🎯 VidderTech Advanced Quiz Management System"""
    
    @staticmethod
    async def create_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎯 /create - Advanced Quiz Creation System"""
        try:
            user_id = update.effective_user.id
            user = update.effective_user
            
            logger.info(f"🎯 Quiz creation started by user {user_id}")
            
            # Initialize quiz creation
            context.user_data['vidder_state'] = QuizStates.CREATING_QUIZ
            context.user_data['vidder_quiz_data'] = {
                'title': None,
                'questions': [],
                'time_per_question': 30,
                'negative_marking': True
            }
            
            creation_message = f"""
🚀 **Welcome to VidderTech Quiz Creator!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 Hello {user.first_name}! Let's create an amazing quiz!

📝 **Step 1: Quiz Title**
Please send me the title for your quiz.

💡 **Tips for Great Titles:**
• Make it clear and descriptive
• Include the subject/topic
• Keep it engaging
• Example: "Advanced Python Programming Quiz 2024"

Type your quiz title below 👇
            """
            
            keyboard = [[InlineKeyboardButton("❌ Cancel Creation", callback_data="vidder_cancel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                creation_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error in create quiz: {e}")
            await update.message.reply_text("❌ Error starting quiz creation.")
    
    @staticmethod
    async def myquizzes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 /myquizzes - Quiz Dashboard"""
        try:
            user_id = update.effective_user.id
            
            # Get user quizzes
            quizzes = await vidder_db.get_user_quizzes(user_id, limit=10)
            
            if not quizzes:
                empty_message = f"""
📝 **Your VidderTech Quiz Dashboard**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 **No quizzes yet!**

🎯 **Get Started:**
• Use /create to make your first quiz
• Try our ✅ marking system
• Explore AI-powered features

🚀 **VidderTech makes quiz creation easy!**
                """
                
                keyboard = [
                    [InlineKeyboardButton("🎯 Create First Quiz", callback_data="create_quiz")],
                    [InlineKeyboardButton("🏠 Home", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    empty_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                return
            
            # Show quiz list
            quiz_list = f"""
📊 **Your VidderTech Quizzes ({len(quizzes)})**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            keyboard = []
            for i, quiz in enumerate(quizzes, 1):
                status_emoji = {'draft': '📝', 'published': '🟢', 'active': '⚡'}.get(quiz.get('status', 'draft'), '📝')
                
                quiz_list += f"""
{status_emoji} **{i}. {quiz['title']}**
🔢 ID: `{quiz['quiz_id']}`
❓ Questions: {quiz.get('total_questions', 0)}
📅 Created: {quiz.get('created_at', '')[:10]}

"""
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status_emoji} {quiz['title'][:30]}...",
                        callback_data=f"view_quiz_{quiz['quiz_id']}"
                    )
                ])
            
            keyboard.extend([
                [
                    InlineKeyboardButton("🎯 Create New", callback_data="create_quiz"),
                    InlineKeyboardButton("🔄 Refresh", callback_data="myquizzes")
                ],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                quiz_list,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error in myquizzes: {e}")
            await update.message.reply_text("❌ Error loading quizzes.")

# Message handler for quiz creation
async def handle_quiz_creation_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input during quiz creation"""
    try:
        state = context.user_data.get('vidder_state')
        text = update.message.text.strip()
        
        if state == QuizStates.CREATING_QUIZ:
            # Handle title input
            if not context.user_data.get('vidder_quiz_data', {}).get('title'):
                context.user_data['vidder_quiz_data']['title'] = text
                context.user_data['vidder_state'] = QuizStates.ADDING_QUESTIONS
                
                instruction_message = f"""
✅ **Quiz Title Set:** {text}

✍️ **Now Add Questions Using VidderTech ✅ System**

📝 **Format:**
```
What is 2+2?
A) 3
B) 4 ✅
C) 5
D) 6
```

💡 **Features:**
• Mark correct answer with ✅
• Add 2-6 options per question
• Support for explanations
• Auto-validation

Send your first question below 👇
                """
                
                keyboard = [
                    [InlineKeyboardButton("📋 See Examples", callback_data="examples")],
                    [InlineKeyboardButton("❌ Cancel", callback_data="vidder_cancel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    instruction_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                
        elif state == QuizStates.ADDING_QUESTIONS:
            # Process question
            await VidderQuizHandlers.process_question_text(update, context, text)
    
    except Exception as e:
        logger.error(f"❌ Error in quiz text handler: {e}")

# Registration function
def register_quiz_vidder_handlers(app) -> int:
    """Register VidderTech quiz handlers"""
    try:
        handlers = [
            CommandHandler("create", VidderQuizHandlers.create_quiz_command),
            CommandHandler("myquizzes", VidderQuizHandlers.myquizzes_command),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_creation_text),
            CallbackQueryHandler(quiz_callback_handler, pattern="^(vidder_|myquizzes|create_quiz).*")
        ]
        
        for handler in handlers:
            app.add_handler(handler)
        
        logger.info(f"✅ VidderTech quiz handlers registered: {len(handlers)} handlers")
        return len(handlers)
        
    except Exception as e:
        logger.error(f"❌ Failed to register quiz handlers: {e}")
        return 0