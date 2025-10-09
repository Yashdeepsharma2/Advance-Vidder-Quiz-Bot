# Powered by Viddertech

from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, DateTime,
    Boolean, Float, Text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=False)  # Telegram User ID
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=True, unique=True)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quizzes = relationship("Quiz", back_populates="creator")
    responses = relationship("Response", back_populates="user")
    filters = relationship("Filter", back_populates="user", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="creator")
    submissions = relationship("Submission", back_populates="student")

class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(String, primary_key=True) # UUID
    title = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_paid = Column(Boolean, default=False)

    creator = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    paid_users = relationship("PaidUser", back_populates="quiz", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(String, ForeignKey('quizzes.id', ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    _options = Column('options', Text, nullable=False) # Store as JSON string
    correct_option_index = Column(Integer, nullable=False)

    @property
    def options(self):
        return json.loads(self._options)

    @options.setter
    def options(self, value):
        self._options = json.dumps(value)

    quiz = relationship("Quiz", back_populates="questions")

class PaidUser(Base):
    __tablename__ = 'paid_users'
    id = Column(Integer, primary_key=True)
    quiz_id = Column(String, ForeignKey('quizzes.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    quiz = relationship("Quiz", back_populates="paid_users")

class Filter(Base):
    __tablename__ = 'filters'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    word = Column(String, nullable=False)

    user = relationship("User", back_populates="filters")

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(String, primary_key=True) # UUID
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    assignment_id = Column(String, ForeignKey('assignments.id', ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text_content = Column(Text, nullable=True)
    file_id = Column(String, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quiz_id = Column(String, nullable=False)
    question_id = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="responses")