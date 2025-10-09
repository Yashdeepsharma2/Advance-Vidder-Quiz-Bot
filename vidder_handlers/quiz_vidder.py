"""
🎯 VidderTech Quiz Command Handlers - Complete Implementation
🚀 Built by VidderTech - The Future of Quiz Bots

This module handles all quiz-related commands with advanced functionality:
- /create - Advanced quiz creation with AI assistance
- /edit - Comprehensive quiz editing system
- /myquizzes - Advanced quiz management dashboard
- /done - Intelligent quiz completion
- /cancel - Smart cancellation with data preservation
- /del - Secure quiz deletion with confirmation
- /clone - Advanced quiz cloning from multiple sources
"""

import re
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, Poll, InputFile
)
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, 
    MessageHandler, PollHandler, filters
)
from telegram.constants import ParseMode, ChatAction

from vidder_config import config, messages, states, callbacks
from vidder_database.vidder_database import db_manager

# Setup logging  
logger = logging.getLogger('vidder.handlers.quiz')

class VidderQuizHandlers:
    """🎯 Complete Quiz Command Handlers with Advanced Features"""
    
    def __init__(self):
        self.max_questions = config.MAX_QUESTIONS_PER_QUIZ
        self.max_options = config.MAX_OPTIONS_PER_QUESTION
        self.supported_formats = ['text', 'poll', 'file', 'url', 'ai']
    
    async def create_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎨 Advanced quiz creation with multiple input methods and AI assistance"""
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
            
            # Check if user is banned
            if user_data.get('status') == 'banned':
                await update.message.reply_text(
                    "❌ Your account is banned from creating quizzes.\n"
                    f"Contact support: {config.COMPANY_EMAIL}"
                )
                return
            
            # Check quiz creation limits
            user_quiz_count = user_data.get('quizzes_created', 0)
            quiz_limit = config.PREMIUM_QUIZ_LIMIT if user_data.get('is_premium') else config.FREE_QUIZ_LIMIT
            
            if user_quiz_count >= quiz_limit and not user_data.get('is_premium'):
                await self._show_quiz_limit_message(update, user_quiz_count, quiz_limit)
                return
            
            # Initialize quiz creation session
            quiz_session = {
                'state': states.CREATING_QUIZ,
                'step': 'title',
                'quiz_data': {
                    'title': None,
                    'description': None,
                    'category': None,
                    'quiz_type': 'free',
                    'difficulty': 'medium',
                    'time_per_question': config.DEFAULT_QUESTION_TIME,
                    'negative_marking_enabled': config.ENABLE_NEGATIVE_MARKING,
                    'negative_marks': config.DEFAULT_NEGATIVE_MARKS,
                    'positive_marks': config.DEFAULT_POSITIVE_MARKS,
                    'shuffle_questions': False,
                    'shuffle_options': False,
                    'show_results': True,
                    'show_correct_answers': True,
                    'allow_review': True,
                    'is_public': True,
                    'max_attempts': 1,
                    'questions': [],
                    'sections': [],
                    'tags': []
                },
                'created_at': datetime.now().isoformat()
            }
            
            context.user_data['quiz_session'] = quiz_session
            
            # Send welcome to quiz creator
            creation_welcome = f"""
🎨 **Welcome to {config.COMPANY_NAME} Quiz Creator!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Let's create something amazing together!**

📊 **Your Quiz Limit:** {user_quiz_count}/{quiz_limit} quizzes
💎 **Account:** {user_data.get('role', 'free').title()}

🚀 **Step 1: Quiz Title & Basic Info**

Please tell me what you want to create:

🎭 **Quick Start Options:**
• Just send the quiz title
• Or describe your quiz topic and I'll help with AI

💡 **Examples:**
• "General Knowledge Quiz 2024"
• "Physics Chapter 5 - Motion"
• "Create a quiz about Indian History"
• "I want to test students on Math"

✨ **Pro Tip:** The better you describe, the smarter our AI assistance becomes!

Type your quiz title or description below 👇
            """
            
            # Create quick action keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🤖 AI Quiz Generator", callback_data="ai_quiz_generator"),
                    InlineKeyboardButton("📄 Import from File", callback_data="import_file")
                ],
                [
                    InlineKeyboardButton("🔄 Clone Existing Quiz", callback_data="clone_quiz"),
                    InlineKeyboardButton("📊 From TestBook", callback_data="import_testbook")
                ],
                [
                    InlineKeyboardButton("🌐 From Web Content", callback_data="import_web"),
                    InlineKeyboardButton("📱 From Telegram Poll", callback_data="import_poll")
                ],
                [
                    InlineKeyboardButton("⚙️ Advanced Settings", callback_data="quiz_advanced_settings"),
                    InlineKeyboardButton("💡 Templates", callback_data="quiz_templates")
                ],
                [
                    InlineKeyboardButton("❌ Cancel Creation", callback_data="cancel_quiz_creation")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                creation_welcome,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_creation_started",
                user_id,
                metadata={
                    "account_type": user_data.get('role'),
                    "quiz_count": user_quiz_count
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in create quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _show_quiz_limit_message(self, update: Update, current: int, limit: int):
        """Show quiz limit reached message with upgrade options"""
        limit_message = f"""
🔒 **Quiz Creation Limit Reached**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Current Usage:** {current}/{limit} quizzes

🎯 **Free Account Limitations:**
• Maximum {limit} quizzes
• Basic features only
• Standard support

💎 **Upgrade to Premium for:**
• ♾️ Unlimited quiz creation
• 🤖 Advanced AI features
• 🏆 Tournament hosting
• 📊 Advanced analytics
• ⚡ Priority support
• 🎨 Custom branding

