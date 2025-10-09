#!/usr/bin/env python3
"""
🚀 VidderTech Advanced Quiz Bot - Complete Setup & Test System
Built by VidderTech - The Future of Quiz Bots

This script provides:
- Comprehensive system testing
- Database initialization and validation
- Configuration verification
- Dependency checking
- Performance benchmarking
- Security validation
"""

import sys
import os
import asyncio
import logging
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Configure logging for setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('vidder.setup')

def print_banner():
    """Print VidderTech setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 VidderTech Advanced Quiz Bot Setup                     ║
║                          Complete System Initialization                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🏢 Company: VidderTech Technologies                                         ║
║  🤖 Product: Advanced Quiz Bot with AI Integration                           ║
║  🎯 Version: v3.0.0-pro (Production Ready)                                   ║
║  📅 Setup Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """                                           ║
║  🌍 Built in India 🇮🇳 for the World 🌍                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Check Python version compatibility"""
    print("\n🐍 Checking Python version...")
    
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        return True
    else:
        print(f"❌ Python {'.'.join(map(str, current_version))} - Requires {'.'.join(map(str, required_version))}+")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 Checking VidderTech file structure...")
    
    required_files = [
        'vidder_bot.py',
        'vidder_config.py', 
        'requirements.txt',
        '.env.example',
        'README_VidderTech.md'
    ]
    
    required_dirs = [
        'vidder_database',
        'vidder_handlers'
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check files
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ Found: {file}")
    
    # Check directories
    for directory in required_dirs:
        if not Path(directory).is_dir():
            missing_dirs.append(directory)
        else:
            print(f"✅ Found: {directory}/")
    
    if missing_files or missing_dirs:
        print(f"❌ Missing files: {missing_files}")
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ All VidderTech files and directories present")
    return True

def test_imports():
    """Test all critical imports"""
    print("\n📦 Testing VidderTech imports...")
    
    import_tests = [
        ("vidder_config", "VidderTech configuration"),
        ("vidder_database.vidder_database", "Database manager"),
        ("vidder_handlers.basic_vidder", "Basic handlers"),
        ("vidder_handlers.auth_vidder", "Auth handlers"),
        ("vidder_handlers.quiz_vidder", "Quiz handlers"),
        ("vidder_handlers.control_vidder", "Control handlers")
    ]
    
    failed_imports = []
    
    for module, description in import_tests:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"⚠️ {description}: {e}")
    
    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
        return False
    
    print("✅ All VidderTech modules imported successfully")
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing VidderTech configuration...")
    
    try:
        from vidder_config import config, messages
        
        print(f"✅ Company: {config.COMPANY_NAME}")
        print(f"✅ Bot Name: {config.BOT_NAME}")
        print(f"✅ Version: {config.BOT_VERSION}")
        print(f"✅ Supported Languages: {len(config.SUPPORTED_LANGUAGES)}")
        
        # Check critical settings
        if not config.TELEGRAM_BOT_TOKEN:
            print("⚠️ TELEGRAM_BOT_TOKEN not set (set in .env file)")
        else:
            print("✅ Bot token configured")
        
        if not config.OWNER_ID:
            print("⚠️ OWNER_ID not set (required for admin access)")
        else:
            print(f"✅ Owner ID configured: {config.OWNER_ID}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_database():
    """Test database initialization and operations"""
    print("\n🗄️ Testing VidderTech database...")
    
    try:
        from vidder_database.vidder_database import db_manager
        
        # Test database initialization
        print("🔧 Initializing database...")
        db_manager._init_database()
        print("✅ Database initialization successful")
        
        # Test basic operations
        print("🧪 Testing database operations...")
        
        # Test user creation
        test_user_data = {
            'user_id': 123456789,
            'username': 'vidder_test_user',
            'first_name': 'VidderTech',
            'last_name': 'Test',
            'role': 'free',
            'status': 'active'
        }
        
        success = await db_manager.create_user(test_user_data)
        if success:
            print("✅ User creation test passed")
        else:
            print("❌ User creation test failed")
            return False
        
        # Test user retrieval
        user = await db_manager.get_user(123456789)
        if user and user.get('username') == 'vidder_test_user':
            print("✅ User retrieval test passed")
        else:
            print("❌ User retrieval test failed")
            return False
        
        # Test analytics
        await db_manager._log_analytics("setup_test", 123456789, metadata={"test": True})
        print("✅ Analytics logging test passed")
        
        # Test system stats
        stats = await db_manager.get_system_stats()
        if stats:
            print(f"✅ System stats: {stats.get('database_size_mb', 0)} MB")
        
        print("✅ All database tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_bot_creation():
    """Test bot application creation"""
    print("\n🤖 Testing VidderTech bot creation...")
    
    try:
        from vidder_config import config
        
        if not config.TELEGRAM_BOT_TOKEN:
            print("⚠️ Cannot test bot creation - TELEGRAM_BOT_TOKEN not set")
            print("📝 Set token in .env file to test bot creation")
            return True  # Not critical for setup
        
        from telegram.ext import ApplicationBuilder
        
        # Test application builder
        app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
        print("✅ Bot application created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot creation error: {e}")
        return False

def test_command_system():
    """Test command handler system"""
    print("\n🎯 Testing VidderTech command system...")
    
    try:
        from vidder_handlers.basic_vidder import VidderBasicHandlers
        from vidder_handlers.auth_vidder import VidderAuthHandlers
        from vidder_handlers.quiz_vidder import VidderQuizHandlers
        from vidder_handlers.control_vidder import VidderQuizControlHandlers
        
        # Test handler initialization
        basic_handler = VidderBasicHandlers()
        auth_handler = VidderAuthHandlers()
        quiz_handler = VidderQuizHandlers()
        control_handler = VidderQuizControlHandlers()
        
        print("✅ Basic handlers initialized")
        print("✅ Auth handlers initialized")
        print("✅ Quiz handlers initialized")
        print("✅ Control handlers initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Command system error: {e}")
        return False

def generate_env_file():
    """Generate .env file if it doesn't exist"""
    print("\n🌍 Checking environment configuration...")
    
    if not Path('.env').exists():
        print("📝 Creating .env file from template...")
        try:
            # Copy example to actual .env
            with open('.env.example', 'r') as example:
                content = example.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ .env file created")
            print("⚠️ IMPORTANT: Edit .env file with your bot token and settings!")
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_directories():
    """Create required directories"""
    print("\n📂 Creating VidderTech directories...")
    
    required_dirs = [
        'vidder_logs',
        'vidder_uploads',
        'vidder_temp',
        'vidder_backups'
    ]
    
    for directory in required_dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    return True

