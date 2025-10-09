# Powered by Viddertech

import logging
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Quiz, Question
from integrations.web_scraper import WebScraper
from integrations.ai_generator import AIGenerator # Assuming we refactor AI logic into its own class

logger = logging.getLogger(__name__)

# Conversation states
AWAIT_URL, AWAIT_NUM_QUESTIONS = range(2)

async def quiztxt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the process of creating a quiz from a web article."""
    await update.message.reply_text(
        "Please send the URL of the article you want to create a quiz from.\n"
        "Supported sites include Wikipedia, BBC, Britannica, and other major news/article sites."
    )
    return AWAIT_URL

async def get_url_and_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives a URL, scrapes it, and asks for the number of questions."""
    url = update.message.text
    if not url.startswith('http'):
        await update.message.reply_text("That doesn't look like a valid URL. Please try again.")
        return AWAIT_URL

    await update.message.reply_text("🔎 Scraping article... this may take a moment.")

    try:
        scraper = WebScraper()
        article_text = scraper.scrape_article_text(url)

        if not article_text or len(article_text) < 200: # Basic check for meaningful content
            await update.message.reply_text("Could not extract enough meaningful text from that URL. The page might be unsupported or empty.")
            return ConversationHandler.END

        context.user_data['scraped_text'] = article_text
        await update.message.reply_text(
            f"✅ Article scraped successfully ({len(article_text)} characters found).\n\n"
            "Now, how many questions should I generate from this text? (e.g., 5, 10)"
        )
        return AWAIT_NUM_QUESTIONS

    except Exception as e:
        await update.message.reply_text(f"An error occurred while scraping: {e}")
        return ConversationHandler.END

async def generate_quiz_from_scraped_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generates a quiz from the scraped text using the AI engine."""
    try:
        num_questions = int(update.message.text)
        if not 1 <= num_questions <= 15:
            await update.message.reply_text("Please enter a number between 1 and 15.")
            return AWAIT_NUM_QUESTIONS
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return AWAIT_NUM_QUESTIONS

    await update.message.reply_text("🤖 Generating quiz with AI... this may take a moment.")

    scraped_text = context.user_data.get('scraped_text')
    user_id = update.effective_user.id

    try:
        # We need to refactor the AI generation logic into a reusable class/function
        # For now, we'll placeholder this call.
        # ai_generator = AIGenerator()
        # quiz_data = await ai_generator.create_quiz_from_text(scraped_text, num_questions)

        # --- Placeholder for AI call ---
        # This part will be replaced when AIGenerator is created.
        from integrations.ai_generator import generate_quiz_from_text_content
        quiz_data = await generate_quiz_from_text_content(scraped_text, num_questions)
        # --- End Placeholder ---

        if not quiz_data or not quiz_data.get('questions'):
            await update.message.reply_text("The AI could not generate a quiz from the article's content. The text might be too complex or not structured like an article.")
            return ConversationHandler.END

        # Save the new quiz to the database
        db: Session = next(get_db())
        try:
            new_quiz = Quiz(
                id=str(uuid.uuid4()),
                title=quiz_data['title'],
                creator_id=user_id,
                quiz_mode='standard',
                questions=[Question(text=q['text'], options=q['options'], correct_option_index=q['correct']) for q in quiz_data['questions']]
            )
            db.add(new_quiz)
            db.commit()
            await update.message.reply_text(f"✅ Quiz '{new_quiz.title}' has been created from the article!")
        except Exception as e:
            logger.error(f"Error saving web-scraped quiz to DB: {e}")
            await update.message.reply_text("An error occurred while saving the generated quiz.")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Quiz generation from text failed: {e}")
        await update.message.reply_text(f"An error occurred during quiz generation: {e}")
    finally:
        context.user_data.clear()

    return ConversationHandler.END

async def quiztxt_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the web scraping process."""
    context.user_data.clear()
    await update.message.reply_text("Process cancelled.")
    return ConversationHandler.END

quiztxt_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("quiztxt", quiztxt_start)],
    states={
        AWAIT_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_url_and_scrape)],
        AWAIT_NUM_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_quiz_from_scraped_text)],
    },
    fallbacks=[CommandHandler("cancel", quiztxt_cancel)],
)