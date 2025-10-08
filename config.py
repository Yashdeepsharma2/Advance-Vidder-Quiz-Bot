"""
Configuration file for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import os
from typing import List, Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class BotConfig(BaseSettings):
    """Bot configuration settings"""
    
    # Bot Credentials
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "@VidderQuizBot")
    
    # Admin Configuration
    ADMIN_IDS: List[int] = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///vidder_quiz_bot.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # External API Keys
    TESTBOOK_API_KEY: Optional[str] = os.getenv("TESTBOOK_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Bot Settings
    MAX_QUESTIONS_PER_QUIZ: int = int(os.getenv("MAX_QUESTIONS_PER_QUIZ", "100"))
    DEFAULT_QUESTION_TIME: int = int(os.getenv("DEFAULT_QUESTION_TIME", "30"))
    MAX_CONCURRENT_QUIZZES: int = int(os.getenv("MAX_CONCURRENT_QUIZZES", "10"))
    
    # File Settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
    SUPPORTED_IMAGE_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif", "bmp", "pdf"]
    
    # Web Scraping Settings
    SCRAPING_DELAY: int = int(os.getenv("SCRAPING_DELAY", "2"))
    MAX_SCRAPING_PAGES: int = int(os.getenv("MAX_SCRAPING_PAGES", "10"))
    
    # Quiz Settings
    NEGATIVE_MARKING: bool = os.getenv("NEGATIVE_MARKING", "true").lower() == "true"
    DEFAULT_NEGATIVE_MARKS: float = float(os.getenv("DEFAULT_NEGATIVE_MARKS", "0.25"))
    QUIZ_EXPIRY_DAYS: int = int(os.getenv("QUIZ_EXPIRY_DAYS", "30"))
    
    # Branding
    BRAND_NAME: str = "VidderTech"
    BRAND_LOGO: str = "🚀"
    BOT_VERSION: str = "2.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize configuration
config = BotConfig()

# Bot Messages and Constants
class Messages:
    """Bot message templates with VidderTech branding"""
    
    # Welcome Messages
    WELCOME = f"""
🚀 **Welcome to {config.BRAND_NAME} Quiz Bot!** 

🎯 **The Most Advanced Quiz Bot on Telegram**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **Ready to create amazing quizzes?**
Use /help to see all available commands
Use /features to explore our powerful features

🏆 **Built with ❤️ by {config.BRAND_NAME}**
Version: {config.BOT_VERSION} | Uptime: 99.99%
    """
    
    HELP_MESSAGE = f"""
🚀 **{config.BRAND_NAME} Quiz Bot - Command Guide**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **BASIC COMMANDS**
/start - Check if bot is alive
/help - Get help to use bot
/features - Get features of bot
/info - Get info about creator
/stats - Get bot statistics

🔐 **AUTHENTICATION**
/login - Login with TestBook via app
/telelogin - Login to extract polls and make txt
/logout - Logout from server

📝 **QUIZ MANAGEMENT**
/create - Start creating quiz
/edit - Edit your quiz
/done - Finish creating quiz
/cancel - Stop creating quiz
/stopedit - Stop editing
/myquizzes - Get list of your quizzes
/del - Delete quiz with quiz id
/quiz - Clone quiz from official quizbot

⚡ **QUIZ CONTROL**
/pause - Pause quiz for short time
/resume - Resume quiz
/stop - Stop ongoing quiz
/fast - Fast quiz in group
/slow - Slow quiz in group
/normal - Reset to normal speed

🎯 **ASSIGNMENTS**
/assignment - Create assignment for students
/submit - Submit homework or assignment

🔧 **FILTERING & MANAGEMENT**
/addfilter - Add words to filter list
/removefilter - Remove words from filter list
/listfilters - Show all filter words
/clearfilters - Remove all filter words
/remove - Add words to delete set
/clearlist - Clear remove words list

👥 **USER MANAGEMENT**
/add - Add user for paid quizzes
/rem - Remove user for paid quizzes
/remall - Bulk remove all paid users
/ban - Ban creator (Admin only)

📢 **BROADCASTING**
/post - Broadcast message (Admin only)
/stopcast - Stop broadcast (Admin only)

🔍 **EXTRACTION & TOOLS**
/extract - Make txt from polls using post links
/lang - Select language of TestBook quizzes

🏆 **Built by {config.BRAND_NAME} | Version {config.BOT_VERSION}**
    """
    
    FEATURES_MESSAGE = """
