import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

DATA_DIR = "quiz_bot/data"
QUIZZES_FILE = os.path.join(DATA_DIR, "quizzes.json")
USER_STATS_FILE = os.path.join(DATA_DIR, "user_stats.json")

def load_data() -> Dict[str, Any]:
    """Loads all data from JSON files into a dictionary."""
    os.makedirs(DATA_DIR, exist_ok=True)

    bot_data = {
        'quizzes': {},
        'user_stats': {}
    }

    try:
        if os.path.exists(QUIZZES_FILE):
            with open(QUIZZES_FILE, 'r') as f:
                # Convert string keys back to int
                bot_data['quizzes'] = {int(k): v for k, v in json.load(f).items()}
        if os.path.exists(USER_STATS_FILE):
            with open(USER_STATS_FILE, 'r') as f:
                bot_data['user_stats'] = {int(k): v for k, v in json.load(f).items()}
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading data: {e}")

    return bot_data

def save_quizzes(quizzes: Dict[int, Any]):
    """Saves the quizzes data to a JSON file."""
    try:
        with open(QUIZZES_FILE, 'w') as f:
            json.dump(quizzes, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving quizzes: {e}")

def save_user_stats(user_stats: Dict[int, Any]):
    """Saves the user stats data to a JSON file."""
    try:
        with open(USER_STATS_FILE, 'w') as f:
            json.dump(user_stats, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving user stats: {e}")