# Powered by Viddertech

import math
import uuid
import logging
import random
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from sqlalchemy.orm import Session

import config
from database.database import get_db
from database.models import User, Quiz, Question
from utils.keyboards import my_quizzes_keyboard, quiz_edit_keyboard, remove_question_keyboard, quiz_settings_keyboard

logger = logging.getLogger(__name__)

# --- Quiz Listing ---
# ... (existing my_quizzes)

# --- Quiz Creation Conversation ---
# ... (existing creation handler and functions)

# --- Quiz Editing Conversation ---
# ... (existing edit handler and functions)


# --- Quiz Playing Logic ---

async def send_live_leaderboard(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message with the current scores (leaderboard)."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session:
        return

    scores = quiz_session.get('scores', {})
    if not scores:
        await context.bot.send_message(chat_id, "No scores yet!")
        return

    sorted_scores = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)

    results_message = "📊 **Live Leaderboard**\n\n"
    for rank, (user_id, data) in enumerate(sorted_scores, 1):
        trophy = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**{rank}.**"
        results_message += f"{trophy} {data['name']}: {round(data['score'], 2)}\n"

    await context.bot.send_message(chat_id, results_message, parse_mode='Markdown')


async def start_quiz_session(update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_id: str):
    """Initializes a quiz session in context and sends the first question."""
    db: Session = next(get_db())
    try:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz or not quiz.questions:
            await update.effective_message.reply_text("This quiz could not be found or has no questions.")
            return
        question_ids = [q.id for q in quiz.questions]
        if quiz.quiz_mode == 'marathon':
            random.shuffle(question_ids)
        context.chat_data['current_quiz'] = {
            'quiz_id': quiz.id, 'quiz_title': quiz.title, 'quiz_mode': quiz.quiz_mode,
            'questions': question_ids, 'current_question_index': 0, 'scores': {},
            'is_active': True, 'is_paused': False, 'open_period': config.DEFAULT_QUESTION_TIME,
            'creator_id': quiz.creator_id
        }
        await send_question(update.effective_chat.id, context)
    finally:
        db.close()

async def send_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Sends the current question of the active quiz session, handling marathon mode."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session or not quiz_session.get('is_active') or quiz_session.get('is_paused'):
        return
    question_index = quiz_session['current_question_index']
    if question_index >= len(quiz_session['questions']):
        if quiz_session.get('quiz_mode') == 'marathon':
            await context.bot.send_message(chat_id, "🏁 Round complete! Shuffling questions for the next round...")
            random.shuffle(quiz_session['questions'])
            quiz_session['current_question_index'] = 0
            await send_question(chat_id, context)
            return
        else:
            await end_quiz_session(chat_id, context)
            return
    db: Session = next(get_db())
    try:
        question_id = quiz_session['questions'][question_index]
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            quiz_session['current_question_index'] += 1
            await send_question(chat_id, context)
            return
        open_period = quiz_session.get('open_period', config.DEFAULT_QUESTION_TIME)
        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=f"({question_index + 1}/{len(quiz_session['questions'])}) {question.text}",
            options=question.options,
            type='quiz', correct_option_id=question.correct_option_index,
            open_period=open_period, is_anonymous=False
        )
        context.chat_data['current_poll_id'] = message.poll.id
        context.chat_data['current_question_correct_id'] = question.correct_option_index
    finally:
        db.close()

async def end_quiz_session(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Calculates and displays the final quiz results, then cleans up."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session: return
    scores = quiz_session.get('scores', {})
    quiz_title = quiz_session.get('quiz_title', 'Quiz')
    if not scores:
        await context.bot.send_message(chat_id, f"🏁 Quiz '{quiz_title}' finished! No one participated.")
    else:
        sorted_scores = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)
        results_message = f"🏁 **Quiz Finished! Final Scores for '{quiz_title}':**\n\n"
        for rank, (user_id, data) in enumerate(sorted_scores, 1):
            trophy = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**{rank}.**"
            results_message += f"{trophy} {data['name']}: {round(data['score'], 2)}\n"
        await context.bot.send_message(chat_id, results_message, parse_mode='Markdown')
    context.chat_data.pop('current_quiz', None)
    context.chat_data.pop('current_poll_id', None)
    context.chat_data.pop('current_question_correct_id', None)

# --- DUMMY PLACEHOLDERS TO PREVENT ERRORS ---
# These will be removed once the file is complete.
async def my_quizzes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: pass
creation_conv_handler = ConversationHandler(entry_points=[], states={}, fallbacks=[])
edit_quiz_conv_handler = ConversationHandler(entry_points=[], states={}, fallbacks=[])