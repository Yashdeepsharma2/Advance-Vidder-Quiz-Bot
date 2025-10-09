# Powered by Viddertech

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from utils.keyboards import main_menu_keyboard
from database.database import get_db
from database.models import User, Quiz, Question
import config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    Greets the user and displays the main menu.
    """
    await update.message.reply_text(
        f"Welcome to the Viddertech Advance Quiz Bot, {update.effective_user.full_name}!",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the comprehensive help message with all commands."""
    help_text = """
*Viddertech Advance Quiz Bot - Command Reference*

*🎯 Basic Commands*
`/start` - Start the bot and show the main menu
`/help` - Get this comprehensive command help
`/features` - View all bot features
`/info` - About VidderTech and this bot
`/stats` - View bot and personal statistics

*📝 Quiz Management*
`/create` - Start creating a new quiz
`/myquizzes` - View your created quizzes with interactive controls
`/del <quiz_id>` - Delete a quiz (use from /myquizzes)
`/edit <quiz_id>` - Edit an existing quiz (use from /myquizzes)

*⚡ Quiz Playing & Control*
`/play <quiz_id>` - Start playing a quiz
`/next` - (Creator only) Move to the next question
`/pause` - (Creator only) Pause the current quiz
`/resume` - (Creator only) Resume a paused quiz
`/stop` - (Creator only) Stop the ongoing quiz and show results
`/fast` - (Creator only) Set question time to 15s
`/slow` - (Creator only) Set question time to 60s
`/normal` - (Creator only) Reset question time to default

*🔄 Content Import & Cloning*
`/quiz <@QuizBot_link>` - Clone a quiz from the official @QuizBot
`/telelogin` - Log in to your Telegram account to enable cloning
`/logout` - Log out of your Telegram account

*📝 Assignments*
`/assignment` - Create a new assignment for students
`/submit` - Submit your work for an assignment
`/view_submissions <assignment_id>` - View all submissions for an assignment

*🔧 Content Filtering*
`/addfilter <word>` - Add a word to your permanent filter list
`/removefilter <word>` - Remove a word from your filter list
`/listfilters` - Show all your filter words
`/clearfilters` - Clear your entire filter list
`/remove <word>` - Add a word to a temporary list for one-time extraction
`/clearlist` - Clear the temporary removal list

*👑 Admin Commands*
`/post <message>` - Broadcast a message to all bot users
`/stopcast` - Stop an ongoing broadcast
`/ban <user_id>` - Ban a user from the bot
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def features_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the detailed list of bot features."""
    features_text = """
*✨ Viddertech Advance Quiz Bot Features ✨*

*🎯 Core Quiz Features*
- **Smart Quiz Creation**: Use a simple text format with ✅ to mark answers.
- **Interactive Management**: Use buttons to Play, Edit, and Delete your quizzes.
- **Full Quiz Control**: As a creator, manually advance questions with `/next`, `/pause`, `/resume`, and `/stop` for a professional hosting experience.
- **Speed Control**: Dynamically change question timers with `/fast`, `/slow`, and `/normal`.

*🔄 Content Import & Integration*
- **QuizBot Cloning**: Provide a link from `@QuizBot` to clone an entire quiz to your account.
- **Secure Login**: Use `/telelogin` to securely connect your user account via Telethon for cloning.

*📝 Assignments & Submissions*
- **Create Assignments**: Use `/assignment` to create tasks for students.
- **Student Submissions**: Students can use `/submit` to send in their work as text or files.
- **View Submissions**: Creators can view all submissions for their assignments.

*🔧 Advanced Filtering & User Management*
- **Permanent Filters**: Set a personal list of words to always be filtered out of imported content.
- **Temporary Filters**: Use `/remove` to specify words to remove for a single session.
- **Paid User Access**: Grant specific users access to your quizzes with `/add`, `/rem`, and `/remall`.

*👑 Admin Capabilities*
- **Broadcasting**: Send messages to all users of the bot.
- **User Moderation**: Ban users from interacting with the bot.
    """
    await update.message.reply_text(features_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays information about the bot and Viddertech."""
    await update.message.reply_text(
        "*Viddertech Advance Quiz Bot*\n\n"
        "This bot is a powerful tool for creating, managing, and conducting quizzes.\n"
        "Developed with ❤️ by VidderTech.\n\n"
        "For more information, visit our website or contact support.",
        parse_mode='Markdown'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays bot and personal statistics."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    try:
        total_users = db.query(User).count()
        total_quizzes = db.query(Quiz).count()
        total_questions = db.query(Question).count()
        user_quizzes = db.query(Quiz).filter(Quiz.creator_id == user_id).count()

        stats_text = (
            "📊 *Bot Statistics*\n"
            f"- Total Users: {total_users}\n"
            f"- Total Quizzes Created: {total_quizzes}\n"
            f"- Total Questions in Database: {total_questions}\n\n"
            "📈 *Your Personal Statistics*\n"
            f"- Quizzes You've Created: {user_quizzes}\n"
        )
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    finally:
        db.close()