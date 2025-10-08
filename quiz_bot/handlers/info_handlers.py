from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Welcome to the Viddertech Advance Quiz Bot. I'm here to help you create and manage quizzes. Use /help to see what I can do.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
*Viddertech Advance Quiz Bot Help*

Here are the available commands:
/start - Check if bot is alive
/help - Get this help message
/features - View bot features
/login - Login with TestBook
/telelogin - Login to extract polls
/logout - Logout from server
/post - Broadcast a message
/stopcast - Stop a broadcast
/lang - Select language for TestBook quizzes
/create - Start creating a quiz
/edit - Edit your quiz
/quiz - Clone a quiz from another bot
/done - Finish creating a quiz
/cancel - Stop creating a quiz
/stopedit - Stop editing a quiz
/myquizzes - Get a list of your quizzes
/assignment - Create an assignment
/submit - Submit homework/assignment
/pause - Pause an ongoing quiz
/resume - Resume a paused quiz
/stop - Stop an ongoing quiz
/fast - Speed up quiz in a group
/slow - Slow down quiz in a group
/normal - Reset quiz speed to normal
/addfilter - Add words to your filter list
/removefilter - Remove words from your filter list
/listfilters - Show all your filter words
/clearfilters - Remove all your filter words
/remove - Add words to delete set
/clearlist - Clear the remove words list
/add - Add a user to your paid quiz
/rem - Remove a user from your paid quiz
/remall - Remove all paid users
/ban - Ban a creator
/extract - Create a txt file from polls
/del - Delete a quiz by ID
/stats - Get bot statistics
/info - Get info about the creator

Powered by Viddertech.
    """
    await update.message.reply_text(help_text)


async def features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /features is issued."""
    features_text = """
*📢 Features Showcase of Viddertech Advance Quiz Bot! 🚀*

🔹 Create questions from text just by providing a ✅ mark to the right options.
🔹 Marathon Quiz Mode: Create unlimited questions for a never-ending challenge.
🔹 Convert Polls to Quizzes: Simply forward polls (e.g., from @quizbot), and unnecessary elements will be auto-removed!
🔹 Smart Filtering: Remove unwanted words (e.g., usernames, links) from forwarded polls.
🔹 Skip, Pause & Resume ongoing quizzes anytime.
🔹 Bulk Question Support via ChatGPT output.
🔹 Negative Marking for accurate scoring.
🔹 Edit Existing Quizzes with ease like shuffle title editing timer adding removing questions and many more.
🔹 Quiz Analytics: View engagement, tracking how many users completed the quiz.
🔹 Inline Query Support: Share quizzes instantly via quiz ID.
🔹 Free & Paid Quizzes: Restrict access to selected users/groups—perfect for paid quiz series!
🔹 Assignment Management: Track student responses via bot submissions.
🔹 View Creator Info using the quiz ID.
🔹 Generate Beautiful HTML Reports with score counters, plus light/dark theme support.
🔹 Manage Paid Quizzes: Add/remove users & groups individually or in bulk.
🔹 Video Tutorials: Find detailed guides in the Help section.
🔹 Auto-Send Group Results: No need to copy-paste manually—send all results in one click!
🔹 Create Sectional Quiz: You can create different sections with different timing 🥳.
🔹 Slow/Fast: Slow or fast ongoing quiz.
🔹 OCR Update - Now extract text from PDFs or Photos
🔹 Comparison of Result with accuracy, percentile and percentage
🔹 Create Questions from TXT.
🔹 Advance Mechanism with 99.99% uptime.
🔹 Automated link and username removal from Poll's description and questions.
🔹 Auto txt quiz creation from Wikipedia Britannia bbc news and 20+ articles sites.

*Latest update 🆕*

🔹 Create Questions from Testbook App by test link.
🔹 Auto clone from official quizbot.
🔹 Create from polls/already finishrd quizzes in channels and all try /extract.
🔹 Create from Drishti IAS web Quiz try /quiztxt.

*🚀 Upcoming Features:*

🔸 Advance Engagement saving + later on perspective.
🔸 More optimizations for a smoother experience.
🔸 Suprising Updates...

*📊 Live Tracker & Analysis:*

✅ Topper Comparisons
✅ Detailed Quiz Performance Analytics

Powered by Viddertech.
    """
    await update.message.reply_text(features_text)