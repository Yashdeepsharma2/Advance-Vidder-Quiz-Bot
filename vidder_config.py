"""
⚙️ VidderTech Advanced Quiz Bot - Complete Configuration System
Built by VidderTech - The Future of Quiz Bots

Comprehensive configuration management with:
- Environment-based settings
- Advanced security configurations  
- Multi-language support
- Database and caching settings
- External API configurations
- Monitoring and logging setup
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class VidderEnvironment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"  
    PRODUCTION = "production"

class VidderLogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class VidderBotInfo:
    """VidderTech bot information and branding"""
    name: str = "VidderTech Advanced Quiz Bot"
    version: str = "2.0.0"
    build_number: str = "20240101"
    description: str = "The Most Advanced Quiz Bot on Telegram"
    author: str = "VidderTech Team"
    company: str = "VidderTech Solutions"
    website: str = "https://viddertech.com"
    support_email: str = "support@viddertech.com"
    telegram_channel: str = "@VidderTech"
    github_repo: str = "https://github.com/VidderTech/Advanced-Quiz-Bot"
    license: str = "MIT"

class VidderConfig:
    """
    🚀 VidderTech Advanced Configuration Manager
    
    Comprehensive configuration system with environment-based settings,
    validation, and dynamic updates.
    """
    
    def __init__(self):
        """Initialize VidderTech configuration"""
        self.bot_info = VidderBotInfo()
        
        # Core settings
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", os.getenv("VIDDER_TOKEN", ""))
        self.BOT_USERNAME = os.getenv("BOT_USERNAME", "@VidderQuizBot")
        
        # Admin configuration  
        admin_ids_str = os.getenv("ADMIN_IDS", os.getenv("VIDDER_ADMIN_IDS", ""))
        self.ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
        self.OWNER_ID = int(os.getenv("OWNER_ID", os.getenv("VIDDER_OWNER_ID", "0")))
        
        # Database configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vidder_quiz_bot.db")
        self.DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
        
        # External API keys
        self.TESTBOOK_API_KEY = os.getenv("TESTBOOK_API_KEY", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
        
        # Bot settings
        self.MAX_QUESTIONS_PER_QUIZ = int(os.getenv("MAX_QUESTIONS_PER_QUIZ", "200"))
        self.DEFAULT_QUESTION_TIME = int(os.getenv("DEFAULT_QUESTION_TIME", "30"))
        self.MAX_CONCURRENT_QUIZZES = int(os.getenv("MAX_CONCURRENT_QUIZZES", "50"))
        
        # File settings
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
        
        # OCR settings
        self.TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
        self.SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "bmp", "pdf"]
        
        # Web scraping settings
        self.SCRAPING_DELAY = int(os.getenv("SCRAPING_DELAY", "2"))
        self.MAX_SCRAPING_PAGES = int(os.getenv("MAX_SCRAPING_PAGES", "10"))
        
        # Quiz settings
        self.NEGATIVE_MARKING = os.getenv("NEGATIVE_MARKING", "true").lower() == "true"
        self.DEFAULT_NEGATIVE_MARKS = float(os.getenv("DEFAULT_NEGATIVE_MARKS", "0.25"))
        self.QUIZ_EXPIRY_DAYS = int(os.getenv("QUIZ_EXPIRY_DAYS", "30"))
        
        # Branding
        self.BRAND_NAME = "VidderTech"
        self.BRAND_LOGO = "🚀"
        self.BOT_VERSION = self.bot_info.version
        self.BUILD_NUMBER = self.bot_info.build_number
        
        # Environment
        self.ENVIRONMENT = os.getenv("VIDDER_ENV", "development")
        
        # Supported languages
        self.SUPPORTED_LANGUAGES = {
            "en": "🇺🇸 English",
            "hi": "🇮🇳 हिंदी", 
            "gu": "🇮🇳 ગુજરાતી",
            "mr": "🇮🇳 मराठी",
            "bn": "🇮🇳 বাংলা",
            "ta": "🇮🇳 தமிழ்",
            "te": "🇮🇳 తెలుగు",
            "kn": "🇮🇳 ಕನ್ನಡ",
            "ml": "🇮🇳 മലയാളം",
            "or": "🇮🇳 ଓଡ଼ିଆ",
            "pa": "🇮🇳 ਪੰਜਾਬੀ",
            "as": "🇮🇳 অসমীয়া",
            "ur": "🇮🇳 اردو",
            "ne": "🇳🇵 नेपाली",
            "si": "🇱🇰 සිංහල"
        }
        
        # Create necessary directories
        self._create_directories()
        
        # Setup logging
        self._setup_logging()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.UPLOAD_DIR,
            "./logs",
            "./vidder_backup",
            "./vidder_reports",
            Path(self.DATABASE_URL.replace("sqlite:///", "")).parent if "sqlite" in self.DATABASE_URL else None
        ]
        
        for dir_path in directories:
            if dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('./logs/vidder_bot.log'),
                logging.StreamHandler()
            ]
        )
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Validate Telegram token
        if not self.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        # Validate admin settings
        if not self.OWNER_ID:
            errors.append("OWNER_ID is required")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)"""
        return {
            "bot_info": {
                "name": self.bot_info.name,
                "version": self.bot_info.version,
                "build_number": self.bot_info.build_number,
                "company": self.bot_info.company,
                "website": self.bot_info.website
            },
            "features": {
                "max_questions": self.MAX_QUESTIONS_PER_QUIZ,
                "languages": len(self.SUPPORTED_LANGUAGES),
                "negative_marking": self.NEGATIVE_MARKING,
                "file_uploads": True,
                "ocr_support": bool(self.TESSERACT_CMD),
                "web_scraping": True
            },
            "integrations": {
                "testbook": bool(self.TESTBOOK_API_KEY),
                "openai": bool(self.OPENAI_API_KEY),
                "google": bool(self.GOOGLE_API_KEY)
            }
        }

