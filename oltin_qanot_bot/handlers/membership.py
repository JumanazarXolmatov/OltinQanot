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
            
            # Use method to update BOTH user status and referrer count
            await db.db.handle_referral_unsubscribe(user_id, referrer_id)
            
            # Check if referrer still has 5 or 10 points
            ref_data = await db.get_user(referrer_id)
            if not ref_data:
                return
                
            current_count = ref_data[4]
            reward_sent_count = ref_data[11]
            
            # Tiered kicking logic based on the batch of the person who LEFT
            target_batch = 0
            if referral_batch == 2 and current_count < 10:
                target_batch = 2
            elif referral_batch == 1 and current_count < 5:
                target_batch = 1
                
            if target_batch > 0:
                # Find who to kick
                beneficiary_id = await db.db.get_reward_beneficiary(referrer_id, target_batch)
                if not beneficiary_id:
                    # If no specific beneficiary found (maybe they joined before tracking started),
                    # default to kicking the referrer themselves for batch 1
                    beneficiary_id = referrer_id if target_batch == 1 else None
                
                if beneficiary_id:
                    try:
                        # Remove from PRIVATE GROUP
                        if Config.PRIVATE_GROUP_ID != 0:
                            await context.bot.ban_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=beneficiary_id)
                            await context.bot.unban_chat_member(chat_id=Config.PRIVATE_GROUP_ID, user_id=beneficiary_id)
                        
                        # Remove from PRIVATE CHANNEL
                        if Config.PRIVATE_CHANNEL_ID != 0:
                            await context.bot.ban_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=beneficiary_id)
                            await context.bot.unban_chat_member(chat_id=Config.PRIVATE_CHANNEL_ID, user_id=beneficiary_id)
                        
                        logger.warning(f"Beneficiary {beneficiary_id} removed from private chats (Referrer {referrer_id} count: {current_count})")
                        
                        # Notify referrer
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=texts.MSG_POINTS_DECREASED,
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Failed to remove/notify beneficiary {beneficiary_id}: {e}")

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
