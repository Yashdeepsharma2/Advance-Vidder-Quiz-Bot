"""
🗄️ VidderTech Database Package - Advanced Data Management
🚀 Built by VidderTech - The Future of Quiz Bots

Complete database system with:
- Advanced SQLite operations with connection pooling
- Comprehensive data models for all entities
- Real-time analytics and performance tracking  
- Automated backups and data migration
- AI-powered query optimization
- Multi-language content support
- Enterprise-grade security and encryption
"""

from .vidder_database import VidderDatabaseManager, db_manager, VIDDER_COMPLETE_SCHEMA

# Database package exports
__all__ = [
    'VidderDatabaseManager',
    'db_manager', 
    'VIDDER_COMPLETE_SCHEMA'
]

# Package initialization
print("🗄️ VidderTech Database Package Loaded")
print("✅ Database manager ready")
print("📊 Schema loaded successfully")