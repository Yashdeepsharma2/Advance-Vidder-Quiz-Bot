"""
🎮 VidderTech Bot Manager
Built by VidderTech - The Future of Quiz Bots

Enterprise bot lifecycle management
"""

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger('vidder.manager')

class VidderBotManager:
    """🎮 VidderTech Bot Manager"""
    
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.is_running = False
    
    async def initialize(self):
        """Initialize bot manager"""
        logger.info("🎮 VidderTech Bot Manager initialized")
    
    async def start(self):
        """Start the bot"""
        try:
            self.is_running = True
            logger.info("🚀 Starting VidderTech bot polling...")
            
            await self.app.get_application().run_polling(
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query', 'inline_query']
            )
            
        except Exception as e:
            logger.error(f"❌ Bot manager error: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        try:
            self.is_running = False
            logger.info("🛑 VidderTech bot manager stopped")
        except Exception as e:
            logger.error(f"❌ Stop error: {e}")