# Powered by Viddertech
import logging
import json
import os
import uuid
import openai
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from viddertech_quiz_bot.persistence import save_quizzes

logger = logging.getLogger(__name__)

# States for AI quiz generation
GET_TOPIC, GET_NUM_QUESTIONS, GET_DIFFICULTY = range(20, 23)

async def generate_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to generate a quiz with AI."""
    await update.message.reply_text(
        "Let's generate a quiz with AI! What topic should the quiz be about?"
    )
    context.user_data['ai_quiz_info'] = {}
    return GET_TOPIC

async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the topic and asks for the number of questions."""
    context.user_data['ai_quiz_info']['topic'] = update.message.text
    await update.message.reply_text("Got it. How many questions should there be? (e.g., 5, 10)")
    return GET_NUM_QUESTIONS

async def get_num_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the number of questions and asks for the difficulty."""
    try:
        num_questions = int(update.message.text)
        if not 1 <= num_questions <= 20:
            await update.message.reply_text("Please enter a number between 1 and 20.")
            return GET_NUM_QUESTIONS
        context.user_data['ai_quiz_info']['num_questions'] = num_questions
        await update.message.reply_text("What difficulty should the quiz be? (e.g., Easy, Medium, Hard)")
        return GET_DIFFICULTY
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return GET_NUM_QUESTIONS

async def get_difficulty_and_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the difficulty and triggers the AI generation."""
    context.user_data['ai_quiz_info']['difficulty'] = update.message.text
    info = context.user_data['ai_quiz_info']

    await update.message.reply_text(
        f"Generating a {info['difficulty']} quiz about '{info['topic']}' with {info['num_questions']} questions. This might take a moment..."
    )

    quiz = await generate_quiz_from_ai(info['topic'], info['num_questions'], info['difficulty'])

    if quiz:
        user_id = update.effective_user.id
        if 'quizzes' not in context.bot_data:
            context.bot_data['quizzes'] = {}
        if user_id not in context.bot_data['quizzes']:
            context.bot_data['quizzes'][user_id] = {}

        quiz_id = str(uuid.uuid4())
        context.bot_data['quizzes'][user_id][quiz_id] = quiz
        save_quizzes(context.bot_data['quizzes'])

        shareable_id = f"quiz_{user_id}_{quiz_id}"

        await update.message.reply_text(
            f"AI-generated quiz '{quiz['title']}' created successfully!\n"
            f"You can start it with the Share ID: <code>{shareable_id}</code>"
        )
    else:
        await update.message.reply_text("Sorry, I couldn't generate the quiz. Please try again later.")

    context.user_data.clear()
    return ConversationHandler.END


async def generate_quiz_from_ai(topic: str, num_questions: int, difficulty: str) -> dict | None:
    """Uses OpenAI API to generate quiz data."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        return None

    prompt = f"""
    Create a quiz about '{topic}'.
    The quiz should have {num_questions} questions and a difficulty level of '{difficulty}'.
    The quiz must have a creative title related to the topic.

    Provide the output in a single, minified JSON object with no markdown formatting.
    The JSON object must follow this structure:
    {{
      "title": "Quiz Title",
      "questions": [
        {{
          "text": "Question 1 text?",
          "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
          "correct": 0
        }},
        {{
          "text": "Question 2 text?",
          "options": ["Option A", "Option B", "Option C"],
          "correct": 2
        }}
      ]
    }}
    The 'correct' field is the 0-based index of the correct option in the 'options' array.
    """

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        quiz_json_str = response.choices[0].message['content']
        quiz_data = json.loads(quiz_json_str)
        if 'title' in quiz_data and 'questions' in quiz_data:
            return quiz_data
        else:
            logger.error(f"AI response is missing required fields: {quiz_json_str}")
            return None
    except Exception as e:
        logger.error(f"Error generating quiz from AI: {e}")
        return None

async def cancel_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the AI quiz generation process."""
    context.user_data.clear()
    await update.message.reply_text("AI quiz generation has been cancelled.")
    return ConversationHandler.END