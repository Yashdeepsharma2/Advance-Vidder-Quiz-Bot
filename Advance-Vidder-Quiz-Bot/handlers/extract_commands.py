# Powered by Viddertech

import logging
import uuid
import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User, Quiz, Question, Filter

logger = logging.getLogger(__name__)

# Conversation states
EXTRACTING, NAMING = range(2)

def apply_all_filters(text: str, permanent_filters: set, temporary_removals: set) -> str:
    """Applies both permanent and temporary filter words to a string."""
    if not text:
        return ""
    # Combine all words to remove, ensuring they are lowercase for case-insensitive matching
    all_words_to_remove = permanent_filters.union(temporary_removals)

    # Remove links and usernames first
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)

    # Remove custom filter words
    for word in all_words_to_remove:
        # Use regex for case-insensitive, whole-word replacement
        text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)

    # Clean up extra whitespace that may result from removals
    return ' '.join(text.split())

async def extract_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the poll extraction conversation."""
    await update.message.reply_text(
        "Ready to extract! Please forward the polls you want to include in the new quiz.\n\n"
        "Your permanent filters and temporary removal list will be applied.\n\n"
        "Send /done when you are finished."
    )
    context.user_data['extracted_quiz'] = {'questions': []}
    return EXTRACTING

async def extract_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives a poll, filters it, and adds it to the new quiz data in user_data."""
    if not update.message.poll:
        await update.message.reply_text("That's not a poll. Please forward a poll message or send /done.")
        return EXTRACTING

    poll = update.message.poll
    user_id = update.effective_user.id
    db: Session = next(get_db())

    try:
        # Fetch user's permanent filters from the database
        user_filters = db.query(Filter.word).filter(Filter.user_id == user_id).all()
        permanent_filters = {word for (word,) in user_filters}

        # Get temporary removal list from the current session
        temporary_removals = context.user_data.get('temp_remove_list', set())

        question_text = apply_all_filters(poll.question, permanent_filters, temporary_removals)
        options = [apply_all_filters(opt.text, permanent_filters, temporary_removals) for opt in poll.options]

        if poll.type != 'quiz' or poll.correct_option_id is None:
            await update.message.reply_text("This is not a quiz poll and has no correct answer. Skipping.")
            return EXTRACTING

        question_data = {
            'text': question_text,
            'options': options,
            'correct': poll.correct_option_id
        }
        context.user_data['extracted_quiz']['questions'].append(question_data)
        await update.message.reply_text(f"✅ Poll extracted. Forward another or send /done.")
    finally:
        db.close()

    return EXTRACTING

async def extract_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Moves to the next step: naming the quiz."""
    if not context.user_data.get('extracted_quiz', {}).get('questions'):
        await update.message.reply_text("No polls were extracted. Cancelling.")
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text("Extraction complete! What should be the title of this new quiz?")
    return NAMING

async def name_and_save_extracted_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the extracted quiz with the given title."""
    title = update.message.text
    quiz_data = context.user_data['extracted_quiz']
    user_id = update.effective_user.id
    db: Session = next(get_db())

    try:
        new_quiz = Quiz(
            id=str(uuid.uuid4()),
            title=title,
            creator_id=user_id,
            questions=[Question(text=q['text'], options=q['options'], correct_option_index=q['correct']) for q in quiz_data['questions']]
        )
        db.add(new_quiz)
        db.commit()
        await update.message.reply_text(f"✅ Quiz '{title}' created successfully from the extracted polls!")
    except Exception as e:
        logger.error(f"Error saving extracted quiz to DB: {e}")
        await update.message.reply_text("An error occurred while saving your quiz.")
    finally:
        db.close()
        context.user_data.clear() # Clear all session data, including temp_remove_list

    return ConversationHandler.END

async def extract_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the extraction process."""
    context.user_data.clear()
    await update.message.reply_text("Extraction cancelled.")
    return ConversationHandler.END

# Define the conversation handler here
extract_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("extract", extract_start)],
    states={
        EXTRACTING: [MessageHandler(filters.POLL, extract_poll)],
        NAMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_and_save_extracted_quiz)],
    },
    fallbacks=[
        CommandHandler("done", extract_done),
        CommandHandler("cancel", extract_cancel)
    ],
)