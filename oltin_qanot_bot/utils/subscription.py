"""
Channel subscription verification utilities
"""
from typing import List, Tuple, Optional
from telegram import Bot
from telegram.error import TelegramError
from utils.logger import logger


async def check_user_subscription(
    bot: Bot, 
    user_id: int, 
    channels: List[str]
) -> Tuple[bool, List[str]]:
    """
    Check if user is subscribed to all required channels
    
    Args:
        bot: Bot instance
        user_id: Telegram user ID
        channels: List of channel usernames (with @)
        
    Returns:
        Tuple of (is_subscribed_to_all, list_of_unsubscribed_channels)
    """
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            
            # Check if user is a member
            if member.status not in ['creator', 'administrator', 'member', 'restricted']:
                not_subscribed.append(channel)
                logger.info(f"User {user_id} not subscribed to {channel}")
        
        except TelegramError as e:
            logger.error(f"Error checking subscription for {channel}: {e}")
            not_subscribed.append(channel)
    
    is_subscribed = len(not_subscribed) == 0
    return is_subscribed, not_subscribed


async def get_channel_info(bot: Bot, channel: str) -> dict:
    """
    Get information about a channel
    """
    try:
        chat = await bot.get_chat(channel)
        return {
            'id': chat.id,
            'title': chat.title,
            'username': chat.username
        }
    except TelegramError as e:
        logger.error(f"Error getting channel info for {channel}: {e}")
        return {}


async def create_one_time_invite_link(bot: Bot, chat_id: int) -> Optional[str]:
    """
    Create a single-use invite link for a chat
    """
    try:
        # member_limit=1 makes it single-use
        link = await bot.create_chat_invite_link(
            chat_id=chat_id,
            member_limit=1,
            name="Reward Link"
        )
        return link.invite_link
    except TelegramError as e:
        logger.error(f"Error creating invite link for {chat_id}: {e}")
        return None
