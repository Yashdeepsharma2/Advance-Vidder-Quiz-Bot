# Powered by Viddertech
import logging
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop
from viddertech_quiz_bot.persistence import save_user_data

logger = logging.getLogger(__name__)

async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A handler that runs for every update to track users and check for bans."""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    # Check if user is banned
    if user_id in context.bot_data.get('banned_users', []):
        logger.info(f"Banned user {user_id} tried to interact with the bot.")
        raise ApplicationHandlerStop # Stop processing further handlers for this user

    # Track new users
    if 'users' not in context.bot_data:
        context.bot_data['users'] = []

    if user_id not in context.bot_data['users']:
        context.bot_data['users'].append(user_id)
        # This needs a new persistence function.
        # For now, let's assume it's saved with general user_data
        if 'user_data' not in context.bot_data:
            context.bot_data['user_data'] = {}
        context.bot_data['user_data']['all_users'] = context.bot_data['users']
        context.bot_data['user_data']['banned_users'] = context.bot_data.get('banned_users', [])
        save_user_data(context.bot_data['user_data'])
        logger.info(f"New user tracked: {user_id}")