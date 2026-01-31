"""
Input validation utilities for Oltin Qanot Bot
"""
import re
from typing import Tuple


def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format
    
    Args:
        phone: Phone number string
        
    Returns:
        Tuple of (is_valid, cleaned_phone)
    """
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (8-15 digits)
    if len(cleaned) < 8 or len(cleaned) > 15:
        return False, cleaned
    
    return True, cleaned


def validate_full_name(name: str) -> Tuple[bool, str]:
    """
    Validate full name (must have at least 2 words)
    
    Args:
        name: Full name string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    name = name.strip()
    
    # Check minimum length
    if len(name) < 3:
        return False, "Ism juda qisqa"
    
    # Check for at least 2 words
    words = name.split()
    if len(words) < 2:
        return False, "Iltimos, to'liq ism familiyangizni kiriting (kamida 2 ta so'z)"
    
    # Check for invalid characters (only letters, spaces, apostrophes, hyphens, and Uzbek special chars)
    if not re.match(r"^[a-zA-ZÀ-ÿа-яА-ЯёЁқҚғҒҳҲўЎ\s'ʻʼ\-]+$", name, re.UNICODE):
        return False, "Ism faqat harflardan iborat bo'lishi kerak"
    
    return True, ""


def sanitize_text(text: str, max_length: int = 4096) -> str:
    """
    Sanitize text input to prevent injection attacks
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Truncate to max length
    text = text[:max_length]
    
    # Remove potential HTML/script tags
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()


def is_valid_user_id(user_id: any) -> bool:
    """
    Check if user_id is valid Telegram user ID
    
    Args:
        user_id: User ID to validate
        
    Returns:
        True if valid
    """
    try:
        uid = int(user_id)
        return uid > 0 and uid < 10**12  # Telegram IDs are positive and reasonable
    except (ValueError, TypeError):
        return False
