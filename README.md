# 🚀 Advance Vidder Quiz Bot

**The Most Advanced Quiz Bot on Telegram** - Built by VidderTech

A comprehensive Python Telegram bot for creating, managing, and conducting interactive quizzes with advanced features like TestBook integration, OCR support, analytics, and much more.

## ✨ Features

### 🎯 Core Quiz Features
- **Smart Quiz Creation** - Create questions with ✅ marking system
- **Marathon Quiz Mode** - Unlimited questions for continuous learning
- **Sectional Quizzes** - Different sections with custom timing
- **Multiple Quiz Types** - Free, Paid, Assignment, Marathon modes
- **Advanced Timer Control** - Customizable time per question (5-600 seconds)
- **Negative Marking** - Configurable penalty system for wrong answers
- **Question Shuffling** - Randomize questions and options
- **Real-time Analytics** - Track engagement and performance

### 🔄 Content Import & Integration
- **TestBook Integration** - Import questions directly from TestBook tests
- **Poll Conversion** - Convert Telegram polls to interactive quizzes
- **Web Scraping** - Extract content from Wikipedia, BBC, Britannica, and 20+ sites
- **OCR Support** - Extract text from PDFs and images
- **QuizBot Cloning** - Import from official @quizbot
- **Bulk Import** - Process multiple questions at once

### 🎮 Interactive Quiz Experience
- **Real-time Hosting** - Live quiz sessions in groups
- **Speed Control** - Fast/Slow/Normal quiz modes
- **Pause & Resume** - Full control over quiz flow  
- **Live Leaderboards** - Real-time scoring and rankings
- **Detailed Results** - Comprehensive performance analysis
- **Beautiful Reports** - HTML reports with light/dark themes

### 🔧 Advanced Management
- **Smart Filtering** - Remove unwanted words, links, usernames
- **User Access Control** - Paid quiz restrictions and permissions
- **Assignment System** - Track student submissions and progress
- **Broadcasting** - Admin message distribution system
- **Multi-language Support** - 10+ Indian languages supported
- **Inline Queries** - Share quizzes instantly via quiz ID

### 📊 Analytics & Insights
- **Performance Tracking** - Individual and group analytics
- **Percentile Calculations** - Compare with other participants
- **Trend Analysis** - Track improvement over time
- **Engagement Metrics** - Quiz completion rates and statistics
- **Export Capabilities** - Generate detailed HTML reports

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Optional: TestBook API access for advanced features

### Quick Setup

1. **Clone Repository**
```bash
git clone https://github.com/Yashdeepsharma2/Advance-Vidder-Quiz-Bot.git
cd Advance-Vidder-Quiz-Bot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Environment Variables**
```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=your_user_id,another_admin_id
OWNER_ID=your_user_id

