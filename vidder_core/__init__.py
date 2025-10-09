"""
🚀 VidderTech Core System Module
Built by VidderTech - The Future of Quiz Bots

Core system initialization and component loading for:
- Bot application management
- System lifecycle control
- Component registration
- Error handling and recovery
- Performance monitoring
"""

from .vidder_app import VidderApplication
from .vidder_manager import VidderBotManager
from .vidder_engine import VidderCoreEngine
from .vidder_monitor import VidderSystemMonitor
from .vidder_scheduler import VidderScheduler

# Version info
__version__ = "2.0.0"
__author__ = "VidderTech Team"
__email__ = "support@viddertech.com"

# Export main components
__all__ = [
    'VidderApplication',
    'VidderBotManager', 
    'VidderCoreEngine',
    'VidderSystemMonitor',
    'VidderScheduler'
]