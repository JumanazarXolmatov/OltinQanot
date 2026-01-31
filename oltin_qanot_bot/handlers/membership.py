"""
Membership tracking for Mathematics Course Bot
Handles users leaving/joining mandatory channels
"""
from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import ContextTypes
import database as db
from config import Config
from utils.logger import logger
import texts


async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat member status changes in mandatory channels"""
    result = update.chat_member
    if not result:
        return

    chat_username = f"@{result.chat.username}" if result.chat.username else None
    
    # Only care about mandatory channels
    if chat_username not in Config.REQUIRED_CHANNELS:
        return

    user_id = result.from_user.id
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    
    logger.info(f"User {user_id} changed status in {chat_username}: {old_status} -> {new_status}")

    # Detect leaving
    was_member = old_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    is_member = new_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]

    if was_member and not is_member:
        # User LEFT the channel
        logger.warning(f"User {user_id} left mandatory channel {chat_username}")
        
        # Get user info to find referrer
        user_data = await db.get_user(user_id)
        if not user_data:
            return

        referrer_id = user_data[3]
        referral_batch = user_data[12] if len(user_data) > 12 else 0

        if referrer_id:
            logger.info(f"Processing unsubscribe for user {user_id} (referrer: {referrer_id}, batch: {referral_batch})")
            
            # 1. Update BOTH user status and referrer count
            await db.db.handle_referral_unsubscribe(user_id, referrer_id)
            
            # 2. Check if referrer still has minimum points (5)
            ref_data = await db.get_user(referrer_id)
            if not ref_data:
                return
                
            current_count = ref_data[4]
            
            # If points drop below 5, kick the referrer from private channels/groups
            if current_count < 5:
                logger.warning(f"Referrer {referrer_id} points dropped to {current_count}. Kicking from private chats.")
                
                try:
                    # Remove from PRIVATE GROUP
                    if Config.PRIVATE_GROUP_ID != 0:
                        await context.bot.ban_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=referrer_id)
                        await context.bot.unban_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=referrer_id)
                    
                    # Remove from PRIVATE CHANNEL
                    if Config.PRIVATE_CHANNEL_ID != 0:
                        await context.bot.ban_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=referrer_id)
                        await context.bot.unban_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=referrer_id)
                    
                    # Notify referrer
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=(
                            "⚠️ <b>Diqqat!</b>\n\n"
                            "Siz taklif qilgan do'stlaringizdan biri kanallardan chiqib ketdi. "
                            f"Hozirda sizning ballaringiz <b>{current_count}</b> ga tushib qoldi.\n\n"
                            "Ballaringiz 5 tadan kam bo'lgani uchun siz yopiq guruh va kanaldan chiqarildingiz. "
                            "Yana qo'shilish uchun ballaringizni 5 taga ko'paytiring!"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to kick/notify referrer {referrer_id}: {e}")
            else:
                # Still has 5+ points, but notify that count decreased
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=(
                            "📉 <b>Ballaringiz kamaydi!</b>\n\n"
                            "Siz taklif qilgan do'stlardan biri kanalni tark etdi. "
                            f"Sizning joriy ballaringiz: <b>{current_count}</b>"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify referrer {referrer_id} about decrease: {e}")

async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log when a user joins via a tracked invite link"""
    # This requires ChatJoinRequest (for private chats with join request) 
    # OR ChatMemberUpdated (if bot is admin and sees invite link usage)
    # The current bot logic uses one-time links without join request usually.
    # To track invite link usage, we need to listen for CHAT_MEMBER updates where invite_link is present.
    result = update.chat_member
    if not result or not result.invite_link:
        return
        
    invite_link = result.invite_link.invite_link
    user_id = result.from_user.id
    new_status = result.new_chat_member.status
    
    if new_status in [ChatMember.MEMBER]:
        await db.db.log_reward_usage(invite_link, user_id)
        logger.info(f"User {user_id} joined chat via tracked link: {invite_link}")