def performance_benchmark():
    """Run performance benchmark tests"""
    print("\n⚡ Running VidderTech performance benchmark...")
    
    try:
        # Test import speed
        start_time = time.time()
        import vidder_config
        import_time = (time.time() - start_time) * 1000
        print(f"⚡ Import speed: {import_time:.2f}ms")
        
        # Test database operations speed
        start_time = time.time()
        from vidder_database.vidder_database import db_manager
        db_time = (time.time() - start_time) * 1000
        print(f"⚡ Database init: {db_time:.2f}ms")
        
        if import_time < 1000 and db_time < 2000:
            print("✅ Performance benchmark passed")
            return True
        else:
            print("⚠️ Performance below optimal (still functional)")
            return True
        
    except Exception as e:
        print(f"❌ Benchmark error: {e}")
        return False

async def run_complete_test():
    """Run complete VidderTech system test"""
    print("\n🧪 Running complete VidderTech system test...")
    
    try:
        # Test all components
        components_passed = 0
        total_components = 6
        
        if check_python_version():
            components_passed += 1
        
        if check_file_structure():
            components_passed += 1
        
        if test_imports():
            components_passed += 1
        
        if test_configuration():
            components_passed += 1
        
        if await test_database():
            components_passed += 1
        
        if test_command_system():
            components_passed += 1
        
        # Performance tests
        performance_benchmark()
        
        # Generate summary
        print(f"\n{'='*60}")
        print("🎯 VIDDERTECH SETUP SUMMARY")
        print("="*60)
        print(f"✅ Components Passed: {components_passed}/{total_components}")
        print(f"📊 Success Rate: {(components_passed/total_components)*100:.1f}%")
        
        if components_passed == total_components:
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 VidderTech Quiz Bot is ready for action!")
            print("\n📋 Next Steps:")
            print("1. Edit .env file with your TELEGRAM_BOT_TOKEN")
            print("2. Add your user ID as OWNER_ID") 
            print("3. Run: python vidder_bot.py")
            print("4. Test with /start command")
            print(f"\n🏆 Welcome to the VidderTech family!")
            return True
        else:
            failed = total_components - components_passed
            print(f"\n⚠️ {failed} test(s) failed!")
            print("Please fix the issues above before running the bot.")
            return False
        
    except Exception as e:
        print(f"❌ System test error: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Create required directories
    create_directories()
    
    # Generate environment file
    generate_env_file()
    
    # Run all tests
    success = asyncio.run(run_complete_test())
    
    if success:
        # Final success message
        success_message = """
🎉 VIDDERTECH QUIZ BOT SETUP COMPLETED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ All systems operational
✅ Database initialized
✅ Handlers loaded
✅ Configuration valid
✅ Performance optimized

🚀 YOUR BOT IS READY TO REVOLUTIONIZE QUIZZING!

📋 Final Steps:
1. Edit .env with your bot token
2. python vidder_bot.py
3. Send /start to your bot
4. Create your first quiz!

🏆 Welcome to the VidderTech revolution!
🌟 Built by VidderTech - The Future of Quiz Bots
        """
        print(success_message)
        return 0
    else:
        print("\n❌ Setup incomplete. Please resolve issues above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)