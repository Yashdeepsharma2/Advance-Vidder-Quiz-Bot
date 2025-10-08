# Powered by Viddertech
import logging
import uuid
from telegram import Update, Poll
from telegram.ext import ContextTypes, ConversationHandler
from viddertech_quiz_bot.persistence import save_quizzes, save_user_stats

logger = logging.getLogger(__name__)

# States for ConversationHandler
TITLE, QUESTIONS = range(2)
SELECT_QUIZ_EDIT, EDIT_ACTION, GET_NEW_TITLE = range(10, 13)

# --- Quiz Creation ---

async def create_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to create a quiz."""
    await update.message.reply_text(
        "Let's create a quiz! First, what is the title of your quiz?"
    )
    context.user_data['quiz'] = {'title': '', 'questions': []}
    return TITLE


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the quiz title and asks for questions."""
    context.user_data['quiz']['title'] = update.message.text
    await update.message.reply_text(
        f"Great! The title of your quiz is '{context.user_data['quiz']['title']}'.\n\n"
        "Now, send me the questions in the correct format.\n"
        "Format:\n"
        "Question text\n"
        "Option 1\n"
        "Option 2\n"
        "Option 3\n"
        "Correct Option Number (e.g., 2)"
        "\n\nSend /done when you have added all questions."
    )
    return QUESTIONS


async def get_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the questions for the quiz."""
    try:
        lines = update.message.text.split('\n')
        question_text = lines[0]
        options = lines[1:-1]
        correct_option_index = int(lines[-1]) - 1

        if not (0 <= correct_option_index < len(options)):
            await update.message.reply_text("Invalid correct option number. Please try again.")
            return QUESTIONS

        question = {
            'text': question_text,
            'options': options,
            'correct': correct_option_index
        }
        context.user_data['quiz']['questions'].append(question)
        await update.message.reply_text("Question added! Send another question or type /done to finish.")
    except (ValueError, IndexError):
        await update.message.reply_text("Invalid format. Please follow the format:\n"
                                     "Question text\n"
                                     "Option 1\n"
                                     "Option 2\n"
                                     "...\n"
                                     "Correct Option Number")
    return QUESTIONS


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ends the conversation and saves the quiz."""
    quiz = context.user_data.get('quiz')
    if not quiz or not quiz['questions']:
        await update.message.reply_text("You haven't added any questions. Quiz creation cancelled.")
    else:
        user_id = update.effective_user.id
        if user_id not in context.bot_data['quizzes']:
            context.bot_data['quizzes'][user_id] = {}

        quiz_id = str(uuid.uuid4())
        context.bot_data['quizzes'][user_id][quiz_id] = quiz
        save_quizzes(context.bot_data['quizzes'])

        await update.message.reply_text(
            f"Quiz '{quiz['title']}' created successfully!\n"
            "You can now manage it with /myquizzes."
        )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the quiz creation process."""
    context.user_data.clear()
    await update.message.reply_text("Quiz creation has been cancelled.")
    return ConversationHandler.END

# --- Quiz Management ---

async def my_quizzes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a list of the user's created quizzes with shareable IDs."""
    user_id = update.effective_user.id
    if 'quizzes' not in context.bot_data or user_id not in context.bot_data['quizzes'] or not context.bot_data['quizzes'][user_id]:
        await update.message.reply_text("You haven't created any quizzes yet. Use /create to get started.")
        return

    user_quizzes = context.bot_data['quizzes'][user_id]
    message = "<b>Here are your quizzes:</b>\n\n"
    for quiz_id, quiz in user_quizzes.items():
        shareable_id = f"quiz_{user_id}_{quiz_id}"
        message += f"<b>Title:</b> {quiz['title']}\n"
        message += f"<b>Questions:</b> {len(quiz['questions'])}\n"
        message += f"<b>Share ID:</b> <code>{shareable_id}</code>\n"
        message += f"<b>Delete Command:</b> <code>/del {quiz_id}</code>\n\n"

    message += "Use <code>/quiz &lt;Share ID&gt;</code> to start a quiz.\n"
    message += "Use <code>/edit &lt;Share ID&gt;</code> to edit a quiz."
    await update.message.reply_html(message)


async def del_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes a user's quiz by its ID."""
    user_id = update.effective_user.id
    try:
        quiz_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Please provide a Quiz ID. Usage: /del <ID>")
        return

    if 'quizzes' in context.bot_data and user_id in context.bot_data['quizzes'] and quiz_id in context.bot_data['quizzes'][user_id]:
        removed_quiz = context.bot_data['quizzes'][user_id].pop(quiz_id)
        save_quizzes(context.bot_data['quizzes'])
        await update.message.reply_text(f"Successfully deleted quiz: '{removed_quiz['title']}'.")
    else:
        await update.message.reply_text("Invalid Quiz ID. Use /myquizzes to see your quizzes and their IDs.")

