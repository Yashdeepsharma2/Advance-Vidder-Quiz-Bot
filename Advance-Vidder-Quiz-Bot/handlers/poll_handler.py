# Powered by Viddertech

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Response, User

logger = logging.getLogger(__name__)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles a user's answer to a quiz poll.
    This function ONLY records the answer and score. It does NOT advance the quiz.
    The quiz flow is managed by the creator via control commands.
    """
    answer = update.poll_answer
    quiz_session = context.chat_data.get('current_quiz')

    # Ensure the answer is for the current, active quiz
    if not quiz_session or answer.poll_id != context.chat_data.get('current_poll_id'):
        return

    user = answer.user
    is_correct = False

    # Check if the answer is correct
    if answer.option_ids and answer.option_ids[0] == context.chat_data.get('current_question_correct_id'):
        is_correct = True
        # Update score in the session
        if user.id not in quiz_session['scores']:
            quiz_session['scores'][user.id] = {'score': 0, 'name': user.full_name}
        quiz_session['scores'][user.id]['score'] += 1

    # --- Persist the response to the database for long-term analytics ---
    db: Session = next(get_db())
    try:
        # Ensure user exists in our User table
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            db_user = User(id=user.id, full_name=user.full_name, username=user.username)
            db.add(db_user)
            db.commit()

        # Record the response
        response_entry = Response(
            user_id=user.id,
            quiz_id=quiz_session['quiz_id'],
            question_id=quiz_session['questions'][quiz_session['current_question_index']],
            is_correct=is_correct
        )
        db.add(response_entry)
        db.commit()
        logger.info(f"Recorded answer from user {user.id} for quiz {quiz_session['quiz_id']}. Correct: {is_correct}")
    except Exception as e:
        logger.error(f"Error saving response to DB: {e}")
        db.rollback()
    finally:
        db.close()

    # The quiz does NOT advance here automatically. It waits for the poll to close
    # or for a manual action from the quiz creator. The logic for showing results
    # and moving to the next question will be handled by a separate command/callback.