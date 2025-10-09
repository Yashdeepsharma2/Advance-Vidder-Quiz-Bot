"""
🗄️ VidderTech Advanced Database Models
Built by VidderTech - The Future of Quiz Bots

Complete data models for enterprise quiz bot with:
- User management and authentication
- Advanced quiz system
- Analytics and performance tracking
- Multi-language support
- Security and permissions
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger('vidder.models')

# 🏷️ Enums for VidderTech System
class UserRole(Enum):
    """User roles in VidderTech system"""
    FREE = "free"
    PREMIUM = "premium"
    EDUCATOR = "educator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"

class QuizType(Enum):
    """Quiz types supported by VidderTech"""
    FREE = "free"
    PREMIUM = "premium"
    ASSIGNMENT = "assignment"
    MARATHON = "marathon"
    SECTIONAL = "sectional"
    TOURNAMENT = "tournament"

class QuizStatus(Enum):
    """Quiz status types"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# 🔧 Utility Functions
def generate_id(prefix: str = "") -> str:
    """Generate unique ID with VidderTech prefix"""
    return f"{prefix}{uuid.uuid4().hex[:12]}"

def serialize_json(data: Any) -> str:
    """Safely serialize data to JSON"""
    try:
        return json.dumps(data, default=str)
    except Exception:
        return "{}"

def deserialize_json(data: str) -> Any:
    """Safely deserialize JSON data"""
    try:
        return json.loads(data) if data else {}
    except Exception:
        return {}

