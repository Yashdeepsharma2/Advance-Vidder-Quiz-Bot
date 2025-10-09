# Powered by Viddertech

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import delete

from database.database import get_db
from database.models import User, Filter, Quiz, PaidUser

logger = logging.getLogger(__name__)

# --- Permanent Filter Commands ---

async def add_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds one or more words to the user's permanent filter list."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    words_to_add = context.args

    if not words_to_add:
        await update.message.reply_text("Usage: /addfilter word1 word2 ...")
        return

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user: # Should not happen if /start is used, but as a fallback
            user = User(id=user_id, full_name=update.effective_user.full_name, username=update.effective_user.username)
            db.add(user)

        existing_filters = {f.word for f in user.filters}
        added_count = 0
        for word in words_to_add:
            if word.lower() not in existing_filters:
                new_filter = Filter(user_id=user_id, word=word.lower())
                db.add(new_filter)
                added_count += 1

        if added_count > 0:
            db.commit()
            await update.message.reply_text(f"✅ Successfully added {added_count} word(s) to your filter list.")
        else:
            await update.message.reply_text("All specified words are already in your filter list.")
    finally:
        db.close()

async def remove_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes one or more words from the user's permanent filter list."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    words_to_remove = [word.lower() for word in context.args]

    if not words_to_remove:
        await update.message.reply_text("Usage: /removefilter word1 word2 ...")
        return

    try:
        stmt = delete(Filter).where(Filter.user_id == user_id, Filter.word.in_(words_to_remove))
        result = db.execute(stmt)
        db.commit()

        if result.rowcount > 0:
            await update.message.reply_text(f"✅ Successfully removed {result.rowcount} word(s) from your filter list.")
        else:
            await update.message.reply_text("None of the specified words were found in your filter list.")
    finally:
        db.close()

async def clear_filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the user's entire permanent filter list."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    try:
        stmt = delete(Filter).where(Filter.user_id == user_id)
        result = db.execute(stmt)
        db.commit()
        if result.rowcount > 0:
            await update.message.reply_text("✅ Your entire filter list has been cleared.")
        else:
            await update.message.reply_text("Your filter list was already empty.")
    finally:
        db.close()

async def list_filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's current filter list."""
    db: Session = next(get_db())
    user_id = update.effective_user.id
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.filters:
            await update.message.reply_text("Your filter list is empty.")
            return

        filter_list = "\n".join([f"- `{f.word}`" for f in user.filters])
        await update.message.reply_text(f"**Your Permanent Filter Words:**\n{filter_list}", parse_mode='Markdown')
    finally:
        db.close()

# --- Paid User Management Commands ---

async def add_paid_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a user to a quiz's paid access list."""
    try:
        quiz_id, user_id_to_add_str = context.args
        user_id_to_add = int(user_id_to_add_str)
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: /add <quiz_id> <user_id>")
        return

    db: Session = next(get_db())
    creator_id = update.effective_user.id
    try:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == creator_id).first()
        if not quiz:
            await update.message.reply_text("Quiz not found or you are not the creator.")
            return

        if not db.query(User).filter(User.id == user_id_to_add).first():
            await update.message.reply_text(f"User with ID {user_id_to_add} has not used the bot yet.")
            return

        if db.query(PaidUser).filter(PaidUser.quiz_id == quiz_id, PaidUser.user_id == user_id_to_add).first():
            await update.message.reply_text("This user already has access.")
            return

        db.add(PaidUser(quiz_id=quiz_id, user_id=user_id_to_add))
        db.commit()
        await update.message.reply_text(f"✅ User {user_id_to_add} granted access to quiz '{quiz.title}'.")
    finally:
        db.close()

async def remove_paid_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes a user from a quiz's paid access list."""
    try:
        quiz_id, user_id_to_remove_str = context.args
        user_id_to_remove = int(user_id_to_remove_str)
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: /rem <quiz_id> <user_id>")
        return

    db: Session = next(get_db())
    creator_id = update.effective_user.id
    try:
        stmt = delete(PaidUser).where(
            PaidUser.quiz_id == quiz_id,
            PaidUser.user_id == user_id_to_remove,
            PaidUser.quiz.has(creator_id=creator_id)
        )
        result = db.execute(stmt)
        db.commit()
        if result.rowcount > 0:
            await update.message.reply_text(f"✅ User {user_id_to_remove}'s access has been revoked.")
        else:
            await update.message.reply_text("User not found in this quiz's paid list, or you are not the creator.")
    finally:
        db.close()

async def remove_all_paid_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes all users from a quiz's paid access list."""
    try:
        quiz_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Usage: /remall <quiz_id>")
        return

    db: Session = next(get_db())
    creator_id = update.effective_user.id
    try:
        stmt = delete(PaidUser).where(
            PaidUser.quiz_id == quiz_id,
            PaidUser.quiz.has(creator_id=creator_id)
        )
        result = db.execute(stmt)
        db.commit()
        if result.rowcount > 0:
            await update.message.reply_text(f"✅ Removed {result.rowcount} users from the paid access list.")
        else:
            await update.message.reply_text("No paid users found for this quiz, or you are not the creator.")
    finally:
        db.close()

# --- Temporary Removal List (Session-based) ---

async def temp_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds words to a temporary list for the next extraction."""
    if 'temp_remove_list' not in context.user_data:
        context.user_data['temp_remove_list'] = set()

    words = context.args
    if not words:
        await update.message.reply_text("Usage: /remove word1 word2 ...")
        return

    context.user_data['temp_remove_list'].update([w.lower() for w in words])
    await update.message.reply_text(f"The following words will be temporarily removed during your next extraction: {', '.join(words)}")

async def clear_temp_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the temporary removal list."""
    context.user_data.pop('temp_remove_list', None)
    await update.message.reply_text("✅ Temporary removal list has been cleared.")