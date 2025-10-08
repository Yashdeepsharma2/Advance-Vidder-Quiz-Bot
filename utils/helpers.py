"""
Helper functions for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import asyncio
import re
import json
import uuid
import hashlib
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Union
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class QuizHelpers:
    """Helper functions for quiz operations"""
    
    @staticmethod
    def generate_quiz_id(prefix: str = "quiz") -> str:
        """Generate unique quiz ID"""
        timestamp = str(int(time.time()))
        random_part = str(random.randint(1000, 9999))
        return f"{prefix}_{timestamp}_{random_part}"
    
    @staticmethod
    def generate_question_id(prefix: str = "q") -> str:
        """Generate unique question ID"""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_session_id(prefix: str = "session") -> str:
        """Generate unique session ID"""
        return f"{prefix}_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def parse_question_text(text: str) -> Dict[str, Any]:
        """
        Parse question text with ✅ marking system
        
        Expected format:
        Question text here?
        A) Option 1
        B) Option 2 ✅
        C) Option 3
        D) Option 4
        """
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        if len(lines) < 3:  # At least question + 2 options
            return {"error": "Insufficient content. Need question and at least 2 options."}
        
        question_text = lines[0]
        options = []
        correct_answer = -1
        
        # Parse options
        for i, line in enumerate(lines[1:], 0):
            # Remove option labels (A), B), etc.)
            option_match = re.match(r'^[A-Za-z]\)\s*(.+)$', line)
            if option_match:
                option_text = option_match.group(1)
            else:
                option_text = line
            
            # Check for correct answer marker
            if '✅' in option_text:
                option_text = option_text.replace('✅', '').strip()
                correct_answer = len(options)
            
            options.append(option_text)
            
            # Limit to 6 options max
            if len(options) >= 6:
                break
        
        if correct_answer == -1:
            return {"error": "No correct answer marked with ✅"}
        
        if len(options) < 2:
            return {"error": "Need at least 2 options"}
        
        return {
            "question_text": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "question_type": "mcq"
        }
    
    @staticmethod
    def parse_bulk_questions(text: str, delimiter: str = "---") -> List[Dict[str, Any]]:
        """Parse multiple questions from bulk text"""
        questions = []
        question_blocks = text.split(delimiter)
        
        for i, block in enumerate(question_blocks, 1):
            block = block.strip()
            if not block:
                continue
            
            parsed = QuizHelpers.parse_question_text(block)
            if "error" in parsed:
                parsed["block_number"] = i
                questions.append(parsed)
            else:
                parsed["question_id"] = QuizHelpers.generate_question_id()
                parsed["order_index"] = len(questions)
                questions.append(parsed)
        
        return questions
    
    @staticmethod
    def calculate_score(responses: List[Dict], negative_marking: bool = True, 
                       negative_marks: float = 0.25) -> Dict[str, Any]:
        """Calculate quiz score with negative marking"""
        total_questions = len(responses)
        correct_answers = 0
        wrong_answers = 0
        unanswered = 0
        total_marks = 0
        
        for response in responses:
            if response.get('selected_answer') is None:
                unanswered += 1
            elif response.get('is_correct', False):
                correct_answers += 1
                total_marks += response.get('marks', 1)
            else:
                wrong_answers += 1
                if negative_marking:
                    total_marks -= response.get('negative_marks', negative_marks)
        
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "unanswered": unanswered,
            "total_marks": round(total_marks, 2),
            "percentage": round(percentage, 2),
            "accuracy": round((correct_answers / (correct_answers + wrong_answers) * 100), 2) if (correct_answers + wrong_answers) > 0 else 0
        }
    
    @staticmethod
    def shuffle_questions(questions: List[Dict]) -> List[Dict]:
        """Shuffle questions while maintaining correct answers"""
        shuffled = questions.copy()
        random.shuffle(shuffled)
        
        # Update order indices
        for i, question in enumerate(shuffled):
            question['order_index'] = i
        
        return shuffled
    
    @staticmethod
    def shuffle_options(question: Dict) -> Dict:
        """Shuffle options while updating correct answer index"""
        if question.get('question_type') != 'mcq':
            return question
        
        options = question.get('options', [])
        correct_answer = question.get('correct_answer', 0)
        
        if len(options) < 2:
            return question
        
        # Create list of (option, is_correct) tuples
        option_pairs = [(opt, i == correct_answer) for i, opt in enumerate(options)]
        
        # Shuffle the pairs
        random.shuffle(option_pairs)
        
        # Rebuild options and find new correct answer index
        new_options = []
        new_correct_answer = 0
        
        for i, (option, is_correct) in enumerate(option_pairs):
            new_options.append(option)
            if is_correct:
                new_correct_answer = i
        
        question_copy = question.copy()
        question_copy['options'] = new_options
        question_copy['correct_answer'] = new_correct_answer
        
        return question_copy

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common unwanted characters
        text = text.replace('\u200c', '')  # Zero-width non-joiner
        text = text.replace('\u200d', '')  # Zero-width joiner
        text = text.replace('\ufeff', '')  # Byte order mark
        
        return text.strip()
    
    @staticmethod
    def remove_links(text: str) -> str:
        """Remove URLs and links from text"""
        # Remove HTTP(S) links
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove telegram links
        text = re.sub(r't\.me/\S+', '', text)
        
        # Remove @username mentions
        text = re.sub(r'@\w+', '', text)
        
        return TextProcessor.clean_text(text)
    
    @staticmethod
    def remove_unwanted_patterns(text: str, patterns: List[str]) -> str:
        """Remove custom unwanted patterns from text"""
        for pattern in patterns:
            if pattern.startswith('regex:'):
                # Regex pattern
                regex_pattern = pattern[6:]
                text = re.sub(regex_pattern, '', text, flags=re.IGNORECASE)
            else:
                # Simple text replacement
                text = text.replace(pattern, '')
        
        return TextProcessor.clean_text(text)
    
    @staticmethod
    def extract_quiz_info_from_url(url: str) -> Dict[str, Any]:
        """Extract quiz information from various URLs"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        info = {
            "platform": "unknown",
            "quiz_id": None,
            "test_id": None,
            "channel": None,
            "post_id": None
        }
        
        # TestBook URLs
        if 'testbook.com' in domain:
            info["platform"] = "testbook"
            # Extract test ID from various TestBook URL formats
            test_match = re.search(r'/test/(\d+)', path)
            if test_match:
                info["test_id"] = test_match.group(1)
        
        # Telegram URLs
        elif 't.me' in domain or 'telegram.me' in domain:
            info["platform"] = "telegram"
            # Extract channel and post info
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 1:
                info["channel"] = path_parts[0]
            if len(path_parts) >= 2:
                info["post_id"] = path_parts[1]
        
        # Quiz bot URLs
        elif any(bot in path.lower() for bot in ['quiz', 'poll']):
            info["platform"] = "quizbot"
            # Try to extract quiz ID
            quiz_match = re.search(r'quiz[/_](\w+)', path, re.IGNORECASE)
            if quiz_match:
                info["quiz_id"] = quiz_match.group(1)
        
        return info
    
    @staticmethod
    def format_time_duration(seconds: int) -> str:
        """Format seconds into human readable duration"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix

class ValidationHelpers:
    """Validation helper functions"""
    
    @staticmethod
    def validate_question_data(question_data: Dict) -> Tuple[bool, str]:
        """Validate question data structure"""
        required_fields = ['question_text', 'options', 'correct_answer']
        
        for field in required_fields:
            if field not in question_data:
                return False, f"Missing required field: {field}"
        
        question_text = question_data.get('question_text', '').strip()
        if not question_text:
            return False, "Question text cannot be empty"
        
        options = question_data.get('options', [])
        if not isinstance(options, list) or len(options) < 2:
            return False, "Need at least 2 options"
        
        if len(options) > 6:
            return False, "Maximum 6 options allowed"
        
        correct_answer = question_data.get('correct_answer')
        if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer >= len(options):
            return False, "Invalid correct answer index"
        
        return True, "Valid question data"
    
    @staticmethod
    def validate_quiz_settings(settings: Dict) -> Tuple[bool, str]:
        """Validate quiz settings"""
        time_per_question = settings.get('time_per_question', 30)
        if not isinstance(time_per_question, int) or time_per_question < 5 or time_per_question > 600:
            return False, "Time per question must be between 5-600 seconds"
        
        negative_marks = settings.get('negative_marks', 0.25)
        if not isinstance(negative_marks, (int, float)) or negative_marks < 0 or negative_marks > 2:
            return False, "Negative marks must be between 0-2"
        
        return True, "Valid quiz settings"
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        # Remove any non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Check for international format
        if not phone.startswith('+'):
            return False, "Phone number must start with country code (+)"
        
        # Remove + for further validation
        phone_digits = phone[1:]
        
        # Check length (typically 10-15 digits after country code)
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            return False, "Invalid phone number length"
        
        # Check if all remaining characters are digits
        if not phone_digits.isdigit():
            return False, "Phone number can only contain digits"
        
        return True, "Valid phone number"
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Validate URL format"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL format"
            
            if result.scheme not in ['http', 'https']:
                return False, "URL must use HTTP or HTTPS"
            
            return True, "Valid URL"
        except Exception:
            return False, "Invalid URL format"

class AnalyticsHelpers:
    """Analytics and statistics helper functions"""
    
    @staticmethod
    def calculate_percentile(score: float, all_scores: List[float]) -> float:
        """Calculate percentile rank of a score"""
        if not all_scores:
            return 0.0
        
        sorted_scores = sorted(all_scores)
        n = len(sorted_scores)
        
        # Count scores less than or equal to the given score
        count = sum(1 for s in sorted_scores if s <= score)
        
        # Calculate percentile
        percentile = (count / n) * 100
        
        return round(percentile, 2)
    
    @staticmethod
    def generate_performance_insights(user_scores: List[Dict]) -> Dict[str, Any]:
        """Generate performance insights from user scores"""
        if not user_scores:
            return {"message": "No data available for analysis"}
        
        scores = [score.get('percentage', 0) for score in user_scores]
        total_quizzes = len(scores)
        
        insights = {
            "total_quizzes": total_quizzes,
            "average_score": round(sum(scores) / total_quizzes, 2),
            "best_score": max(scores),
            "worst_score": min(scores),
            "improvement_trend": "stable"
        }
        
        # Calculate trend
        if total_quizzes >= 3:
            recent_scores = scores[-3:]
            earlier_scores = scores[:-3] if len(scores) > 3 else scores[:1]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            earlier_avg = sum(earlier_scores) / len(earlier_scores)
            
            if recent_avg > earlier_avg + 5:
                insights["improvement_trend"] = "improving"
            elif recent_avg < earlier_avg - 5:
                insights["improvement_trend"] = "declining"
        
        # Performance categories
        excellent = sum(1 for s in scores if s >= 90)
        good = sum(1 for s in scores if 70 <= s < 90)
        average = sum(1 for s in scores if 50 <= s < 70)
        poor = sum(1 for s in scores if s < 50)
        
        insights["performance_distribution"] = {
            "excellent": excellent,
            "good": good,
            "average": average,
            "poor": poor
        }
        
        return insights
    
    @staticmethod
    def format_analytics_summary(analytics_data: Dict) -> str:
        """Format analytics data into readable summary"""
        summary = "📊 **Performance Analytics**\n"
        summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Basic stats
        total_quizzes = analytics_data.get('total_quizzes', 0)
        avg_score = analytics_data.get('average_score', 0)
        best_score = analytics_data.get('best_score', 0)
        
        summary += f"📝 Total Quizzes: {total_quizzes}\n"
        summary += f"📊 Average Score: {avg_score}%\n"
        summary += f"🏆 Best Score: {best_score}%\n\n"
        
        # Trend
        trend = analytics_data.get('improvement_trend', 'stable')
        trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}
        summary += f"{trend_emoji.get(trend, '➡️')} Trend: {trend.title()}\n\n"
        
        # Distribution
        dist = analytics_data.get('performance_distribution', {})
        summary += "🎯 **Performance Distribution:**\n"
        summary += f"🌟 Excellent (90%+): {dist.get('excellent', 0)}\n"
        summary += f"👍 Good (70-89%): {dist.get('good', 0)}\n"
        summary += f"📝 Average (50-69%): {dist.get('average', 0)}\n"
        summary += f"📉 Poor (<50%): {dist.get('poor', 0)}\n"
        
        return summary

class SecurityHelpers:
    """Security and encryption helper functions"""
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Create hash of token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        import secrets
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def is_admin_user(user_id: int) -> bool:
        """Check if user is admin"""
        from config import config
        return user_id in config.ADMIN_IDS or user_id == config.OWNER_ID
    
    @staticmethod
    def rate_limit_check(user_id: int, action: str, limit: int = 10, 
                        window: int = 60) -> Tuple[bool, int]:
        """
        Basic rate limiting check
        Returns (allowed, remaining_time)
        """
        # This is a simple in-memory rate limiter
        # In production, use Redis or database
        current_time = int(time.time())
        key = f"{user_id}_{action}"
        
        # For simplicity, always allow for now
        # In production implementation:
        # 1. Check if key exists in cache
        # 2. Count requests in time window
        # 3. Return appropriate response
        
        return True, 0