# --- Quiz Taking ---

async def play_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts a quiz in the chat."""
    if 'current_quiz' in context.chat_data:
        await update.message.reply_text("A quiz is already in progress in this chat.")
        return

    try:
        shareable_id = context.args[0]
        _, creator_id_str, quiz_id = shareable_id.split('_')
        creator_id = int(creator_id_str)
        quiz = context.bot_data['quizzes'][creator_id][quiz_id]
    except (IndexError, ValueError, KeyError):
        await update.message.reply_text("Invalid or expired Share ID. Please use a valid ID from /myquizzes.")
        return

    context.chat_data['current_quiz'] = {
        'quiz_data': quiz,
        'current_question': 0,
        'scores': {},
        'is_active': True,
        'creator_id': creator_id
    }

    await update.message.reply_text(f"Starting quiz: <b>{quiz['title']}</b>!", parse_mode='HTML')
    await send_next_question(update.effective_chat.id, context)


async def send_next_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the next question in the quiz as a poll, respecting speed controls."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session or not quiz_session.get('is_active', False) or quiz_session.get('is_paused', False):
        return

    question_index = quiz_session['current_question']
    quiz_data = quiz_session['quiz_data']

    if question_index >= len(quiz_data['questions']):
        await end_quiz(chat_id, context)
        return

    question = quiz_data['questions'][question_index]
    # Use the speed setting from the session, or default to 30 seconds
    open_period = quiz_session.get('open_period', 30)

    message = await context.bot.send_poll(
        chat_id=chat_id,
        question=question['text'],
        options=question['options'],
        type=Poll.QUIZ,
        correct_option_id=question['correct'],
        open_period=open_period,
        is_anonymous=False,
    )
    context.chat_data['current_poll_id'] = message.poll.id

# This is the single, corrected version of the function
async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles a user's answer to a quiz poll, scoring and tracking stats."""
    poll_answer = update.poll_answer
    if poll_answer.poll_id != context.chat_data.get('current_poll_id'):
        return

    user = poll_answer.user
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session: return

    question_index = quiz_session['current_question']
    question = quiz_session['quiz_data']['questions'][question_index]
    is_correct = poll_answer.option_ids and poll_answer.option_ids[0] == question['correct']

    # --- Stats Tracking ---
    if 'user_stats' not in context.bot_data:
        context.bot_data['user_stats'] = {}
    if user.id not in context.bot_data['user_stats']:
        context.bot_data['user_stats'][user.id] = {'quizzes_played': 0, 'correct_answers': 0, 'total_questions': 0}

    stats = context.bot_data['user_stats'][user.id]
    if question_index == 0:
        stats['quizzes_played'] += 1
    stats['total_questions'] += 1
    if is_correct:
        stats['correct_answers'] += 1
    save_user_stats(context.bot_data['user_stats'])

    # --- Scoring Logic ---
    if is_correct:
        if quiz_session.get('is_team_mode', False):
            user_team = next((name for name, data in context.chat_data.get('teams', {}).items() if user.id in data['members']), None)
            if user_team:
                if 'scores' not in quiz_session: quiz_session['scores'] = {}
                if user_team not in quiz_session['scores']: quiz_session['scores'][user_team] = {'score': 0, 'name': user_team}
                quiz_session['scores'][user_team]['score'] += 1
        else: # Individual scoring
            if 'scores' not in quiz_session: quiz_session['scores'] = {}
            if user.id not in quiz_session['scores']: quiz_session['scores'][user.id] = {'score': 0, 'name': user.full_name}
            quiz_session['scores'][user.id]['score'] += 1

        # Move to next question ONLY if answered correctly
        quiz_session['current_question'] += 1
        await send_next_question(poll_answer.chat_id, context)


async def end_quiz(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ends the quiz and displays the final scores."""
    quiz_session = context.chat_data.get('current_quiz')
    if not quiz_session: return

    scores = quiz_session.get('scores', {})
    is_team_mode = quiz_session.get('is_team_mode', False)

    if not scores:
        await context.bot.send_message(chat_id, "Quiz finished! No one participated.")
    else:
        sorted_scores = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)
        results_message = "<b>Quiz Finished! Final Scores:</b>\n\n"
        for entity_id, data in sorted_scores:
            results_message += f"🏆 {data['name']}: {data['score']}\n"
        await context.bot.send_message(chat_id, results_message, parse_mode='HTML')

    context.chat_data.pop('current_quiz', None)
    context.chat_data.pop('teams', None)


async def stop_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops the currently running quiz."""
    if 'current_quiz' not in context.chat_data:
        await update.message.reply_text("There is no quiz currently running in this chat.")
        return

    context.chat_data['current_quiz']['is_active'] = False
    await update.message.reply_text("The quiz has been stopped.")
    await end_quiz(update.effective_chat.id, context)