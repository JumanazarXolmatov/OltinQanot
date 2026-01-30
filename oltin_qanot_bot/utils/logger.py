"""
Centralized logging configuration for Oltin Qanot Bot
"""
import logging
import sys
from pathlib import Path

# Import config after it's available
try:
    from config import Config
except ImportError:
    # Fallback for initial import
    class Config:
        LOG_LEVEL = 'INFO'
        LOG_FILE = 'bot.log'



def setup_logger(name: str = 'oltin_qanot_bot') -> logging.Logger:
    """
    Configure and return logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = Path(__file__).parent.parent / Config.LOG_FILE
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()
