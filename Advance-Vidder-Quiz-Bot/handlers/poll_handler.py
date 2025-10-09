# Powered by Viddertech

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Response, User, Quiz

logger = logging.getLogger(__name__)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles a user's answer to a quiz poll.
    Records the answer, and applies negative marking if enabled.
    """
    answer = update.poll_answer
    quiz_session = context.chat_data.get('current_quiz')

    if not quiz_session or answer.poll_id != context.chat_data.get('current_poll_id'):
        return

    user = answer.user
    is_correct = False

    # Initialize user's score if they haven't answered before in this session
    if user.id not in quiz_session['scores']:
        quiz_session['scores'][user.id] = {'score': 0, 'name': user.full_name}

    db: Session = next(get_db())
    try:
        # Fetch the quiz to check its settings
        quiz = db.query(Quiz).filter(Quiz.id == quiz_session['quiz_id']).first()
        if not quiz:
            logger.error(f"Could not find quiz with ID {quiz_session['quiz_id']} during poll handling.")
            return

        # Check if the submitted answer is correct
        if answer.option_ids and answer.option_ids[0] == context.chat_data.get('current_question_correct_id'):
            is_correct = True
            quiz_session['scores'][user.id]['score'] += 1
        else:
            # Apply negative marking if it's enabled for this quiz
            if quiz.negative_marking:
                quiz_session['scores'][user.id]['score'] -= quiz.negative_marks
                logger.info(f"Applied negative marking of {quiz.negative_marks} to user {user.id}")

        # --- Persist the response to the database for long-term analytics ---
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            db_user = User(id=user.id, full_name=user.full_name, username=user.username)
            db.add(db_user)
            db.commit()

        response_entry = Response(
            user_id=user.id,
            quiz_id=quiz_session['quiz_id'],
            question_id=quiz_session['questions'][quiz_session['current_question_index']],
            is_correct=is_correct
        )
        db.add(response_entry)
        db.commit()
        logger.info(f"Recorded answer from user {user.id}. Correct: {is_correct}")

    except Exception as e:
        logger.error(f"Error in poll handler: {e}")
        db.rollback()
    finally:
        db.close()

    # Note: The quiz flow is advanced manually by the creator using /next.
    # This handler's only job is to record the answer and update the score.