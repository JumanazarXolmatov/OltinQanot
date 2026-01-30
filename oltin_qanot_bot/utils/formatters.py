"""
Text formatting utilities for Oltin Qanot Bot
"""
from datetime import datetime
from typing import Optional


def format_number(num: int) -> str:
    """Format number with thousand separators"""
    return f"{num:,}".replace(',', ' ')


def format_date(date_str: Optional[str]) -> str:
    """Format date string to readable format"""
    if not date_str:
        return "Noma'lum"
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, AttributeError):
        return date_str


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rstrip() + suffix


def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def format_user_profile(user_data: dict) -> str:
    """Format user profile data for display"""
    return (
        f"👤 **Mening hisobim**\n\n"
        f"👤 F.I.Sh: {user_data.get('full_name', 'N/A')}\n"
        f"📱 Tel: {user_data.get('phone_number', 'N/A')}\n"
        f"🆔 ID: {user_data.get('user_id', 'N/A')}\n"
        f"👥 Taklif qilganlaringiz: {user_data.get('referral_count', 0)} ta"
    )


def format_referral_link(user_id: int, bot_username: str) -> str:
    """Generate referral link for user"""
    return f"https://t.me/{bot_username}?start={user_id}"
