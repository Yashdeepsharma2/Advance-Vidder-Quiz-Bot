# Powered by Viddertech

import logging
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Quiz, Question

logger = logging.getLogger(__name__)

# Conversation states
GET_BULK_TITLE, GET_BULK_QUESTIONS = range(2)

async def bulk_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the bulk quiz creation process."""
    await update.message.reply_text(
        "Let's create a quiz from a block of text.\n\n"
        "First, what is the title of this quiz?"
    )
    return GET_BULK_TITLE

async def get_bulk_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the title and asks for the block of questions."""
    context.user_data['bulk_quiz_title'] = update.message.text
    await update.message.reply_text(
        f"Title set to '{update.message.text}'.\n\n"
        "Now, please paste the full block of questions. Each question should be separated by `---` on its own line, like this:\n\n"
        "```\n"
        "Question 1?\n"
        "Option A\n"
        "Option B ✅\n\n"
        "---\n\n"
        "Question 2?\n"
        "Option X ✅\n"
        "Option Y\n"
        "```",
        parse_mode='Markdown'
    )
    return GET_BULK_QUESTIONS

async def process_bulk_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the block of questions and saves the quiz."""
    raw_text = update.message.text
    question_blocks = raw_text.split('---')

    parsed_questions = []
    errors = []

    for i, block in enumerate(question_blocks, 1):
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        if len(lines) < 2:
            errors.append(f"Question #{i} is malformed.")
            continue

        question_title = lines[0]
        options = []
        correct_option_index = None

        for j, line in enumerate(lines[1:]):
            line = line.strip()
            if not line:
                continue
            if '✅' in line:
                correct_option_index = j
                options.append(line.replace('✅', '').strip())
            else:
                options.append(line)

        if correct_option_index is None:
            errors.append(f"Question #{i} ('{question_title[:20]}...') is missing a correct answer marker ✅.")
            continue

        parsed_questions.append({
            'text': question_title,
            'options': options,
            'correct': correct_option_index
        })

    if errors:
        error_message = "Found some errors in your formatting:\n\n" + "\n".join(errors)
        await update.message.reply_text(error_message + "\n\nPlease correct them and paste the block again.")
        return GET_BULK_QUESTIONS

    if not parsed_questions:
        await update.message.reply_text("No valid questions were found. Please check your formatting and try again.")
        return GET_BULK_QUESTIONS

    # All questions parsed successfully, now save to DB
    db: Session = next(get_db())
    quiz_title = context.user_data['bulk_quiz_title']
    user_id = update.effective_user.id
    try:
        new_quiz = Quiz(
            id=str(uuid.uuid4()),
            title=quiz_title,
            creator_id=user_id,
            quiz_mode='standard', # Bulk quizzes are standard by default
            questions=[Question(text=q['text'], options=q['options'], correct_option_index=q['correct']) for q in parsed_questions]
        )
        db.add(new_quiz)
        db.commit()
        await update.message.reply_text(f"✅ Success! Quiz '{quiz_title}' with {len(parsed_questions)} questions has been created.")
    except Exception as e:
        logger.error(f"Error saving bulk quiz to DB: {e}")
        await update.message.reply_text("An error occurred while saving the quiz.")
    finally:
        db.close()
        context.user_data.clear()

    return ConversationHandler.END

async def bulk_create_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the bulk creation process."""
    context.user_data.clear()
    await update.message.reply_text("Bulk creation cancelled.")
    return ConversationHandler.END

bulk_creation_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("bulkcreate", bulk_create_start)], # Using /bulkcreate to not conflict
    states={
        GET_BULK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bulk_title)],
        GET_BULK_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_bulk_questions)],
    },
    fallbacks=[CommandHandler("cancel", bulk_create_cancel)],
)