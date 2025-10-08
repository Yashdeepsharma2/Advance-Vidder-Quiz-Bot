# Powered by Viddertech
import logging
from telegram import Update
from telegram.ext import ContextTypes
from .quiz_handler import send_next_question

logger = logging.getLogger(__name__)

async def pause_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pauses the currently running quiz."""
    chat_id = update.effective_chat.id
    if 'current_quiz' not in context.chat_data or not context.chat_data['current_quiz'].get('is_active'):
        await update.message.reply_text("There is no active quiz to pause.")
        return

    quiz_session = context.chat_data['current_quiz']
    if quiz_session.get('is_paused', False):
        await update.message.reply_text("The quiz is already paused.")
        return

    quiz_session['is_paused'] = True
    await update.message.reply_text("Quiz paused. Use /resume to continue.")


async def resume_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resumes a paused quiz."""
    chat_id = update.effective_chat.id
    if 'current_quiz' not in context.chat_data or not context.chat_data['current_quiz'].get('is_active'):
        await update.message.reply_text("There is no active quiz to resume.")
        return

    quiz_session = context.chat_data['current_quiz']
    if not quiz_session.get('is_paused', False):
        await update.message.reply_text("The quiz is not currently paused.")
        return

    quiz_session['is_paused'] = False
    await update.message.reply_text("Quiz resumed!")
    await send_next_question(chat_id, context)

async def _set_quiz_speed(update: Update, context: ContextTypes.DEFAULT_TYPE, speed: str) -> None:
    """Helper function to set the speed of the quiz."""
    if 'current_quiz' not in context.chat_data or not context.chat_data['current_quiz'].get('is_active'):
        await update.message.reply_text("There is no active quiz to change the speed of.")
        return

    quiz_session = context.chat_data['current_quiz']

    speed_map = {
        "fast": 15,
        "normal": 30,
        "slow": 60,
    }

    quiz_session['open_period'] = speed_map.get(speed)
    await update.message.reply_text(f"Quiz speed has been set to {speed}.")

async def fast_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets quiz speed to fast."""
    await _set_quiz_speed(update, context, "fast")

async def slow_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets quiz speed to slow."""
    await _set_quiz_speed(update, context, "slow")

async def normal_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets quiz speed to normal."""
    await _set_quiz_speed(update, context, "normal")