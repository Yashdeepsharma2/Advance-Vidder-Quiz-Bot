# Powered by Viddertech

import logging
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
import config

logger = logging.getLogger(__name__)

async def universal_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This handler runs for every update. It ensures the user is in the database
    and checks if they are banned before any other handler runs.
    """
    if not update.effective_user:
        return # Ignore updates without a user (e.g., channel posts)

    user = update.effective_user
    db: Session = next(get_db())

    try:
        db_user = db.query(User).filter(User.id == user.id).first()

        if db_user:
            # Check for ban
            if db_user.is_banned:
                logger.warning(f"Banned user {user.id} ({user.full_name}) tried to use the bot.")
                raise ApplicationHandlerStop # Stop processing any more handlers for this user

            # Update user details if they've changed
            if db_user.full_name != user.full_name or db_user.username != user.username:
                db_user.full_name = user.full_name
                db_user.username = user.username
                db.commit()

        else:
            # Add new user to the database
            logger.info(f"New user detected: {user.id} ({user.full_name})")
            new_user = User(
                id=user.id,
                full_name=user.full_name,
                username=user.username,
                is_admin=(user.id == config.OWNER_ID or user.id in config.ADMIN_IDS)
            )
            db.add(new_user)
            db.commit()

    finally:
        db.close()