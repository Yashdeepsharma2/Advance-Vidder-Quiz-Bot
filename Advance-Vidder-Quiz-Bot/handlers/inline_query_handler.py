# Powered by Viddertech

import logging
import uuid
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.database import get_db
from database.models import Quiz

logger = logging.getLogger(__name__)

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles inline queries.
    Allows users to search for their created quizzes and share them in any chat.
    """
    query = update.inline_query.query
    user_id = update.inline_query.from_user.id
    db: Session = next(get_db())

    results = []

    try:
        # Search for quizzes created by the user that match the query
        quizzes_query = db.query(Quiz).filter(
            Quiz.creator_id == user_id,
            or_(
                Quiz.title.ilike(f"%{query}%"),
                # You could also search descriptions if they existed
            )
        ).limit(20) # Limit to a reasonable number of results

        for quiz in quizzes_query.all():
            # For each quiz, create a result article

            # The message that will be sent when a user clicks the result
            message_content = InputTextMessageContent(
                f"I've shared the quiz: **{quiz.title}**!\n\n"
                "Press the button below to start playing.",
                parse_mode='Markdown'
            )

            # The interactive button that goes with the message
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"▶️ Play '{quiz.title}'", callback_data=f"play_{quiz.id}")]
            ])

            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"Share Quiz: {quiz.title}",
                    description=f"Mode: {quiz.quiz_mode.capitalize()} | Questions: {len(quiz.questions)}",
                    input_message_content=message_content,
                    reply_markup=reply_markup
                )
            )

    except Exception as e:
        logger.error(f"Error processing inline query for user {user_id}: {e}")
    finally:
        db.close()

    await update.inline_query.answer(results, cache_time=10)