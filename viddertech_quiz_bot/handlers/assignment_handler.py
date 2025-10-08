# Powered by Viddertech
import logging
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from viddertech_quiz_bot.persistence import save_assignments

logger = logging.getLogger(__name__)

# States for conversations
# Assignment Creation
CREATE_A_TITLE, CREATE_A_DESC = range(300, 302)
# Submission
SUBMIT_A_ID, SUBMIT_A_WORK = range(302, 304)


# --- Assignment Creation ---

async def assignment_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to create an assignment."""
    await update.message.reply_text("Let's create a new assignment. First, what is the title?")
    context.user_data['new_assignment'] = {}
    return CREATE_A_TITLE

async def get_assignment_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the title and asks for the description."""
    context.user_data['new_assignment']['title'] = update.message.text
    await update.message.reply_text("Great. Now, please send the full description or questions for the assignment.")
    return CREATE_A_DESC

async def get_assignment_desc_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the description and saves the assignment."""
    assignment_data = context.user_data['new_assignment']
    assignment_data['description'] = update.message.text

    user_id = update.effective_user.id
    assignment_id = str(uuid.uuid4())

    if 'assignments' not in context.bot_data:
        context.bot_data['assignments'] = {}

    new_assignment = {
        'id': assignment_id,
        'creator_id': user_id,
        'title': assignment_data['title'],
        'description': assignment_data['description'],
        'submissions': {} # To store submissions by user_id
    }

    context.bot_data['assignments'][assignment_id] = new_assignment
    save_assignments(context.bot_data['assignments'])

    await update.message.reply_text(
        f"Assignment '{assignment_data['title']}' created successfully!\n\n"
        f"Share this ID with students for submission:\n<code>{assignment_id}</code>"
    )
    context.user_data.clear()
    return ConversationHandler.END

async def assignment_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the assignment creation process."""
    context.user_data.clear()
    await update.message.reply_text("Assignment creation has been cancelled.")
    return ConversationHandler.END

# --- Assignment Submission ---

async def submit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation for a student to submit work."""
    await update.message.reply_text("Please send the ID of the assignment you are submitting for.")
    return SUBMIT_A_ID

async def get_submission_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the assignment ID and asks for the work."""
    assignment_id = update.message.text.strip()
    if 'assignments' not in context.bot_data or assignment_id not in context.bot_data['assignments']:
        await update.message.reply_text("Invalid Assignment ID. Please check the ID and try again.")
        return SUBMIT_A_ID

    context.user_data['submission_assignment_id'] = assignment_id
    await update.message.reply_text("Assignment found. Please send your submission now. This can be text or a file.")
    return SUBMIT_A_WORK

async def get_submission_work_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the work and saves the submission."""
    assignment_id = context.user_data['submission_assignment_id']
    assignment = context.bot_data['assignments'][assignment_id]
    user = update.effective_user

    submission_text = update.message.text or update.message.caption
    file_id = update.message.document.file_id if update.message.document else None

    assignment['submissions'][user.id] = {
        'user_name': user.full_name,
        'text': submission_text,
        'file_id': file_id,
        'timestamp': update.message.date.isoformat()
    }

    save_assignments(context.bot_data['assignments'])

    await update.message.reply_text("Your submission has been received successfully!")
    # Notify the creator
    try:
        await context.bot.send_message(
            chat_id=assignment['creator_id'],
            text=f"New submission for '{assignment['title']}' from {user.full_name}."
        )
    except Exception as e:
        logger.error(f"Failed to send submission notification: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def submit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the submission process."""
    context.user_data.clear()
    await update.message.reply_text("Submission has been cancelled.")
    return ConversationHandler.END

# --- View Submissions ---

async def view_submissions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allows a creator to view submissions for an assignment."""
    try:
        assignment_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Please provide an Assignment ID. Usage: /view_submissions <ID>")
        return

    user_id = update.effective_user.id
    if 'assignments' not in context.bot_data or assignment_id not in context.bot_data['assignments']:
        await update.message.reply_text("Invalid Assignment ID.")
        return

    assignment = context.bot_data['assignments'][assignment_id]
    if assignment['creator_id'] != user_id:
        await update.message.reply_text("You are not the creator of this assignment.")
        return

    if not assignment['submissions']:
        await update.message.reply_text(f"There are no submissions for '{assignment['title']}' yet.")
        return

    message = f"<b>Submissions for '{assignment['title']}':</b>\n\n"
    for sub_user_id, submission in assignment['submissions'].items():
        message += f"<b>From:</b> {submission['user_name']}\n"
        message += f"<b>Date:</b> {submission['timestamp']}\n"
        if submission['text']:
            message += f"<b>Submission:</b> {submission['text']}\n"
        if submission['file_id']:
            message += "A file was submitted. You can access it from the original submission message.\n"
        message += "---\n"

    await update.message.reply_html(message)