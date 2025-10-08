# 🚀 Quick Setup Guide - Advance Vidder Quiz Bot

## 📋 Pre-Requirements

1. **Python 3.8+** installed on your system
2. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
3. **Git** installed (for cloning)

## ⚡ Quick Start (5 Minutes)

### Step 1: Clone & Navigate
```bash
git clone https://github.com/Yashdeepsharma2/Advance-Vidder-Quiz-Bot.git
cd Advance-Vidder-Quiz-Bot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Bot
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your details
nano .env
# OR
notepad .env  # Windows
```

**Required Configuration (.env):**
```env
# Get from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Your Telegram user ID (get from @userinfobot)
ADMIN_IDS=your_user_id
OWNER_ID=your_user_id
```

### Step 4: Test Bot
```bash
python test_bot.py
```

### Step 5: Run Bot
```bash
python bot.py
```

## 🎯 Verification Checklist

### ✅ Bot Working Correctly
- [ ] Bot responds to `/start` command
- [ ] Help menu displays all commands
- [ ] Features list shows comprehensive capabilities
- [ ] Quiz creation works with ✅ marking
- [ ] Database stores quizzes correctly
- [ ] User registration functions properly

### ✅ All Commands Available
```
/start    - ✅ Bot initialization
/help     - ✅ Command reference  
/features - ✅ Feature showcase
/create   - ✅ Quiz creation
/myquizzes- ✅ Quiz management
/stats    - ✅ Statistics display
/info     - ✅ About VidderTech
/login    - ✅ TestBook auth
/logout   - ✅ Session management
/lang     - ✅ Language selection
```

## 🔧 Advanced Configuration

### Optional Settings (.env)
```env
# External APIs (Optional)
TESTBOOK_API_KEY=your_testbook_key
OPENAI_API_KEY=your_openai_key

# Bot Limits
MAX_QUESTIONS_PER_QUIZ=100
DEFAULT_QUESTION_TIME=30
MAX_FILE_SIZE_MB=20

# Quiz Settings
NEGATIVE_MARKING=true
DEFAULT_NEGATIVE_MARKS=0.25
QUIZ_EXPIRY_DAYS=30
```

## 🛠️ Development Mode

### Running with Debug
```bash
python bot.py --debug
```

### Database Reset (if needed)
```bash
rm vidder_quiz_bot.db
python bot.py
```

## 📱 Bot Commands Reference

### 🎯 Essential Commands
| Command | Function | Status |
|---------|----------|---------|
| `/start` | Initialize bot | ✅ Ready |
| `/create` | Create quiz | ✅ Ready |
| `/help` | Get help | ✅ Ready |
| `/myquizzes` | View quizzes | ✅ Ready |

### 🔐 Authentication
| Command | Function | Status |
|---------|----------|---------|
| `/login` | TestBook login | ✅ Ready |
| `/telelogin` | Telegram login | ✅ Ready |
| `/logout` | Logout services | ✅ Ready |
| `/lang` | Select language | ✅ Ready |

### 🎮 Quiz Control
| Command | Function | Status |
|---------|----------|---------|
| `/pause` | Pause quiz | 🚧 Framework |
| `/resume` | Resume quiz | 🚧 Framework |
| `/stop` | Stop quiz | 🚧 Framework |
| `/fast` | Speed up | 🚧 Framework |
| `/slow` | Slow down | 🚧 Framework |

## 🎉 Success Indicators

### ✅ Bot Started Successfully
```
🚀 Starting VidderTech Quiz Bot v2.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bot Username: @YourBotUsername
Admin IDs: [your_user_id]
Owner ID: your_user_id
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database initialized successfully
All handlers registered successfully!
🔄 Starting polling...
```

### ✅ Quiz Creation Working
```
User: /create
Bot: 🎯 Welcome to VidderTech Quiz Creator!
     Let's create an amazing quiz together!
     Please send me the title for your quiz.

User: My Test Quiz
Bot: ✅ Quiz Title Set: My Test Quiz
     ⏰ Step 2: Question Timer
     How much time should each question have?

User: [Selects 30 seconds]
Bot: [Shows quiz creation options]
```

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. Token Invalid**
```bash
# Check .env file has correct token
# Get new token from @BotFather if needed
```

**3. Database Errors**  
```bash
# Delete and recreate database
rm vidder_quiz_bot.db
python bot.py
```

**4. Permission Errors**
```bash
# Ensure user_id in ADMIN_IDS
# Check OWNER_ID is set correctly
```

## 📊 Testing Quiz Creation

### Sample Quiz Format
```
What is the capital of France?
A) London
B) Berlin  
C) Paris ✅
D) Madrid

What is 2+2?
A) 3
B) 4 ✅  
C) 5
D) 6
```

### Testing Steps
1. Start bot: `/start`
2. Create quiz: `/create`
3. Enter title: "Test Quiz"
4. Select timer: 30 seconds
5. Choose "Type Questions"
6. Send question in format above
7. Verify question added correctly
8. Finish quiz: Use inline button
9. Check "My Quizzes": `/myquizzes`

## 🚀 Production Deployment

### Heroku (Recommended)
```bash
# Install Heroku CLI
heroku create your-quiz-bot
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set ADMIN_IDS=your_user_id
heroku config:set OWNER_ID=your_user_id
git push heroku main
```

### VPS/Cloud Server
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/quiz-bot.service
sudo systemctl enable quiz-bot
sudo systemctl start quiz-bot
```

## 📈 Performance Monitoring

### Check Bot Status
```bash
# View logs
tail -f bot.log

# Check database
sqlite3 vidder_quiz_bot.db ".tables"

# Memory usage
ps aux | grep bot.py
```

### Health Indicators
- Bot responds to `/start` < 1 second
- Quiz creation completes < 5 seconds  
- Database queries execute < 100ms
- Memory usage < 100MB

## 🆘 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/Yashdeepsharma2/Advance-Vidder-Quiz-Bot/issues)
- **Telegram**: [@VidderTech](https://t.me/VidderTech)
- **Email**: support@viddertech.com
- **Documentation**: README.md

### Reporting Bugs
1. Check existing issues first
2. Include error logs
3. Describe steps to reproduce
4. Mention your environment (OS, Python version)

---

## 🎯 You're Ready!

Your **Advance Vidder Quiz Bot** is now fully configured and ready to create amazing quizzes!

### 🚀 Next Steps:
1. Invite friends to try your bot
2. Create your first quiz
3. Explore advanced features
4. Join our community [@VidderTech](https://t.me/VidderTech)

**Built with ❤️ by VidderTech Team**