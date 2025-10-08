# Powered by Viddertech
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from viddertech_quiz_bot.persistence import save_user_data, save_quizzes

logger = logging.getLogger(__name__)

# --- User Tracking & Admin Controls ---

def get_admin_ids(context: ContextTypes.DEFAULT_TYPE) -> list:
    """A simple way to manage admins. In a real bot, this would be more robust."""
    # For now, let's say the first user to ever use the bot is the owner/superadmin.
    if 'users' in context.bot_data and context.bot_data['users']:
        return [next(iter(context.bot_data['users']))]
    return []

def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user is an admin."""
    return update.effective_user.id in get_admin_ids(context)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bans a user from using the bot."""
    if not is_admin(update, context):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        user_to_ban_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid user ID to ban. Usage: /ban <user_id>")
        return

    if 'banned_users' not in context.bot_data:
        context.bot_data['banned_users'] = []

    if user_to_ban_id in context.bot_data['banned_users']:
        await update.message.reply_text("This user is already banned.")
        return

    context.bot_data['banned_users'].append(user_to_ban_id)
    # This would require a new persistence function, for now it's in memory
    # save_banned_users(context.bot_data['banned_users'])
    await update.message.reply_text(f"User {user_to_ban_id} has been banned.")

# --- Broadcast ---

async def post_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast a message to all users."""
    if not is_admin(update, context):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    message_to_send = update.message.text.split('/post', 1)[1].strip()
    if not message_to_send:
        await update.message.reply_text("Please provide a message to broadcast. Usage: /post <message>")
        return

    all_users = context.bot_data.get('users', [])
    if not all_users:
        await update.message.reply_text("No users to broadcast to.")
        return

    job_name = "active_broadcast"
    # Remove any existing broadcast job before starting a new one
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()

    context.job_queue.run_once(broadcast_job, 0, context={'users': all_users, 'message': message_to_send}, name=job_name)
    await update.message.reply_text(f"Starting broadcast to {len(all_users)} users. Use /stopcast to cancel.")

async def stop_cast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops an ongoing broadcast."""
    if not is_admin(update, context):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    job_name = "active_broadcast"
    current_jobs = context.job_queue.get_jobs_by_name(job_name)

    if not current_jobs:
        await update.message.reply_text("There is no active broadcast to stop.")
        return

    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text("Broadcast has been stopped.")

async def broadcast_job(context: ContextTypes.DEFAULT_TYPE):
    """The background job that sends the broadcast."""
    job_context = context.job.context
    users = job_context['users']
    message = job_context['message']

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            await asyncio.sleep(0.1) # Avoid hitting rate limits
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")

# --- Paid User Management ---

async def add_paid_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a user to a quiz's paid access list."""
    if not is_admin(update, context):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        quiz_id, user_id_str = context.args
        user_id = int(user_id_str)
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: /add <quiz_id> <user_id>")
        return

    # Find the quiz across all creators
    found_quiz = None
    creator_id = None
    for c_id, user_quizzes in context.bot_data.get('quizzes', {}).items():
        if quiz_id in user_quizzes:
            found_quiz = user_quizzes[quiz_id]
            creator_id = c_id
            break

    if not found_quiz:
        await update.message.reply_text("Quiz not found.")
        return

    if 'paid_users' not in found_quiz:
        found_quiz['paid_users'] = []

    if user_id not in found_quiz['paid_users']:
        found_quiz['paid_users'].append(user_id)
        save_quizzes(context.bot_data['quizzes'])
        await update.message.reply_text(f"User {user_id} has been given access to quiz '{found_quiz['title']}'.")
    else:
        await update.message.reply_text("User already has access to this quiz.")

async def remove_paid_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes a user from a quiz's paid access list."""
    if not is_admin(update, context):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        quiz_id, user_id_str = context.args
        user_id = int(user_id_str)
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: /rem <quiz_id> <user_id>")
        return

    found_quiz = None
    for c_id, user_quizzes in context.bot_data.get('quizzes', {}).items():
        if quiz_id in user_quizzes:
            found_quiz = user_quizzes[quiz_id]
            break

    if not found_quiz or 'paid_users' not in found_quiz or user_id not in found_quiz['paid_users']:
        await update.message.reply_text("User does not have access to this quiz or quiz not found.")
        return

    found_quiz['paid_users'].remove(user_id)
    save_quizzes(context.bot_data['quizzes'])
    await update.message.reply_text(f"User {user_id}'s access to quiz '{found_quiz['title']}' has been revoked.")

async def remove_all_paid_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes all users from a quiz's paid access list."""
    if not is_admin(update, context):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        quiz_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Usage: /remall <quiz_id>")
        return

    found_quiz = None
    for c_id, user_quizzes in context.bot_data.get('quizzes', {}).items():
        if quiz_id in user_quizzes:
            found_quiz = user_quizzes[quiz_id]
            break

    if not found_quiz or 'paid_users' not in found_quiz:
        await update.message.reply_text("Quiz not found or it has no paid users.")
        return

    found_quiz['paid_users'] = []
    save_quizzes(context.bot_data['quizzes'])
    await update.message.reply_text(f"All paid users have been removed from quiz '{found_quiz['title']}'.")