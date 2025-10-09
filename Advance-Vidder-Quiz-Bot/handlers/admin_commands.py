# Powered by Viddertech

import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, Application
from sqlalchemy.orm import Session

import config
from database.database import get_db
from database.models import User

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Checks if a user is an admin based on the config."""
    return user_id == config.OWNER_ID or user_id in config.ADMIN_IDS

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcasts a message to all users of the bot."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    message_to_send = update.message.text.split('/post', 1)[1].strip()
    if not message_to_send:
        await update.message.reply_text("Usage: /post <message>")
        return

    job_name = "active_broadcast"
    # Remove any existing broadcast job before starting a new one
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()

    context.job_queue.run_once(broadcast_job, 0, context={'message': message_to_send}, name=job_name)
    await update.message.reply_text("📢 Starting broadcast... Use /stopcast to cancel.")

async def broadcast_job(context: ContextTypes.DEFAULT_TYPE):
    """The background job that sends the broadcast message."""
    job_context = context.job.context
    message = job_context['message']

    db: Session = next(get_db())
    try:
        all_user_ids = [user.id for user in db.query(User.id).all()]
        logger.info(f"Broadcasting to {len(all_user_ids)} users.")

        for user_id in all_user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                await asyncio.sleep(0.1) # To avoid hitting Telegram's rate limits
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {user_id}: {e}")
    finally:
        db.close()
    logger.info("Broadcast finished.")

async def stopcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops an ongoing broadcast job."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    job_name = "active_broadcast"
    current_jobs = context.job_queue.get_jobs_by_name(job_name)

    if not current_jobs:
        await update.message.reply_text("There is no active broadcast to stop.")
        return

    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text("✅ Broadcast has been stopped.")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bans a user from using the bot."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        user_to_ban_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /ban <user_id>")
        return

    db: Session = next(get_db())
    try:
        user_to_ban = db.query(User).filter(User.id == user_to_ban_id).first()
        if not user_to_ban:
            await update.message.reply_text("User not found in the database.")
            return

        if user_to_ban.is_banned:
            await update.message.reply_text("This user is already banned.")
            return

        user_to_ban.is_banned = True
        db.commit()
        await update.message.reply_text(f"🚫 User {user_to_ban.full_name} ({user_to_ban_id}) has been banned.")
    finally:
        db.close()