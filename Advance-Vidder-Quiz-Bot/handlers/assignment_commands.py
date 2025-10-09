# Powered by Viddertech

import logging
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Assignment, Submission, User

logger = logging.getLogger(__name__)

# Conversation states
GET_A_TITLE, GET_A_DESC = range(2)
SUBMIT_A_ID, SUBMIT_A_WORK = range(2, 4)

# --- Assignment Creation Conversation ---

async def create_assignment_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to create an assignment."""
    await update.message.reply_text("Let's create a new assignment.\n\nFirst, what is the title?")
    context.user_data['new_assignment'] = {}
    return GET_A_TITLE

async def get_assignment_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the title and asks for the description."""
    context.user_data['new_assignment']['title'] = update.message.text
    await update.message.reply_text("Great. Now, please send the full description or questions for the assignment.")
    return GET_A_DESC

async def get_assignment_desc_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the description and saves the assignment to the database."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    assignment_data = context.user_data['new_assignment']
    assignment_data['description'] = update.message.text

    try:
        new_assignment = Assignment(
            id=str(uuid.uuid4()),
            creator_id=user_id,
            title=assignment_data['title'],
            description=assignment_data['description']
        )
        db.add(new_assignment)
        db.commit()

        await update.message.reply_text(
            f"✅ Assignment '{new_assignment.title}' created successfully!\n\n"
            f"Share this ID with students for submission:\n`{new_assignment.id}`"
        )
    except Exception as e:
        logger.error(f"Error saving assignment to DB: {e}")
        await update.message.reply_text("An error occurred while saving the assignment.")
    finally:
        db.close()
        context.user_data.clear()

    return ConversationHandler.END

async def create_assignment_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the assignment creation process."""
    context.user_data.clear()
    await update.message.reply_text("Assignment creation cancelled.")
    return ConversationHandler.END


# --- Assignment Submission Conversation ---

async def submit_assignment_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation for a student to submit their work."""
    await update.message.reply_text("Please send the ID of the assignment you are submitting for.")
    return SUBMIT_A_ID

async def get_submission_assignment_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the assignment ID and asks for the work to be submitted."""
    db: Session = next(get_db())
    assignment_id = update.message.text.strip()
    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            await update.message.reply_text("Invalid Assignment ID. Please check the ID and try again.")
            return SUBMIT_A_ID

        context.user_data['submission_assignment_id'] = assignment_id
        await update.message.reply_text("Assignment found. Please send your submission now. This can be text or a file/document.")
        return SUBMIT_A_WORK
    finally:
        db.close()

async def get_submission_work_and_save(update: Update, context: ContextTypes.DEFAULT_TfYPE) -> int:
    """Receives the work (text or file) and saves the submission."""
    db: Session = next(get_db())
    assignment_id = context.user_data['submission_assignment_id']
    user = update.effective_user

    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            await update.message.reply_text("Error: Could not find the assignment. Please try again.")
            return ConversationHandler.END

        submission = Submission(
            assignment_id=assignment_id,
            student_id=user.id,
            text_content=update.message.text or update.message.caption,
            file_id=update.message.document.file_id if update.message.document else None
        )
        db.add(submission)
        db.commit()

        await update.message.reply_text("✅ Your submission has been received successfully!")

        # Notify the creator
        await context.bot.send_message(
            chat_id=assignment.creator_id,
            text=f"📬 New submission for '{assignment.title}' from {user.full_name}."
        )
    except Exception as e:
        logger.error(f"Error saving submission: {e}")
        await update.message.reply_text("An error occurred while saving your submission.")
    finally:
        db.close()
        context.user_data.clear()

    return ConversationHandler.END

async def submit_assignment_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the submission process."""
    context.user_data.clear()
    await update.message.reply_text("Submission cancelled.")
    return ConversationHandler.END

# --- View Submissions Command ---

async def view_submissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allows a creator to view all submissions for a given assignment."""
    try:
        assignment_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Usage: /view_submissions <assignment_id>")
        return

    db: Session = next(get_db())
    user_id = update.effective_user.id
    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.creator_id == user_id).first()
        if not assignment:
            await update.message.reply_text("Assignment not found or you are not the creator.")
            return

        if not assignment.submissions:
            await update.message.reply_text(f"There are no submissions for '{assignment.title}' yet.")
            return

        message = f"Submissions for '{assignment.title}':\n\n"
        for sub in assignment.submissions:
            student_name = sub.student.full_name if sub.student else f"User ID: {sub.student_id}"
            message += f"From: {student_name}\n"
            if sub.text_content:
                message += f"Content: {sub.text_content}\n"
            if sub.file_id:
                message += "File submitted (file ID stored).\n" # Cannot resend file easily, but can notify
            message += "---\n"

        await update.message.reply_text(message)
    finally:
        db.close()