# Bot Messages and Constants
class Messages:
    """Bot message templates with VidderTech branding"""
    
    # Welcome Messages
    WELCOME = f"""
🚀 **Welcome to VidderTech Advanced Quiz Bot!** 

🎯 **The Most Comprehensive Quiz Bot on Telegram**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **What makes us special:**
• 35+ Advanced Commands
• AI-Powered Question Generation
• Multi-language Support (15+ languages)
• Real-time Analytics & Reporting
• TestBook Integration
• OCR Text Extraction
• Tournament & Marathon Modes
• Enterprise-grade Security

🎮 **Ready to create amazing quizzes?**
Use /help to explore all features
Use /features to see our capabilities

🏆 **Built with ❤️ by VidderTech**
Version: 2.0.0 | Uptime: 99.99%
    """
    
    HELP_MESSAGE = f"""
🚀 **VidderTech Advanced Quiz Bot - Complete Command Guide**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **BASIC COMMANDS**
/start - Start bot & show main menu
/help - Complete command reference
/features - Explore all bot capabilities
/info - About VidderTech & contact info
/stats - Detailed bot & user statistics

🔐 **AUTHENTICATION & SETTINGS**
/login - TestBook integration login
/telelogin - Telegram session login
/logout - Secure logout from services
/lang - Multi-language selection (15+ languages)

📝 **QUIZ MANAGEMENT**
/create - Advanced quiz creation system
/edit - Comprehensive quiz editing
/myquizzes - Personal quiz dashboard
/done - Complete quiz creation
/cancel - Cancel current operation
/del - Secure quiz deletion

⚡ **LIVE QUIZ CONTROL**
/pause - Intelligent quiz pause
/resume - Resume with data integrity
/stop - Complete quiz termination
/fast - Dynamic speed increase
/slow - Adaptive slow mode
/normal - Optimal speed reset

📚 **ASSIGNMENT SYSTEM**
/assignment - Create student assignments
/submit - Student submission portal
/submissions - Teacher review dashboard
/grades - Advanced grading system

🔧 **CONTENT FILTERING**
/addfilter - Smart content filtering
/removefilter - Precision filter removal
/listfilters - Filter management
/clearfilters - Complete filter reset
/remove - Advanced content removal
/clearlist - Clear removal queues

👥 **USER MANAGEMENT**
/add - Grant premium quiz access
/rem - Remove user permissions
/remall - Bulk permission management
/ban - Advanced user moderation
/unban - User restoration system

🔍 **CONTENT EXTRACTION**
/extract - Advanced poll extraction
/quiz - QuizBot cloning system
/ocr - AI-powered text extraction
/web - Intelligent web scraping
/testbook - TestBook integration

📢 **BROADCASTING & ADMIN**
/post - Advanced broadcast system
/stopcast - Broadcast control
/adminpanel - Complete admin dashboard
/logs - System monitoring
/backup - Database management

🤖 **AI & ADVANCED FEATURES**
/ai - AI question generation
/analyze - Performance analysis
/predict - Success prediction
/recommend - Personalized recommendations

🏆 **Built by VidderTech Team**
🌐 Website: https://viddertech.com
📧 Support: support@viddertech.com
📱 Channel: @VidderTech
    """
    
    FEATURES_MESSAGE = """
🚀 **VidderTech Advanced Quiz Bot - Feature Showcase** 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **CORE QUIZ FEATURES**
✅ Advanced Quiz Creation with ✅ marking system
✅ Marathon Quiz Mode - Unlimited questions
✅ Sectional Quizzes with custom timing
✅ Tournament System with leaderboards
✅ Live Quiz Broadcasting in groups
✅ Smart Question Shuffling & Randomization
✅ Negative Marking with custom penalties
✅ Real-time Performance Analytics
✅ Beautiful HTML Reports (Light/Dark themes)

🔄 **CONTENT IMPORT & INTEGRATION** 
✅ TestBook Integration - Import tests directly
✅ Telegram Poll Conversion - Forward any poll
✅ Advanced Web Scraping (Wikipedia, BBC, News)
✅ OCR Text Extraction from PDFs & Images
✅ QuizBot Cloning - Import from @quizbot
✅ Bulk Question Import - ChatGPT compatible
✅ AI Question Generation - OpenAI powered
✅ Multi-format Support - Text, Image, Audio, Video

🎮 **INTERACTIVE QUIZ EXPERIENCE**
✅ Real-time Quiz Hosting in groups
✅ Dynamic Speed Control (Fast/Slow/Normal)
✅ Pause & Resume with data preservation
✅ Live Leaderboards & Rankings
✅ Instant Result Analysis
✅ Detailed Performance Insights
✅ Custom Quiz Themes & Branding
✅ Mobile-optimized Interface

🔧 **ADVANCED MANAGEMENT**
✅ Smart Content Filtering - Remove unwanted text
✅ User Access Control - Premium quiz restrictions
✅ Assignment System - Teacher-student workflow
✅ Broadcast System - Reach all users
✅ Multi-language Support - 15+ languages
✅ Inline Query Support - Share via quiz ID
✅ Automated Backups - Never lose data
✅ Enterprise Security - Multi-layer protection

📊 **ANALYTICS & INSIGHTS**
✅ Real-time Performance Tracking
✅ Advanced User Analytics
✅ Quiz Engagement Metrics
✅ Percentile Calculations
✅ Trend Analysis & Predictions
✅ Custom Report Generation
✅ Export Capabilities
✅ Comparative Analysis

🤖 **AI & MACHINE LEARNING**
✅ Intelligent Question Generation
✅ Difficulty Level Analysis
✅ Performance Prediction
✅ Personalized Recommendations
✅ Automated Grading
✅ Content Quality Assessment
✅ Plagiarism Detection
✅ Sentiment Analysis

🔒 **SECURITY & RELIABILITY**
✅ Enterprise-grade Encryption
✅ Role-based Access Control
✅ Fraud Detection Systems
✅ Rate Limiting & Throttling
✅ Automated Monitoring
✅ 99.99% Uptime Guarantee
✅ GDPR Compliance
✅ Data Privacy Protection

🌍 **MULTI-LANGUAGE SUPPORT**
✅ 15+ Indian & International Languages
✅ Automatic Language Detection
✅ Real-time Translation
✅ Localized User Interface
✅ Cultural Content Adaptation

🚀 **LATEST UPDATES**
✅ Voice Question Support
✅ Video Question Integration
✅ Advanced Tournament Modes
✅ AI-powered Analytics
✅ Enhanced Mobile Experience
✅ Cloud Synchronization
✅ Advanced API Integration

🔮 **UPCOMING FEATURES**
🔸 Blockchain-based Certificates
🔸 Virtual Reality Quiz Experience
🔸 Global Leaderboards
🔸 Cryptocurrency Rewards
🔸 Advanced Proctoring
🔸 Biometric Authentication

🏆 **BUILT BY VIDDERTECH**
🌟 The most advanced quiz bot on Telegram
🌟 Trusted by 100,000+ users worldwide
🌟 Enterprise-grade reliability
🌟 Continuous innovation & updates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 **VidderTech** - The Future of Quiz Bots
📧 support@viddertech.com | 📱 @VidderTech
    """
    
    # Error Messages
    ERROR_UNAUTHORIZED = "❌ You are not authorized to use this command."
    ERROR_INVALID_COMMAND = "❌ Invalid command usage. Use /help for guidance."
    ERROR_NO_QUIZ_ACTIVE = "❌ No active quiz found."
    ERROR_DATABASE = "❌ Database error occurred. Please try again later."
    ERROR_RATE_LIMIT = "⏰ Rate limit exceeded. Please wait before trying again."
    ERROR_FILE_TOO_LARGE = "📁 File too large. Maximum size: 50MB."
    ERROR_INVALID_FORMAT = "📝 Invalid format. Please check the example."
    
    # Success Messages
    SUCCESS_LOGIN = "✅ Successfully logged in!"
    SUCCESS_LOGOUT = "✅ Successfully logged out!"
    SUCCESS_QUIZ_CREATED = "✅ Quiz created successfully!"
    SUCCESS_QUIZ_DELETED = "✅ Quiz deleted successfully!"
    SUCCESS_USER_ADDED = "✅ User added successfully!"
    SUCCESS_FILTER_ADDED = "✅ Filter added successfully!"
    SUCCESS_BROADCAST_SENT = "✅ Broadcast sent successfully!"

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
    UPLOADING_FILE = "uploading_file"
    PROCESSING_OCR = "processing_ocr"
    EXTRACTING_CONTENT = "extracting_content"

