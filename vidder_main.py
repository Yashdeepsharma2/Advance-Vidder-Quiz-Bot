#!/usr/bin/env python3
"""
🚀 VidderTech Advanced Quiz Bot - Main Entry Point
Built by VidderTech - The Future of Quiz Bots

Main bot initialization and startup with comprehensive features:
- 35+ Advanced commands with full functionality
- Real-time quiz hosting and management
- Advanced authentication and user management
- Multi-language support (15+ languages)
- Enterprise-grade security and monitoring
- AI-powered features and analytics
"""

import asyncio
import logging
import sys
import signal
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core imports
from vidder_core.vidder_app import VidderApplication
from vidder_core.vidder_manager import VidderBotManager
from vidder_core.vidder_monitor import VidderSystemMonitor
from vidder_config import VidderConfig
from vidder_logs.vidder_logger import VidderLogger

# Initialize VidderTech logger
logger = VidderLogger.get_logger('vidder.main')

class VidderTechBot:
    """
    🚀 VidderTech Advanced Quiz Bot
    Main bot class with enterprise-grade features
    """
    
    def __init__(self):
        """Initialize VidderTech bot with comprehensive setup"""
        self.config = VidderConfig()
        self.app = None
        self.manager = None
        self.monitor = None
        self.start_time = datetime.now()
        self.is_running = False
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("🚀 VidderTech Advanced Quiz Bot initializing...")
        
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Initialize all bot components"""
        try:
            # Validate configuration
            if not self.config.validate():
                raise ValueError("❌ Invalid configuration. Please check your settings.")
            
            logger.info("⚙️ Initializing VidderTech components...")
            
            # Initialize bot application
            self.app = VidderApplication(self.config)
            await self.app.initialize()
            
            # Initialize bot manager
            self.manager = VidderBotManager(self.app, self.config)
            await self.manager.initialize()
            
            # Initialize system monitor
            self.monitor = VidderSystemMonitor(self.config)
            await self.monitor.start()
            
            logger.info("✅ All VidderTech components initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize VidderTech bot: {e}")
            raise
    
    async def start(self):
        """Start the VidderTech bot"""
        try:
            await self.initialize()
            
            # Display startup banner
            self._display_startup_banner()
            
            # Start the bot
            self.is_running = True
            logger.info("🚀 Starting VidderTech Advanced Quiz Bot...")
            
            await self.manager.start()
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("🔄 Initiating VidderTech bot shutdown...")
        
        try:
            # Shutdown components in reverse order
            if self.monitor:
                await self.monitor.stop()
                logger.info("📊 System monitor stopped")
            
            if self.manager:
                await self.manager.stop()
                logger.info("🎮 Bot manager stopped")
            
            if self.app:
                await self.app.shutdown()
                logger.info("🤖 Bot application stopped")
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            logger.info(f"⏱️ Total uptime: {uptime}")
            
            logger.info("✅ VidderTech bot shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def _display_startup_banner(self):
        """Display VidderTech startup banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    🚀 VidderTech Advanced Quiz Bot                    ║
║                     The Future of Quiz Bots                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  Version: {self.config.BOT_VERSION:<20} Build: {self.config.BUILD_NUMBER:<20}  ║
║  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<20} Mode: {self.config.ENVIRONMENT:<21}   ║
╠══════════════════════════════════════════════════════════════════════╣
║  🎯 Features: 35+ Advanced Commands                                  ║
║  🗄️ Database: Advanced SQLite with 12+ Tables                      ║
║  🔐 Security: Enterprise-grade Authentication                        ║
║  🌍 Languages: 15+ Multi-language Support                           ║
║  🤖 AI: Machine Learning Powered Features                           ║
║  📊 Analytics: Real-time Monitoring & Reporting                     ║
║  🚀 Deployment: Production-ready Architecture                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  📧 Support: support@viddertech.com                                  ║
║  🌐 Website: https://viddertech.com                                  ║
║  📱 Telegram: @VidderTech                                            ║
╚══════════════════════════════════════════════════════════════════════╝

🔥 Starting advanced quiz bot with enterprise features...
"""
        print(banner)
        logger.info("🎨 VidderTech startup banner displayed")

async def main():
    """Main entry point for VidderTech bot"""
    
    # Display initial info
    print("🚀 VidderTech Advanced Quiz Bot")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🏢 Built by VidderTech")
    print("📧 support@viddertech.com")
    print("🌐 https://viddertech.com")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Error: Python 3.8+ required!")
            print(f"Current version: {sys.version}")
            sys.exit(1)
        
        # Check environment
        if not os.path.exists('.env') and not os.getenv('VIDDER_TOKEN'):
            print("⚠️  Warning: No .env file or VIDDER_TOKEN found!")
            print("Please create .env file from .env.example")
            print("Or set VIDDER_TOKEN environment variable")
        
        # Initialize and start bot
        bot = VidderTechBot()
        await bot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.error(f"Critical startup error: {e}", exc_info=True)
        sys.exit(1)

def run_bot():
    """Synchronous wrapper for running the bot"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye from VidderTech!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set process title
    try:
        import setproctitle
        setproctitle.setproctitle("VidderTech-Quiz-Bot")
    except ImportError:
        pass
    
    # Run the bot
    run_bot()