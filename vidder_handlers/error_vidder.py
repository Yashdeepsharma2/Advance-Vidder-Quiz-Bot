"""
❌ VidderTech Error Handlers
Built by VidderTech - The Future of Quiz Bots
"""

import logging

logger = logging.getLogger('vidder.handlers.error')

def register_error_vidder_handlers(app) -> int:
    """Register error handlers"""
    logger.info("❌ VidderTech error handlers ready")
    return 1