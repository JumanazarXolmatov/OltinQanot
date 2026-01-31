from telegram import Bot
from config import Config
import database as db
from utils.subscription import create_one_time_invite_link
from utils.logger import logger
import texts

from telegram.error import TelegramError

async def check_and_send_reward(bot: Bot, user_id: int):
    """
    Check qualification and send reward link if eligible.
    Logic:
    1. Count ACTIVE referrals (status='active').
    2. If >= 5 active refs -> Check if user is in Private Group. If NOT, send link.
    3. If >= 10 active refs -> Check if user is in Private Channel. If NOT, send link.
    """
    # 1. Get fresh ACTIVE referral count
    # We query the count directly to be 100% sure we are counting only active users
    active_count = await db.get_active_referral_count(user_id)
    
    logger.info(f"Checking rewards for user {user_id}. Active referrals: {active_count}")
    
    # 2. Check qualifications
    group_needed = False
    channel_needed = False
    
    if active_count >= 5:
        # User qualifies for group. Check if they are already inside.
        if Config.PRIVATE_GROUP_ID and Config.PRIVATE_GROUP_ID != 0:
            try:
                member = await bot.get_chat_member(Config.PRIVATE_GROUP_ID, user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    # User is NOT in the group (left, kicked, or never joined)
                    group_needed = True
                    logger.info(f"User {user_id} qualifies for GROUP (5+) and is not a member (status: {member.status})")
            except Exception as e:
                # If we get "User not found" or similar, they are not in chat
                group_needed = True
                logger.warning(f"Could not check group membership for {user_id}: {e}. Assuming needs link.")
    
    if active_count >= 10:
        # User qualifies for channel. Check if they are already inside.
        if Config.PRIVATE_CHANNEL_ID and Config.PRIVATE_CHANNEL_ID != 0:
            try:
                member = await bot.get_chat_member(Config.PRIVATE_CHANNEL_ID, user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    channel_needed = True
                    logger.info(f"User {user_id} qualifies for CHANNEL (10+) and is not a member (status: {member.status})")
            except Exception as e:
                channel_needed = True
                logger.warning(f"Could not check channel membership for {user_id}: {e}. Assuming needs link.")

    # 3. Generate and send links if needed
    if not group_needed and not channel_needed:
        return

    group_link = None
    channel_link = None
    
    try:
        if group_needed:
            group_link = await create_one_time_invite_link(bot, Config.PRIVATE_GROUP_ID)
            if not group_link and Config.STATIC_GROUP_LINK:
                group_link = Config.STATIC_GROUP_LINK

        if channel_needed:
            channel_link = await create_one_time_invite_link(bot, Config.PRIVATE_CHANNEL_ID)
            if not channel_link and Config.STATIC_CHANNEL_LINK:
                channel_link = Config.STATIC_CHANNEL_LINK

    except Exception as e:
        logger.error(f"Error creating invite links for user {user_id}: {e}")

    if group_link or channel_link:
        try:
            # Prepare message
            text = f"🎉 <b>Tabriklaymiz!</b> Sizda <b>{active_count}</b> ta faol taklif mavjud.\n\n"
            text += "Siz yopiq chatlarga kirish huquqiga egasiz. Mana yangi havolalar:\n\n"
            
            if group_link:
                text += f"👥 <b>Yopiq guruh:</b> {group_link}\n"
                # Log usage
                await db.db.add_reward_invite(user_id, group_link, 1)
                
            if channel_link:
                text += f"📢 <b>Yopiq kanal:</b> {channel_link}\n"
                # Log usage
                await db.db.add_reward_invite(user_id, channel_link, 2)
            
            text += "\n⚠️ <b>Eslatma:</b> Agar yana chiqib ketsangiz, qayta kirish uchun ballaringiz yetarli bo'lishi kerak!"

            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            logger.info(f"Sent reward links to {user_id} (Group: {bool(group_link)}, Channel: {bool(channel_link)})")
            
        except Exception as e:
            logger.error(f"Failed to send reward message to {user_id}: {e}")
