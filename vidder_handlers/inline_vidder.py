"""
🔗 VidderTech Inline Query Handlers
Built by VidderTech - The Future of Quiz Bots
"""

import logging

logger = logging.getLogger('vidder.handlers.inline')

def register_inline_vidder_handlers(app) -> int:
    """Register inline handlers"""
    logger.info("🔗 VidderTech inline handlers ready")
    return 1