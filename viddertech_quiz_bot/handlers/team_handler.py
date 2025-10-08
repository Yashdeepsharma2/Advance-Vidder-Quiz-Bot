# Powered by Viddertech
from telegram import Update
from telegram.ext import ContextTypes
from viddertech_quiz_bot.handlers.quiz_handler import send_next_question

async def create_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Creates a new team in the chat."""
    try:
        team_name = context.args[0]
    except IndexError:
        await update.message.reply_text("Please provide a team name. Usage: /team_create <team_name>")
        return

    if 'teams' not in context.chat_data:
        context.chat_data['teams'] = {}

    if team_name in context.chat_data['teams']:
        await update.message.reply_text(f"A team with the name '{team_name}' already exists.")
        return

    context.chat_data['teams'][team_name] = {'members': {}}
    await update.message.reply_text(f"Team '{team_name}' has been created! Use /team_join {team_name} to join.")


async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allows a user to join a team."""
    try:
        team_name = context.args[0]
    except IndexError:
        await update.message.reply_text("Please provide a team name. Usage: /team_join <team_name>")
        return

    user = update.effective_user

    if 'teams' not in context.chat_data or team_name not in context.chat_data['teams']:
        await update.message.reply_text(f"Team '{team_name}' does not exist.")
        return

    # Remove user from any other team they might be in
    for name, team_data in context.chat_data['teams'].items():
        if user.id in team_data['members']:
            del team_data['members'][user.id]
            await update.message.reply_text(f"{user.full_name} has left team '{name}'.")

    context.chat_data['teams'][team_name]['members'][user.id] = user.full_name
    await update.message.reply_text(f"{user.full_name} has joined team '{team_name}'!")


async def view_teams(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the current teams and their members."""
    if 'teams' not in context.chat_data or not context.chat_data['teams']:
        await update.message.reply_text("No teams have been created yet. Use /team_create to start one.")
        return

    message = "<b>Current Teams:</b>\n\n"
    for team_name, team_data in context.chat_data['teams'].items():
        message += f"<b>Team: {team_name}</b>\n"
        if team_data['members']:
            for member_name in team_data['members'].values():
                message += f"- {member_name}\n"
        else:
            message += "- (empty)\n"
        message += "\n"
    await update.message.reply_html(message)


async def team_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts a quiz in team mode."""
    if 'current_quiz' in context.chat_data:
        await update.message.reply_text("A quiz is already in progress in this chat.")
        return

    if 'teams' not in context.chat_data or len(context.chat_data['teams']) < 2:
        await update.message.reply_text("You need at least two teams to start a team quiz. Use /team_create and /team_join.")
        return

    try:
        shareable_id = context.args[0]
        _, creator_id_str, quiz_id = shareable_id.split('_')
        creator_id = int(creator_id_str)
        quiz = context.bot_data['quizzes'][creator_id][quiz_id]
    except (IndexError, ValueError, KeyError):
        await update.message.reply_text("Invalid Share ID. Usage: /team_quiz <Share ID>")
        return

    context.chat_data['current_quiz'] = {
        'quiz_data': quiz,
        'current_question': 0,
        'scores': {},
        'is_active': True,
        'is_team_mode': True,
        'creator_id': creator_id
    }

    await update.message.reply_text(f"Starting team quiz: <b>{quiz['title']}</b>!", parse_mode='HTML')
    await send_next_question(update.effective_chat.id, context)