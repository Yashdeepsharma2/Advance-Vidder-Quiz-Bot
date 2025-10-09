# Powered by Viddertech
import logging
import math
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

import config
from database.database import get_db
from database.models import Quiz
from utils.keyboards import main_menu_keyboard, my_quizzes_keyboard, delete_confirmation_keyboard
from .quiz_commands import start_quiz_session # Import the quiz playing logic

logger = logging.getLogger(__name__)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses all callback queries and routes them to the appropriate handler."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "main_menu":
        await main_menu_callback(update, context)
    elif data.startswith("my_quizzes_"):
        await my_quizzes_callback(update, context)
    elif data.startswith("delete_start_"):
        await delete_start_callback(update, context)
    elif data.startswith("delete_confirm_"):
        await delete_confirm_callback(update, context)
    elif data.startswith("delete_cancel_"):
        await my_quizzes_callback(update, context, from_cancel=True)
    elif data.startswith("play_"):
        await play_quiz_callback(update, context)
    # Future routes here

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'Back to Main Menu' button press."""
    query = update.callback_query
    await query.edit_message_text(
        text="Welcome to the Viddertech Advance Quiz Bot!",
        reply_markup=main_menu_keyboard()
    )

async def my_quizzes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, from_cancel: bool = False):
    """Handles pagination for the /myquizzes command."""
    query = update.callback_query
    db: Session = next(get_db())
    user_id = query.from_user.id

    page = 0
    if not from_cancel:
        try:
            page = int(query.data.split("_")[-1])
        except (IndexError, ValueError):
            page = 0

    try:
        quizzes_query = db.query(Quiz).filter(Quiz.creator_id == user_id)
        total_quizzes = quizzes_query.count()
        total_pages = math.ceil(total_quizzes / config.QUIZZES_PER_PAGE)

        offset = page * config.QUIZZES_PER_PAGE
        user_quizzes = quizzes_query.order_by(Quiz.created_at.desc()).offset(offset).limit(config.QUIZZES_PER_PAGE).all()

        if not user_quizzes:
            await query.edit_message_text(text="You haven't created any quizzes yet. Use the 'Create New Quiz' button to start!")
            return

        reply_markup = my_quizzes_keyboard(user_quizzes, page, total_pages)
        await query.edit_message_text("Here are your quizzes:", reply_markup=reply_markup)
    finally:
        db.close()

async def delete_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks for confirmation before deleting a quiz."""
    query = update.callback_query
    db: Session = next(get_db())
    quiz_id = query.data.split("_")[-1]

    try:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            await query.edit_message_text(text="Error: This quiz does not exist.")
            return

        await query.edit_message_text(
            text=f"Are you sure you want to delete the quiz '{quiz.title}'?",
            reply_markup=delete_confirmation_keyboard(quiz_id)
        )
    finally:
        db.close()

async def delete_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes the quiz after confirmation."""
    query = update.callback_query
    db: Session = next(get_db())
    quiz_id = query.data.split("_")[-1]
    user_id = query.from_user.id

    try:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == user_id).first()
        if quiz:
            quiz_title = quiz.title
            db.delete(quiz)
            db.commit()
            await query.edit_message_text(text=f"Quiz '{quiz_title}' has been deleted.")
        else:
            await query.edit_message_text(text="Error: Could not find the quiz to delete. It might have been deleted already.")
    finally:
        db.close()

async def play_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts a quiz when the 'Play' button is pressed."""
    query = update.callback_query
    quiz_id = query.data.split("_")[-1]

    # Let the user know the quiz is starting
    await query.edit_message_text(text=f"Starting quiz...")

    # Call the function from quiz_commands to handle the session
    await start_quiz_session(update, context, quiz_id)