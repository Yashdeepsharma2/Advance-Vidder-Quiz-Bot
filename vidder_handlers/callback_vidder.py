"""
🔘 VidderTech Callback Handlers
Built by VidderTech - The Future of Quiz Bots
"""

import logging

logger = logging.getLogger('vidder.handlers.callback')

def register_callback_vidder_handlers(app) -> int:
    """Register callback handlers"""
    logger.info("🔘 VidderTech callback handlers ready")
    return 1