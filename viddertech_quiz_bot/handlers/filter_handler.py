# Powered by Viddertech
import logging
from telegram import Update
from telegram.ext import ContextTypes
from viddertech_quiz_bot.persistence import save_user_data

logger = logging.getLogger(__name__)

def get_user_filters(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> list:
    """Safely retrieves the filter list for a user."""
    if 'user_data' not in context.bot_data:
        context.bot_data['user_data'] = {}
    if user_id not in context.bot_data['user_data']:
        context.bot_data['user_data'][user_id] = {}
    if 'filters' not in context.bot_data['user_data'][user_id]:
        context.bot_data['user_data'][user_id]['filters'] = []
    return context.bot_data['user_data'][user_id]['filters']

async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds one or more words to the user's filter list."""
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Please provide the word(s) to filter. Usage: /addfilter word1 word2 ...")
        return

    filters = get_user_filters(context, user_id)
    added_words = []
    for word in context.args:
        if word.lower() not in filters:
            filters.append(word.lower())
            added_words.append(word)

    if added_words:
        save_user_data(context.bot_data['user_data'])
        await update.message.reply_text(f"Added to filter list: {', '.join(added_words)}")
    else:
        await update.message.reply_text("The specified words are already in your filter list.")

async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes one or more words from the user's filter list."""
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Please provide the word(s) to remove. Usage: /removefilter word1 word2 ...")
        return

    filters = get_user_filters(context, user_id)
    removed_words = []
    for word in context.args:
        if word.lower() in filters:
            filters.remove(word.lower())
            removed_words.append(word)

    if removed_words:
        save_user_data(context.bot_data['user_data'])
        await update.message.reply_text(f"Removed from filter list: {', '.join(removed_words)}")
    else:
        await update.message.reply_text("Could not find the specified words in your filter list.")

async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's current filter list."""
    user_id = update.effective_user.id
    filters = get_user_filters(context, user_id)
    if not filters:
        await update.message.reply_text("Your filter list is empty. Use /addfilter to add words.")
    else:
        message = "<b>Your current filter words:</b>\n\n"
        message += "\n".join([f"- <code>{word}</code>" for word in filters])
        await update.message.reply_html(message)

async def clear_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the user's entire filter list."""
    user_id = update.effective_user.id
    filters = get_user_filters(context, user_id)
    if not filters:
        await update.message.reply_text("Your filter list is already empty.")
        return

    context.bot_data['user_data'][user_id]['filters'] = []
    save_user_data(context.bot_data['user_data'])
    await update.message.reply_text("Your filter list has been cleared.")