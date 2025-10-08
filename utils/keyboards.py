"""
Keyboard utilities for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

from typing import List, Dict, Optional, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import config

class KeyboardBuilder:
    """Helper class for building Telegram keyboards"""
    
    @staticmethod
    def create_inline_keyboard(buttons: List[List[Dict[str, str]]], 
                             row_width: int = 2) -> InlineKeyboardMarkup:
        """
        Create inline keyboard from button data
        
        Args:
            buttons: List of button rows, each containing button dictionaries
            row_width: Number of buttons per row (default: 2)
        
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for button in row:
                if 'url' in button:
                    keyboard_row.append(
                        InlineKeyboardButton(
                            text=button['text'],
                            url=button['url']
                        )
                    )
                elif 'callback_data' in button:
                    keyboard_row.append(
                        InlineKeyboardButton(
                            text=button['text'],
                            callback_data=button['callback_data']
                        )
                    )
                elif 'switch_inline_query' in button:
                    keyboard_row.append(
                        InlineKeyboardButton(
                            text=button['text'],
                            switch_inline_query=button['switch_inline_query']
                        )
                    )
                elif 'switch_inline_query_current_chat' in button:
                    keyboard_row.append(
                        InlineKeyboardButton(
                            text=button['text'],
                            switch_inline_query_current_chat=button['switch_inline_query_current_chat']
                        )
                    )
            
            if keyboard_row:
                keyboard.append(keyboard_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def main_menu_keyboard() -> InlineKeyboardMarkup:
        """Create main menu keyboard"""
        buttons = [
            [
                {'text': '📋 Help', 'callback_data': 'help'},
                {'text': '🚀 Features', 'callback_data': 'features'}
            ],
            [
                {'text': '📊 My Quizzes', 'callback_data': 'myquizzes'},
                {'text': '📈 Statistics', 'callback_data': 'stats'}
            ],
            [
                {'text': '🎯 Create Quiz', 'callback_data': 'create_quiz'},
                {'text': '⚙️ Settings', 'callback_data': 'settings'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def quiz_creation_keyboard() -> InlineKeyboardMarkup:
        """Create quiz creation keyboard"""
        buttons = [
            [
                {'text': '✍️ Type Questions', 'callback_data': 'add_manual'},
                {'text': '📄 From Text/File', 'callback_data': 'add_from_text'}
            ],
            [
                {'text': '🔄 From Poll', 'callback_data': 'add_from_poll'},
                {'text': '🌐 From Web', 'callback_data': 'add_from_web'}
            ],
            [
                {'text': '🤖 AI Generated', 'callback_data': 'add_ai'},
                {'text': '📱 From TestBook', 'callback_data': 'add_testbook'}
            ],
            [
                {'text': '⚙️ Advanced Settings', 'callback_data': 'quiz_settings'},
                {'text': '✅ Finish Quiz', 'callback_data': 'finish_quiz'}
            ],
            [
                {'text': '❌ Cancel', 'callback_data': 'cancel_quiz'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def quiz_control_keyboard(session_id: str, is_paused: bool = False) -> InlineKeyboardMarkup:
        """Create quiz control keyboard"""
        if is_paused:
            buttons = [
                [
                    {'text': '▶️ Resume', 'callback_data': f'resume_quiz_{session_id}'},
                    {'text': '⏹️ Stop', 'callback_data': f'stop_quiz_{session_id}'}
                ]
            ]
        else:
            buttons = [
                [
                    {'text': '⏸️ Pause', 'callback_data': f'pause_quiz_{session_id}'},
                    {'text': '⏩ Next', 'callback_data': f'next_question_{session_id}'}
                ],
                [
                    {'text': '🐌 Slow', 'callback_data': f'slow_quiz_{session_id}'},
                    {'text': '⚡ Fast', 'callback_data': f'fast_quiz_{session_id}'}
                ],
                [
                    {'text': '📊 Results', 'callback_data': f'show_results_{session_id}'},
                    {'text': '⏹️ Stop', 'callback_data': f'stop_quiz_{session_id}'}
                ]
            ]
        
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def quiz_options_keyboard(quiz_id: str) -> InlineKeyboardMarkup:
        """Create quiz options keyboard"""
        buttons = [
            [
                {'text': '🎮 Start Quiz', 'callback_data': f'start_quiz_{quiz_id}'},
                {'text': '✏️ Edit Quiz', 'callback_data': f'edit_quiz_{quiz_id}'}
            ],
            [
                {'text': '📊 View Stats', 'callback_data': f'quiz_stats_{quiz_id}'},
                {'text': '📤 Share Quiz', 'callback_data': f'share_quiz_{quiz_id}'}
            ],
            [
                {'text': '🗑️ Delete Quiz', 'callback_data': f'delete_quiz_{quiz_id}'},
                {'text': '📋 Clone Quiz', 'callback_data': f'clone_quiz_{quiz_id}'}
            ],
            [
                {'text': '🏠 Back to Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def admin_keyboard() -> InlineKeyboardMarkup:
        """Create admin control keyboard"""
        buttons = [
            [
                {'text': '📢 Broadcast', 'callback_data': 'admin_broadcast'},
                {'text': '📊 Admin Stats', 'callback_data': 'admin_stats'}
            ],
            [
                {'text': '👥 User Management', 'callback_data': 'admin_users'},
                {'text': '🚫 Ban Management', 'callback_data': 'admin_bans'}
            ],
            [
                {'text': '🗄️ Database', 'callback_data': 'admin_database'},
                {'text': '⚙️ Bot Settings', 'callback_data': 'admin_settings'}
            ],
            [
                {'text': '🏠 Back to Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def timer_selection_keyboard() -> InlineKeyboardMarkup:
        """Create timer selection keyboard"""
        buttons = [
            [
                {'text': '15s ⚡', 'callback_data': 'timer_15'},
                {'text': '30s 📝', 'callback_data': 'timer_30'},
                {'text': '60s 🤔', 'callback_data': 'timer_60'}
            ],
            [
                {'text': '120s 📚', 'callback_data': 'timer_120'},
                {'text': 'Custom ⚙️', 'callback_data': 'timer_custom'}
            ],
            [
                {'text': '❌ Cancel', 'callback_data': 'cancel_quiz'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def language_keyboard(current_lang: str) -> InlineKeyboardMarkup:
        """Create language selection keyboard"""
        languages = [
            ("🇺🇸", "English", "en"),
            ("🇮🇳", "हिंदी", "hi"),
            ("🇮🇳", "ગુજરાતી", "gu"),
            ("🇮🇳", "मराठी", "mr"),
            ("🇮🇳", "বাংলা", "bn"),
            ("🇮🇳", "தமிழ்", "ta"),
            ("🇮🇳", "తెలుగు", "te"),
            ("🇮🇳", "ಕನ್ನಡ", "kn"),
            ("🇮🇳", "മലയാളം", "ml"),
            ("🇮🇳", "ଓଡ଼ିଆ", "or")
        ]
        
        buttons = []
        for flag, name, code in languages:
            current = "✅ " if code == current_lang else ""
            buttons.append([{
                'text': f"{flag} {current}{name}",
                'callback_data': f'set_lang_{code}'
            }])
        
        buttons.append([{'text': '🏠 Home', 'callback_data': 'start'}])
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def pagination_keyboard(current_page: int, total_pages: int, 
                          callback_prefix: str, extra_buttons: Optional[List[Dict]] = None) -> InlineKeyboardMarkup:
        """Create pagination keyboard"""
        buttons = []
        
        # Navigation buttons
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append({
                'text': '◀️ Previous',
                'callback_data': f'{callback_prefix}_prev_{current_page - 1}'
            })
        
        nav_buttons.append({
            'text': f'{current_page + 1}/{total_pages}',
            'callback_data': 'noop'
        })
        
        if current_page < total_pages - 1:
            nav_buttons.append({
                'text': '▶️ Next',
                'callback_data': f'{callback_prefix}_next_{current_page + 1}'
            })
        
        buttons.append(nav_buttons)
        
        # Extra buttons
        if extra_buttons:
            buttons.extend(extra_buttons)
        
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def confirmation_keyboard(confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
        """Create confirmation keyboard"""
        buttons = [
            [
                {'text': '✅ Yes', 'callback_data': confirm_data},
                {'text': '❌ No', 'callback_data': cancel_data}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def filter_management_keyboard() -> InlineKeyboardMarkup:
        """Create filter management keyboard"""
        buttons = [
            [
                {'text': '➕ Add Filter', 'callback_data': 'add_filter'},
                {'text': '➖ Remove Filter', 'callback_data': 'remove_filter'}
            ],
            [
                {'text': '📋 List Filters', 'callback_data': 'list_filters'},
                {'text': '🗑️ Clear All', 'callback_data': 'clear_filters'}
            ],
            [
                {'text': '🚫 Remove Words', 'callback_data': 'remove_words'},
                {'text': '📝 Clear List', 'callback_data': 'clear_remove_list'}
            ],
            [
                {'text': '🏠 Back to Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def assignment_keyboard() -> InlineKeyboardMarkup:
        """Create assignment management keyboard"""
        buttons = [
            [
                {'text': '📝 Create Assignment', 'callback_data': 'create_assignment'},
                {'text': '📊 View Assignments', 'callback_data': 'view_assignments'}
            ],
            [
                {'text': '✅ Check Submissions', 'callback_data': 'check_submissions'},
                {'text': '📈 Assignment Stats', 'callback_data': 'assignment_stats'}
            ],
            [
                {'text': '🏠 Back to Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def extraction_tools_keyboard() -> InlineKeyboardMarkup:
        """Create extraction tools keyboard"""
        buttons = [
            [
                {'text': '📊 Extract from Polls', 'callback_data': 'extract_polls'},
                {'text': '🌐 Extract from Web', 'callback_data': 'extract_web'}
            ],
            [
                {'text': '📱 From TestBook', 'callback_data': 'extract_testbook'},
                {'text': '🤖 From QuizBot', 'callback_data': 'extract_quizbot'}
            ],
            [
                {'text': '📄 From PDF/Image', 'callback_data': 'extract_ocr'},
                {'text': '📝 From Text File', 'callback_data': 'extract_text'}
            ],
            [
                {'text': '🏠 Back to Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def create_reply_keyboard(buttons: List[List[str]], 
                            resize_keyboard: bool = True,
                            one_time_keyboard: bool = False) -> ReplyKeyboardMarkup:
        """Create reply keyboard"""
        keyboard = []
        for row in buttons:
            keyboard.append([KeyboardButton(text) for text in row])
        
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard
        )
    
    @staticmethod
    def quiz_type_keyboard() -> InlineKeyboardMarkup:
        """Create quiz type selection keyboard"""
        buttons = [
            [
                {'text': '🆓 Free Quiz', 'callback_data': 'quiz_type_free'},
                {'text': '💰 Paid Quiz', 'callback_data': 'quiz_type_paid'}
            ],
            [
                {'text': '📚 Assignment', 'callback_data': 'quiz_type_assignment'},
                {'text': '🏃‍♂️ Marathon Quiz', 'callback_data': 'quiz_type_marathon'}
            ],
            [
                {'text': '📊 Sectional Quiz', 'callback_data': 'quiz_type_sectional'}
            ],
            [
                {'text': '🏠 Back to Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)

class QuizKeyboards:
    """Specialized keyboards for quiz functionality"""
    
    @staticmethod
    def create_mcq_keyboard(options: List[str], question_id: str, 
                          show_numbers: bool = True) -> InlineKeyboardMarkup:
        """Create MCQ answer keyboard"""
        buttons = []
        
        for i, option in enumerate(options):
            prefix = f"{chr(65+i)}) " if show_numbers else ""
            buttons.append([{
                'text': f"{prefix}{option}",
                'callback_data': f'answer_{question_id}_{i}'
            }])
        
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def create_true_false_keyboard(question_id: str) -> InlineKeyboardMarkup:
        """Create True/False answer keyboard"""
        buttons = [
            [
                {'text': '✅ True', 'callback_data': f'answer_{question_id}_0'},
                {'text': '❌ False', 'callback_data': f'answer_{question_id}_1'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)
    
    @staticmethod
    def create_quiz_result_keyboard(session_id: str, quiz_id: str) -> InlineKeyboardMarkup:
        """Create quiz result actions keyboard"""
        buttons = [
            [
                {'text': '📊 Detailed Results', 'callback_data': f'detailed_results_{session_id}'},
                {'text': '📈 Analytics', 'callback_data': f'quiz_analytics_{quiz_id}'}
            ],
            [
                {'text': '📄 Generate Report', 'callback_data': f'generate_report_{session_id}'},
                {'text': '📤 Share Results', 'callback_data': f'share_results_{session_id}'}
            ],
            [
                {'text': '🔄 Retake Quiz', 'callback_data': f'retake_quiz_{quiz_id}'},
                {'text': '🏠 Home', 'callback_data': 'start'}
            ]
        ]
        return KeyboardBuilder.create_inline_keyboard(buttons)

# Predefined keyboards
MAIN_MENU = KeyboardBuilder.main_menu_keyboard()
QUIZ_CREATION = KeyboardBuilder.quiz_creation_keyboard()
TIMER_SELECTION = KeyboardBuilder.timer_selection_keyboard()
FILTER_MANAGEMENT = KeyboardBuilder.filter_management_keyboard()
ASSIGNMENT_MANAGEMENT = KeyboardBuilder.assignment_keyboard()
EXTRACTION_TOOLS = KeyboardBuilder.extraction_tools_keyboard()
ADMIN_PANEL = KeyboardBuilder.admin_keyboard()
QUIZ_TYPES = KeyboardBuilder.quiz_type_keyboard()