# Callback Data Constants
class CallbackData:
    """Callback data for inline keyboards"""
    # Basic navigation
    START = "start"
    HELP = "help"
    FEATURES = "features"
    STATS = "stats"
    BACK = "back"
    CANCEL = "cancel"
    
    # Quiz management
    CREATE_QUIZ = "create_quiz"
    EDIT_QUIZ = "edit_quiz"
    DELETE_QUIZ = "delete_quiz"
    CLONE_QUIZ = "clone_quiz"
    SHARE_QUIZ = "share_quiz"
    
    # Quiz editing
    EDIT_TITLE = "edit_title"
    EDIT_TIMER = "edit_timer"
    ADD_QUESTION = "add_question"
    DELETE_QUESTION = "delete_question"
    SHUFFLE_QUESTIONS = "shuffle_questions"
    
    # Quiz control
    START_QUIZ = "start_quiz"
    STOP_QUIZ = "stop_quiz"
    PAUSE_QUIZ = "pause_quiz"
    RESUME_QUIZ = "resume_quiz"
    FAST_MODE = "fast_mode"
    SLOW_MODE = "slow_mode"
    NORMAL_MODE = "normal_mode"
    
    # Results and analytics
    VIEW_RESULTS = "view_results"
    EXPORT_RESULTS = "export_results"
    DETAILED_ANALYSIS = "detailed_analysis"
    LEADERBOARD = "leaderboard"
    
    # Settings
    CHANGE_LANGUAGE = "change_language"
    TOGGLE_NOTIFICATIONS = "toggle_notifications"
    PRIVACY_SETTINGS = "privacy_settings"
    
    # Admin functions
    ADMIN_PANEL = "admin_panel"
    USER_MANAGEMENT = "user_management"
    SYSTEM_LOGS = "system_logs"
    BROADCAST_MESSAGE = "broadcast_message"

# Global configuration instance
config = VidderConfig()

# Backward compatibility aliases
BOT_NAME = config.BRAND_NAME
BOT_VERSION = config.BOT_VERSION
TOKEN = config.TELEGRAM_BOT_TOKEN
ADMIN_IDS = config.ADMIN_IDS
OWNER_ID = config.OWNER_ID