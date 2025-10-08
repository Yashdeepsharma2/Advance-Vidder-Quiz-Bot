from telegram import Update
from telegram.ext import ContextTypes

async def not_implemented(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A placeholder for features that are not yet implemented."""
    await update.message.reply_text("This feature is not yet implemented. Stay tuned for future updates!")

# You can alias the function for all the commands that are not ready
login = not_implemented
telelogin = not_implemented
logout = not_implemented
post = not_implemented
stopcast = not_implemented
lang = not_implemented
assignment = not_implemented
submit = not_implemented
pause = not_implemented
resume = not_implemented
fast = not_implemented
slow = not_implemented
normal = not_implemented
addfilter = not_implemented
removefilter = not_implemented
listfilters = not_implemented
clearfilters = not_implemented
remove = not_implemented
clearlist = not_implemented
add = not_implemented
rem = not_implemented
remall = not_implemented
ban = not_implemented
extract = not_implemented
info = not_implemented
quiz_clone = not_implemented # for the /quiz command to clone from other bots
my_stats = not_implemented # The current implementation is basic, a full one can be added later