# Optional
TESTBOOK_API_KEY=your_testbook_api_key
OPENAI_API_KEY=your_openai_api_key
```

5. **Run the Bot**
```bash
python bot.py
```

## 📋 Command Reference

### 🎯 Basic Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Get comprehensive command help |
| `/features` | View all bot features |
| `/info` | About VidderTech and bot information |
| `/stats` | View bot and personal statistics |

### 📝 Quiz Management
| Command | Description |
|---------|-------------|
| `/create` | Start creating a new quiz |
| `/done` | Finish current quiz creation |
| `/cancel` | Cancel quiz creation process |
| `/myquizzes` | View your created quizzes |
| `/edit quiz_id` | Edit existing quiz |
| `/del quiz_id` | Delete a quiz |
| `/quiz quiz_id` | Clone quiz from other bots |

### 🔐 Authentication
| Command | Description |
|---------|-------------|
| `/login` | Login to TestBook for content import |
| `/telelogin` | Login to Telegram for poll extraction |
| `/logout` | Logout from all services |
| `/lang` | Select language for TestBook quizzes |

### ⚡ Quiz Control (During Active Quiz)
| Command | Description |
|---------|-------------|
| `/pause` | Pause current quiz temporarily |
| `/resume` | Resume paused quiz |
| `/stop` | Stop ongoing quiz completely |
| `/fast` | Speed up quiz (reduce time per question) |
| `/slow` | Slow down quiz (increase time per question) |
| `/normal` | Reset to normal quiz speed |

### 📝 Assignments
| Command | Description |
|---------|-------------|
| `/assignment` | Create assignment for students |
| `/submit` | Submit assignment work (student command) |

### 🔧 Content Filtering
| Command | Description |
|---------|-------------|
| `/addfilter word1,word2` | Add words to filter list |
| `/removefilter word1,word2` | Remove words from filter list |
| `/listfilters` | Show all your filter words |
| `/clearfilters` | Clear all filter words |
| `/remove word1,word2` | Add words to deletion list |
| `/clearlist` | Clear removal words list |

### 👥 User Management (Quiz Creators)
| Command | Description |
|---------|-------------|
| `/add @username` | Add user to paid quiz access |
| `/rem @username` | Remove user from paid quiz access |
| `/remall` | Remove all users from paid quiz access |

### 🔍 Content Extraction
| Command | Description |
|---------|-------------|
| `/extract start_link end_link` | Extract questions from post range |

### 📢 Admin Commands
| Command | Description |
|---------|-------------|
| `/post` | Broadcast message to all users |
| `/stopcast` | Stop ongoing broadcast |
| `/ban @username` | Ban user from bot |

## 🎯 Quiz Creation Guide

### Method 1: Text-based Creation (Recommended)
```
What is the capital of France?
A) London
B) Berlin
C) Paris ✅
D) Madrid
```

### Method 2: Poll Forwarding
1. Forward any Telegram poll to the bot
2. Bot automatically converts it to a quiz
3. Unwanted elements like [1/100] are auto-removed

### Method 3: TestBook Integration
1. Use `/login` to authenticate with TestBook
2. Provide TestBook test link
3. Bot extracts all questions automatically

### Method 4: Bulk Import
```
Question 1 text here?
A) Option 1
B) Option 2 ✅
C) Option 3
D) Option 4

---

Question 2 text here?
A) Option 1 ✅
B) Option 2
C) Option 3
```

## 🏗️ Architecture

```
├── bot.py                    # Main bot entry point
├── config.py                 # Configuration and constants
├── requirements.txt          # Dependencies
├── handlers/                 # Command handlers
│   ├── basic_commands.py     # Basic bot commands
│   ├── auth_commands.py      # Authentication handlers
│   ├── quiz_commands.py      # Quiz management
│   └── ...
├── database/                 # Database layer
│   ├── models.py            # Data models
│   └── database.py          # Database operations
├── utils/                   # Utility functions
│   ├── keyboards.py         # Telegram keyboards
│   ├── helpers.py           # Helper functions
│   └── ...
└── integrations/           # External integrations
    ├── testbook.py         # TestBook API
    ├── ocr_processor.py    # OCR functionality
    └── ...
```

## 🔧 Configuration Options

### Quiz Settings
```python
# Default question time (15-600 seconds)
DEFAULT_QUESTION_TIME = 30

# Maximum questions per quiz
MAX_QUESTIONS_PER_QUIZ = 100

# Negative marking settings
NEGATIVE_MARKING = True
DEFAULT_NEGATIVE_MARKS = 0.25

# Quiz expiry (days)
QUIZ_EXPIRY_DAYS = 30
```

### File & OCR Settings
```python
# Maximum upload file size (MB)
MAX_FILE_SIZE_MB = 20

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "bmp", "pdf"]

