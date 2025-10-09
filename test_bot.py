#!/usr/bin/env python3
"""
Test script for Advance Vidder Quiz Bot
VidderTech - Advanced Quiz Bot Solution
"""

import sys
import os
import asyncio
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports work correctly"""
    print("🔍 Testing imports...")

    try:
        # Test config import
        from config import config, Messages
        print("✅ Config import successful")

        # Test database imports
        from database.database import db_manager
        from database.models import User, Quiz, Question
        print("✅ Database imports successful")

        # Test handler imports
        from handlers.basic_commands import BasicCommandHandlers
        from handlers.auth_commands import AuthCommandHandlers
        from handlers.quiz_commands import QuizCommandHandlers
        print("✅ Handler imports successful")

        # Test utility imports
        from utils.helpers import QuizHelpers, TextProcessor
        from utils.keyboards import KeyboardBuilder
        print("✅ Utility imports successful")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_setup():
    """Test database setup"""
    print("\n🗄️ Testing database setup...")

    try:
        # Initialize database
        db_manager.init_database()
        print("✅ Database initialized successfully")

        # Test ID generation
        quiz_id = db_manager.generate_id("quiz_")
        question_id = db_manager.generate_id("q_")
        print(f"✅ ID generation working: {quiz_id}, {question_id}")

        return True

    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def test_text_processing():
    """Test text processing utilities"""
    print("\n📝 Testing text processing...")

    try:
        from utils.helpers import QuizHelpers

        # Test question parsing
        test_question = """What is 2+2?
A) 3
B) 4 ✅
C) 5
D) 6"""

        result = QuizHelpers.parse_question_text(test_question)

        if "error" in result:
            print(f"❌ Question parsing failed: {result['error']}")
            return False

        print("✅ Question parsing successful")
        print(f"   Question: {result['question_text']}")
        print(f"   Options: {result['options']}")
        print(f"   Correct: {result['correct_answer']}")

        return True

    except Exception as e:
        print(f"❌ Text processing error: {e}")
        return False

def test_keyboard_generation():
    """Test keyboard generation"""
    print("\n⌨️ Testing keyboard generation...")

    try:
        from utils.keyboards import KeyboardBuilder

        # Test main menu keyboard
        main_menu = KeyboardBuilder.main_menu_keyboard()
        print("✅ Main menu keyboard generated")

        # Test quiz creation keyboard
        quiz_keyboard = KeyboardBuilder.quiz_creation_keyboard()
        print("✅ Quiz creation keyboard generated")

        return True

    except Exception as e:
        print(f"❌ Keyboard generation error: {e}")
        return False

def test_bot_configuration():
    """Test bot configuration"""
    print("\n⚙️ Testing bot configuration...")

    try:
        from config import config

        print(f"✅ Brand name: {config.BRAND_NAME}")
        print(f"✅ Bot version: {config.BOT_VERSION}")
        print(f"✅ Max questions per quiz: {config.MAX_QUESTIONS_PER_QUIZ}")
        print(f"✅ Default question time: {config.DEFAULT_QUESTION_TIME}s")

        # Check if token is set (without exposing it)
        if config.TELEGRAM_BOT_TOKEN:
            print("✅ Telegram bot token is configured")
        else:
            print("⚠️ Telegram bot token not set (expected for testing)")

        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_async_operations():
    """Test async database operations"""
    print("\n🔄 Testing async operations...")

    try:
        from database.models import User, UserRole
        from database.database import db_manager

        # Test user creation
        test_user = User(
            user_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            role=UserRole.USER
        )

        result = await db_manager.create_user(test_user)
        if result:
            print("✅ User creation test passed")
        else:
            print("❌ User creation test failed")
            return False

        # Test user retrieval
        retrieved_user = await db_manager.get_user(12345)
        if retrieved_user and retrieved_user.username == "testuser":
            print("✅ User retrieval test passed")
        else:
            print("❌ User retrieval test failed")
            return False

        # Test bot stats
        stats = await db_manager.get_bot_stats()
        print(f"✅ Bot stats retrieved: {stats.total_users} users")

        return True

    except Exception as e:
        print(f"❌ Async operations error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VidderTech Quiz Bot - System Test")
    print("═" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Database Setup", test_database_setup),
        ("Text Processing", test_text_processing),
        ("Keyboard Generation", test_keyboard_generation),
        ("Bot Configuration", test_bot_configuration)
    ]

    passed = 0
    failed = 0

    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        if test_func():
            passed += 1
        else:
            failed += 1

    # Run async tests
    print(f"\n{'=' * 20} Async Operations {'=' * 20}")
    try:
        if asyncio.run(test_async_operations()):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        failed += 1

    # Summary
    print(f"\n{'=' * 50}")
    print("🎯 TEST SUMMARY")
    print("═" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Bot is ready to run!")
        print("\nNext steps:")
        print("1. Set TELEGRAM_BOT_TOKEN in .env file")
        print("2. Run: python bot.py")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed!")
        print("Please fix the issues before running the bot.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)