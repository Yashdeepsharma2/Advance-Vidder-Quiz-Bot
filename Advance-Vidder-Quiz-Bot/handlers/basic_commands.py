# Powered by Viddertech

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from utils.keyboards import main_menu_keyboard
from database.database import get_db
from database.models import User, Quiz, Question, Response
import config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and displays the main menu."""
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
`/stats` - View your personal performance dashboard
`/leaderboard` - View the global top 10 players
`/report <quiz_id>` - Get a detailed HTML report for a quiz you created

*📝 Quiz Management*
`/myquizzes` - View your created quizzes with interactive controls
`/create` - Start creating a new quiz (Standard or Marathon)
`/bulkcreate` - Create a quiz from a large block of text
`/del <quiz_id>` - Delete a quiz (use from /myquizzes)
`/edit <quiz_id>` - Edit a quiz's title, questions, and settings

*🔄 Content Import & Cloning*
`/extract` - Create a quiz by forwarding polls
`/ocr` - Create a quiz by uploading a PDF or image
`/quiztxt` - Create a quiz from a web article URL
`/quiz <@QuizBot_link>` - Clone a quiz from the official @QuizBot
`/telelogin` - Log in to your Telegram account to enable cloning
`/logout` - Log out of your Telegram account

*⚡ Quiz Playing & Control*
`/pause` - (Creator only) Pause the current quiz
`/resume` - (Creator only) Resume a paused quiz
`/stop` - (Creator only) Stop the ongoing quiz and show results
`/next` - (Creator only) Show live scores and move to the next question
`/fast` / `/slow` / `/normal` - (Creator only) Adjust question timers

*📝 Assignments*
`/assignment` - Create a new assignment for students
`/submit` - Submit your work for an assignment
`/view_submissions <assignment_id>` - View all submissions

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
- **Advanced Quiz Modes**: Create Standard, Marathon, or Sectional quizzes.
- **Interactive Management**: Use buttons to Play, Edit, and Delete your quizzes.
- **Full Quiz Control**: Manually advance questions with `/next`, `/pause`, `/resume`, and `/stop`.
- **Speed Control**: Dynamically change question timers with `/fast`, `/slow`, and `/normal`.
- **Negative Marking**: Configure point deductions for wrong answers on a per-quiz basis.

*🔄 Content Import & Integration*
- **QuizBot Cloning**: Provide a link from `@QuizBot` to clone an entire quiz to your account.
- **Poll Extraction**: Create a quiz by forwarding polls from any source.
- **Web Scraper**: Generate a quiz directly from a Wikipedia, BBC, or other article URL with `/quiztxt`.
- **OCR Support**: Upload a PDF or image, and the bot will extract the text for you with `/ocr`.
- **Bulk Creation**: Paste a large, pre-formatted text block to create many questions at once with `/bulkcreate`.

*📝 Assignments & Reporting*
- **Assignment System**: Create assignments, receive student submissions (text or file), and view them.
- **HTML Reports**: Generate a beautiful, shareable HTML report for any quiz you've created with `/report`.

*🔧 Advanced Filtering & User Management*
- **Permanent & Temporary Filters**: Manage lists of words to automatically remove from imported content.
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
    """Acts as a personal performance analytics dashboard."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    try:
        user_responses = db.query(Response).filter(Response.user_id == user_id).all()
        quizzes_played = db.query(Response.quiz_id).filter(Response.user_id == user_id).distinct().count()
        total_questions_answered = len(user_responses)
        correct_answers = sum(1 for r in user_responses if r.is_correct)
        accuracy = (correct_answers / total_questions_answered * 100) if total_questions_answered > 0 else 0

        all_user_scores = db.query(Response.user_id).group_by(Response.user_id).order_by(func.sum(case((Response.is_correct, 1), else_=0)).desc()).all()
        user_rank = next((i for i, (uid,) in enumerate(all_user_scores, 1) if uid == user_id), None)
        total_users_with_scores = len(all_user_scores)

        total_users = db.query(User).count()
        total_quizzes = db.query(Quiz).count()

        stats_text = (
            f"📊 **Your Personal Analytics Dashboard**\n\n"
            f"🔹 **Quizzes Played:** {quizzes_played}\n"
            f"🔹 **Questions Answered:** {total_questions_answered}\n"
            f"🔹 **Correct Answers:** {correct_answers}\n"
            f"🔹 **Overall Accuracy:** {accuracy:.2f}%\n"
            f"🔹 **Global Rank:** {user_rank}/{total_users_with_scores if user_rank else 'N/A'}\n\n"
            f"🤖 **Bot-Wide Stats**\n"
            f"- Total Users: {total_users}\n"
            f"- Total Quizzes: {total_quizzes}"
        )
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    finally:
        db.close()

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the global leaderboard for the top 10 users."""
    db: Session = next(get_db())
    try:
        top_users = (
            db.query(
                User.full_name,
                func.sum(case((Response.is_correct, 1), else_=0)).label("total_score")
            )
            .join(Response, User.id == Response.user_id)
            .group_by(User.full_name)
            .order_by(func.sum(case((Response.is_correct, 1), else_=0)).desc())
            .limit(10)
            .all()
        )
        if not top_users:
            await update.message.reply_text("No scores recorded yet. Play some quizzes to get on the leaderboard!")
            return
        leaderboard_text = "🏆 **Global Leaderboard (Top 10)** 🏆\n\n"
        for rank, (name, score) in enumerate(top_users, 1):
            trophy = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**{rank}.**"
            leaderboard_text += f"{trophy} {name}: {score} correct answers\n"
        await update.message.reply_text(leaderboard_text, parse_mode='Markdown')
    finally:
        db.close()