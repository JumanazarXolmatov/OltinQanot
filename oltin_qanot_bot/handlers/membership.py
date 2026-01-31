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
    
    # Only care about mandatory channels (Case-Insensitive Check)
    if not chat_username:
        return

    required_lower = [c.lower() for c in Config.REQUIRED_CHANNELS]
    if chat_username.lower() not in required_lower:
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
        
        # 1. Kick the user from PRIVATE chats (even if they were in as a reward)
        # BUT skip if they are admin/creator of those chats
        kicked_from_group = False
        kicked_from_channel = False
        
        try:
            # Remove from PRIVATE GROUP
            if Config.PRIVATE_GROUP_ID != 0:
                try:
                    # Check if user is admin in private group
                    member = await context.bot.get_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=user_id)
                    if member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                        logger.info(f"User {user_id} is admin/owner in private group, skipping kick")
                    else:
                        await context.bot.ban_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=user_id)
                        await context.bot.unban_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=user_id)
                        kicked_from_group = True
                except Exception as e:
                    logger.error(f"Failed to kick user {user_id} from private group: {e}")
            
            # Remove from PRIVATE CHANNEL
            if Config.PRIVATE_CHANNEL_ID != 0:
                try:
                    # Check if user is admin in private channel
                    member = await context.bot.get_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=user_id)
                    if member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                        logger.info(f"User {user_id} is admin/owner in private channel, skipping kick")
                    else:
                        await context.bot.ban_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=user_id)
                        await context.bot.unban_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=user_id)
                        kicked_from_channel = True
                except Exception as e:
                    logger.error(f"Failed to kick user {user_id} from private channel: {e}")
            
            if kicked_from_group or kicked_from_channel:
                logger.info(f"Kicked user {user_id} from private chats for leaving mandatory channel {chat_username}")
        except Exception as e:
            logger.error(f"Failed to process kick for user {user_id}: {e}")

        # 2. Notify the user who left
        try:
            channel_name = chat_username
            if "Matematika_darslari_dtm" in chat_username:
                channel_name = "MATEMATIKA DARSLARI"
            elif "matematika2021u" in chat_username:
                channel_name = "Matematika guruhi"
                
            await context.bot.send_message(
                chat_id=user_id,
                text=texts.MSG_LEFT_NOTIFICATION.format(channel_name=channel_name),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id} about leaving: {e}")

        # 3. Get user info to find referrer
        user_data = await db.get_user(user_id)
        if not user_data:
            return

        referrer_id = user_data[3]
        referral_batch = user_data[12] if len(user_data) > 12 else 0

        if referrer_id:
            logger.info(f"Processing unsubscribe for user {user_id} (referrer: {referrer_id})")
            
            # 1. Update BOTH user status and referrer count
            await db.db.handle_referral_unsubscribe(user_id, referrer_id)
        else:
            # No referrer, but we must still mark USER as unsubscribed
            logger.info(f"User {user_id} left mandatory channel (no referrer). Marking as unsubscribed.")
            await db.db.execute(
                "UPDATE users SET status = 'unsubscribed', updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", 
                (user_id,)
            )
            await db.db.commit()

        if referrer_id:
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
                    
                    # Notify referrer with NAME of person who left
                    left_user_name = user_data[2] if user_data[2] else "Foydalanuvchi"
                    
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=(
                            "⚠️ <b>Diqqat!</b>\n\n"
                            f"<b>{left_user_name}</b> majburiy kanallardan chiqib ketdi. "
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
                    left_user_name = user_data[2] if user_data[2] else "Foydalanuvchi"
                    
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=(
                            "📉 <b>Ballaringiz kamaydi!</b>\n\n"
                            f"<b>{left_user_name}</b> kanalni tark etdi. "
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