# Tesseract OCR path
TESSERACT_CMD = "tesseract"
```

## 📊 Database Schema

### Core Tables
- **users** - User profiles and authentication
- **quizzes** - Quiz metadata and settings
- **questions** - Individual quiz questions
- **quiz_sessions** - Active quiz instances
- **responses** - User answers and scores
- **analytics** - Event tracking and statistics

### Advanced Tables
- **filters** - Word filtering preferences
- **assignments** - Student assignment tracking
- **broadcasts** - Admin message distribution
- **bot_stats** - System performance metrics

## 🚀 Advanced Features

### 1. Sectional Quizzes
Create quizzes with different sections, each having custom timing:
```json
{
  "sections": [
    {"name": "Mathematics", "time": 60, "questions": 20},
    {"name": "Physics", "time": 45, "questions": 15},
    {"name": "Chemistry", "time": 30, "questions": 10}
  ]
}
```

### 2. Marathon Mode
Unlimited questions for continuous practice with automatic difficulty adjustment.

### 3. AI-Powered Analytics
- Performance trend analysis
- Personalized difficulty recommendations
- Weakness identification and improvement suggestions

### 4. Multi-language Support
Supports content in:
- English, Hindi, Gujarati, Marathi
- Bengali, Tamil, Telugu, Kannada
- Malayalam, Odia

## 📈 Performance & Scalability

### Optimizations
- **Database Indexing** - Optimized queries for large datasets
- **Caching** - Redis-ready for high-traffic deployments
- **Async Operations** - Non-blocking database operations
- **Rate Limiting** - Prevent spam and abuse

### Monitoring
- **Real-time Analytics** - Track bot usage patterns
- **Error Logging** - Comprehensive error tracking
- **Performance Metrics** - Response time monitoring
- **Uptime Tracking** - 99.99% availability guarantee

## 🛡️ Security Features

### Data Protection
- **Encrypted Storage** - Sensitive data encryption
- **Secure Authentication** - OAuth-style token management
- **Privacy Controls** - User data access controls
- **GDPR Compliance** - Data protection compliance

### Access Control
- **Role-based Permissions** - Admin, Premium, User roles
- **Paid Quiz Protection** - Access restriction system
- **Rate Limiting** - Anti-spam protection
- **Banned User Management** - Comprehensive ban system

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_quiz_creation.py
pytest tests/test_database.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Coverage
- Unit tests for all core functions
- Integration tests for external APIs
- Database operation testing
- Command handler testing

## 🚀 Deployment

### Local Development
```bash
python bot.py
```

### Production Deployment

#### Docker (Recommended)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
```

#### Heroku
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### VPS/Cloud Server
```bash
# Install as systemd service
sudo cp vidder-quiz-bot.service /etc/systemd/system/
sudo systemctl enable vidder-quiz-bot
sudo systemctl start vidder-quiz-bot
```

## 📝 API Documentation

### Webhook Integration
```python
# Set webhook for production
await bot.set_webhook(
    url="https://yourapp.com/webhook",
    secret_token="your_secret_token"
)
```

### Database API
```python
# Create quiz
quiz = Quiz(title="My Quiz", creator_id=user_id)
await db_manager.create_quiz(quiz)

# Add questions
question = Question(quiz_id=quiz_id, text="Question?", options=["A", "B"])
await db_manager.add_question(question)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Write comprehensive docstrings
- Include unit tests for new features

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

### Getting Help
- **Documentation**: Comprehensive guides and API reference
- **Issues**: [GitHub Issues](https://github.com/Yashdeepsharma2/Advance-Vidder-Quiz-Bot/issues)
- **Telegram**: [@VidderTech](https://t.me/VidderTech)
- **Email**: support@viddertech.com

### Community
- **Telegram Channel**: [@VidderTech](https://t.me/VidderTech)
- **Updates**: Follow for bot updates and new features
- **Feedback**: Share your suggestions and feature requests

## 🏆 About VidderTech

**VidderTech** is a leading technology company specializing in innovative Telegram bot solutions. We create powerful, scalable, and user-friendly tools that enhance productivity and engagement.

### Our Products
- **Quiz Bots** - Advanced quiz management systems
- **Utility Bots** - Productivity and automation tools
- **Custom Solutions** - Tailored bot development services

### Contact Us
- **Website**: [https://viddertech.com](https://viddertech.com)
- **Email**: contact@viddertech.com
- **Telegram**: [@VidderTech](https://t.me/VidderTech)
- **Support**: support@viddertech.com

---

## 🎯 Quick Start Example

```python
# Create a simple quiz
/start
# Click "Create Quiz"
# Enter title: "General Knowledge Quiz"
# Select 30 seconds per question
# Add questions using ✅ format:

What is 2+2?
A) 3
B) 4 ✅
C) 5
D) 6

# Click "Finish Quiz"
# Share quiz ID with others!
```

## 🔮 Roadmap

### Version 2.1 (Coming Soon)
- [ ] Advanced AI question generation
- [ ] Voice message support
- [ ] Video question integration
- [ ] Advanced analytics dashboard

### Version 2.2 (Future)
- [ ] Mobile app integration
- [ ] Blockchain-based certificates
- [ ] VR quiz experiences
- [ ] Global leaderboards

---

**Built with ❤️ by VidderTech Team**

*Making learning interactive and fun, one quiz at a time!*

🚀 **Start creating amazing quizzes today!**