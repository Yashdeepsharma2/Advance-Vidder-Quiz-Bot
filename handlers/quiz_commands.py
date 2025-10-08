"""
Quiz command handlers for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import asyncio
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll, PollOption
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, 
    MessageHandler, PollHandler, filters
)
from telegram.constants import ParseMode

from config import config, Messages, QuizStates, CallbackData
from database.database import db_manager
from database.models import User, Quiz, Question, QuizType, QuizStatus, Analytics

# Configure logging
logger = logging.getLogger(__name__)

class QuizCommandHandlers:
    """Quiz command handlers for the bot"""
    
    @staticmethod
    async def create_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command to start creating quiz"""
        try:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Check if user exists
            user = await db_manager.get_user(user_id)
            if not user:
                await update.message.reply_text("❌ Please use /start first to register.")
                return
            
            if user.is_banned:
                await update.message.reply_text("❌ You are banned from creating quizzes.")
                return
            
            # Set user state to creating quiz
            context.user_data['state'] = QuizStates.CREATING_QUIZ
            context.user_data['quiz_data'] = {
                'title': None,
                'description': None,
                'questions': [],
                'quiz_type': 'free',
                'time_per_question': config.DEFAULT_QUESTION_TIME,
                'negative_marking': config.NEGATIVE_MARKING,
                'negative_marks': config.DEFAULT_NEGATIVE_MARKS,
                'sections': []
            }
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="quiz_creation_started",
                user_id=user_id,
                metadata={"chat_id": chat_id}
            )
            await db_manager.log_analytics(analytics)
            
            creation_message = f"""
🎯 **Welcome to {config.BRAND_NAME} Quiz Creator!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let's create an amazing quiz together! 

📝 **Step 1: Quiz Title**
Please send me the title for your quiz.

💡 **Tips for a great title:**
• Keep it clear and descriptive
• Use engaging language
• Mention the topic/subject
• Example: "General Knowledge Challenge 2024"

🚀 **What you can create:**
✅ Multiple Choice Questions
✅ True/False Questions  
✅ Sectional Quizzes
✅ Marathon Quizzes
✅ Assignment Quizzes

Type your quiz title below 👇
            """
            
            keyboard = [
                [InlineKeyboardButton("❌ Cancel Creation", callback_data="cancel_quiz")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                creation_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in create quiz command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def handle_quiz_creation_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input during quiz creation"""
        try:
            user_id = update.effective_user.id
            text = update.message.text.strip()
            state = context.user_data.get('state')
            
            if state == QuizStates.CREATING_QUIZ:
                # Handle quiz title input
                if not context.user_data.get('quiz_data', {}).get('title'):
                    context.user_data['quiz_data']['title'] = text
                    context.user_data['state'] = QuizStates.SETTING_TIMER
                    
                    timer_message = f"""
✅ **Quiz Title Set:** `{text}`

⏰ **Step 2: Question Timer**
How much time should each question have?

🕐 **Recommended Times:**
• 15 seconds - Quick fire quiz
• 30 seconds - Standard quiz (recommended)
• 60 seconds - Thoughtful quiz
• 120 seconds - Complex questions

Send the time in seconds (15-300), or use the buttons below:
                    """
                    
                    keyboard = [
                        [
                            InlineKeyboardButton("15s ⚡", callback_data="timer_15"),
                            InlineKeyboardButton("30s 📝", callback_data="timer_30"),
                            InlineKeyboardButton("60s 🤔", callback_data="timer_60")
                        ],
                        [
                            InlineKeyboardButton("120s 📚", callback_data="timer_120"),
                            InlineKeyboardButton("Custom ⚙️", callback_data="timer_custom")
                        ],
                        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_quiz")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        timer_message,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                    return
            
            elif state == QuizStates.SETTING_TIMER:
                # Handle timer input
                try:
                    timer = int(text)
                    if 15 <= timer <= 300:
                        context.user_data['quiz_data']['time_per_question'] = timer
                        await QuizCommandHandlers.show_quiz_options(update, context)
                    else:
                        await update.message.reply_text("❌ Timer must be between 15-300 seconds.")
                except ValueError:
                    await update.message.reply_text("❌ Please enter a valid number.")
                return
            
            elif state == QuizStates.ADDING_QUESTIONS:
                # Handle question input
                await QuizCommandHandlers.process_question_text(update, context, text)
                return
            
        except Exception as e:
            logger.error(f"Error handling quiz creation text: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def show_quiz_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show quiz creation options"""
        quiz_data = context.user_data.get('quiz_data', {})
        
        options_message = f"""
🎯 **Quiz Configuration**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Title:** `{quiz_data['title']}`
⏰ **Time per Question:** `{quiz_data['time_per_question']} seconds`
🎲 **Quiz Type:** `{quiz_data['quiz_type'].title()}`

📚 **Choose how to add questions:**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✍️ Type Questions", callback_data="add_manual"),
                InlineKeyboardButton("📄 From Text/File", callback_data="add_from_text")
            ],
            [
                InlineKeyboardButton("🔄 From Poll", callback_data="add_from_poll"),
                InlineKeyboardButton("🌐 From Web", callback_data="add_from_web")
            ],
            [
                InlineKeyboardButton("🤖 AI Generated", callback_data="add_ai"),
                InlineKeyboardButton("📱 From TestBook", callback_data="add_testbook")
            ],
            [
                InlineKeyboardButton("⚙️ Advanced Settings", callback_data="quiz_settings"),
                InlineKeyboardButton("✅ Finish Quiz", callback_data="finish_quiz")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_quiz")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                options_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                options_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    @staticmethod
    async def process_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Process question text with ✅ marking system"""
        try:
            lines = text.strip().split('\n')
            if len(lines) < 5:  # Question + at least 4 options
                await update.message.reply_text(
                    "❌ Invalid format. Please provide question and at least 4 options.\n\n"
                    "Format:\n"
                    "Question text here?\n"
                    "A) Option 1\n"
                    "B) Option 2 ✅\n"
                    "C) Option 3\n"
                    "D) Option 4"
                )
                return
            
            question_text = lines[0].strip()
            options = []
            correct_answer = -1
            
            for i, line in enumerate(lines[1:], 1):
                line = line.strip()
                if not line:
                    continue
                
                # Remove option letters (A), B), etc.)
                option_text = re.sub(r'^[A-Za-z]\)\s*', '', line)
                option_text = option_text.replace('✅', '').strip()
                
                if '✅' in line:
                    correct_answer = len(options)
                
                options.append(option_text)
                
                if len(options) >= 6:  # Max 6 options
                    break
            
            if correct_answer == -1:
                await update.message.reply_text(
                    "❌ Please mark the correct answer with ✅\n\n"
                    "Example:\n"
                    "What is 2+2?\n"
                    "A) 3\n"
                    "B) 4 ✅\n"
                    "C) 5\n"
                    "D) 6"
                )
                return
            
            if len(options) < 2:
                await update.message.reply_text("❌ Please provide at least 2 options.")
                return
            
            # Create question object
            question_id = db_manager.generate_id("q_")
            question = {
                'question_id': question_id,
                'question_text': question_text,
                'options': options,
                'correct_answer': correct_answer,
                'explanation': None,
                'question_type': 'mcq',
                'marks': 1,
                'time_limit': context.user_data['quiz_data']['time_per_question']
            }
            
            # Add to quiz data
            if 'questions' not in context.user_data['quiz_data']:
                context.user_data['quiz_data']['questions'] = []
            
            context.user_data['quiz_data']['questions'].append(question)
            question_count = len(context.user_data['quiz_data']['questions'])
            
            # Show confirmation
            confirmation_message = f"""
✅ **Question {question_count} Added Successfully!**

❓ **Question:** {question_text}

📝 **Options:**
"""
            for i, option in enumerate(options):
                marker = "✅" if i == correct_answer else "❌"
                confirmation_message += f"{chr(65+i)}) {option} {marker}\n"
            
            confirmation_message += f"\n📊 **Total Questions:** {question_count}"
            
            keyboard = [
                [
                    InlineKeyboardButton("➕ Add Another", callback_data="add_another"),
                    InlineKeyboardButton("✏️ Edit This", callback_data=f"edit_q_{question_count-1}")
                ],
                [
                    InlineKeyboardButton("🔙 Question Menu", callback_data="question_menu"),
                    InlineKeyboardButton("✅ Finish Quiz", callback_data="finish_quiz")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                confirmation_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error processing question text: {e}")
            await update.message.reply_text("❌ Error processing question. Please try again.")
    
    @staticmethod
    async def finish_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /done command to finish creating quiz"""
        try:
            user_id = update.effective_user.id
            quiz_data = context.user_data.get('quiz_data')
            
            if not quiz_data or not quiz_data.get('title'):
                await update.message.reply_text("❌ No quiz creation in progress. Use /create to start.")
                return
            
            if not quiz_data.get('questions'):
                await update.message.reply_text("❌ Please add at least one question to your quiz.")
                return
            
            # Create quiz in database
            quiz_id = db_manager.generate_id("quiz_")
            quiz = Quiz(
                quiz_id=quiz_id,
                creator_id=user_id,
                title=quiz_data['title'],
                description=quiz_data.get('description'),
                quiz_type=QuizType(quiz_data.get('quiz_type', 'free')),
                status=QuizStatus.DRAFT,
                time_per_question=quiz_data.get('time_per_question', 30),
                negative_marking=quiz_data.get('negative_marking', True),
                negative_marks=quiz_data.get('negative_marks', 0.25),
                sections=quiz_data.get('sections', []),
                total_questions=len(quiz_data['questions'])
            )
            
            success = await db_manager.create_quiz(quiz)
            if not success:
                await update.message.reply_text(Messages.ERROR_DATABASE)
                return
            
            # Add questions to database
            for i, q_data in enumerate(quiz_data['questions']):
                question = Question(
                    question_id=q_data['question_id'],
                    quiz_id=quiz_id,
                    question_text=q_data['question_text'],
                    options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data.get('explanation'),
                    question_type=q_data.get('question_type', 'mcq'),
                    order_index=i,
                    marks=q_data.get('marks', 1),
                    time_limit=q_data.get('time_limit')
                )
                await db_manager.add_question(question)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="quiz_created",
                user_id=user_id,
                quiz_id=quiz_id,
                metadata={
                    "title": quiz_data['title'],
                    "question_count": len(quiz_data['questions']),
                    "quiz_type": quiz_data.get('quiz_type', 'free')
                }
            )
            await db_manager.log_analytics(analytics)
            
            # Clear user state
            context.user_data.pop('state', None)
            context.user_data.pop('quiz_data', None)
            
            # Success message
            success_message = f"""
🎉 **Quiz Created Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Quiz Details:**
🏷️ Title: `{quiz_data['title']}`
🔢 ID: `{quiz_id}`
❓ Questions: `{len(quiz_data['questions'])}`
⏰ Time per Question: `{quiz_data['time_per_question']}s`
🎯 Type: `{quiz_data.get('quiz_type', 'free').title()}`

🚀 **What's Next:**
• Use `/edit {quiz_id}` to modify your quiz
• Share quiz ID with others to let them play
• Start quiz in groups with inline commands

🏆 **Built with {config.BRAND_NAME}**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✏️ Edit Quiz", callback_data=f"edit_quiz_{quiz_id}"),
                    InlineKeyboardButton("🎮 Test Quiz", callback_data=f"test_quiz_{quiz_id}")
                ],
                [
                    InlineKeyboardButton("📊 My Quizzes", callback_data="myquizzes"),
                    InlineKeyboardButton("🎯 Create Another", callback_data="create_quiz")
                ],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                success_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error finishing quiz: {e}")
            await update.message.reply_text(Messages.ERROR_DATABASE)
    
    @staticmethod
    async def my_quizzes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /myquizzes command"""
        try:
            user_id = update.effective_user.id
            
            # Get user quizzes
            quizzes = await db_manager.get_user_quizzes(user_id, limit=20)
            
            if not quizzes:
                empty_message = f"""
📝 **No Quizzes Yet**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You haven't created any quizzes yet!

🎯 **Get Started:**
• Use /create to create your first quiz
• Import from polls or TestBook
• Generate AI-powered questions

🚀 **{config.BRAND_NAME} makes quiz creation easy!**
                """
                
                keyboard = [
                    [InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz")],
                    [InlineKeyboardButton("🏠 Home", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    empty_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                return
            
            # Create quiz list message
            quiz_list = f"""
📊 **Your Quizzes ({len(quizzes)})**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            keyboard = []
            for i, quiz in enumerate(quizzes[:10], 1):
                status_emoji = {
                    'draft': '📝',
                    'active': '🟢', 
                    'completed': '✅',
                    'paused': '⏸️'
                }.get(quiz.status.value, '📝')
                
                quiz_list += f"""
{status_emoji} **{i}. {quiz.title}**
🔢 ID: `{quiz.quiz_id}`
❓ Questions: {quiz.total_questions}
📅 Created: {quiz.created_at.strftime('%Y-%m-%d') if quiz.created_at else 'Unknown'}
"""
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status_emoji} {quiz.title[:25]}...",
                        callback_data=f"view_quiz_{quiz.quiz_id}"
                    )
                ])
            
            # Add navigation buttons
            if len(quizzes) > 10:
                keyboard.append([
                    InlineKeyboardButton("◀️ Previous", callback_data="quizzes_prev_0"),
                    InlineKeyboardButton("▶️ Next", callback_data="quizzes_next_10")
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
            logger.error(f"Error in my quizzes command: {e}")
            await update.message.reply_text(Messages.ERROR_DATABASE)
    
    @staticmethod
    async def delete_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /del command to delete quiz"""
        try:
            user_id = update.effective_user.id
            
            if not context.args:
                await update.message.reply_text("❌ Please provide quiz ID: `/del quiz_id`", parse_mode=ParseMode.MARKDOWN)
                return
            
            quiz_id = context.args[0]
            
            # Check if quiz exists and user owns it
            quiz = await db_manager.get_quiz(quiz_id)
            if not quiz:
                await update.message.reply_text("❌ Quiz not found.")
                return
            
            if quiz.creator_id != user_id:
                await update.message.reply_text("❌ You can only delete your own quizzes.")
                return
            
            # Confirm deletion
            confirm_message = f"""
🗑️ **Confirm Quiz Deletion**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **WARNING:** This action cannot be undone!

📝 **Quiz to Delete:**
🏷️ Title: `{quiz.title}`
🔢 ID: `{quiz_id}`
❓ Questions: `{quiz.total_questions}`

Are you sure you want to delete this quiz?
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{quiz_id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                confirm_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in delete quiz command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)
    
    @staticmethod
    async def cancel_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command to stop quiz creation"""
        try:
            user_id = update.effective_user.id
            
            if context.user_data.get('state') not in [QuizStates.CREATING_QUIZ, QuizStates.ADDING_QUESTIONS, QuizStates.SETTING_TIMER]:
                await update.message.reply_text("❌ No quiz creation in progress.")
                return
            
            # Clear user state
            context.user_data.pop('state', None)
            context.user_data.pop('quiz_data', None)
            
            # Log analytics
            analytics = Analytics(
                analytics_id=db_manager.generate_id("analytics_"),
                event_type="quiz_creation_cancelled",
                user_id=user_id
            )
            await db_manager.log_analytics(analytics)
            
            cancel_message = f"""
❌ **Quiz Creation Cancelled**

No worries! You can start creating a quiz anytime.

🎯 **Quick Actions:**
• Use /create to start a new quiz
• Use /myquizzes to see existing quizzes
• Use /help for all commands

🚀 **{config.BRAND_NAME} is here when you're ready!**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz"),
                    InlineKeyboardButton("📊 My Quizzes", callback_data="myquizzes")
                ],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                cancel_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in cancel quiz command: {e}")
            await update.message.reply_text(Messages.ERROR_INVALID_COMMAND)

# Callback query handlers for quiz commands
async def quiz_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries for quiz commands"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "create_quiz":
            # Simulate create command
            context.user_data['state'] = QuizStates.CREATING_QUIZ
            context.user_data['quiz_data'] = {
                'title': None,
                'description': None,
                'questions': [],
                'quiz_type': 'free',
                'time_per_question': config.DEFAULT_QUESTION_TIME,
                'negative_marking': config.NEGATIVE_MARKING,
                'negative_marks': config.DEFAULT_NEGATIVE_MARKS,
                'sections': []
            }
            
            creation_message = f"""
🎯 **Welcome to {config.BRAND_NAME} Quiz Creator!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let's create an amazing quiz together! 

📝 **Step 1: Quiz Title**
Please send me the title for your quiz.

Type your quiz title below 👇
            """
            
            keyboard = [
                [InlineKeyboardButton("❌ Cancel Creation", callback_data="cancel_quiz")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                creation_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        elif data == "myquizzes":
            # Show user's quizzes
            quizzes = await db_manager.get_user_quizzes(user_id, limit=10)
            
            if not quizzes:
                empty_message = f"""
📝 **No Quizzes Yet**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You haven't created any quizzes yet!

🎯 **Get Started:**
Use the button below to create your first quiz!
                """
                
                keyboard = [
                    [InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz")],
                    [InlineKeyboardButton("🏠 Home", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    empty_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                quiz_list = f"📊 **Your Quizzes ({len(quizzes)})**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                keyboard = []
                for i, quiz in enumerate(quizzes, 1):
                    status_emoji = {
                        'draft': '📝',
                        'active': '🟢', 
                        'completed': '✅'
                    }.get(quiz.status.value, '📝')
                    
                    quiz_list += f"{status_emoji} **{i}. {quiz.title}**\n🔢 ID: `{quiz.quiz_id}`\n❓ Questions: {quiz.total_questions}\n\n"
                    
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{status_emoji} {quiz.title[:30]}...",
                            callback_data=f"view_quiz_{quiz.quiz_id}"
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
                
                await query.edit_message_text(
                    quiz_list,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                
        elif data.startswith("timer_"):
            # Handle timer selection
            timer_value = data.split("_")[1]
            if timer_value != "custom":
                context.user_data['quiz_data']['time_per_question'] = int(timer_value)
                await QuizCommandHandlers.show_quiz_options(update, context)
            
        elif data == "add_manual":
            # Switch to manual question adding mode
            context.user_data['state'] = QuizStates.ADDING_QUESTIONS
            
            instruction_message = f"""
✍️ **Manual Question Entry Mode**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **How to add questions:**
1. Type your question text
2. Add options (A, B, C, D, etc.)
3. Mark correct answer with ✅

📋 **Example Format:**
```
What is the capital of France?
A) London
B) Berlin  
C) Paris ✅
D) Madrid
```

💡 **Tips:**
• You can add 2-6 options per question
• Mark only ONE correct answer with ✅
• Questions are added immediately after sending

Type your first question below 👇
            """
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Options", callback_data="question_menu")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_quiz")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                instruction_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        elif data == "finish_quiz":
            # Finish quiz creation
            quiz_data = context.user_data.get('quiz_data')
            
            if not quiz_data or not quiz_data.get('questions'):
                await query.edit_message_text("❌ Please add at least one question to your quiz.")
                return
            
            # Create quiz in database (similar to done command)
            await QuizCommandHandlers.finish_quiz_creation(query, context)
            
        elif data == "cancel_quiz":
            # Cancel quiz creation
            context.user_data.pop('state', None)
            context.user_data.pop('quiz_data', None)
            
            await query.edit_message_text(
                "❌ Quiz creation cancelled. Use /create to start again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎯 Create Quiz", callback_data="create_quiz"),
                    InlineKeyboardButton("🏠 Home", callback_data="start")
                ]])
            )
        
    except Exception as e:
        logger.error(f"Error in quiz callback handler: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

# Register handlers
def register_quiz_handlers(app):
    """Register quiz command handlers"""
    app.add_handler(CommandHandler("create", QuizCommandHandlers.create_quiz_command))
    app.add_handler(CommandHandler("done", QuizCommandHandlers.finish_quiz_command))
    app.add_handler(CommandHandler("myquizzes", QuizCommandHandlers.my_quizzes_command))
    app.add_handler(CommandHandler("del", QuizCommandHandlers.delete_quiz_command))
    app.add_handler(CommandHandler("cancel", QuizCommandHandlers.cancel_quiz_command))
    
    # Message handler for quiz creation
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        QuizCommandHandlers.handle_quiz_creation_text
    ))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(
        quiz_callback_handler,
        pattern="^(create_quiz|myquizzes|timer_|add_manual|finish_quiz|cancel_quiz|question_menu).*"
    ))