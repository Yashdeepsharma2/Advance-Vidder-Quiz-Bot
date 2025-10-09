# Powered by Viddertech
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Creates the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🚀 Create New Quiz", callback_data="create_quiz_menu")],
        [InlineKeyboardButton("📚 My Quizzes", callback_data="my_quizzes_0")], # 0 is the page number
        [InlineKeyboardButton("🌐 Clone from Web/Bot", callback_data="clone_start")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def create_quiz_type_keyboard() -> InlineKeyboardMarkup:
    """Displays options for the type of quiz to create."""
    keyboard = [
        [InlineKeyboardButton("📊 Standard Quiz", callback_data="create_quiz_start_standard")],
        [InlineKeyboardButton("🏃‍♂️ Marathon Quiz (Unlimited)", callback_data="create_quiz_start_marathon")],
        [InlineKeyboardButton("🧩 Sectional Quiz", callback_data="create_quiz_start_sectional")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")],
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

def remove_question_keyboard(questions: list, quiz_id: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Creates a keyboard to select a question to remove."""
    keyboard = []
    for q in questions:
        # Truncate question text for the button
        question_text = (q.text[:40] + '...') if len(q.text) > 40 else q.text
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {question_text}", callback_data=f"remove_q_confirm_{q.id}")
        ])

    pagination_row = []
    if page > 0:
        pagination_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"edit_remove_question_{quiz_id}_{page - 1}"))
    if page < total_pages - 1:
        pagination_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"edit_remove_question_{quiz_id}_{page + 1}"))

    if pagination_row:
        keyboard.append(pagination_row)

    keyboard.append([InlineKeyboardButton("⬅️ Back to Edit Menu", callback_data=f"edit_menu_{quiz_id}")])
    return InlineKeyboardMarkup(keyboard)

def quiz_settings_keyboard(quiz, quiz_id: str) -> InlineKeyboardMarkup:
    """Creates a keyboard for managing quiz settings like negative marking."""

    nm_status = "✅ ON" if quiz.negative_marking else "❌ OFF"

    keyboard = [
        [InlineKeyboardButton(f"Negative Marking: {nm_status}", callback_data=f"toggle_nm_{quiz_id}")],
        [InlineKeyboardButton(f"Set Negative Marks ({quiz.negative_marks} points)", callback_data=f"set_nm_marks_{quiz_id}")],
        [InlineKeyboardButton("⬅️ Back to Edit Menu", callback_data=f"edit_menu_{quiz_id}")],
    ]
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