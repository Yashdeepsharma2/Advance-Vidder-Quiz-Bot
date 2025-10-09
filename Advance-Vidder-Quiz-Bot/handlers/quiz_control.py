# Powered by Viddertech

import logging
from telegram import Update
from telegram.ext import ContextTypes

import config
from .quiz_commands import send_question, end_quiz_session # Import the quiz flow functions

logger = logging.getLogger(__name__)

def is_quiz_active(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if there is a quiz currently active in the chat."""
    return 'current_quiz' in context.chat_data and context.chat_data['current_quiz'].get('is_active')

def is_quiz_creator(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user is the creator of the current quiz."""
    if not is_quiz_active(context):
        return False
    # In a real bot, you'd also check for group admin privileges here.
    return user_id == context.chat_data['current_quiz'].get('creator_id')

async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops the current poll and sends the next question."""
    if not is_quiz_active(context) or not is_quiz_creator(update.effective_user.id, context):
        await update.message.reply_text("There is no active quiz or you are not the creator.")
        return

    quiz_session = context.chat_data['current_quiz']

    # Stop the current poll to show the results
    if 'current_poll_id' in context.chat_data:
        try:
            await context.bot.stop_poll(update.effective_chat.id, context.chat_data['current_poll_id'])
        except Exception as e:
            logger.warning(f"Could not stop poll (it might have auto-closed): {e}")

    # Advance to the next question
    quiz_session['current_question_index'] += 1
    await send_question(update.effective_chat.id, context)


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pauses the currently running quiz."""
    if not is_quiz_active(context) or not is_quiz_creator(update.effective_user.id, context):
        await update.message.reply_text("There is no active quiz to pause or you are not the creator.")
        return

    quiz_session = context.chat_data['current_quiz']
    if quiz_session.get('is_paused', False):
        await update.message.reply_text("The quiz is already paused.")
        return

    quiz_session['is_paused'] = True
    await update.message.reply_text("⏸️ Quiz paused. Use /resume to continue.")

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resumes a paused quiz."""
    if not is_quiz_active(context) or not is_quiz_creator(update.effective_user.id, context):
        await update.message.reply_text("There is no active quiz to resume or you are not the creator.")
        return

    quiz_session = context.chat_data['current_quiz']
    if not quiz_session.get('is_paused', False):
        await update.message.reply_text("The quiz is not currently paused.")
        return

    quiz_session['is_paused'] = False
    await update.message.reply_text("▶️ Quiz resumed!")
    await send_question(update.effective_chat.id, context)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops the ongoing quiz completely and shows the final leaderboard."""
    if not is_quiz_active(context) or not is_quiz_creator(update.effective_user.id, context):
        await update.message.reply_text("There is no active quiz to stop or you are not the creator.")
        return

    await end_quiz_session(update.effective_chat.id, context)

async def _set_quiz_speed(update: Update, context: ContextTypes.DEFAULT_TYPE, speed: str, speed_value: int) -> None:
    """Helper function to set the speed of the quiz."""
    if not is_quiz_active(context) or not is_quiz_creator(update.effective_user.id, context):
        await update.message.reply_text("There is no active quiz to change the speed of or you are not the creator.")
        return

    context.chat_data['current_quiz']['open_period'] = speed_value
    await update.message.reply_text(f"⏱️ Quiz speed has been set to {speed} ({speed_value} seconds per question).")

async def fast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets quiz speed to fast (e.g., 15 seconds)."""
    await _set_quiz_speed(update, context, "fast", 15)

async def slow_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets quiz speed to slow (e.g., 60 seconds)."""
    await _set_quiz_speed(update, context, "slow", 60)

async def normal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resets quiz speed to the default."""
    await _set_quiz_speed(update, context, "normal", config.DEFAULT_QUESTION_TIME)