# Powered by Viddertech
import logging
import os
import asyncio
import uuid
from telethon import TelegramClient, events
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from viddertech_quiz_bot.persistence import save_quizzes

logger = logging.getLogger(__name__)

# --- Session Management ---
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "viddertech_user_session"
SESSION_PATH = os.path.join("viddertech_quiz_bot/data", SESSION_NAME)

# States for conversation
PHONE, CODE, PASSWORD = range(100, 103)

async def telelogin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to log in to a user account."""
    if not API_ID or not API_HASH:
        await update.message.reply_text("Bot owner has not configured API_ID and API_HASH in environment variables. Cloning is disabled.")
        return ConversationHandler.END
    if os.path.exists(f"{SESSION_PATH}.session"):
        await update.message.reply_text("A user account is already logged in. Use /logout first to switch accounts.")
        return ConversationHandler.END

    await update.message.reply_text("Please send your phone number in international format (e.g., +1234567890).")
    return PHONE

async def get_phone_and_connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the phone number and attempts to connect."""
    phone = update.message.text
    context.user_data['phone'] = phone

    client = TelegramClient(f"{SESSION_PATH}", int(API_ID), API_HASH)
    context.user_data['telethon_client'] = client

    try:
        await client.connect()
        sent_code = await client.send_code_request(phone)
        context.user_data['phone_code_hash'] = sent_code.phone_code_hash
        await update.message.reply_text("I've sent a code to your Telegram account. Please send it to me.")
        return CODE
    except Exception as e:
        logger.error(f"Telethon connection failed: {e}")
        await update.message.reply_text(f"Connection failed: {e}\nPlease try again with /telelogin.")
        context.user_data.clear()
        return ConversationHandler.END

async def get_code_and_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the login code and signs in."""
    code = update.message.text
    phone = context.user_data['phone']
    phone_code_hash = context.user_data['phone_code_hash']
    client = context.user_data['telethon_client']

    try:
        await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
        await update.message.reply_text("Login successful! You can now use the cloning features.")
        await client.disconnect()
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        if "password" in str(e).lower():
            await update.message.reply_text("You have a two-factor authentication password. Please send it to me now.")
            return PASSWORD
        logger.error(f"Telethon sign-in failed: {e}")
        await update.message.reply_text(f"Sign-in failed: {e}\nPlease try again with /telelogin.")
        await client.disconnect()
        context.user_data.clear()
        return ConversationHandler.END

async def get_password_and_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the 2FA password and signs in."""
    password = update.message.text
    client = context.user_data['telethon_client']

    try:
        await client.sign_in(password=password)
        await update.message.reply_text("Login successful! You can now use the cloning features.")
    except Exception as e:
        logger.error(f"Telethon 2FA sign-in failed: {e}")
        await update.message.reply_text(f"Password login failed: {e}\nPlease try again with /telelogin.")
    finally:
        await client.disconnect()
        context.user_data.clear()
    return ConversationHandler.END

async def telelogin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the login process."""
    if 'telethon_client' in context.user_data and context.user_data['telethon_client'].is_connected():
        await context.user_data['telethon_client'].disconnect()
    context.user_data.clear()
    await update.message.reply_text("Login process has been cancelled.")
    return ConversationHandler.END

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs the user out by deleting the session file."""
    session_file = f"{SESSION_PATH}.session"
    if os.path.exists(session_file):
        os.remove(session_file)
        await update.message.reply_text("You have been successfully logged out.")
    else:
        await update.message.reply_text("You are not logged in.")

# --- Cloning Logic ---

async def clone_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the process of cloning a quiz from a link."""
    if not os.path.exists(f"{SESSION_PATH}.session"):
        await update.message.reply_text("You must be logged in to use the clone feature. Use /telelogin first.")
        return

    try:
        link = context.args[0]
        if 't.me/quizbot?start=' not in link.lower(): # Targeting QuizBot specifically
             await update.message.reply_text("Invalid link. Please provide a valid start link from @QuizBot.")
             return
    except IndexError:
        await update.message.reply_text("Please provide a quiz link to clone. Usage: /quiz <link>")
        return

    await update.message.reply_text("Starting clone process... This may take a few minutes. I will send a message when it's complete.")

    context.job_queue.run_once(
        clone_in_background,
        0,
        context={'chat_id': update.effective_chat.id, 'user_id': update.effective_user.id, 'link': link},
        name=f"clone_{update.effective_chat.id}"
    )

async def clone_in_background(context: ContextTypes.DEFAULT_TYPE):
    """The actual cloning logic that runs in a background job."""
    job_context = context.job.context
    chat_id = job_context['chat_id']
    user_id = job_context['user_id']
    link = job_context['link']

    client = TelegramClient(f"{SESSION_PATH}", int(API_ID), API_HASH)
    new_quiz = {'title': f"Cloned from {link}", 'questions': []}

    try:
        await client.connect()
        quiz_bot_entity = await client.get_entity('QuizBot')

        # Start a conversation
        async with client.conversation(quiz_bot_entity, timeout=300) as conv:
            await conv.send_message(f"/start {link.split('=')[-1]}")

            while True:
                try:
                    response = await conv.get_response(timeout=30)

                    if response.poll:
                        # It's a question poll
                        poll = response.poll
                        question_text = poll.question
                        options = [opt.text for opt in poll.options]

                        # Wait for the correct answer explanation
                        explanation = await conv.get_response(timeout=30)

                        # The correct answer is usually bold in the explanation
                        correct_answer_text = None
                        if explanation.entities:
                            for entity, text in zip(explanation.entities, explanation.raw_text.split()):
                                if isinstance(entity, (types.MessageEntityBold, types.MessageEntityTextUrl)):
                                    correct_answer_text = text.strip()
                                    break

                        if not correct_answer_text:
                            # Fallback if we can't find the bold text
                            logger.warning("Could not determine correct answer from explanation.")
                            continue

                        correct_option_index = -1
                        for i, opt_text in enumerate(options):
                            if correct_answer_text in opt_text:
                                correct_option_index = i
                                break

                        if correct_option_index != -1:
                            new_quiz['questions'].append({
                                'text': question_text,
                                'options': options,
                                'correct': correct_option_index
                            })
                        else:
                            logger.warning(f"Could not match answer '{correct_answer_text}' to options.")

                    elif "That's all!" in response.text or "You can now share this quiz" in response.text:
                        break # End of the quiz

                except asyncio.TimeoutError:
                    await context.bot.send_message(chat_id, "Cloning failed: The quiz bot did not respond in time.")
                    return

    except Exception as e:
        logger.error(f"Cloning failed: {e}")
        await context.bot.send_message(chat_id, f"Cloning process failed with an error: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

    if new_quiz['questions']:
        if user_id not in context.bot_data['quizzes']:
            context.bot_data['quizzes'][user_id] = {}

        quiz_id = str(uuid.uuid4())
        context.bot_data['quizzes'][user_id][quiz_id] = new_quiz
        save_quizzes(context.bot_data['quizzes'])

        await context.bot.send_message(
            chat_id,
            f"Cloning complete! Quiz '{new_quiz['title']}' with {len(new_quiz['questions'])} questions has been saved to your account."
        )
    else:
        await context.bot.send_message(chat_id, "Cloning finished, but no questions were found. The quiz may have expired or the format may be unsupported.")