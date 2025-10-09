"""
🔧 VidderTech Utility Modules
Built by VidderTech - The Future of Quiz Bots

Advanced utility functions and helpers for:
- Text processing and validation
- Security and encryption
- Multi-language support
- File operations
- Performance optimization
"""

from .text_processor_vidder import VidderTextProcessor
from .vidder_helpers import VidderHelpers
from .security_vidder import VidderSecurity
from .lang_vidder import VidderLanguage

# Version info
__version__ = "2.0.0"
__author__ = "VidderTech Utils Team"

# Export main components
__all__ = [
    'VidderTextProcessor',
    'VidderHelpers',
    'VidderSecurity', 
    'VidderLanguage'
]