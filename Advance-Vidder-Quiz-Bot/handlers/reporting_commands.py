# Powered by Viddertech

import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from database.database import get_db
from database.models import Quiz, Response, User
from utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)
REPORT_DIR = "reports"

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates and sends an HTML report for a completed quiz."""
    try:
        quiz_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Please provide a Quiz ID. You can find this in /myquizzes.\nUsage: /report <quiz_id>")
        return

    user_id = update.effective_user.id
    db: Session = next(get_db())

    try:
        # 1. Verify user is the creator
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == user_id).first()
        if not quiz:
            await update.message.reply_text("Quiz not found, or you are not the creator.")
            return

        # 2. Aggregate results from the database
        # This query groups responses by user, counts correct answers, and joins with the User table for names.
        # A more complex query could also calculate negative marking. For now, we count correct answers.
        results = (
            db.query(
                Response.user_id,
                User.full_name,
                func.sum(case((Response.is_correct, 1), else_=0)).label("score")
            )
            .join(User, User.id == Response.user_id)
            .filter(Response.quiz_id == quiz_id)
            .group_by(Response.user_id, User.full_name)
            .order_by(func.sum(case((Response.is_correct, 1), else_=0)).desc())
            .all()
        )

        if not results:
            await update.message.reply_text("No one has participated in this quiz yet, so a report cannot be generated.")
            return

        await update.message.reply_text("Generating report, please wait...")

        # Convert SQLAlchemy results to the format the generator expects
        scores_dict = {user_id: {'name': name, 'score': score} for user_id, name, score in results}

        # 3. Generate HTML
        report_generator = ReportGenerator()
        html_content = report_generator.generate_html_report(quiz.title, scores_dict)

        # 4. Save to a temporary file
        os.makedirs(REPORT_DIR, exist_ok=True)
        report_path = os.path.join(REPORT_DIR, f"report_{quiz_id}.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 5. Send the file
        await update.message.reply_document(
            document=open(report_path, 'rb'),
            filename=f"Viddertech-Report-{quiz.title}.html",
            caption=f"Here is the detailed report for your quiz: '{quiz.title}'."
        )

    except Exception as e:
        logger.error(f"Failed to generate report for quiz {quiz_id}: {e}")
        await update.message.reply_text("An error occurred while generating the report.")
    finally:
        db.close()
        # 6. Clean up the file
        if 'report_path' in locals() and os.path.exists(report_path):
            os.remove(report_path)