🚀 **Features Showcase of Advance Quiz Bot!** 

🔹 Create questions from text just by providing a ✅ mark to the right options.
🔹 Marathon Quiz Mode: Create unlimited questions for a never-ending challenge.
🔹 Convert Polls to Quizzes: Simply forward polls (e.g., from @quizbot), and unnecessary elements like [1/100] will be auto-removed!
🔹 Smart Filtering: Remove unwanted words (e.g., usernames, links) from forwarded polls.
🔹 Skip, Pause & Resume ongoing quizzes anytime.
🔹 Bulk Question Support via ChatGPT output.
🔹 Negative Marking for accurate scoring.
🔹 Edit Existing Quizzes with ease like shuffle title editing timer adding removing questions and many more.
🔹 Quiz Analytics: View engagement, tracking how many users completed the quiz.
🔹 Inline Query Support: Share quizzes instantly via quiz ID.
🔹 Free & Paid Quizzes: Restrict access to selected users/groups—perfect for paid quiz series!
🔹 Assignment Management: Track student responses via bot submissions.
🔹 View Creator Info using the quiz ID.
🔹 Generate Beautiful HTML Reports with score counters, plus light/dark theme support.
🔹 Manage Paid Quizzes: Add/remove users & groups individually or in bulk.
🔹 Video Tutorials: Find detailed guides in the Help section.
🔹 Auto-Send Group Results: No need to copy-paste manually—send all results in one click!
🔹 Create Sectional Quiz: You can create different sections with different timing 🥳.
🔹 Slow/Fast: Slow or fast ongoing quiz.
🔹 OCR Update - Now extract text from PDFs or Photos
🔹 Comparison of Result with accuracy, percentile and percentage
🔹 Create Questions from TXT.
🔹 Advance Mechanism with 99.99% uptime.
🔹 Automated link and username removal from Poll's description and questions.
🔹 Auto txt quiz creation from Wikipedia Britannia bbc news and 20+ articles sites.

**Latest update 🆕**

🔹 Create Questions from Testbook App by test link.
🔹 Auto clone from official quizbot.
🔹 Create from polls/already finished quizzes in channels and all try /extract.
🔹 Create from Drishti IAS web Quiz try /quiztxt.

🚀 **Upcoming Features:**

🔸 Advance Engagement saving + later on perspective.
🔸 More optimizations for a smoother experience.
🔸 Surprising Updates...

📊 **Live Tracker & Analysis:**

✅ Topper Comparisons
✅ Detailed Quiz Performance Analytics

🏆 **Powered by VidderTech | The Future of Quiz Bots**
    """
    
    # Error Messages
    ERROR_UNAUTHORIZED = "❌ You are not authorized to use this command."
    ERROR_INVALID_COMMAND = "❌ Invalid command usage. Use /help for guidance."
    ERROR_NO_QUIZ_ACTIVE = "❌ No active quiz found."
    ERROR_DATABASE = "❌ Database error occurred. Please try again later."
    
    # Success Messages
    SUCCESS_LOGIN = "✅ Successfully logged in!"
    SUCCESS_LOGOUT = "✅ Successfully logged out!"
    SUCCESS_QUIZ_CREATED = "✅ Quiz created successfully!"
    SUCCESS_QUIZ_DELETED = "✅ Quiz deleted successfully!"

# Quiz States
class QuizStates:
    """Quiz creation and management states"""
    IDLE = "idle"
    CREATING_QUIZ = "creating_quiz"
    EDITING_QUIZ = "editing_quiz"
    ADDING_QUESTIONS = "adding_questions"
    SETTING_TIMER = "setting_timer"
    SETTING_TITLE = "setting_title"
    QUIZ_ACTIVE = "quiz_active"
    QUIZ_PAUSED = "quiz_paused"

# Callback Data Constants
class CallbackData:
    """Callback data for inline keyboards"""
    EDIT_TITLE = "edit_title"
    EDIT_TIMER = "edit_timer"
    ADD_QUESTION = "add_question"
    DELETE_QUESTION = "delete_question"
    START_QUIZ = "start_quiz"
    STOP_QUIZ = "stop_quiz"
    PAUSE_QUIZ = "pause_quiz"
    RESUME_QUIZ = "resume_quiz"
    VIEW_RESULTS = "view_results"
    EXPORT_RESULTS = "export_results"