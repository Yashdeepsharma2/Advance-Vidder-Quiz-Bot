# Powered by Viddertech

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./vidder_quiz_bot.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite with threading
    echo=False # Set to True to see raw SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def get_db() -> Session:
    """
    Dependency to get a database session.
    Ensures the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# You can add specific database operation functions here later
# For example:
#
# from .models import User
#
# def get_user(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()
#
# def create_user(db: Session, user: User):
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user