# 🗄️ VidderTech Database Schema
VIDDER_DATABASE_SCHEMA = """
-- VidderTech Advanced Quiz Bot Database Schema
-- Built by VidderTech - The Future of Quiz Bots

-- Enhanced users table with comprehensive profile
CREATE TABLE IF NOT EXISTS vidder_users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    
    -- Role and permissions
    role TEXT DEFAULT 'free',
    status TEXT DEFAULT 'active',
    is_premium BOOLEAN DEFAULT 0,
    premium_expires TEXT,
    
    -- Authentication
    password_hash TEXT,
    session_token TEXT,
    last_login TEXT,
    login_attempts INTEGER DEFAULT 0,
    
    -- External authentications
    testbook_token TEXT,
    testbook_user_id TEXT,
    telegram_session TEXT,
    google_id TEXT,
    
    -- Preferences
    language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    notification_preferences TEXT DEFAULT '{}',
    ui_preferences TEXT DEFAULT '{}',
    
    -- Statistics
    quizzes_created INTEGER DEFAULT 0,
    quizzes_taken INTEGER DEFAULT 0,
    total_score REAL DEFAULT 0.0,
    avg_score REAL DEFAULT 0.0,
    best_score REAL DEFAULT 0.0,
    streak_current INTEGER DEFAULT 0,
    streak_best INTEGER DEFAULT 0,
    
    -- Profile
    bio TEXT,
    avatar_url TEXT,
    country TEXT,
    city TEXT,
    organization TEXT,
    
    -- Timestamps
    created_at TEXT,
    updated_at TEXT,
    last_active TEXT
);

-- Advanced quizzes table
CREATE TABLE IF NOT EXISTS vidder_quizzes (
    quiz_id TEXT PRIMARY KEY,
    creator_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    
    -- Configuration
    quiz_type TEXT DEFAULT 'free',
    status TEXT DEFAULT 'draft',
    difficulty TEXT DEFAULT 'medium',
    category TEXT,
    tags TEXT DEFAULT '[]',
    
    -- Timing
    time_per_question INTEGER DEFAULT 30,
    total_time_limit INTEGER,
    start_time TEXT,
    end_time TEXT,
    
    -- Scoring
    positive_marks REAL DEFAULT 1.0,
    negative_marks REAL DEFAULT 0.25,
    negative_marking_enabled BOOLEAN DEFAULT 1,
    pass_percentage REAL DEFAULT 40.0,
    
    -- Display
    shuffle_questions BOOLEAN DEFAULT 0,
    shuffle_options BOOLEAN DEFAULT 0,
    show_results BOOLEAN DEFAULT 1,
    show_correct_answers BOOLEAN DEFAULT 1,
    allow_review BOOLEAN DEFAULT 1,
    
    -- Access control
    is_public BOOLEAN DEFAULT 1,
    password_protected BOOLEAN DEFAULT 0,
    password_hash TEXT,
    allowed_users TEXT DEFAULT '[]',
    allowed_groups TEXT DEFAULT '[]',
    max_attempts INTEGER DEFAULT 1,
    
    -- Statistics
    total_questions INTEGER DEFAULT 0,
    total_participants INTEGER DEFAULT 0,
    total_completions INTEGER DEFAULT 0,
    average_score REAL DEFAULT 0.0,
    
    -- Advanced features
    sections TEXT DEFAULT '[]',
    marathon_mode BOOLEAN DEFAULT 0,
    live_mode BOOLEAN DEFAULT 0,
    tournament_mode BOOLEAN DEFAULT 0,
    
    -- Metadata
    source TEXT,
    source_url TEXT,
    version INTEGER DEFAULT 1,
    
    -- Timestamps
    created_at TEXT,
    updated_at TEXT,
    published_at TEXT,
    expires_at TEXT,
    
    FOREIGN KEY (creator_id) REFERENCES vidder_users (user_id)
);

-- Enhanced questions table
CREATE TABLE IF NOT EXISTS vidder_questions (
    question_id TEXT PRIMARY KEY,
    quiz_id TEXT,
    question_text TEXT NOT NULL,
    question_type TEXT DEFAULT 'mcq',
    options TEXT DEFAULT '[]',
    correct_answer TEXT,
    explanation TEXT,
    
    -- Media support
    question_image TEXT,
    question_audio TEXT,
    question_video TEXT,
    
    -- Configuration
    difficulty TEXT DEFAULT 'medium',
    category TEXT,
    tags TEXT DEFAULT '[]',
    order_index INTEGER DEFAULT 0,
    section_id TEXT,
    
    -- Scoring
    marks REAL DEFAULT 1.0,
    negative_marks REAL DEFAULT 0.25,
    time_limit INTEGER,
    
    -- Statistics
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    accuracy_rate REAL DEFAULT 0.0,
    avg_time_taken REAL DEFAULT 0.0,
    
    -- Metadata
    hint TEXT,
    reference_url TEXT,
    source TEXT,
    
    created_at TEXT,
    updated_at TEXT,
    
    FOREIGN KEY (quiz_id) REFERENCES vidder_quizzes (quiz_id)
);

-- Quiz sessions for live management
CREATE TABLE IF NOT EXISTS vidder_quiz_sessions (
    session_id TEXT PRIMARY KEY,
    quiz_id TEXT,
    participant_id INTEGER,
    group_id INTEGER,
    session_name TEXT,
    
    -- Status
    status TEXT DEFAULT 'waiting',
    current_question INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    
    -- Timing
    started_at TEXT,
    paused_at TEXT,
    completed_at TEXT,
    expires_at TEXT,
    
    -- Settings
    speed_multiplier REAL DEFAULT 1.0,
    auto_next BOOLEAN DEFAULT 1,
    show_answers BOOLEAN DEFAULT 1,
    
    -- Results
    total_score REAL DEFAULT 0.0,
    percentage REAL DEFAULT 0.0,
    time_taken INTEGER DEFAULT 0,
    rank INTEGER,
    
    -- Statistics
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    questions_wrong INTEGER DEFAULT 0,
    questions_skipped INTEGER DEFAULT 0,
    
    -- Data
    session_data TEXT DEFAULT '{}',
    answers TEXT DEFAULT '{}',
    
    created_at TEXT,
    updated_at TEXT,
    
    FOREIGN KEY (quiz_id) REFERENCES vidder_quizzes (quiz_id),
    FOREIGN KEY (participant_id) REFERENCES vidder_users (user_id)
);

-- Responses table
CREATE TABLE IF NOT EXISTS vidder_responses (
    response_id TEXT PRIMARY KEY,
    session_id TEXT,
    question_id TEXT,
    user_id INTEGER,
    
    -- Response data
    selected_answer TEXT,
    user_answer_text TEXT,
    is_correct BOOLEAN DEFAULT 0,
    partial_score REAL DEFAULT 0.0,
    
    -- Timing
    time_taken REAL DEFAULT 0.0,
    time_remaining REAL DEFAULT 0.0,
    
    -- Scoring
    marks_awarded REAL DEFAULT 0.0,
    negative_marks_applied REAL DEFAULT 0.0,
    
    -- Metadata
    confidence_level INTEGER,
    flag_for_review BOOLEAN DEFAULT 0,
    
    submitted_at TEXT,
    
    FOREIGN KEY (session_id) REFERENCES vidder_quiz_sessions (session_id),
    FOREIGN KEY (question_id) REFERENCES vidder_questions (question_id),
    FOREIGN KEY (user_id) REFERENCES vidder_users (user_id)
);

-- Analytics table
CREATE TABLE IF NOT EXISTS vidder_analytics (
    analytics_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    user_id INTEGER,
    quiz_id TEXT,
    session_id TEXT,
    question_id TEXT,
    
    event_data TEXT DEFAULT '{}',
    metadata TEXT DEFAULT '{}',
    
    -- Context
    group_id INTEGER,
    platform TEXT,
    ip_address TEXT,
    
    timestamp TEXT,
    date TEXT
);

-- Filters table
CREATE TABLE IF NOT EXISTS vidder_filters (
    filter_id TEXT PRIMARY KEY,
    user_id INTEGER,
    filter_name TEXT NOT NULL,
    filter_words TEXT DEFAULT '[]',
    remove_words TEXT DEFAULT '[]',
    auto_filter BOOLEAN DEFAULT 1,
    
    created_at TEXT,
    updated_at TEXT,
    
    FOREIGN KEY (user_id) REFERENCES vidder_users (user_id)
);

-- Assignments table
CREATE TABLE IF NOT EXISTS vidder_assignments (
    assignment_id TEXT PRIMARY KEY,
    creator_id INTEGER,
    quiz_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    
    assigned_users TEXT DEFAULT '[]',
    assigned_groups TEXT DEFAULT '[]',
    due_date TEXT,
    max_attempts INTEGER DEFAULT 1,
    
    submissions TEXT DEFAULT '[]',
    status TEXT DEFAULT 'draft',
    
    created_at TEXT,
    updated_at TEXT,
    
    FOREIGN KEY (creator_id) REFERENCES vidder_users (user_id),
    FOREIGN KEY (quiz_id) REFERENCES vidder_quizzes (quiz_id)
);

-- Broadcasts table
CREATE TABLE IF NOT EXISTS vidder_broadcasts (
    broadcast_id TEXT PRIMARY KEY,
    admin_id INTEGER,
    message_text TEXT NOT NULL,
    
    target_users TEXT DEFAULT '[]',
    target_groups TEXT DEFAULT '[]',
    
    status TEXT DEFAULT 'pending',
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    
    FOREIGN KEY (admin_id) REFERENCES vidder_users (user_id)
);

-- Bot statistics
CREATE TABLE IF NOT EXISTS vidder_bot_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    
    -- User metrics
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    premium_users INTEGER DEFAULT 0,
    
    -- Quiz metrics  
    total_quizzes INTEGER DEFAULT 0,
    active_quizzes INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    total_responses INTEGER DEFAULT 0,
    
    -- Performance
    uptime_percentage REAL DEFAULT 100.0,
    avg_response_time REAL DEFAULT 0.0,
    
    updated_at TEXT
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_users_role ON vidder_users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON vidder_users(last_active);
CREATE INDEX IF NOT EXISTS idx_quizzes_creator ON vidder_quizzes(creator_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_status ON vidder_quizzes(status);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON vidder_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON vidder_quiz_sessions(participant_id);
CREATE INDEX IF NOT EXISTS idx_responses_session ON vidder_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event ON vidder_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON vidder_analytics(date);
"""

logger.info("🗄️ VidderTech Database Models: 10+ comprehensive tables defined")