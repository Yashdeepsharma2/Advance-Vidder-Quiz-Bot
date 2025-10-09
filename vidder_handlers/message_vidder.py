"""
💬 VidderTech Message Handlers
Built by VidderTech - The Future of Quiz Bots
"""

import logging

logger = logging.getLogger('vidder.handlers.message')

def register_message_vidder_handlers(app) -> int:
    """Register message handlers"""
    logger.info("💬 VidderTech message handlers ready")
    return 1