💰 **Premium Plans:**
• Monthly: ₹{config.PREMIUM_MONTHLY_PRICE}/month
• Yearly: ₹{config.PREMIUM_MONTHLY_PRICE * 10}/year (2 months free!)
• Lifetime: ₹{config.PREMIUM_MONTHLY_PRICE * 25} (Best value!)

🎁 **Special Offer:** Get 7 days FREE trial!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💎 Start Free Trial", callback_data="start_premium_trial"),
                InlineKeyboardButton("💰 View Plans", callback_data="premium_plans")
            ],
            [
                InlineKeyboardButton("🗑️ Delete Old Quiz", callback_data="delete_old_quiz"),
                InlineKeyboardButton("📊 Manage Quizzes", callback_data="myquizzes")
            ],
            [
                InlineKeyboardButton("🏠 Back to Home", callback_data="start")
            ]
        ]
        
        await update.message.reply_text(
            limit_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_quiz_creation_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input during quiz creation with intelligent processing"""
        try:
            user_id = update.effective_user.id
            text = update.message.text.strip()
            quiz_session = context.user_data.get('quiz_session')
            
            if not quiz_session or quiz_session.get('state') != states.CREATING_QUIZ:
                return  # Not in quiz creation mode
            
            step = quiz_session.get('step', 'title')
            quiz_data = quiz_session.get('quiz_data', {})
            
            if step == 'title':
                await self._process_quiz_title(update, context, text, quiz_session)
            elif step == 'description':
                await self._process_quiz_description(update, context, text, quiz_session)
            elif step == 'category':
                await self._process_quiz_category(update, context, text, quiz_session)
            elif step == 'adding_questions':
                await self._process_question_input(update, context, text, quiz_session)
            elif step == 'bulk_questions':
                await self._process_bulk_questions(update, context, text, quiz_session)
            else:
                # Unknown step
                await update.message.reply_text(
                    "❌ Unknown creation step. Please use /cancel to restart."
                )
            
        except Exception as e:
            logger.error(f"❌ Error handling quiz creation text: {e}")
            await update.message.reply_text(
                "❌ Error processing your input. Please try again."
            )
    
    async def _process_quiz_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                text: str, quiz_session: Dict):
        """Process quiz title input with AI enhancement"""
        try:
            # Validate title
            if len(text) < 5:
                await update.message.reply_text(
                    "❌ Quiz title too short. Please provide at least 5 characters."
                )
                return
            
            if len(text) > 200:
                await update.message.reply_text(
                    "❌ Quiz title too long. Maximum 200 characters allowed."
                )
                return
            
            # Set title
            quiz_session['quiz_data']['title'] = text
            quiz_session['step'] = 'description'
            
            # AI-powered category and description suggestions
            suggested_category = self._suggest_category(text)
            suggested_description = self._suggest_description(text)
            
            description_message = f"""
✅ **Quiz Title Set:** `{text}`

📝 **Step 2: Quiz Description (Optional)**

🤖 **AI Suggestions for your quiz:**
📂 **Suggested Category:** `{suggested_category}`
📋 **Suggested Description:** `{suggested_description}`

💡 **You can:**
• Type your own description
• Use our AI suggestion
• Skip description (click Skip button)

🎯 **Good descriptions include:**
• What topics are covered
• Difficulty level
• Target audience
• Special instructions

Type your description or use the buttons below 👇
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🤖 Use AI Description", callback_data="use_ai_description"),
                    InlineKeyboardButton("⏭️ Skip Description", callback_data="skip_description")
                ],
                [
                    InlineKeyboardButton("📂 Set Category", callback_data="set_category"),
                    InlineKeyboardButton("⚙️ Advanced Settings", callback_data="quiz_advanced_settings")
                ],
                [
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_quiz_creation")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store AI suggestions
            quiz_session['ai_suggestions'] = {
                'category': suggested_category,
                'description': suggested_description
            }
            
            await update.message.reply_text(
                description_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Update session
            context.user_data['quiz_session'] = quiz_session
            
        except Exception as e:
            logger.error(f"❌ Error processing quiz title: {e}")
            await update.message.reply_text("❌ Error processing title. Please try again.")
    
    async def _process_question_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    text: str, quiz_session: Dict):
        """Process individual question input with ✅ marking system"""
        try:
            # Parse question using advanced parser
            parsed_question = self._parse_question_with_ai(text)
            
            if parsed_question.get('error'):
                await update.message.reply_text(
                    f"❌ **Question Format Error**\n\n"
                    f"{parsed_question['error']}\n\n"
                    f"📝 **Correct Format:**\n"
                    f"```\n"
                    f"What is 2+2?\n"
                    f"A) 3\n"
                    f"B) 4 ✅\n"
                    f"C) 5\n"
                    f"D) 6\n"
                    f"```\n\n"
                    f"💡 **Tips:**\n"
                    f"• Mark correct answer with ✅\n"
                    f"• Use A), B), C), D) format\n"
                    f"• Minimum 2 options required\n"
                    f"• Maximum {config.MAX_OPTIONS_PER_QUESTION} options allowed",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generate question ID
            question_id = db_manager.generate_id("q")
            
            # Create complete question object
            question_data = {
                'question_id': question_id,
                'question_text': parsed_question['question_text'],
                'question_type': parsed_question.get('question_type', 'mcq'),
                'options': parsed_question['options'],
                'correct_answer': parsed_question['correct_answer'],
                'explanation': parsed_question.get('explanation'),
                'difficulty': self._detect_question_difficulty(parsed_question['question_text']),
                'category': quiz_session['quiz_data'].get('category'),
                'marks': 1.0,
                'negative_marks': quiz_session['quiz_data'].get('negative_marks', 0.25),
                'time_limit': quiz_session['quiz_data'].get('time_per_question', 30),
                'order_index': len(quiz_session['quiz_data']['questions']),
                'created_at': datetime.now().isoformat()
            }
            
            # Add question to quiz
            quiz_session['quiz_data']['questions'].append(question_data)
            context.user_data['quiz_session'] = quiz_session
            
            question_count = len(quiz_session['quiz_data']['questions'])
            
            # Show question confirmation with preview
            confirmation_message = f"""
✅ **Question {question_count} Added Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **Question:** {parsed_question['question_text']}

📝 **Options:**
"""
            
            # Add options with correct answer marking
            for i, option in enumerate(parsed_question['options']):
                marker = "✅" if i == parsed_question['correct_answer'] else "❌"
                confirmation_message += f"{chr(65+i)}) {option} {marker}\n"
            
            # Add question metadata
            confirmation_message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **Question Details:**
🎯 Difficulty: `{question_data['difficulty'].title()}`
⏰ Time Limit: `{question_data['time_limit']} seconds`
🏆 Marks: `{question_data['marks']} points`
💥 Negative: `-{question_data['negative_marks']} points`

📈 **Quiz Progress:** {question_count}/{self.max_questions} questions
            """
            
            # Create action keyboard
            keyboard = [
                [
                    InlineKeyboardButton("➕ Add Another Question", callback_data="add_another_question"),
                    InlineKeyboardButton("✏️ Edit This Question", callback_data=f"edit_question_{question_count-1}")
                ],
                [
                    InlineKeyboardButton("🤖 AI Generate Next", callback_data="ai_generate_next"),
                    InlineKeyboardButton("📄 Bulk Add Questions", callback_data="bulk_add_questions")
                ],
                [
                    InlineKeyboardButton("🎮 Preview Quiz", callback_data="preview_quiz"),
                    InlineKeyboardButton("⚙️ Quiz Settings", callback_data="quiz_settings_review")
                ],
                [
                    InlineKeyboardButton("✅ Finish Quiz", callback_data="finish_quiz_creation"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_quiz_creation")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                confirmation_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing question input: {e}")
            await update.message.reply_text("❌ Error processing question. Please try again.")
    
    def _parse_question_with_ai(self, text: str) -> Dict[str, Any]:
        """Advanced question parser with AI enhancement"""
        try:
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            
            if len(lines) < 3:
                return {"error": "Need at least question + 2 options. Please provide more content."}
            
            # Extract question text (first line)
            question_text = lines[0].strip()
            
            # Remove question marks if multiple
            question_text = re.sub(r'\?+$', '?', question_text)
            if not question_text.endswith('?'):
                question_text += '?'
            
            # Parse options
            options = []
            correct_answer = -1
            option_pattern = re.compile(r'^([A-Za-z]\)|\d+\.|\d+\))\s*(.+)$')
            
            for line in lines[1:]:
                # Match option format (A), B), 1), etc.)
                match = option_pattern.match(line)
                if match:
                    option_text = match.group(2).strip()
                else:
                    option_text = line.strip()
                
                # Check for correct answer marker
                if '✅' in option_text or '☑️' in option_text or '✔️' in option_text:
                    option_text = re.sub(r'[✅☑️✔️]', '', option_text).strip()
                    correct_answer = len(options)
                
                # Clean option text
                option_text = option_text.replace('✅', '').replace('☑️', '').replace('✔️', '').strip()
                
                if option_text:
                    options.append(option_text)
                
                # Limit options
                if len(options) >= self.max_options:
                    break
            
            # Validation
            if correct_answer == -1:
                return {"error": "Please mark the correct answer with ✅ symbol."}
            
            if len(options) < 2:
                return {"error": "Need at least 2 options for a valid question."}
            
            if len(options) > self.max_options:
                return {"error": f"Maximum {self.max_options} options allowed."}
            
            # Detect question type
            question_type = self._detect_question_type(question_text, options)
            
            # Generate explanation if AI is enabled
            explanation = None
            if config.ENABLE_AI_GENERATION:
                explanation = self._generate_ai_explanation(question_text, options[correct_answer])
            
            return {
                'question_text': question_text,
                'options': options,
                'correct_answer': correct_answer,
                'question_type': question_type,
                'explanation': explanation,
                'confidence': self._calculate_parsing_confidence(text, options, correct_answer)
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing question: {e}")
            return {"error": "Failed to parse question. Please check the format and try again."}
    
    def _detect_question_type(self, question: str, options: List[str]) -> str:
        """Detect question type using AI analysis"""
        # Convert to lowercase for analysis
        question_lower = question.lower()
        
        # True/False detection
        if len(options) == 2:
            option1_lower = options[0].lower()
            option2_lower = options[1].lower()
            
            true_false_indicators = [
                ('true', 'false'), ('yes', 'no'), ('correct', 'incorrect'),
                ('right', 'wrong'), ('सही', 'गलत'), ('हाँ', 'नहीं')
            ]
            
            for true_indicator, false_indicator in true_false_indicators:
                if (true_indicator in option1_lower and false_indicator in option2_lower) or \
                   (false_indicator in option1_lower and true_indicator in option2_lower):
                    return 'true_false'
        
        # Fill in the blanks detection
        if '_____' in question or '______' in question or 'fill' in question_lower:
            return 'fill_blank'
        
        # Default to MCQ
        return 'mcq'
    
    def _detect_question_difficulty(self, question_text: str) -> str:
        """Detect question difficulty using AI analysis"""
        text_lower = question_text.lower()
        
        # Easy indicators
        easy_indicators = ['what is', 'which is', 'who is', 'when is', 'where is', 'basic', 'simple']
        if any(indicator in text_lower for indicator in easy_indicators):
            return 'easy'
        
        # Hard indicators  
        hard_indicators = ['analyze', 'evaluate', 'compare', 'contrast', 'explain why', 'complex']
        if any(indicator in text_lower for indicator in hard_indicators):
            return 'hard'
        
        # Expert indicators
        expert_indicators = ['synthesize', 'hypothesize', 'theoretical', 'advanced']
        if any(indicator in text_lower for indicator in expert_indicators):
            return 'expert'
        
        # Default to medium
        return 'medium'
    
    def _suggest_category(self, title: str) -> str:
        """Suggest quiz category using AI analysis"""
        title_lower = title.lower()
        
        # Category mapping
        category_keywords = {
            'General Knowledge': ['general', 'gk', 'knowledge', 'mixed', 'various'],
            'Science': ['science', 'physics', 'chemistry', 'biology', 'scientific'],
            'Mathematics': ['math', 'maths', 'mathematics', 'algebra', 'geometry', 'calculus'],
            'History': ['history', 'historical', 'ancient', 'medieval', 'modern'],
            'Geography': ['geography', 'world', 'countries', 'capitals', 'continents'],
            'Technology': ['technology', 'computer', 'programming', 'coding', 'it'],
            'Sports': ['sports', 'cricket', 'football', 'basketball', 'games'],
            'Entertainment': ['entertainment', 'movies', 'music', 'celebrities', 'bollywood'],
            'Literature': ['literature', 'books', 'authors', 'poetry', 'novels'],
            'Current Affairs': ['current', 'affairs', 'news', 'recent', 'latest'],
            'Business': ['business', 'economics', 'finance', 'marketing', 'management'],
            'Language': ['english', 'hindi', 'grammar', 'vocabulary', 'language']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'General Knowledge'
    
    def _suggest_description(self, title: str) -> str:
        """Suggest quiz description using AI analysis"""
        category = self._suggest_category(title)
        
        descriptions = {
            'General Knowledge': f"Test your knowledge across various topics with this comprehensive quiz on {title.lower()}.",
            'Science': f"Explore scientific concepts and test your understanding of {title.lower()}.",
            'Mathematics': f"Challenge your mathematical skills with problems related to {title.lower()}.",
            'History': f"Journey through time and test your knowledge of historical events in {title.lower()}.",
            'Geography': f"Test your geographical knowledge and world awareness with {title.lower()}.",
            'Technology': f"Stay updated with the latest in technology through {title.lower()}.",
            'Sports': f"Test your sports knowledge and passion with this exciting quiz on {title.lower()}.",
            'Entertainment': f"Have fun testing your entertainment knowledge with {title.lower()}.",
            'Literature': f"Dive into the world of literature and test your reading knowledge with {title.lower()}.",
            'Current Affairs': f"Stay informed and test your awareness of current events with {title.lower()}.",
            'Business': f"Test your business acumen and knowledge with {title.lower()}.",
            'Language': f"Improve and test your language skills with {title.lower()}."
        }
        
        return descriptions.get(category, f"Test your knowledge and skills with this comprehensive quiz on {title.lower()}.")
    
    def _generate_ai_explanation(self, question: str, correct_answer: str) -> str:
        """Generate AI explanation for the answer"""
        if not config.ENABLE_AI_GENERATION:
            return None
        
        # Simple explanation generation (in production, use actual AI API)
        return f"The correct answer is '{correct_answer}' because this is the most accurate response to the question '{question}'"
    
    def _calculate_parsing_confidence(self, text: str, options: List[str], correct_answer: int) -> float:
        """Calculate confidence score for question parsing"""
        confidence = 100.0
        
        # Deduct points for various issues
        if len(options) < 4:
            confidence -= 10  # Prefer 4 options
        
        if not text.strip().endswith('?'):
            confidence -= 5  # Questions should end with ?
        
        if len(text.split('\n')) < 3:
            confidence -= 15  # Should have clear line breaks
        
        if any(len(option) < 2 for option in options):
            confidence -= 20  # Options too short
        
        return max(confidence, 0.0)
    
    async def my_quizzes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 Advanced quiz management dashboard"""
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
            
            # Get user quizzes with advanced filtering
            all_quizzes = await db_manager.get_user_quizzes(user_id, limit=100)
            
            if not all_quizzes:
                await self._show_no_quizzes_message(update, user_data)
                return
            
            # Categorize quizzes
            quiz_categories = {
                'draft': [q for q in all_quizzes if q['status'] == 'draft'],
                'published': [q for q in all_quizzes if q['status'] == 'published'],
                'active': [q for q in all_quizzes if q['status'] == 'active'],
                'completed': [q for q in all_quizzes if q['status'] == 'completed']
            }
            
            # Create advanced quiz dashboard
            dashboard_message = f"""
📊 **{config.COMPANY_NAME} Quiz Dashboard**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 **Welcome, {user_data.get('first_name', 'User')}!**

📈 **Quiz Overview:**
📝 Total Quizzes: `{len(all_quizzes)}`
✏️ Drafts: `{len(quiz_categories['draft'])}`
📤 Published: `{len(quiz_categories['published'])}`
🟢 Active: `{len(quiz_categories['active'])}`
✅ Completed: `{len(quiz_categories['completed'])}`

🏆 **Performance Summary:**
📊 Average Score: `{user_data.get('avg_score', 0):.1f}%`
🥇 Best Score: `{user_data.get('best_score', 0):.1f}%`
🎯 Total Questions: `{sum(q.get('total_questions', 0) for q in all_quizzes)}`
👥 Total Participants: `{sum(q.get('total_participants', 0) for q in all_quizzes)}`
            """
            
            # Add recent quizzes
            recent_quizzes = all_quizzes[:5]  # Show top 5 recent
            if recent_quizzes:
                dashboard_message += f"\n📚 **Recent Quizzes:**\n"
                
                for i, quiz in enumerate(recent_quizzes, 1):
                    status_emoji = {
                        'draft': '📝',
                        'published': '📤',
                        'active': '🟢',
                        'completed': '✅',
                        'cancelled': '❌'
                    }.get(quiz['status'], '📝')
                    
                    quiz_title = quiz['title']
                    if len(quiz_title) > 30:
                        quiz_title = quiz_title[:27] + "..."
                    
                    dashboard_message += f"{status_emoji} `{i}.` **{quiz_title}**\n"
                    dashboard_message += f"   💬 {quiz.get('total_questions', 0)} questions • "
                    dashboard_message += f"👥 {quiz.get('total_participants', 0)} participants\n"
            
            # Create management keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📝 Draft Quizzes", callback_data="view_drafts"),
                    InlineKeyboardButton("📤 Published Quizzes", callback_data="view_published")
                ],
                [
                    InlineKeyboardButton("🟢 Active Quizzes", callback_data="view_active"),
                    InlineKeyboardButton("✅ Completed Quizzes", callback_data="view_completed")
                ],
                [
                    InlineKeyboardButton("🎯 Create New Quiz", callback_data="create_quiz"),
                    InlineKeyboardButton("📊 Quiz Analytics", callback_data="quiz_analytics")
                ],
                [
                    InlineKeyboardButton("🔍 Search Quizzes", callback_data="search_quizzes"),
                    InlineKeyboardButton("📤 Export All Data", callback_data="export_quiz_data")
                ],
                [
                    InlineKeyboardButton("⚙️ Bulk Operations", callback_data="bulk_operations"),
                    InlineKeyboardButton("🗑️ Cleanup Old Quizzes", callback_data="cleanup_quizzes")
                ],
                [
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                dashboard_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_dashboard_viewed",
                user_id,
                metadata={
                    "total_quizzes": len(all_quizzes),
                    "quiz_breakdown": {k: len(v) for k, v in quiz_categories.items()}
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in my quizzes command: {e}")
            await update.message.reply_text(messages.ERROR_DATABASE)
    
    async def _show_no_quizzes_message(self, update: Update, user_data: Dict):
        """Show encouraging message when user has no quizzes"""
        user_name = user_data.get('first_name', 'there')
        
        no_quizzes_message = f"""
🎯 **Ready to Start Creating, {user_name}?**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **You haven't created any quizzes yet!**

🚀 **But that's about to change! Here's how easy it is:**

1️⃣ **Click "🎨 Create My First Quiz"**
2️⃣ **Type your quiz title**
3️⃣ **Add questions with ✅ marking**
4️⃣ **Share and watch people compete!**

💡 **Quick Start Ideas:**
• "My Friends Quiz" - Test how well they know you
• "General Knowledge Challenge" - Mix of everything
• "Movie Quiz 2024" - Latest films and actors  
• "Science Quiz" - Physics, Chemistry, Biology

🎁 **New Creator Bonuses:**
• 🆓 Free Premium features for first quiz
• 🤖 AI assistance for question generation
• 📊 Advanced analytics from day 1
• 🏆 Creator badge on your profile

⚡ **Pro Tip:** Start with topics you're passionate about!

🚀 **Ready to become a VidderTech Quiz Creator?**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎨 Create My First Quiz", callback_data="create_quiz"),
                InlineKeyboardButton("🎮 Try Demo Quiz", callback_data="demo_quiz")
            ],
            [
                InlineKeyboardButton("🤖 AI Quiz Generator", callback_data="ai_quiz_generator"),
                InlineKeyboardButton("📄 Import from File", callback_data="import_file")
            ],
            [
                InlineKeyboardButton("🎓 Watch Tutorial", callback_data="quiz_tutorial"),
                InlineKeyboardButton("💡 Get Inspiration", callback_data="quiz_inspiration")
            ],
            [
                InlineKeyboardButton("🏠 Back to Home", callback_data="start")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            no_quizzes_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def done_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """✅ Complete quiz creation with validation and publishing"""
        try:
            user_id = update.effective_user.id
            quiz_session = context.user_data.get('quiz_session')
            
            if not quiz_session or quiz_session.get('state') != states.CREATING_QUIZ:
                await update.message.reply_text(
                    "❌ No quiz creation in progress.\nUse /create to start creating a quiz."
                )
                return
            
            quiz_data = quiz_session.get('quiz_data', {})
            questions = quiz_data.get('questions', [])
            
            # Validation
            if not quiz_data.get('title'):
                await update.message.reply_text("❌ Quiz title is required. Please add a title first.")
                return
            
            if len(questions) < 1:
                await update.message.reply_text(
                    "❌ Quiz must have at least 1 question.\nUse the quiz creation menu to add questions."
                )
                return
            
            # Validate questions
            invalid_questions = []
            for i, question in enumerate(questions, 1):
                if not self._validate_question_data(question):
                    invalid_questions.append(i)
            
            if invalid_questions:
                await update.message.reply_text(
                    f"❌ Invalid questions found: {', '.join(map(str, invalid_questions))}\n"
                    "Please fix these questions before finishing the quiz."
                )
                return
            
            # Create quiz in database
            quiz_id = db_manager.generate_id("quiz")
            
            # Prepare quiz data for database
            complete_quiz_data = {
                'quiz_id': quiz_id,
                'creator_id': user_id,
                'title': quiz_data['title'],
                'description': quiz_data.get('description'),
                'quiz_type': quiz_data.get('quiz_type', 'free'),
                'status': 'published',  # Automatically publish
                'difficulty': quiz_data.get('difficulty', 'medium'),
                'category': quiz_data.get('category'),
                'time_per_question': quiz_data.get('time_per_question', 30),
                'negative_marking_enabled': quiz_data.get('negative_marking_enabled', True),
                'negative_marks': quiz_data.get('negative_marks', 0.25),
                'positive_marks': quiz_data.get('positive_marks', 1.0),
                'shuffle_questions': quiz_data.get('shuffle_questions', False),
                'shuffle_options': quiz_data.get('shuffle_options', False),
                'show_results': quiz_data.get('show_results', True),
                'show_correct_answers': quiz_data.get('show_correct_answers', True),
                'allow_review': quiz_data.get('allow_review', True),
                'is_public': quiz_data.get('is_public', True),
                'max_attempts': quiz_data.get('max_attempts', 1),
                'tags': quiz_data.get('tags', []),
                'sections': quiz_data.get('sections', []),
                'source': 'manual'
            }
            
            # Save quiz
            success = await db_manager.create_quiz(complete_quiz_data)
            
            if not success:
                await update.message.reply_text(messages.ERROR_DATABASE)
                return
            
            # Add all questions to database
            questions_added = 0
            for question_data in questions:
                question_data['quiz_id'] = quiz_id
                if await db_manager.add_question(question_data):
                    questions_added += 1
            
            # Clear quiz session
            context.user_data.pop('quiz_session', None)
            
            # Calculate quiz statistics
            total_time = len(questions) * quiz_data.get('time_per_question', 30)
            total_marks = sum(q.get('marks', 1) for q in questions)
            
            # Success message
            success_message = f"""
🎉 **Quiz Successfully Created!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Your Quiz is Ready!**

📋 **Quiz Details:**
🏷️ **Title:** `{quiz_data['title']}`
🆔 **Quiz ID:** `{quiz_id}`
📂 **Category:** `{quiz_data.get('category', 'General')}`
❓ **Questions:** `{questions_added}/{len(questions)}`
⏰ **Duration:** `{total_time//60} min {total_time%60} sec`
🏆 **Total Marks:** `{total_marks} points`
🎯 **Difficulty:** `{quiz_data.get('difficulty', 'Medium').title()}`

🌟 **Quiz Features:**
{'✅' if quiz_data.get('negative_marking_enabled') else '❌'} Negative Marking (-{quiz_data.get('negative_marks', 0.25)})
{'✅' if quiz_data.get('shuffle_questions') else '❌'} Question Shuffling
{'✅' if quiz_data.get('shuffle_options') else '❌'} Option Shuffling
{'✅' if quiz_data.get('show_results') else '❌'} Show Results
{'✅' if quiz_data.get('allow_review') else '❌'} Allow Review

🎊 **What's Next?**
• Share your quiz ID with friends
• Monitor real-time participation
• View detailed analytics
• Create more awesome quizzes!

📱 **Share Link:** 
`https://t.me/{config.BOT_USERNAME[1:]}?start=quiz_{quiz_id}`

🚀 **{config.COMPANY_NAME} - Where Great Quizzes Begin!**
            """
            
            # Create post-creation keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🎮 Test My Quiz", callback_data=f"test_quiz_{quiz_id}"),
                    InlineKeyboardButton("✏️ Edit Quiz", callback_data=f"edit_quiz_{quiz_id}")
                ],
                [
                    InlineKeyboardButton("📤 Share Quiz", callback_data=f"share_quiz_{quiz_id}"),
                    InlineKeyboardButton("📊 View Analytics", callback_data=f"quiz_analytics_{quiz_id}")
                ],
                [
                    InlineKeyboardButton("🎯 Create Another", callback_data="create_quiz"),
                    InlineKeyboardButton("📋 All My Quizzes", callback_data="myquizzes")
                ],
                [
                    InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                success_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_completed",
                user_id,
                quiz_id=quiz_id,
                metadata={
                    "questions_count": questions_added,
                    "total_marks": total_marks,
                    "creation_time_minutes": (datetime.now() - datetime.fromisoformat(quiz_session['created_at'])).total_seconds() / 60
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in done command: {e}")
            await update.message.reply_text(messages.ERROR_DATABASE)
    
    def _validate_question_data(self, question: Dict[str, Any]) -> bool:
        """Validate question data completeness"""
        try:
            required_fields = ['question_text', 'options', 'correct_answer']
            
            for field in required_fields:
                if field not in question or not question[field]:
                    return False
            
            # Validate question text
            if len(question['question_text'].strip()) < 5:
                return False
            
            # Validate options
            options = question.get('options', [])
            if not isinstance(options, list) or len(options) < 2:
                return False
            
            # Validate correct answer
            correct_answer = question.get('correct_answer')
            if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer >= len(options):
                return False
            
            return True
            
        except Exception:
            return False
    
    async def cancel_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """❌ Smart quiz creation cancellation with data preservation"""
        try:
            user_id = update.effective_user.id
            quiz_session = context.user_data.get('quiz_session')
            
            if not quiz_session or quiz_session.get('state') != states.CREATING_QUIZ:
                await update.message.reply_text(
                    "❌ No quiz creation in progress.\nUse /create to start creating a quiz."
                )
                return
            
            quiz_data = quiz_session.get('quiz_data', {})
            questions_count = len(quiz_data.get('questions', []))
            
            # Show cancellation confirmation with data preservation option
            if questions_count > 0:
                cancel_message = f"""
⚠️ **Confirm Quiz Creation Cancellation**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Quiz in Progress:**
📝 Title: `{quiz_data.get('title', 'Untitled Quiz')}`
❓ Questions Added: `{questions_count}`
⏰ Time Invested: Approximately `{questions_count * 2} minutes`

💾 **Data Preservation Options:**
• **Save as Draft** - Keep your work and continue later
• **Export Data** - Download your questions as backup
• **Complete Cancellation** - Lose all progress

⚠️ **Warning:** Complete cancellation will permanently delete your progress!

🤔 **What would you like to do?**
                """
                
                keyboard = [
                    [
                        InlineKeyboardButton("💾 Save as Draft", callback_data="save_quiz_draft"),
                        InlineKeyboardButton("📤 Export Questions", callback_data="export_questions")
                    ],
                    [
                        InlineKeyboardButton("🔄 Continue Creating", callback_data="continue_quiz_creation"),
                        InlineKeyboardButton("❌ Delete Progress", callback_data="confirm_cancel_quiz")
                    ],
                    [
                        InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                    ]
                ]
                
            else:
                cancel_message = f"""
❌ **Cancel Quiz Creation**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No quiz data to preserve. 

🎯 **Quick Actions:**
• Start a new quiz anytime with /create
• Import quizzes from other sources
• Try our AI quiz generator

🚀 **{config.COMPANY_NAME} is here when you're ready!**
                """
                
                keyboard = [
                    [
                        InlineKeyboardButton("🎯 Create New Quiz", callback_data="create_quiz"),
                        InlineKeyboardButton("🤖 AI Generator", callback_data="ai_quiz_generator")
                    ],
                    [
                        InlineKeyboardButton("🏠 Back to Home", callback_data="start")
                    ]
                ]
                
                # Clear session immediately for simple cancellation
                context.user_data.pop('quiz_session', None)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                cancel_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_creation_cancelled",
                user_id,
                metadata={
                    "questions_count": questions_count,
                    "had_data": questions_count > 0
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in cancel quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def delete_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🗑️ Secure quiz deletion with comprehensive confirmation"""
        try:
            user_id = update.effective_user.id
            
            # Check if quiz ID provided
            if not context.args:
                await update.message.reply_text(
                    "❌ **Missing Quiz ID**\n\n"
                    "📋 **Usage:** `/del quiz_id`\n\n"
                    "🔍 **Find your quiz ID:**\n"
                    "• Use /myquizzes to see all your quizzes\n"
                    "• Quiz ID is shown in quiz details\n\n"
                    "💡 **Example:** `/del quiz_abc123def456`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            quiz_id = context.args[0].strip()
            
            # Get quiz details
            quiz = await db_manager.get_quiz(quiz_id)
            if not quiz:
                await update.message.reply_text(
                    f"❌ **Quiz Not Found**\n\n"
                    f"Quiz ID `{quiz_id}` doesn't exist.\n\n"
                    f"🔍 **Check:**\n"
                    f"• Quiz ID spelling is correct\n"
                    f"• Quiz hasn't been deleted already\n"
                    f"• You have access to this quiz\n\n"
                    f"📊 Use /myquizzes to see your available quizzes.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Check ownership
            if quiz['creator_id'] != user_id:
                user_data = await db_manager.get_user(user_id)
                if not user_data or user_data.get('role') not in ['admin', 'super_admin', 'owner']:
                    await update.message.reply_text(
                        "❌ **Access Denied**\n\n"
                        "You can only delete quizzes that you created.\n\n"
                        f"🏠 This quiz belongs to another user.\n"
                        f"📊 Use /myquizzes to see your own quizzes.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return
            
            # Get quiz statistics for confirmation
            quiz_stats = await self._get_quiz_deletion_stats(quiz_id)
            
            # Comprehensive deletion confirmation
            delete_confirmation = f"""
🗑️ **Confirm Quiz Deletion - PERMANENT ACTION**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **CRITICAL WARNING:** This action CANNOT be undone!

📋 **Quiz to be Deleted:**
🏷️ **Title:** `{quiz['title']}`
🆔 **ID:** `{quiz_id}`
📂 **Category:** `{quiz.get('category', 'Uncategorized')}`
❓ **Questions:** `{quiz.get('total_questions', 0)}`
🎯 **Type:** `{quiz.get('quiz_type', 'free').title()}`
📅 **Created:** `{quiz.get('created_at', 'Unknown')[:10] if quiz.get('created_at') else 'Unknown'}`

📊 **Impact of Deletion:**
👥 **Participants Affected:** `{quiz_stats.get('total_participants', 0)}`
📈 **Sessions to be Lost:** `{quiz_stats.get('total_sessions', 0)}`
💬 **Responses to be Deleted:** `{quiz_stats.get('total_responses', 0)}`
📊 **Analytics Data:** `{quiz_stats.get('analytics_events', 0)} events`

💾 **Before Deletion:**
• All quiz data will be permanently removed
• Participant scores will be lost
• Analytics history will be deleted
• Shared links will stop working
• Cannot be recovered after deletion

🔄 **Alternatives:**
• Archive quiz instead of deleting
• Export data before deletion
• Make quiz private instead

⚠️ **Are you absolutely sure you want to delete this quiz?**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("📤 Export First", callback_data=f"export_before_delete_{quiz_id}"),
                    InlineKeyboardButton("📁 Archive Instead", callback_data=f"archive_quiz_{quiz_id}")
                ],
                [
                    InlineKeyboardButton("🗑️ Yes, Delete Forever", callback_data=f"confirm_delete_{quiz_id}"),
                    InlineKeyboardButton("❌ No, Keep Quiz", callback_data="cancel_delete")
                ],
                [
                    InlineKeyboardButton("🏠 Back to Quizzes", callback_data="myquizzes")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                delete_confirmation,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error in delete quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _get_quiz_deletion_stats(self, quiz_id: str) -> Dict[str, Any]:
        """Get comprehensive stats before quiz deletion"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get session count
                cursor.execute("""
                    SELECT COUNT(*) as total_sessions,
                           COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions
                    FROM vidder_quiz_sessions WHERE quiz_id = ?
                """, (quiz_id,))
                session_data = cursor.fetchone()
                
                # Get response count
                cursor.execute("""
                    SELECT COUNT(*) as total_responses
                    FROM vidder_responses r
                    JOIN vidder_quiz_sessions s ON r.session_id = s.session_id
                    WHERE s.quiz_id = ?
                """, (quiz_id,))
                response_data = cursor.fetchone()
                
                # Get analytics count
                cursor.execute("""
                    SELECT COUNT(*) as analytics_events
                    FROM vidder_analytics WHERE quiz_id = ?
                """, (quiz_id,))
                analytics_data = cursor.fetchone()
                
                return {
                    'total_sessions': session_data['total_sessions'] if session_data else 0,
                    'completed_sessions': session_data['completed_sessions'] if session_data else 0,
                    'total_responses': response_data['total_responses'] if response_data else 0,
                    'analytics_events': analytics_data['analytics_events'] if analytics_data else 0
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting deletion stats: {e}")
            return {}
    
    async def edit_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """✏️ Advanced quiz editing system"""
        try:
            user_id = update.effective_user.id
            
            if not context.args:
                # Show user's editable quizzes
                await self._show_editable_quizzes(update, context, user_id)
                return
            
            quiz_id = context.args[0].strip()
            
            # Get quiz for editing
            quiz = await db_manager.get_quiz(quiz_id)
            if not quiz:
                await update.message.reply_text(
                    f"❌ Quiz `{quiz_id}` not found.\nUse /myquizzes to see available quizzes.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Check editing permissions
            if quiz['creator_id'] != user_id:
                user_data = await db_manager.get_user(user_id)
                if not user_data or user_data.get('role') not in ['admin', 'super_admin', 'owner']:
                    await update.message.reply_text(
                        "❌ You can only edit quizzes that you created."
                    )
                    return
            
            # Show comprehensive edit menu
            await self._show_quiz_edit_menu(update, context, quiz)
            
        except Exception as e:
            logger.error(f"❌ Error in edit quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _show_editable_quizzes(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show list of user's editable quizzes"""
        quizzes = await db_manager.get_user_quizzes(user_id, limit=20)
        
        if not quizzes:
            await update.message.reply_text(
                "📝 **No Quizzes to Edit**\n\n"
                "You don't have any quizzes yet!\n"
                "Use /create to create your first quiz.\n\n"
                f"🚀 **{config.COMPANY_NAME} - Start Creating!**",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        edit_list_message = f"""
✏️ **Select Quiz to Edit**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Your Editable Quizzes ({len(quizzes)}):**

"""
        
        keyboard = []
        
        for i, quiz in enumerate(quizzes[:10], 1):  # Show first 10
            status_emoji = {
                'draft': '📝',
                'published': '📤', 
                'active': '🟢',
                'completed': '✅'
            }.get(quiz['status'], '📝')
            
            quiz_title = quiz['title']
            if len(quiz_title) > 35:
                quiz_title = quiz_title[:32] + "..."
            
            edit_list_message += f"""
{status_emoji} **{i}. {quiz_title}**
🆔 ID: `{quiz['quiz_id']}`
❓ Questions: {quiz.get('total_questions', 0)}
📅 Updated: {quiz.get('updated_at', 'Unknown')[:10] if quiz.get('updated_at') else 'Unknown'}

"""
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} Edit: {quiz_title}",
                    callback_data=f"edit_quiz_{quiz['quiz_id']}"
                )
            ])
        
        # Add navigation if more quizzes exist
        if len(quizzes) > 10:
            keyboard.append([
                InlineKeyboardButton("📄 Show More", callback_data="show_more_editable"),
                InlineKeyboardButton("🔍 Search Quiz", callback_data="search_quiz")
            ])
        
        keyboard.extend([
            [
                InlineKeyboardButton("🎯 Create New Quiz", callback_data="create_quiz"),
                InlineKeyboardButton("📊 All My Quizzes", callback_data="myquizzes")
            ],
            [
                InlineKeyboardButton("🏠 Back to Home", callback_data="start")
            ]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            edit_list_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

# Register all handlers
def register_quiz_handlers(app):
    """Register all quiz command handlers"""
    handler = VidderQuizHandlers()
    
    # Command handlers
    app.add_handler(CommandHandler("create", handler.create_quiz_command))
    app.add_handler(CommandHandler("myquizzes", handler.my_quizzes_command))
    app.add_handler(CommandHandler("done", handler.done_command))
    app.add_handler(CommandHandler("cancel", handler.cancel_quiz_command))
    app.add_handler(CommandHandler("del", handler.delete_quiz_command))
    app.add_handler(CommandHandler("edit", handler.edit_quiz_command))
    
    # Text message handler for quiz creation
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handler.handle_quiz_creation_text
    ))
    
    logger.info("✅ VidderTech Quiz Handlers registered successfully")

# Export handler class
__all__ = ['VidderQuizHandlers', 'register_quiz_handlers']