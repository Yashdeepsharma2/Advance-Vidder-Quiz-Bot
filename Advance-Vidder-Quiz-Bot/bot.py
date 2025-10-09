# Powered by Viddertech

import logging
import config
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters, PollAnswerHandler
)

from database.database import init_db
from handlers import (
    basic_commands, quiz_commands, callbacks, poll_handler, auth_commands,
    quiz_control, assignment_commands, filter_commands, admin_commands, user_management
)

def main() -> None:
    """Start the Viddertech Advance Quiz Bot."""

    # --- Logging Setup ---
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=config.LOGGING_LEVEL
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot...")

    # --- Database Initialization ---
    init_db()

    # --- Telegram Bot Application Setup ---
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # --- Universal User Handler (runs first) ---
    application.add_handler(MessageHandler(filters.ALL, user_management.universal_user_handler), group=-1)

    # --- Conversation Handlers ---
    telelogin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("telelogin", auth_commands.telelogin_start)],
        states={
            auth_commands.PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_commands.get_phone_and_connect)],
            auth_commands.CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_commands.get_code_and_login)],
            auth_commands.PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_commands.get_password_and_login)],
        },
        fallbacks=[CommandHandler("cancel", auth_commands.telelogin_cancel)],
    )
    creation_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("create", quiz_commands.create_quiz_start),
            CallbackQueryHandler(quiz_commands.create_quiz_start, pattern="^create_quiz_start$")
        ],
        states={
            quiz_commands.GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_commands.get_quiz_title)],
            quiz_commands.GET_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_commands.get_quiz_question)],
        },
        fallbacks=[
            CommandHandler("done", quiz_commands.creation_done),
            CommandHandler("cancel", quiz_commands.creation_cancel)
        ],
    )
    assignment_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("assignment", assignment_commands.create_assignment_start)],
        states={
            assignment_commands.GET_A_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, assignment_commands.get_assignment_title)],
            assignment_commands.GET_A_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, assignment_commands.get_assignment_desc_and_save)],
        },
        fallbacks=[CommandHandler("cancel", assignment_commands.create_assignment_cancel)],
    )
    submit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("submit", assignment_commands.submit_assignment_start)],
        states={
            assignment_commands.SUBMIT_A_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, assignment_commands.get_submission_assignment_id)],
            assignment_commands.SUBMIT_A_WORK: [MessageHandler(filters.TEXT | filters.Document.ALL, assignment_commands.get_submission_work_and_save)],
        },
        fallbacks=[CommandHandler("cancel", assignment_commands.submit_assignment_cancel)],
    )

    application.add_handler(telelogin_conv_handler)
    application.add_handler(creation_conv_handler)
    application.add_handler(assignment_conv_handler)
    application.add_handler(submit_conv_handler)

    # --- Command Handlers ---
    # Basic Commands
    application.add_handler(CommandHandler("start", basic_commands.start))
    application.add_handler(CommandHandler("help", basic_commands.help_command))
    application.add_handler(CommandHandler("features", basic_commands.features_command))
    application.add_handler(CommandHandler("info", basic_commands.info_command))
    application.add_handler(CommandHandler("stats", basic_commands.stats_command))

    # Auth & Cloning Commands
    application.add_handler(CommandHandler("quiz", auth_commands.clone_quiz_command))
    application.add_handler(CommandHandler("logout", auth_commands.logout))

    # Quiz Management Commands
    application.add_handler(CommandHandler("myquizzes", quiz_commands.my_quizzes))

    # Quiz Control Commands
    application.add_handler(CommandHandler("pause", quiz_control.pause_command))
    application.add_handler(CommandHandler("resume", quiz_control.resume_command))
    application.add_handler(CommandHandler("stop", quiz_control.stop_command))
    application.add_handler(CommandHandler("fast", quiz_control.fast_command))
    application.add_handler(CommandHandler("slow", quiz_control.slow_command))
    application.add_handler(CommandHandler("normal", quiz_control.normal_command))
    application.add_handler(CommandHandler("next", quiz_control.next_command))

    # Assignment Commands
    application.add_handler(CommandHandler("view_submissions", assignment_commands.view_submissions_command))

    # Filter and Paid User Management Commands
    application.add_handler(CommandHandler("addfilter", filter_commands.add_filter_command))
    application.add_handler(CommandHandler("removefilter", filter_commands.remove_filter_command))
    application.add_handler(CommandHandler("clearfilters", filter_commands.clear_filters_command))
    application.add_handler(CommandHandler("listfilters", filter_commands.list_filters_command))
    application.add_handler(CommandHandler("add", filter_commands.add_paid_user_command))
    application.add_handler(CommandHandler("rem", filter_commands.remove_paid_user_command))
    application.add_handler(CommandHandler("remall", filter_commands.remove_all_paid_users_command))
    application.add_handler(CommandHandler("remove", filter_commands.temp_remove_command))
    application.add_handler(CommandHandler("clearlist", filter_commands.clear_temp_list_command))

    # Admin Commands
    application.add_handler(CommandHandler("post", admin_commands.post_command))
    application.add_handler(CommandHandler("stopcast", admin_commands.stopcast_command))
    application.add_handler(CommandHandler("ban", admin_commands.ban_command))


    # --- Other Handlers ---
    application.add_handler(PollAnswerHandler(poll_handler.handle_poll_answer))
    application.add_handler(CallbackQueryHandler(callbacks.handle_callback_query))

    # --- Start the Bot ---
    logger.info("Bot is polling for updates...")
    application.run_polling()

if __name__ == "__main__":
    main()