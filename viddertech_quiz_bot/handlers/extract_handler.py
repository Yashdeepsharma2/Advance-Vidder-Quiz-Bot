# Powered by Viddertech
import logging
import re
import uuid
from telegram import Update, Poll
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from viddertech_quiz_bot.persistence import save_quizzes
from viddertech_quiz_bot.handlers.filter_handler import get_user_filters

logger = logging.getLogger(__name__)

# States for conversation
EXTRACTING, NAMING = range(2)

def apply_filters(text: str, permanent_filters: list, temporary_removals: list) -> str:
    """Applies both permanent and temporary filter words to a string."""
    if not text:
        return ""
    # Combine both lists for removal
    all_words_to_remove = set(permanent_filters + [word.lower() for word in temporary_removals])

    # Remove links
    text = re.sub(r'http\S+', '', text)
    # Remove usernames
    text = re.sub(r'@\w+', '', text)
    # Remove custom filter words
    for word in all_words_to_remove:
        # Use regex for whole word replacement to avoid partial matches
        text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)
    # Clean up extra whitespace
    return ' '.join(text.split())

async def extract_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to extract polls."""
    await update.message.reply_text(
        "Ready to extract! Please forward the polls you want to include in the new quiz.\n\n"
        "Send /done when you are finished."
    )
    context.user_data['extracted_quiz'] = {'title': '', 'questions': []}
    return EXTRACTING

async def extract_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives a poll, filters it, and adds it to the new quiz."""
    if not update.message.poll:
        await update.message.reply_text("Please forward a poll message.")
        return EXTRACTING

    poll = update.message.poll
    user_id = update.effective_user.id
    permanent_filters = get_user_filters(context, user_id)
    temporary_removals = context.user_data.get('removal_list', [])

    # Filter question and options
    question_text = apply_filters(poll.question, permanent_filters, temporary_removals)
    options = [apply_filters(opt.text, permanent_filters, temporary_removals) for opt in poll.options]

    # Find the correct option index
    correct_option_id = -1
    for i, option in enumerate(poll.options):
        if option.voter_count > 0:  # In forwarded polls, the correct option has a voter
             # This is a heuristic. A better way would be to check the original poll's `correct_option_id` if available
             # For now, we assume the creator voted for the correct answer
            if poll.type == 'quiz' and hasattr(poll, 'correct_option_id'):
                correct_option_id = poll.correct_option_id
                break

    # A fallback if we can't determine the correct answer
    if correct_option_id == -1:
        await update.message.reply_text("Could not determine the correct answer for the last poll. It has been skipped.")
        return EXTRACTING

    question = {
        'text': question_text,
        'options': options,
        'correct': correct_option_id
    }
    context.user_data['extracted_quiz']['questions'].append(question)
    await update.message.reply_text(f"Poll '{question_text[:30]}...' extracted. Forward another or send /done.")
    return EXTRACTING

async def extract_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for the title of the new quiz."""
    if not context.user_data.get('extracted_quiz', {}).get('questions'):
        await update.message.reply_text("No polls were extracted. Cancelling.")
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text("Extraction complete! What should be the title of this new quiz?")
    return NAMING

async def name_and_save_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the extracted quiz with the given title."""
    title = update.message.text
    quiz = context.user_data['extracted_quiz']
    quiz['title'] = title

    user_id = update.effective_user.id
    if 'quizzes' not in context.bot_data:
        context.bot_data['quizzes'] = {}
    if user_id not in context.bot_data['quizzes']:
        context.bot_data['quizzes'][user_id] = {}

    quiz_id = str(uuid.uuid4())
    context.bot_data['quizzes'][user_id][quiz_id] = quiz
    save_quizzes(context.bot_data['quizzes'])

    await update.message.reply_text(
        f"Quiz '{title}' created successfully from extracted polls!\n"
        "You can manage it with /myquizzes."
    )
    context.user_data.clear()
    return ConversationHandler.END

async def extract_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the extraction process."""
    context.user_data.clear()
    await update.message.reply_text("Extraction has been cancelled.")
    return ConversationHandler.END