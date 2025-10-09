"""
📝 VidderTech Advanced Logging System
Built by VidderTech - The Future of Quiz Bots

Enterprise logging with:
- Structured logging
- Performance monitoring
- Error tracking
- Analytics integration
"""

import logging
import sys
from pathlib import Path

class VidderLogger:
    """📝 VidderTech Advanced Logger"""
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get configured logger for VidderTech"""
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            # Create logs directory
            Path("./logs").mkdir(exist_ok=True)
            
            # Configure handler
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger