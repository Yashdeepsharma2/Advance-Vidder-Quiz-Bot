"""
Database operations for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import sqlite3
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from contextlib import asynccontextmanager
import logging

from .models import (
    User, Quiz, Question, QuizSession, Response, Analytics, 
    Filter, Assignment, Broadcast, BotStats, DatabaseHelper,
    CREATE_TABLES_SQL, UserRole, QuizType, QuizStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_path: str = "vidder_quiz_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(CREATE_TABLES_SQL)
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with context manager"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # User Operations
    async def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, role, created_at, last_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id, user.username, user.first_name, user.last_name,
                    user.role.value, DatabaseHelper.datetime_to_string(user.created_at),
                    DatabaseHelper.datetime_to_string(user.last_active)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating user {user.user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        role=UserRole(row['role']),
                        is_banned=bool(row['is_banned']),
                        testbook_token=row['testbook_token'],
                        telegram_session=row['telegram_session'],
                        language=row['language'],
                        created_at=DatabaseHelper.string_to_datetime(row['created_at']),
                        last_active=DatabaseHelper.string_to_datetime(row['last_active']),
                        quiz_count=row['quiz_count'],
                        total_score=row['total_score']
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user_activity(self, user_id: int) -> bool:
        """Update user last active timestamp"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET last_active = ? WHERE user_id = ?
                """, (DatabaseHelper.datetime_to_string(datetime.now()), user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user activity {user_id}: {e}")
            return False
    
    async def ban_user(self, user_id: int, is_banned: bool = True) -> bool:
        """Ban or unban a user"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET is_banned = ? WHERE user_id = ?
                """, (is_banned, user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    # Quiz Operations
    async def create_quiz(self, quiz: Quiz) -> bool:
        """Create a new quiz"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quizzes 
                    (quiz_id, creator_id, title, description, quiz_type, status,
                     questions, settings, allowed_users, allowed_groups,
                     created_at, updated_at, time_per_question, negative_marking,
                     negative_marks, sections)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    quiz.quiz_id, quiz.creator_id, quiz.title, quiz.description,
                    quiz.quiz_type.value, quiz.status.value,
                    DatabaseHelper.serialize_list(quiz.questions),
                    DatabaseHelper.serialize_dict(quiz.settings),
                    DatabaseHelper.serialize_list(quiz.allowed_users),
                    DatabaseHelper.serialize_list(quiz.allowed_groups),
                    DatabaseHelper.datetime_to_string(quiz.created_at),
                    DatabaseHelper.datetime_to_string(quiz.updated_at),
                    quiz.time_per_question, quiz.negative_marking,
                    quiz.negative_marks,
                    DatabaseHelper.serialize_list(quiz.sections)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating quiz {quiz.quiz_id}: {e}")
            return False
    
    async def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Get quiz by ID"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM quizzes WHERE quiz_id = ?", (quiz_id,))
                row = cursor.fetchone()
                
                if row:
                    return Quiz(
                        quiz_id=row['quiz_id'],
                        creator_id=row['creator_id'],
                        title=row['title'],
                        description=row['description'],
                        quiz_type=QuizType(row['quiz_type']),
                        status=QuizStatus(row['status']),
                        questions=DatabaseHelper.deserialize_list(row['questions']),
                        settings=DatabaseHelper.deserialize_dict(row['settings']),
                        allowed_users=DatabaseHelper.deserialize_list(row['allowed_users']),
                        allowed_groups=DatabaseHelper.deserialize_list(row['allowed_groups']),
                        created_at=DatabaseHelper.string_to_datetime(row['created_at']),
                        updated_at=DatabaseHelper.string_to_datetime(row['updated_at']),
                        total_questions=row['total_questions'],
                        time_per_question=row['time_per_question'],
                        negative_marking=bool(row['negative_marking']),
                        negative_marks=row['negative_marks'],
                        sections=DatabaseHelper.deserialize_list(row['sections'])
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting quiz {quiz_id}: {e}")
            return None
    
    async def get_user_quizzes(self, user_id: int, limit: int = 50) -> List[Quiz]:
        """Get quizzes created by user"""
        quizzes = []
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM quizzes WHERE creator_id = ? 
                    ORDER BY created_at DESC LIMIT ?
                """, (user_id, limit))
                rows = cursor.fetchall()
                
                for row in rows:
                    quiz = Quiz(
                        quiz_id=row['quiz_id'],
                        creator_id=row['creator_id'],
                        title=row['title'],
                        description=row['description'],
                        quiz_type=QuizType(row['quiz_type']),
                        status=QuizStatus(row['status']),
                        questions=DatabaseHelper.deserialize_list(row['questions']),
                        created_at=DatabaseHelper.string_to_datetime(row['created_at']),
                        total_questions=row['total_questions'],
                        time_per_question=row['time_per_question']
                    )
                    quizzes.append(quiz)
                    
        except Exception as e:
            logger.error(f"Error getting user quizzes {user_id}: {e}")
        
        return quizzes
    
    async def delete_quiz(self, quiz_id: str, creator_id: int) -> bool:
        """Delete a quiz"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user owns the quiz
                cursor.execute("""
                    SELECT creator_id FROM quizzes WHERE quiz_id = ?
                """, (quiz_id,))
                row = cursor.fetchone()
                
                if not row or row['creator_id'] != creator_id:
                    return False
                
                # Delete related data
                cursor.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
                cursor.execute("DELETE FROM quiz_sessions WHERE quiz_id = ?", (quiz_id,))
                cursor.execute("DELETE FROM quizzes WHERE quiz_id = ?", (quiz_id,))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting quiz {quiz_id}: {e}")
            return False
    
    # Question Operations
    async def add_question(self, question: Question) -> bool:
        """Add a question to quiz"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO questions 
                    (question_id, quiz_id, question_text, options, correct_answer,
                     explanation, question_type, section_id, order_index, 
                     time_limit, marks, negative_marks, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    question.question_id, question.quiz_id, question.question_text,
                    DatabaseHelper.serialize_list(question.options),
                    question.correct_answer, question.explanation,
                    question.question_type, question.section_id,
                    question.order_index, question.time_limit,
                    question.marks, question.negative_marks,
                    DatabaseHelper.datetime_to_string(question.created_at)
                ))
                
                # Update quiz question count
                cursor.execute("""
                    UPDATE quizzes SET total_questions = (
                        SELECT COUNT(*) FROM questions WHERE quiz_id = ?
                    ) WHERE quiz_id = ?
                """, (question.quiz_id, question.quiz_id))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding question {question.question_id}: {e}")
            return False
    
    async def get_quiz_questions(self, quiz_id: str) -> List[Question]:
        """Get all questions for a quiz"""
        questions = []
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM questions WHERE quiz_id = ? ORDER BY order_index
                """, (quiz_id,))
                rows = cursor.fetchall()
                
                for row in rows:
                    question = Question(
                        question_id=row['question_id'],
                        quiz_id=row['quiz_id'],
                        question_text=row['question_text'],
                        options=DatabaseHelper.deserialize_list(row['options']),
                        correct_answer=row['correct_answer'],
                        explanation=row['explanation'],
                        question_type=row['question_type'],
                        section_id=row['section_id'],
                        order_index=row['order_index'],
                        time_limit=row['time_limit'],
                        marks=row['marks'],
                        negative_marks=row['negative_marks'],
                        created_at=DatabaseHelper.string_to_datetime(row['created_at'])
                    )
                    questions.append(question)
                    
        except Exception as e:
            logger.error(f"Error getting quiz questions {quiz_id}: {e}")
        
        return questions
    
    # Quiz Session Operations
    async def create_quiz_session(self, session: QuizSession) -> bool:
        """Create a new quiz session"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quiz_sessions 
                    (session_id, quiz_id, group_id, creator_id, status,
                     participants, responses, started_at, speed_multiplier,
                     auto_next, show_answers)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, session.quiz_id, session.group_id,
                    session.creator_id, session.status.value,
                    DatabaseHelper.serialize_list(session.participants),
                    DatabaseHelper.serialize_dict(session.responses),
                    DatabaseHelper.datetime_to_string(session.started_at),
                    session.speed_multiplier, session.auto_next,
                    session.show_answers
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating quiz session {session.session_id}: {e}")
            return False
    
    async def get_active_session(self, group_id: int) -> Optional[QuizSession]:
        """Get active quiz session for a group"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM quiz_sessions 
                    WHERE group_id = ? AND status IN ('active', 'paused')
                    ORDER BY started_at DESC LIMIT 1
                """, (group_id,))
                row = cursor.fetchone()
                
                if row:
                    return QuizSession(
                        session_id=row['session_id'],
                        quiz_id=row['quiz_id'],
                        group_id=row['group_id'],
                        creator_id=row['creator_id'],
                        current_question=row['current_question'],
                        status=QuizStatus(row['status']),
                        participants=DatabaseHelper.deserialize_list(row['participants']),
                        responses=DatabaseHelper.deserialize_dict(row['responses']),
                        started_at=DatabaseHelper.string_to_datetime(row['started_at']),
                        paused_at=DatabaseHelper.string_to_datetime(row['paused_at']),
                        speed_multiplier=row['speed_multiplier'],
                        auto_next=bool(row['auto_next']),
                        show_answers=bool(row['show_answers'])
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting active session for group {group_id}: {e}")
            return None
    
    # Analytics Operations
    async def log_analytics(self, analytics: Analytics) -> bool:
        """Log analytics event"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analytics 
                    (analytics_id, event_type, user_id, quiz_id, session_id,
                     group_id, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analytics.analytics_id, analytics.event_type,
                    analytics.user_id, analytics.quiz_id,
                    analytics.session_id, analytics.group_id,
                    DatabaseHelper.serialize_dict(analytics.metadata),
                    DatabaseHelper.datetime_to_string(analytics.timestamp)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging analytics: {e}")
            return False
    
    # Statistics Operations
    async def get_bot_stats(self) -> BotStats:
        """Get bot statistics"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get user stats
                cursor.execute("SELECT COUNT(*) as count FROM users")
                total_users = cursor.fetchone()['count']
                
                # Get active users today
                today = datetime.now().date()
                cursor.execute("""
                    SELECT COUNT(*) as count FROM users 
                    WHERE DATE(last_active) = ?
                """, (today,))
                active_today = cursor.fetchone()['count']
                
                # Get quiz stats
                cursor.execute("SELECT COUNT(*) as count FROM quizzes")
                total_quizzes = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT COUNT(*) as count FROM quiz_sessions 
                    WHERE status = 'active'
                """)
                active_quizzes = cursor.fetchone()['count']
                
                # Get question stats
                cursor.execute("SELECT COUNT(*) as count FROM questions")
                total_questions = cursor.fetchone()['count']
                
                # Get response stats
                cursor.execute("SELECT COUNT(*) as count FROM responses")
                total_responses = cursor.fetchone()['count']
                
                return BotStats(
                    total_users=total_users,
                    active_users_today=active_today,
                    total_quizzes=total_quizzes,
                    active_quizzes=active_quizzes,
                    total_questions=total_questions,
                    total_responses=total_responses,
                    last_updated=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return BotStats()
    
    # Utility Methods
    def generate_id(self, prefix: str = "") -> str:
        """Generate unique ID"""
        return f"{prefix}{uuid.uuid4().hex[:12]}"
    
    async def cleanup_expired_data(self):
        """Clean up expired quizzes and sessions"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=30)
                
                # Delete old completed sessions
                cursor.execute("""
                    DELETE FROM quiz_sessions 
                    WHERE status = 'completed' AND ended_at < ?
                """, (DatabaseHelper.datetime_to_string(cutoff_date),))
                
                # Delete expired quizzes
                cursor.execute("""
                    DELETE FROM quizzes 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (DatabaseHelper.datetime_to_string(datetime.now()),))
                
                conn.commit()
                logger.info("Expired data cleaned up successfully")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")

# Global database instance
db_manager = DatabaseManager()