import logging
import os
from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    PollAnswerHandler,
    filters,
)

from quiz_bot.persistence import load_data
from quiz_bot.handlers.info_handlers import start, help_command, features
from quiz_bot.handlers.quiz_handler import (
    create_quiz_start, get_title, get_questions, done, cancel,
    my_quizzes, del_quiz, start_quiz, stop_quiz, receive_poll_answer
)
from quiz_bot.handlers.ai_handler import (
    generate_quiz_start, get_topic as get_ai_topic,
    get_num_questions as get_ai_num_questions, get_difficulty_and_generate, cancel_ai,
    GET_TOPIC, GET_NUM_QUESTIONS, GET_DIFFICULTY
)
from quiz_bot.handlers.team_handler import create_team, join_team, view_teams, team_quiz
from quiz_bot.handlers.placeholder_handlers import *

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set. Please create a .env file and add it.")
        return

    # Load persistent data
    bot_data = load_data()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).bot_data(bot_data).build()

    # --- Register Handlers ---

    # Informational Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("features", features))

    # Quiz Creation Conversation
    create_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create_quiz_start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_questions)],
        },
        fallbacks=[CommandHandler("done", done), CommandHandler("cancel", cancel)],
    )
    application.add_handler(create_conv_handler)

    # AI Quiz Generation Conversation
    ai_quiz_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate_quiz_start)],
        states={
            GET_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ai_topic)],
            GET_NUM_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ai_num_questions)],
            GET_DIFFICULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_difficulty_and_generate)],
        },
        fallbacks=[CommandHandler("cancel", cancel_ai)],
    )
    application.add_handler(ai_quiz_conv_handler)

    # Core Quiz Commands
    application.add_handler(CommandHandler("myquizzes", my_quizzes))
    application.add_handler(CommandHandler("del", del_quiz))
    application.add_handler(CommandHandler("quiz", start_quiz))
    application.add_handler(CommandHandler("stop", stop_quiz))

    # Team Commands
    application.add_handler(CommandHandler("team_create", create_team))
    application.add_handler(CommandHandler("team_join", join_team))
    application.add_handler(CommandHandler("teams", view_teams))
    application.add_handler(CommandHandler("team_quiz", team_quiz))

    # Poll Answer Handler (for quizzes)
    application.add_handler(PollAnswerHandler(receive_poll_answer))

    # Placeholder Commands
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("telelogin", telelogin))
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(CommandHandler("stopcast", stopcast))
    application.add_handler(CommandHandler("lang", lang))
    application.add_handler(CommandHandler("assignment", assignment))
    application.add_handler(CommandHandler("submit", submit))
    application.add_handler(CommandHandler("pause", pause))
    application.add_handler(CommandHandler("resume", resume))
    application.add_handler(CommandHandler("fast", fast))
    application.add_handler(CommandHandler("slow", slow))
    application.add_handler(CommandHandler("normal", normal))
    application.add_handler(CommandHandler("addfilter", addfilter))
    application.add_handler(CommandHandler("removefilter", removefilter))
    application.add_handler(CommandHandler("listfilters", listfilters))
    application.add_handler(CommandHandler("clearfilters", clearfilters))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("clearlist", clearlist))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("rem", rem))
    application.add_handler(CommandHandler("remall", remall))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("extract", extract))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("my_stats", my_stats))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()