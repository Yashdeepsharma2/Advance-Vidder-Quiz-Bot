# Powered by Viddertech
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Creates the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🚀 Create New Quiz", callback_data="create_quiz_start")],
        [InlineKeyboardButton("📚 My Quizzes", callback_data="my_quizzes_0")], # 0 is the page number
        [InlineKeyboardButton("🌐 Clone from Web/Bot", callback_data="clone_start")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def my_quizzes_keyboard(quizzes: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Creates an interactive keyboard for the user's list of quizzes with pagination."""
    keyboard = []
    for quiz in quizzes:
        keyboard.append([
            InlineKeyboardButton(f"▶️ Play '{quiz.title}'", callback_data=f"play_{quiz.id}"),
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{quiz.id}"),
            InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_start_{quiz.id}"),
        ])

    # Pagination controls
    pagination_row = []
    if page > 0:
        pagination_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"my_quizzes_{page - 1}"))
    if page < total_pages - 1:
        pagination_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"my_quizzes_{page + 1}"))

    if pagination_row:
        keyboard.append(pagination_row)

    keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def delete_confirmation_keyboard(quiz_id: str) -> InlineKeyboardMarkup:
    """Creates a confirmation keyboard for deleting a quiz."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Delete It", callback_data=f"delete_confirm_{quiz_id}"),
            InlineKeyboardButton("❌ No, Go Back", callback_data=f"my_quizzes_0"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def quiz_edit_keyboard(quiz_id: str) -> InlineKeyboardMarkup:
    """Creates a keyboard for quiz editing options."""
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Title", callback_data=f"edit_title_{quiz_id}")],
        [InlineKeyboardButton("➕ Add Question", callback_data=f"edit_add_question_{quiz_id}")],
        [InlineKeyboardButton("🗑️ Remove Question", callback_data=f"edit_remove_question_{quiz_id}")],
        [InlineKeyboardButton("⚙️ Settings (Timer, etc.)", callback_data=f"edit_settings_{quiz_id}")],
        [InlineKeyboardButton("⬅️ Back to My Quizzes", callback_data="my_quizzes_0")],
    ]
    return InlineKeyboardMarkup(keyboard)