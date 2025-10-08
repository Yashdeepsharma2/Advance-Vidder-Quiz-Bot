# Powered by Viddertech
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

from viddertech_quiz_bot.persistence import load_data
from viddertech_quiz_bot.handlers.info_handlers import (
    start, help_command, features, get_creator_info, my_stats
)
from viddertech_quiz_bot.handlers.quiz_handler import (
    create_quiz_start, get_title, get_questions, done, cancel,
    my_quizzes, del_quiz, play_quiz, stop_quiz, receive_poll_answer
)
from viddertech_quiz_bot.handlers.ai_handler import (
    generate_quiz_start, get_topic as get_ai_topic,
    get_num_questions as get_ai_num_questions, get_difficulty_and_generate, cancel_ai,
    GET_TOPIC, GET_NUM_QUESTIONS, GET_DIFFICULTY
)
from viddertech_quiz_bot.handlers.team_handler import create_team, join_team, view_teams, team_quiz
from viddertech_quiz_bot.handlers.filter_handler import add_filter, remove_filter, list_filters, clear_filters
from viddertech_quiz_bot.handlers.extract_handler import (
    extract_start, extract_poll, extract_done, name_and_save_quiz, extract_cancel,
    EXTRACTING, NAMING
)
from viddertech_quiz_bot.handlers.telethon_handler import (
    telelogin_start, get_api_id, get_api_hash, get_phone_and_connect,
    get_code_and_login, get_password_and_login, telelogin_cancel, logout, clone_start,
    API_ID, API_HASH, PHONE, CODE, PASSWORD
)
from viddertech_quiz_bot.handlers.quiz_control_handler import (
    pause_quiz, resume_quiz, fast_quiz, slow_quiz, normal_quiz
)
from viddertech_quiz_bot.handlers.assignment_handler import (
    assignment_start, get_assignment_title, get_assignment_desc_and_save, assignment_cancel,
    submit_start, get_submission_id, get_submission_work_and_save, submit_cancel,
    view_submissions,
    CREATE_A_TITLE, CREATE_A_DESC, SUBMIT_A_ID, SUBMIT_A_WORK
)
from viddertech_quiz_bot.handlers.admin_handler import (
    ban_user, post_message, stop_cast, add_paid_user, remove_paid_user, remove_all_paid_users
)
from viddertech_quiz_bot.handlers.user_tracker_handler import track_users
from viddertech_quiz_bot.handlers.text_removal_handler import remove_words, clear_list
from viddertech_quiz_bot.handlers.placeholder_handler import login, lang

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

    # User tracker and ban checker (runs first)
    application.add_handler(MessageHandler(filters.ALL, track_users), group=-1)

    # Informational Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("features", features))
    application.add_handler(CommandHandler("info", get_creator_info))
    application.add_handler(CommandHandler("my_stats", my_stats))

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

    # Poll Extraction Conversation
    extract_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("extract", extract_start)],
        states={
            EXTRACTING: [MessageHandler(filters.POLL, extract_poll)],
            NAMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_and_save_quiz)],
        },
        fallbacks=[CommandHandler("done", extract_done), CommandHandler("cancel", extract_cancel)],
    )
    application.add_handler(extract_conv_handler)

    # Telethon Login Conversation
    telelogin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("telelogin", telelogin_start)],
        states={
            API_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_id)],
            API_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_hash)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_and_connect)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code_and_login)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password_and_login)],
        },
        fallbacks=[CommandHandler("cancel", telelogin_cancel)],
        conversation_timeout=300
    )
    application.add_handler(telelogin_conv_handler)

    # Core Quiz Commands
    application.add_handler(CommandHandler("myquizzes", my_quizzes))
    application.add_handler(CommandHandler("del", del_quiz))
    application.add_handler(CommandHandler("quiz", clone_start)) # For cloning
    application.add_handler(CommandHandler("play", play_quiz))   # For taking a quiz
    application.add_handler(CommandHandler("stop", stop_quiz))

    # Team Commands
    application.add_handler(CommandHandler("team_create", create_team))
    application.add_handler(CommandHandler("team_join", join_team))
    application.add_handler(CommandHandler("teams", view_teams))
    application.add_handler(CommandHandler("team_quiz", team_quiz))

    # Filter Commands
    application.add_handler(CommandHandler("addfilter", add_filter))
    application.add_handler(CommandHandler("removefilter", remove_filter))
    application.add_handler(CommandHandler("listfilters", list_filters))
    application.add_handler(CommandHandler("clearfilters", clear_filters))
    application.add_handler(CommandHandler("remove", remove_words))
    application.add_handler(CommandHandler("clearlist", clear_list))

    # Poll Answer Handler (for quizzes)
    application.add_handler(PollAnswerHandler(receive_poll_answer))

    # Quiz Control Commands
    application.add_handler(CommandHandler("pause", pause_quiz))
    application.add_handler(CommandHandler("resume", resume_quiz))
    application.add_handler(CommandHandler("fast", fast_quiz))
    application.add_handler(CommandHandler("slow", slow_quiz))
    application.add_handler(CommandHandler("normal", normal_quiz))

    # Assignment Conversation Handlers
    assignment_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("assignment", assignment_start)],
        states={
            CREATE_A_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_assignment_title)],
            CREATE_A_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_assignment_desc_and_save)],
        },
        fallbacks=[CommandHandler("cancel", assignment_cancel)],
    )
    application.add_handler(assignment_conv_handler)

    submit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("submit", submit_start)],
        states={
            SUBMIT_A_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_submission_id)],
            SUBMIT_A_WORK: [MessageHandler(filters.TEXT | filters.Document.ALL, get_submission_work_and_save)],
        },
        fallbacks=[CommandHandler("cancel", submit_cancel)],
    )
    application.add_handler(submit_conv_handler)

    application.add_handler(CommandHandler("view_submissions", view_submissions))

    # Admin Commands
    application.add_handler(CommandHandler("post", post_message))
    application.add_handler(CommandHandler("stopcast", stop_cast))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("add", add_paid_user))
    application.add_handler(CommandHandler("rem", remove_paid_user))
    application.add_handler(CommandHandler("remall", remove_all_paid_users))

    # Remaining Placeholder Commands
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("lang", lang))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()