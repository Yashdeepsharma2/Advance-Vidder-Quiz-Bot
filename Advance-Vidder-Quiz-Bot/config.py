# Powered by Viddertech

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Core Bot Settings ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables.")

# --- Admin & Ownership ---
# Get admin IDs, ensuring they are integers
raw_admin_ids = os.getenv("ADMIN_IDS", "").split(',')
ADMIN_IDS = [int(admin_id) for admin_id in raw_admin_ids if admin_id]

OWNER_ID = os.getenv("OWNER_ID")
if not OWNER_ID:
    raise ValueError("OWNER_ID is not set in the environment variables.")
OWNER_ID = int(OWNER_ID)

# --- Database Settings ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vidder_quiz_bot.db")

# --- Quiz Settings ---
DEFAULT_QUESTION_TIME = int(os.getenv("DEFAULT_QUESTION_TIME", 30))
MAX_QUESTIONS_PER_QUIZ = int(os.getenv("MAX_QUESTIONS_PER_QUIZ", 100))
QUIZZES_PER_PAGE = int(os.getenv("QUIZZES_PER_PAGE", 5)) # For pagination in /myquizzes

# --- API Keys for Integrations ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")

# --- Logging Configuration ---
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()

# --- Session Names ---
TELETHON_SESSION_NAME = "viddertech_user_session"
TELETHON_SESSION_PATH = os.path.join("data", TELETHON_SESSION_NAME) # data folder will be in the root

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")