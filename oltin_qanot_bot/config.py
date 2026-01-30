"""
Configuration management for Oltin Qanot Bot
Loads settings from environment variables with validation
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
# Try current directory first, then parent directory
env_paths = [
    Path(__file__).parent.absolute() / '.env',          # Inside oltin_qanot_bot/
    Path(__file__).parent.parent.absolute() / '.env'   # Project root
]

found_env = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        print(f"DEBUG: Loaded environment variables from {env_path}")
        found_env = True
        break

if not found_env:
    # If none found, just try default load_dotenv (current working directory)
    load_dotenv(override=True)
    print("DEBUG: Using default load_dotenv (current working directory)")



class Config:
    """Bot configuration loaded from environment variables"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    BOT_USERNAME: str = os.getenv('BOT_USERNAME', '')
    
    # Admin Configuration
    ADMIN_IDS: List[int] = [
        int(id.strip()) 
        for id in os.getenv('ADMIN_IDS', '').split(',') 
        if id.strip().isdigit()
    ]
    
    # Channel Configuration
    REQUIRED_CHANNELS: List[str] = [
        channel.strip() 
        for channel in os.getenv('REQUIRED_CHANNELS', '').split(',') 
        if channel.strip()
    ]
    
    # Private Group Configuration
    PRIVATE_GROUP_ID: int = int(os.getenv('PRIVATE_GROUP_ID', '0'))
    PRIVATE_CHANNEL_ID: int = int(os.getenv('PRIVATE_CHANNEL_ID', '0'))
    
    # Initial debug prints
    print(f"DEBUG: PRIVATE_GROUP_ID = {PRIVATE_GROUP_ID}")
    print(f"DEBUG: PRIVATE_CHANNEL_ID = {PRIVATE_CHANNEL_ID}")
    
    # Static Fallback Links (use if dynamic creation fails)
    STATIC_GROUP_LINK: str = os.getenv('STATIC_GROUP_LINK', '')
    STATIC_CHANNEL_LINK: str = os.getenv('STATIC_CHANNEL_LINK', '')
    
    # Database Configuration
    DATABASE_NAME: str = os.getenv('DATABASE_NAME', 'oltin_qanot.db')
    BACKUP_DIR: str = os.getenv('BACKUP_DIR', 'backups')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'bot.log')
    
    # Contest Configuration
    CONTEST_NAME: str = os.getenv('CONTEST_NAME', 'Oltin Qanot Referral Contest')
    CONTEST_START_DATE: str = os.getenv('CONTEST_START_DATE', '2026-01-28')
    CONTEST_END_DATE: str = os.getenv('CONTEST_END_DATE', '2026-02-28')
    
    # Feature Flags
    ENABLE_MULTI_LANGUAGE: bool = os.getenv('ENABLE_MULTI_LANGUAGE', 'true').lower() == 'true'
    ENABLE_AUTO_BACKUP: bool = os.getenv('ENABLE_AUTO_BACKUP', 'true').lower() == 'true'
    ENABLE_RATE_LIMITING: bool = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = int(os.getenv('RATE_LIMIT_MESSAGES', '20'))
    RATE_LIMIT_COMMANDS: int = int(os.getenv('RATE_LIMIT_COMMANDS', '10'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in .env file")
        
        if not cls.BOT_USERNAME:
            print("WARNING: BOT_USERNAME is not configured in .env")
        
        if not cls.ADMIN_IDS:
            print("WARNING: No ADMIN_IDS configured")
        
        if not cls.REQUIRED_CHANNELS:
            print("WARNING: No REQUIRED_CHANNELS configured")
        
        return True
    
    @classmethod
    def get_database_path(cls) -> Path:
        """Get absolute path to database file"""
        return Path(__file__).parent / cls.DATABASE_NAME
    
    @classmethod
    def get_backup_dir(cls) -> Path:
        """Get absolute path to backup directory"""
        backup_path = Path(__file__).parent.parent / cls.BACKUP_DIR
        backup_path.mkdir(exist_ok=True)
        return backup_path

    @classmethod
    def get_asset_path(cls, filename: str) -> Path:
        """Get absolute path to an asset file"""
        # Try both root/assets and oltin_qanot_bot/assets
        paths = [
            Path(__file__).parent / 'assets' / filename,
            Path(__file__).parent.parent / 'assets' / filename
        ]
        for path in paths:
            if path.exists():
                return path
        return paths[0] # Default to bot-folder assets


# Validate configuration on import
Config.validate()
