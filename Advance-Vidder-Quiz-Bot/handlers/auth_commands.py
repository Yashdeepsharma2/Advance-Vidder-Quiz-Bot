# Powered by Viddertech

import logging
import uuid
import os
from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import SessionPasswordNeededError

import config
from database.database import get_db
from database.models import Quiz, Question
from integrations.telethon_client import VidderTelethonClient

logger = logging.getLogger(__name__)

# --- Telelogin Conversation ---
PHONE, CODE, PASSWORD = range(3)

async def telelogin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to log in to a user account."""
    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        await update.message.reply_text("Cloning feature is not configured by the bot owner.")
        return ConversationHandler.END
    if os.path.exists(config.TELETHON_SESSION_PATH + ".session"):
        await update.message.reply_text("You are already logged in. Use /logout first.")
        return ConversationHandler.END

    await update.message.reply_text("Please send your phone number in international format (e.g., +1234567890) to log in for cloning.")
    return PHONE

async def get_phone_and_connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets phone, connects, and sends login code."""
    phone = update.message.text
    context.user_data['phone'] = phone

    client = TelegramClient(config.TELETHON_SESSION_PATH, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    context.user_data['telethon_client'] = client

    try:
        await client.connect()
        sent_code = await client.send_code_request(phone)
        context.user_data['phone_code_hash'] = sent_code.phone_code_hash
        await update.message.reply_text("A login code has been sent to you. Please send it to me.")
        return CODE
    except Exception as e:
        logger.error(f"Telethon connection failed: {e}")
        await update.message.reply_text(f"Connection failed. Please try again.")
        context.user_data.clear()
        return ConversationHandler.END

async def get_code_and_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets login code and attempts to sign in."""
    code = update.message.text
    client = context.user_data['telethon_client']
    phone = context.user_data['phone']
    phone_code_hash = context.user_data['phone_code_hash']

    try:
        await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        await update.message.reply_text("You have a two-factor authentication password. Please send it now.")
        return PASSWORD
    except Exception as e:
        logger.error(f"Telethon sign-in failed: {e}")
        await update.message.reply_text(f"Sign-in failed. Please try again.")
        await client.disconnect()
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text("Login successful! You can now use the /quiz command to clone.")
    await client.disconnect()
    context.user_data.clear()
    return ConversationHandler.END

async def get_password_and_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets 2FA password and completes sign in."""
    password = update.message.text
    client = context.user_data['telethon_client']

    try:
        await client.sign_in(password=password)
        await update.message.reply_text("Login successful! You can now use the /quiz command to clone.")
    except Exception as e:
        logger.error(f"Telethon 2FA sign-in failed: {e}")
        await update.message.reply_text(f"Password login failed. Please try again.")
    finally:
        await client.disconnect()
        context.user_data.clear()

    return ConversationHandler.END

async def telelogin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the login process."""
    if 'telethon_client' in context.user_data and context.user_data['telethon_client'].is_connected():
        await context.user_data['telethon_client'].disconnect()
    context.user_data.clear()
    await update.message.reply_text("Login process cancelled.")
    return ConversationHandler.END

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs the user out by deleting the session file."""
    session_file = config.TELETHON_SESSION_PATH + ".session"
    if os.path.exists(session_file):
        os.remove(session_file)
        await update.message.reply_text("You have been successfully logged out.")
    else:
        await update.message.reply_text("You are not logged in.")

# --- Quiz Cloning ---

async def clone_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /quiz command to start the cloning process."""
    if not os.path.exists(config.TELETHON_SESSION_PATH + ".session"):
        await update.message.reply_text("You must be logged in to clone. Use /telelogin first.")
        return

    try:
        link = context.args[0]
        if 't.me/quizbot?start=' not in link.lower():
             await update.message.reply_text("Invalid link. Please provide a valid start link from @QuizBot.")
             return
    except IndexError:
        await update.message.reply_text("Usage: /quiz <@QuizBot_start_link>")
        return

    await update.message.reply_text("Starting clone process... This may take a moment. I will send a message when it's complete.")

    context.job_queue.run_once(
        run_cloning_job,
        0,
        context={'chat_id': update.effective_chat.id, 'user_id': update.effective_user.id, 'link': link},
        name=f"clone_{update.effective_chat.id}"
    )

async def run_cloning_job(context: ContextTypes.DEFAULT_TYPE):
    """The background job that executes the cloning."""
    job_context = context.job.context
    chat_id = job_context['chat_id']
    user_id = job_context['user_id']
    link = job_context['link']

    telethon_client = VidderTelethonClient()
    try:
        cloned_data = await telethon_client.clone_quiz_from_bot(link)

        if not cloned_data or not cloned_data['questions']:
            await context.bot.send_message(chat_id, "Cloning finished, but no questions were found. The quiz may have expired or the format is unsupported.")
            return

        # Save the cloned quiz to the database
        db: Session = next(get_db())
        try:
            new_quiz = Quiz(
                id=str(uuid.uuid4()),
                title=cloned_data['title'],
                creator_id=user_id,
                questions=[Question(text=q['text'], options=q['options'], correct_option_index=q['correct']) for q in cloned_data['questions']]
            )
            db.add(new_quiz)
            db.commit()
            await context.bot.send_message(
                chat_id,
                f"✅ Cloning complete! Quiz '{new_quiz.title}' with {len(new_quiz.questions)} questions has been saved to your account."
            )
        except Exception as e:
            logger.error(f"Error saving cloned quiz to DB: {e}")
            await context.bot.send_message(chat_id, "An error occurred while saving the cloned quiz.")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Cloning job failed: {e}")
        await context.bot.send_message(chat_id, f"Cloning process failed: {e}")