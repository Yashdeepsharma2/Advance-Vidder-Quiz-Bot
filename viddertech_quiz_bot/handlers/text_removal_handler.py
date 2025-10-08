# Powered by Viddertech
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def get_removal_list(context: ContextTypes.DEFAULT_TYPE) -> list:
    """Safely retrieves the temporary removal list from user_data."""
    if 'removal_list' not in context.user_data:
        context.user_data['removal_list'] = []
    return context.user_data['removal_list']

async def remove_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds words to the temporary removal list for the current session."""
    if not context.args:
        await update.message.reply_text("Please provide the word(s) to remove. Usage: /remove word1 word2 ...")
        return

    removal_list = get_removal_list(context)
    added_words = []
    for word in context.args:
        if word not in removal_list:
            removal_list.append(word)
            added_words.append(word)

    if added_words:
        await update.message.reply_text(
            f"The following words will be removed during the next extraction: {', '.join(added_words)}\n"
            "This list will be cleared after the extraction is complete."
        )
    else:
        await update.message.reply_text("The specified words are already in the removal list.")

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the temporary removal list."""
    removal_list = get_removal_list(context)
    if not removal_list:
        await update.message.reply_text("The temporary removal list is already empty.")
        return

    context.user_data['removal_list'] = []
    await update.message.reply_text("The temporary removal list has been cleared.")