from telegram import Bot
from config import Config
import database as db
from utils.subscription import create_one_time_invite_link
from utils.logger import logger
import texts

async def check_and_send_reward(bot: Bot, user_id: int):
    """Check qualification and send reward link if eligible"""
    # Get fresh user data
    user = await db.get_user(user_id)
    if not user:
        return

    referral_count = user[4] or 0
    reward_sent_level = user[11] or 0 # reward_sent_count column used as level (1 for 5 refs, 2 for 10 refs)
    
    # Determine the batches
    batches_to_process = []
    if referral_count >= 5 and reward_sent_level < 1:
        batches_to_process.append(1)
    if referral_count >= 10 and reward_sent_level < 2:
        batches_to_process.append(2)
        
    for batch in batches_to_process:
        logger.info(f"User {user_id} processing reward batch {batch} (refs: {referral_count})")
        
        group_link = None
        channel_link = None
        
        # Try to generate dynamic links
        try:
            if Config.PRIVATE_GROUP_ID and Config.PRIVATE_GROUP_ID != 0:
                group_link = await create_one_time_invite_link(bot, Config.PRIVATE_GROUP_ID)
                # Fallback to static if dynamic failed
                if not group_link and Config.STATIC_GROUP_LINK:
                    group_link = Config.STATIC_GROUP_LINK
                    logger.info(f"Using static fallback group link for user {user_id}")
            
            if Config.PRIVATE_CHANNEL_ID and Config.PRIVATE_CHANNEL_ID != 0:
                channel_link = await create_one_time_invite_link(bot, Config.PRIVATE_CHANNEL_ID)
                # Fallback to static if dynamic failed
                if not channel_link and Config.STATIC_CHANNEL_LINK:
                    channel_link = Config.STATIC_CHANNEL_LINK
                    logger.info(f"Using static fallback channel link for user {user_id}")
        except Exception as e:
            logger.error(f"Critical error creating/getting invite links for user {user_id}: {e}")

        # If we have at least one link, send it
        if group_link or channel_link:
            try:
                # Store links for tracking
                if group_link:
                    await db.db.add_reward_invite(user_id, group_link, batch)
                if channel_link:
                    await db.db.add_reward_invite(user_id, channel_link, batch)

                # Prepare message text
                count_target = 5 if batch == 1 else 10
                congrats_text = f"🎉 <b>Tabriklaymiz!</b> Siz {count_target} ta do'stingizni taklif qildingiz."
                
                if batch == 2:
                    congrats_text += "\n🌟 Bu sizning <b>IKKINCHI</b> mukofot havolalaringiz! Raxmat!"

                text = f"{congrats_text}\n\nMana sizning bir martalik havolalaringiz:\n\n"
                if group_link:
                    text += f"👥 <b>Yopiq guruh:</b> {group_link}\n"
                if channel_link:
                    text += f"📢 <b>Yopiq kanal:</b> {channel_link}\n"
                
                text += "\n⚠️ <b>Eslatma:</b> Ushbu havolalar faqat bir marta ishlaydi!"

                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML"
                )
                
                # Mark as sent
                await db.db.mark_reward_sent(user_id, batch)
                logger.info(f"Reward batch {batch} successfully delivered to {user_id}")
            except Exception as e:
                logger.error(f"Failed to deliver reward message to {user_id}: {e}")
        else:
            # FAILURE CASE: Bot couldn't generate links
            reason = ""
            if not Config.PRIVATE_GROUP_ID or Config.PRIVATE_GROUP_ID == 0:
                reason += "PRIVATE_GROUP_ID is missing or 0. "
            if not Config.PRIVATE_CHANNEL_ID or Config.PRIVATE_CHANNEL_ID == 0:
                reason += "PRIVATE_CHANNEL_ID is missing or 0. "
            
            error_msg = (
                f"❌ <b>Xatolik:</b> Siz {5 if batch == 1 else 10} ta do'st taklif qildingiz, lekin bot hozirda yopiq guruh havolasini yarata olmadi.\n\n"
                f"Iltimos, adminga murojaat qiling: @jumanazar_xolmatov"
            )
            logger.error(f"Reward generation failed for user {user_id} (batch {batch}). Reason: {reason or 'Invite link generation returned None'}. Check bot admin status in groups.")
            try:
                await bot.send_message(chat_id=user_id, text=error_msg, parse_mode="HTML")
            except Exception as send_err:
                logger.error(f"Could not send error message to user {user_id}: {send_err}")
