"""
Database models for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class UserRole(Enum):
    """User roles in the system"""
    USER = "user"
    PREMIUM = "premium" 
    ADMIN = "admin"
    OWNER = "owner"

class QuizType(Enum):
    """Types of quizzes"""
    FREE = "free"
    PAID = "paid"
    ASSIGNMENT = "assignment"
    MARATHON = "marathon"
    SECTIONAL = "sectional"

class QuizStatus(Enum):
    """Quiz status types"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class User:
    """User model"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_banned: bool = False
    testbook_token: Optional[str] = None
    telegram_session: Optional[str] = None
    language: str = "en"
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    quiz_count: int = 0
    total_score: int = 0

@dataclass 
class Quiz:
    """Quiz model"""
    quiz_id: str
    creator_id: int
    title: str
    description: Optional[str] = None
    quiz_type: QuizType = QuizType.FREE
    status: QuizStatus = QuizStatus.DRAFT
    questions: List[Dict] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)
    allowed_users: List[int] = field(default_factory=list)
    allowed_groups: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    total_questions: int = 0
    time_per_question: int = 30
    negative_marking: bool = True
    negative_marks: float = 0.25
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_results: bool = True
    sections: List[Dict] = field(default_factory=list)

@dataclass
class Question:
    """Question model"""
    question_id: str
    quiz_id: str
    question_text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    question_type: str = "mcq"
    section_id: Optional[str] = None
    order_index: int = 0
    time_limit: Optional[int] = None
    marks: int = 1
    negative_marks: float = 0.25
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class QuizSession:
    """Quiz session model for active quizzes"""
    session_id: str
    quiz_id: str
    group_id: int
    creator_id: int
    current_question: int = 0
    status: QuizStatus = QuizStatus.ACTIVE
    participants: List[int] = field(default_factory=list)
    responses: Dict = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    paused_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    speed_multiplier: float = 1.0
    auto_next: bool = True
    show_answers: bool = True

@dataclass
class Response:
    """User response model"""
    response_id: str
    session_id: str
    user_id: int
    question_id: str
    selected_answer: Optional[int] = None
    is_correct: bool = False
    time_taken: float = 0.0
    marks_awarded: float = 0.0
    submitted_at: datetime = field(default_factory=datetime.now)

@dataclass
class Analytics:
    """Analytics model"""
    analytics_id: str
    event_type: str
    user_id: Optional[int] = None
    quiz_id: Optional[str] = None
    session_id: Optional[str] = None
    group_id: Optional[int] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Filter:
    """Filter model for word filtering"""
    filter_id: str
    user_id: int
    filter_words: List[str] = field(default_factory=list)
    remove_words: List[str] = field(default_factory=list)
    auto_filter: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Assignment:
    """Assignment model"""
    assignment_id: str
    creator_id: int
    quiz_id: str
    title: str
    description: Optional[str] = None
    assigned_users: List[int] = field(default_factory=list)
    assigned_groups: List[int] = field(default_factory=list)
    due_date: Optional[datetime] = None
    submissions: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    max_attempts: int = 1
    show_results_after: str = "submission"  # submission, due_date, manual

@dataclass
class Broadcast:
    """Broadcast model"""
    broadcast_id: str
    admin_id: int
    message_text: str
    target_users: List[int] = field(default_factory=list)
    target_groups: List[int] = field(default_factory=list)
    sent_count: int = 0
    failed_count: int = 0
    status: str = "pending"  # pending, running, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class BotStats:
    """Bot statistics model"""
    total_users: int = 0
    active_users_today: int = 0
    active_users_week: int = 0
    total_quizzes: int = 0
    active_quizzes: int = 0
    total_questions: int = 0
    total_responses: int = 0
    uptime: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

# Database Helper Functions
class DatabaseHelper:
    """Helper functions for database operations"""
    
    @staticmethod
    def serialize_list(data: List) -> str:
        """Serialize list to JSON string"""
        return json.dumps(data) if data else "[]"
    
    @staticmethod
    def deserialize_list(data: str) -> List:
        """Deserialize JSON string to list"""
        try:
            return json.loads(data) if data else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def serialize_dict(data: Dict) -> str:
        """Serialize dict to JSON string"""
        return json.dumps(data) if data else "{}"
    
    @staticmethod
    def deserialize_dict(data: str) -> Dict:
        """Deserialize JSON string to dict"""
        try:
            return json.loads(data) if data else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @staticmethod
    def datetime_to_string(dt: datetime) -> str:
        """Convert datetime to string"""
        return dt.isoformat() if dt else ""
    
    @staticmethod
    def string_to_datetime(dt_string: str) -> Optional[datetime]:
        """Convert string to datetime"""
        try:
            return datetime.fromisoformat(dt_string) if dt_string else None
        except ValueError:
            return None

# SQL Schemas
CREATE_TABLES_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    role TEXT DEFAULT 'user',
    is_banned BOOLEAN DEFAULT 0,
    testbook_token TEXT,
    telegram_session TEXT,
    language TEXT DEFAULT 'en',
    created_at TEXT,
    last_active TEXT,
    quiz_count INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id TEXT PRIMARY KEY,
    creator_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    quiz_type TEXT DEFAULT 'free',
    status TEXT DEFAULT 'draft',
    questions TEXT DEFAULT '[]',
    settings TEXT DEFAULT '{}',
    allowed_users TEXT DEFAULT '[]',
    allowed_groups TEXT DEFAULT '[]',
    created_at TEXT,
    updated_at TEXT,
    expires_at TEXT,
    total_questions INTEGER DEFAULT 0,
    time_per_question INTEGER DEFAULT 30,
    negative_marking BOOLEAN DEFAULT 1,
    negative_marks REAL DEFAULT 0.25,
    shuffle_questions BOOLEAN DEFAULT 0,
    shuffle_options BOOLEAN DEFAULT 0,
    show_results BOOLEAN DEFAULT 1,
    sections TEXT DEFAULT '[]',
    FOREIGN KEY (creator_id) REFERENCES users (user_id)
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    quiz_id TEXT,
    question_text TEXT NOT NULL,
    options TEXT NOT NULL,
    correct_answer INTEGER,
    explanation TEXT,
    question_type TEXT DEFAULT 'mcq',
    section_id TEXT,
    order_index INTEGER DEFAULT 0,
    time_limit INTEGER,
    marks INTEGER DEFAULT 1,
    negative_marks REAL DEFAULT 0.25,
    created_at TEXT,
    FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id)
);

-- Quiz sessions table
CREATE TABLE IF NOT EXISTS quiz_sessions (
    session_id TEXT PRIMARY KEY,
    quiz_id TEXT,
    group_id INTEGER,
    creator_id INTEGER,
    current_question INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    participants TEXT DEFAULT '[]',
    responses TEXT DEFAULT '{}',
    started_at TEXT,
    paused_at TEXT,
    ended_at TEXT,
    speed_multiplier REAL DEFAULT 1.0,
    auto_next BOOLEAN DEFAULT 1,
    show_answers BOOLEAN DEFAULT 1,
    FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id)
);

-- Responses table
CREATE TABLE IF NOT EXISTS responses (
    response_id TEXT PRIMARY KEY,
    session_id TEXT,
    user_id INTEGER,
    question_id TEXT,
    selected_answer INTEGER,
    is_correct BOOLEAN DEFAULT 0,
    time_taken REAL DEFAULT 0.0,
    marks_awarded REAL DEFAULT 0.0,
    submitted_at TEXT,
    FOREIGN KEY (session_id) REFERENCES quiz_sessions (session_id),
    FOREIGN KEY (question_id) REFERENCES questions (question_id)
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    analytics_id TEXT PRIMARY KEY,
    event_type TEXT,
    user_id INTEGER,
    quiz_id TEXT,
    session_id TEXT,
    group_id INTEGER,
    metadata TEXT DEFAULT '{}',
    timestamp TEXT
);

-- Filters table
CREATE TABLE IF NOT EXISTS filters (
    filter_id TEXT PRIMARY KEY,
    user_id INTEGER,
    filter_words TEXT DEFAULT '[]',
    remove_words TEXT DEFAULT '[]',
    auto_filter BOOLEAN DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id TEXT PRIMARY KEY,
    creator_id INTEGER,
    quiz_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    assigned_users TEXT DEFAULT '[]',
    assigned_groups TEXT DEFAULT '[]',
    due_date TEXT,
    submissions TEXT DEFAULT '[]',
    created_at TEXT,
    max_attempts INTEGER DEFAULT 1,
    show_results_after TEXT DEFAULT 'submission',
    FOREIGN KEY (creator_id) REFERENCES users (user_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id)
);

-- Broadcasts table
CREATE TABLE IF NOT EXISTS broadcasts (
    broadcast_id TEXT PRIMARY KEY,
    admin_id INTEGER,
    message_text TEXT NOT NULL,
    target_users TEXT DEFAULT '[]',
    target_groups TEXT DEFAULT '[]',
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (admin_id) REFERENCES users (user_id)
);

-- Bot stats table
CREATE TABLE IF NOT EXISTS bot_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_users INTEGER DEFAULT 0,
    active_users_today INTEGER DEFAULT 0,
    active_users_week INTEGER DEFAULT 0,
    total_quizzes INTEGER DEFAULT 0,
    active_quizzes INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    total_responses INTEGER DEFAULT 0,
    uptime REAL DEFAULT 0.0,
    last_updated TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_quizzes_creator ON quizzes(creator_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_status ON quizzes(status);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_sessions_group ON quiz_sessions(group_id);
CREATE INDEX IF NOT EXISTS idx_responses_session ON responses(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_user ON responses(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);
"""