# Powered by Viddertech

import logging
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Quiz, Section, Question

logger = logging.getLogger(__name__)

# Conversation states
(
    GET_QUIZ_TITLE,
    SECTION_MENU,
    GET_SECTION_NAME,
    GET_SECTION_TIMER,
    ADD_QUESTIONS
) = range(5)

async def start_sectional_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the sectional quiz creation process."""
    query = update.callback_query
    await query.edit_message_text("Let's create a Sectional Quiz! First, what is the overall title of the quiz?")

    # Initialize the quiz structure in user_data
    context.user_data['sectional_quiz'] = {
        'title': None,
        'sections': []
    }
    return GET_QUIZ_TITLE

async def get_quiz_title_and_show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the quiz title and shows the section management menu."""
    title = update.message.text
    context.user_data['sectional_quiz']['title'] = title

    # Create the quiz object in the database now
    db: Session = next(get_db())
    try:
        new_quiz = Quiz(
            id=str(uuid.uuid4()),
            title=title,
            creator_id=update.effective_user.id,
            quiz_mode='sectional'
        )
        db.add(new_quiz)
        db.commit()
        context.user_data['sectional_quiz']['id'] = new_quiz.id
        logger.info(f"Created sectional quiz shell for '{title}' with ID {new_quiz.id}")
    except Exception as e:
        logger.error(f"Failed to create sectional quiz shell in DB: {e}")
        await update.message.reply_text("An error occurred. Please try again.")
        return ConversationHandler.END
    finally:
        db.close()

    await update.message.reply_text(
        f"Quiz '{title}' created. Now let's add some sections.\n\n"
        "Please send the name for your first section (e.g., 'Physics')."
    )
    return GET_SECTION_NAME

async def get_section_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the name for a new section."""
    section_name = update.message.text
    context.user_data['current_section'] = {'name': section_name}
    await update.message.reply_text(f"Section '{section_name}' created. Now, how many seconds per question for this section? (e.g., 30)")
    return GET_SECTION_TIMER

async def get_section_timer_and_add_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the timer for the section and prompts for questions."""
    try:
        timer = int(update.message.text)
        if not 5 <= timer <= 600:
            await update.message.reply_text("Please enter a time between 5 and 600 seconds.")
            return GET_SECTION_TIMER
    except ValueError:
        await update.message.reply_text("Please enter a valid number for the timer.")
        return GET_SECTION_TIMER

    context.user_data['current_section']['timer'] = timer

    # Save the section to the database
    db: Session = next(get_db())
    quiz_id = context.user_data['sectional_quiz']['id']
    section_data = context.user_data['current_section']
    try:
        new_section = Section(
            quiz_id=quiz_id,
            name=section_data['name'],
            time_per_question=section_data['timer']
        )
        db.add(new_section)
        db.commit()
        context.user_data['current_section']['id'] = new_section.id
        logger.info(f"Saved section '{new_section.name}' to quiz {quiz_id}")
    except Exception as e:
        logger.error(f"Failed to save section to DB: {e}")
        await update.message.reply_text("An error occurred saving the section. Please try again.")
        return GET_SECTION_NAME # Go back to trying to add a section
    finally:
        db.close()

    await update.message.reply_text(
        f"Section '{section_data['name']}' added with a {timer}s timer.\n\n"
        "Now, send me questions for this section in the format:\n\n"
        "```\nWhat is the question?\nOption A\nOption B ✅\nOption C\n```\n\n"
        "Send /done_section when you are finished adding questions to this section."
    )
    return ADD_QUESTIONS

async def add_question_to_section(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Adds a question to the current section."""
    question_text = update.message.text
    lines = question_text.strip().split('\n')

    if len(lines) < 2 or '✅' not in question_text:
        await update.message.reply_text("Invalid format. Please provide a question and at least one option marked with ✅.")
        return ADD_QUESTIONS

    question_title = lines[0]
    options = [line.replace('✅', '').strip() for line in lines[1:]]
    correct_option_index = [i for i, line in enumerate(lines[1:]) if '✅' in line][0]

    db: Session = next(get_db())
    quiz_id = context.user_data['sectional_quiz']['id']
    section_id = context.user_data['current_section']['id']
    try:
        new_question = Question(
            quiz_id=quiz_id,
            section_id=section_id,
            text=question_title,
            options=options,
            correct_option_index=correct_option_index
        )
        db.add(new_question)
        db.commit()
        await update.message.reply_text("✅ Question added to the current section. Send another or /done_section.")
    except Exception as e:
        logger.error(f"Error adding question to section in DB: {e}")
        await update.message.reply_text("An error occurred.")
    finally:
        db.close()

    return ADD_QUESTIONS

async def done_with_section(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finishes adding questions to a section and returns to the section menu."""
    context.user_data.pop('current_section', None)
    await update.message.reply_text(
        "Section complete!\n\n"
        "You can now add another section by sending its name, or type /finish_quiz to complete the entire quiz."
    )
    return GET_SECTION_NAME # Loop back to allow adding another section

async def finish_sectional_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finalizes the sectional quiz."""
    quiz_title = context.user_data['sectional_quiz']['title']
    await update.message.reply_text(f"✅ Sectional quiz '{quiz_title}' is complete and has been saved!")
    context.user_data.clear()
    return ConversationHandler.END

async def sectional_creation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the sectional quiz creation process."""
    # Also needs to delete the quiz shell that was created
    db: Session = next(get_db())
    quiz_id = context.user_data.get('sectional_quiz', {}).get('id')
    if quiz_id:
        try:
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if quiz:
                db.delete(quiz)
                db.commit()
                logger.info(f"Deleted quiz shell {quiz_id} due to cancellation.")
        except Exception as e:
            logger.error(f"Error deleting quiz shell on cancel: {e}")
        finally:
            db.close()

    context.user_data.clear()
    await update.message.reply_text("Sectional quiz creation cancelled.")
    return ConversationHandler.END

sectional_creation_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_sectional_creation, pattern="^create_quiz_start_sectional$")],
    states={
        GET_QUIZ_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quiz_title_and_show_menu)],
        GET_SECTION_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_section_name)],
        GET_SECTION_TIMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_section_timer_and_add_questions)],
        ADD_QUESTIONS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_question_to_section),
            CommandHandler("done_section", done_with_section),
        ],
    },
    fallbacks=[
        CommandHandler("finish_quiz", finish_sectional_quiz),
        CommandHandler("cancel", sectional_creation_cancel)
    ],
)