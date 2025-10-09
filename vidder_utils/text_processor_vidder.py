"""
📝 VidderTech Advanced Text Processor
Built by VidderTech - The Future of Quiz Bots

Advanced text processing system with:
- Intelligent question parsing
- ✅ marking system recognition
- Multi-format support
- Smart validation
- Content optimization
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Initialize logger
logger = logging.getLogger('vidder.text_processor')

class VidderTextProcessor:
    """📝 VidderTech Advanced Text Processing Engine"""
    
    def __init__(self):
        """Initialize VidderTech text processor"""
        self.question_patterns = {
            'mcq': r'^(.+\?)\s*\n((?:[A-Za-z]\)\s*.+\n?)+)$',
            'true_false': r'^(.+\?)\s*\n(?:A\)\s*True|True)\s*([✅❌]?)\s*\n(?:B\)\s*False|False)\s*([✅❌]?)$',
            'fill_blank': r'^(.+)(_____+)(.*)$'
        }
        
        logger.info("📝 VidderTech Text Processor initialized")
    
    async def parse_single_question(self, text: str) -> Dict[str, Any]:
        """
        Parse single question with VidderTech ✅ system
        
        Supported formats:
        - Multiple choice with ✅ marking
        - True/False questions
        - Fill in the blanks
        - Short answer questions
        """
        try:
            text = self.clean_text(text)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) < 3:
                return {
                    "error": "Invalid format. Need question and at least 2 options.",
                    "suggestion": "Use format: Question?\nA) Option 1\nB) Option 2 ✅"
                }
            
            # Extract question text
            question_text = lines[0].strip()
            if not question_text.endswith('?'):
                question_text += '?'
            
            # Parse options and find correct answer
            options = []
            correct_answer = -1
            explanation = None
            
            for i, line in enumerate(lines[1:], 0):
                line = line.strip()
                
                # Check for explanation
                if line.lower().startswith(('explanation:', 'explain:', 'note:')):
                    explanation = line.split(':', 1)[1].strip()
                    continue
                
                # Parse option
                option_match = re.match(r'^[A-Za-z]\)\s*(.+)$', line)
                if option_match:
                    option_text = option_match.group(1).strip()
                    
                    # Check for correct answer marker
                    if '✅' in option_text:
                        option_text = option_text.replace('✅', '').strip()
                        correct_answer = len(options)
                    
                    options.append(option_text)
                    
                    if len(options) >= 6:  # Max 6 options
                        break
            
            # Validation
            if correct_answer == -1:
                return {
                    "error": "No correct answer marked with ✅",
                    "suggestion": "Mark the correct answer with ✅ symbol"
                }
            
            if len(options) < 2:
                return {
                    "error": "Need at least 2 options",
                    "suggestion": "Add more options (minimum 2, maximum 6)"
                }
            
            # Detect question type
            question_type = self._detect_question_type(question_text, options)
            
            return {
                "question_text": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "question_type": question_type,
                "marks": 1.0,
                "confidence_score": self._calculate_confidence_score(question_text, options)
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing question: {e}")
            return {
                "error": "Failed to parse question",
                "suggestion": "Please check the format and try again"
            }
    
    async def parse_bulk_questions(self, text: str, delimiter: str = "---") -> List[Dict[str, Any]]:
        """Parse multiple questions from bulk text"""
        try:
            questions = []
            question_blocks = text.split(delimiter)
            
            for i, block in enumerate(question_blocks, 1):
                block = block.strip()
                if not block:
                    continue
                
                parsed = await self.parse_single_question(block)
                parsed['block_number'] = i
                parsed['order_index'] = len(questions)
                
                questions.append(parsed)
            
            logger.info(f"📝 Parsed {len(questions)} questions from bulk text")
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error parsing bulk questions: {e}")
            return []
    
    async def validate_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate question using VidderTech standards"""
        try:
            validation = {
                "valid": True,
                "message": "Question is valid",
                "suggestions": [],
                "score": 100
            }
            
            # Validate question text
            question_text = question_data.get('question_text', '')
            if len(question_text) < 10:
                validation["valid"] = False
                validation["message"] = "Question too short"
                validation["suggestions"].append("Make question more descriptive")
                validation["score"] -= 30
            
            if len(question_text) > 500:
                validation["valid"] = False
                validation["message"] = "Question too long"
                validation["suggestions"].append("Keep question under 500 characters")
                validation["score"] -= 20
            
            # Validate options
            options = question_data.get('options', [])
            if len(options) < 2:
                validation["valid"] = False
                validation["message"] = "Need at least 2 options"
                validation["suggestions"].append("Add more answer options")
                validation["score"] -= 50
            
            # Check for duplicate options
            if len(set(options)) != len(options):
                validation["suggestions"].append("Remove duplicate options")
                validation["score"] -= 10
            
            # Validate correct answer
            correct_answer = question_data.get('correct_answer')
            if correct_answer is None or correct_answer < 0 or correct_answer >= len(options):
                validation["valid"] = False
                validation["message"] = "Invalid correct answer"
                validation["suggestions"].append("Mark correct answer with ✅")
                validation["score"] -= 40
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Error validating question: {e}")
            return {"valid": False, "message": "Validation error", "suggestions": []}
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text with VidderTech standards"""
        if not text:
            return ""
        
        # Remove unwanted characters
        text = text.replace('\u200c', '')  # Zero-width non-joiner
        text = text.replace('\u200d', '')  # Zero-width joiner
        text = text.replace('\ufeff', '')  # Byte order mark
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove common quiz artifacts
        text = re.sub(r'\[\d+/\d+\]', '', text)  # Remove [1/10] patterns
        text = re.sub(r'Question \d+:', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def remove_unwanted_words(self, text: str, filter_words: List[str] = None) -> str:
        """Remove unwanted words and patterns"""
        if not filter_words:
            filter_words = [
                '@', 'http://', 'https://', 't.me/', 'telegram.me/',
                'follow us', 'subscribe', 'like', 'share'
            ]
        
        for word in filter_words:
            if word.startswith('regex:'):
                pattern = word[6:]
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            else:
                text = text.replace(word, '')
        
        return self.clean_text(text)
    
    def _detect_question_type(self, question: str, options: List[str]) -> str:
        """Detect question type from content"""
        # True/False detection
        if len(options) == 2 and any(opt.lower() in ['true', 'false', 'yes', 'no'] for opt in options):
            return 'true_false'
        
        # Fill in the blank detection
        if '_____' in question or '______' in question:
            return 'fill_blank'
        
        # Default to multiple choice
        return 'mcq'
    
    def _calculate_confidence_score(self, question: str, options: List[str]) -> float:
        """Calculate confidence score for question quality"""
        score = 100.0
        
        # Length checks
        if len(question) < 20:
            score -= 10
        if len(question) > 200:
            score -= 5
        
        # Option quality
        avg_option_length = sum(len(opt) for opt in options) / len(options)
        if avg_option_length < 5:
            score -= 15
        
        # Complexity check
        if len(question.split()) < 5:
            score -= 10
        
        return max(0.0, min(100.0, score))

# Global text processor instance
vidder_text_processor = VidderTextProcessor()