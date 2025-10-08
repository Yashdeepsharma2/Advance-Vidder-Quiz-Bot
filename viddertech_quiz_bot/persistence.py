# Powered by Viddertech
# Powered by Viddertech
import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

DATA_DIR = "viddertech_quiz_bot/data"
QUIZZES_FILE = os.path.join(DATA_DIR, "quizzes.json")
USER_STATS_FILE = os.path.join(DATA_DIR, "user_stats.json")
USER_DATA_FILE = os.path.join(DATA_DIR, "user_data.json")
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.json")

def load_data() -> Dict[str, Any]:
    """Loads all data from JSON files into a dictionary."""
    os.makedirs(DATA_DIR, exist_ok=True)

    bot_data = {
        'quizzes': {},
        'user_stats': {},
        'user_data': {},
        'assignments': {}
    }

    def _load_json_file(file_path, keys_are_ints=True):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                if keys_are_ints:
                    return {int(k): v for k, v in data.items()}
                return data
        return {}

    try:
        bot_data['quizzes'] = _load_json_file(QUIZZES_FILE)
        bot_data['user_stats'] = _load_json_file(USER_STATS_FILE)
        bot_data['user_data'] = _load_json_file(USER_DATA_FILE)
        bot_data['assignments'] = _load_json_file(ASSIGNMENTS_FILE, keys_are_ints=False) # Assignment IDs are UUIDs (strings)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading data: {e}")

    return bot_data

def _save_json_file(file_path: str, data: Dict):
    """Generic function to save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving data to {file_path}: {e}")

def save_quizzes(quizzes: Dict):
    """Saves the quizzes data to a JSON file."""
    _save_json_file(QUIZZES_FILE, quizzes)

def save_user_stats(user_stats: Dict):
    """Saves the user stats data to a JSON file."""
    _save_json_file(USER_STATS_FILE, user_stats)

def save_user_data(user_data: Dict):
    """Saves the general user data (e.g., filters) to a JSON file."""
    _save_json_file(USER_DATA_FILE, user_data)

def save_assignments(assignments: Dict):
    """Saves the assignments data to a JSON file."""
    _save_json_file(ASSIGNMENTS_FILE, assignments)