# Powered by Viddertech

import math
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

import config
from database.database import get_db
from database.models import User, Quiz
from utils.keyboards import my_quizzes_keyboard

async def my_quizzes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a paginated list of the user's created quizzes with interactive buttons."""
    db: Session = next(get_db())
    user_id = update.effective_user.id

    # This is triggered by a command, so we start at page 0
    page = 0

    try:
        quizzes_query = db.query(Quiz).filter(Quiz.creator_id == user_id)
        total_quizzes = quizzes_query.count()
        total_pages = math.ceil(total_quizzes / config.QUIZZES_PER_PAGE)

        offset = page * config.QUIZZES_PER_PAGE
        user_quizzes = quizzes_query.offset(offset).limit(config.QUIZZES_PER_PAGE).all()

        if not user_quizzes:
            await update.message.reply_text("You haven't created any quizzes yet. Use the 'Create New Quiz' button to start!")
            return

        reply_markup = my_quizzes_keyboard(user_quizzes, page, total_pages)
        await update.message.reply_text("Here are your quizzes:", reply_markup=reply_markup)

    finally:
        db.close()


# --- Quiz Creation Conversation ---
GET_TITLE, GET_QUESTIONS = range(2)

async def create_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the quiz creation conversation.
    This can be triggered by a command or a callback.
    """
    message_text = "Let's create a new quiz!\n\nFirst, what is the title of your quiz?"

    # Check if this was triggered by a callback query
    query = update.callback_query
    if query:
        await query.edit_message_text(text=message_text)
    else:
        await update.message.reply_text(text=message_text)

    context.user_data['new_quiz'] = {'questions': []}
    return GET_TITLE

async def get_quiz_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the quiz title and asks for the first question."""
    title = update.message.text
    context.user_data['new_quiz']['title'] = title

    await update.message.reply_text(
        f"Great! The title is '{title}'.\n\n"
        "Now, send me the first question in the specified format:\n\n"
        "```\n"
        "What is the capital of France?\n"
        "A) London\n"
        "B) Berlin\n"
        "C) Paris ✅\n"
        "D) Madrid\n"
        "```\n\n"
        "Use the ✅ emoji to mark the correct answer. "
        "Send /done when you have added all your questions, or /cancel to stop."
    )
    return GET_QUESTIONS

async def get_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses a question, adds it to the quiz, and asks for the next one."""
    question_text = update.message.text
    lines = question_text.strip().split('\n')

    if len(lines) < 2:
        await update.message.reply_text("Invalid format. Please provide a question and at least one option.")
        return GET_QUESTIONS

    question = lines[0]
    options = []
    correct_option_index = None

    for i, line in enumerate(lines[1:]):
        if '✅' in line:
            correct_option_index = i
            options.append(line.replace('✅', '').strip())
        else:
            options.append(line.strip())

    if correct_option_index is None:
        await update.message.reply_text("Invalid format. You must mark one option as correct with a ✅.")
        return GET_QUESTIONS

    context.user_data['new_quiz']['questions'].append({
        'text': question,
        'options': options,
        'correct': correct_option_index
    })

    await update.message.reply_text("Question added! Send another question, or type /done to finish.")
    return GET_QUESTIONS


async def creation_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the completed quiz to the database."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    new_quiz_data = context.user_data.get('new_quiz')

    if not new_quiz_data or not new_quiz_data.get('questions'):
        await update.message.reply_text("You haven't added any questions. Quiz creation cancelled.")
    else:
        try:
            new_quiz = Quiz(
                id=str(uuid.uuid4()),
                title=new_quiz_data['title'],
                creator_id=user_id,
                questions=[Question(text=q['text'], options=q['options'], correct_option_index=q['correct']) for q in new_quiz_data['questions']]
            )
            db.add(new_quiz)
            db.commit()
            await update.message.reply_text(f"Quiz '{new_quiz.title}' created successfully!")
        except Exception as e:
            logger.error(f"Error saving quiz to DB: {e}")
            await update.message.reply_text("An error occurred while saving your quiz. Please try again.")
        finally:
            db.close()

    context.user_data.pop('new_quiz', None)
    return ConversationHandler.END


async def creation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the quiz creation process."""
    context.user_data.pop('new_quiz', None)
    await update.message.reply_text("Quiz creation cancelled.")
    return ConversationHandler.END


# --- Quiz Playing Logic ---

async def start_quiz_session(update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_id: str):
    """Initializes a quiz session in context and sends the first question."""
    db: Session = next(get_db())
    try:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz or not quiz.questions:
            await update.effective_message.reply_text("This quiz could not be found or has no questions.")
            return

        # TODO: Add logic here to check for paid quizzes and user access

        context.chat_data['current_quiz'] = {
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'questions': [q.id for q in quiz.questions], # Store only IDs
            'current_question_index': 0,
            'scores': {},
            'is_active': True,
            'is_paused': False,
            'open_period': config.DEFAULT_QUESTION_TIME
        }

        await send_question(update.effective_chat.id, context)

    finally:
        db.close()

async def end_quiz_session(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Calculates and displays the final quiz results, then cleans up."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session:
        return

    scores = quiz_session.get('scores', {})
    quiz_title = quiz_session.get('quiz_title', 'Quiz')

    if not scores:
        await context.bot.send_message(chat_id, f"🏁 Quiz '{quiz_title}' finished! No one participated.")
    else:
        sorted_scores = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)

        results_message = f"🏁 **Quiz Finished! Final Scores for '{quiz_title}':**\n\n"
        for rank, (user_id, data) in enumerate(sorted_scores, 1):
            trophy = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**{rank}.**"
            results_message += f"{trophy} {data['name']}: {data['score']}\n"

        await context.bot.send_message(chat_id, results_message, parse_mode='Markdown')

    # Clean up session data
    context.chat_data.pop('current_quiz', None)
    context.chat_data.pop('current_poll_id', None)
    context.chat_data.pop('current_question_correct_id', None)


async def send_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Sends the current question of the active quiz session, respecting pause and speed controls."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session or not quiz_session.get('is_active') or quiz_session.get('is_paused'):
        return

    db: Session = next(get_db())
    try:
        question_index = quiz_session['current_question_index']
        if question_index >= len(quiz_session['questions']):
            await end_quiz_session(chat_id, context)
            return

        question_id = quiz_session['questions'][question_index]
        question = db.query(Question).filter(Question.id == question_id).first()

        if not question:
            quiz_session['current_question_index'] += 1
            await send_question(chat_id, context)
            return

        # Use the open_period from the session, which is now controlled by /fast, /slow, /normal
        open_period = quiz_session.get('open_period', config.DEFAULT_QUESTION_TIME)

        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question.text,
            options=question.options,
            type='quiz',
            correct_option_id=question.correct_option_index,
            open_period=open_period,
            is_anonymous=False,
            explanation=f"Answer to: {question.text}"
        )
        context.chat_data['current_poll_id'] = message.poll.id
        context.chat_data['current_question_correct_id'] = question.correct_option_index
    finally:
        db.close()