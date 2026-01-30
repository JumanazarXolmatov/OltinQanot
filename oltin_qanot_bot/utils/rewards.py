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

    referral_count = user[4]     # index 4
    reward_sent_count = user[11] # index 11
    
    logger.info(f"Checking reward for user {user_id}: refs={referral_count}, sent_count={reward_sent_count}")
    
    # Determine the batches
    batches_to_process = []
    if referral_count >= 5 and reward_sent_count < 1:
        batches_to_process.append(1)
    if referral_count >= 10 and reward_sent_count < 2:
        batches_to_process.append(2)
        
    for batch in batches_to_process:
        logger.info(f"User {user_id} processing reward batch {batch}")
        
        # Generate links for both Group and Channel if IDs are set
        group_link = None
        channel_link = None
        
        if Config.PRIVATE_GROUP_ID and Config.PRIVATE_GROUP_ID != 0:
            group_link = await create_one_time_invite_link(bot, Config.PRIVATE_GROUP_ID)
            if not group_link:
                logger.error(f"Failed to generate Group Invite for {Config.PRIVATE_GROUP_ID}. Bot might not be admin.")
        
        if Config.PRIVATE_CHANNEL_ID and Config.PRIVATE_CHANNEL_ID != 0:
            channel_link = await create_one_time_invite_link(bot, Config.PRIVATE_CHANNEL_ID)
            if not channel_link:
                logger.error(f"Failed to generate Channel Invite for {Config.PRIVATE_CHANNEL_ID}. Bot might not be admin or ID is wrong.")
        
        # If we have at least one link, send it
        if group_link or channel_link:
            try:
                # Store links for tracking
                if group_link:
                    await db.db.add_reward_invite(user_id, group_link, batch)
                if channel_link:
                    await db.db.add_reward_invite(user_id, channel_link, batch)

                # Prepare message text based on available links
                count_str = "5 ta" if batch == 1 else "10 ta"
                congrats_text = f"🎉 <b>Tabriklaymiz!</b> Siz {count_str} do'stingizni taklif qildingiz."
                if batch == 2:
                    congrats_text += "\n🌟 Bu sizning <b>IKKINCHI</b> mukofot havolalaringiz! Buni yaqinlaringizga ulashishingiz mumkin."

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
                
                # Mark as sent immediately to prevent duplicates
                await db.db.mark_reward_sent(user_id, batch)
                logger.info(f"Reward links (batch {batch}) sent to {user_id}")
            except Exception as e:
                logger.error(f"Failed to send reward message to {user_id}: {e}")
        else:
            logger.error(f"CRITICAL: Failed to generate ANY reward links for {user_id} (batch {batch}). Check if Bot is ADMIN in {Config.PRIVATE_GROUP_ID} and {Config.PRIVATE_CHANNEL_ID}")
    
    if referral_count >= 5 and referral_count < 10 and reward_sent_count >= 1:
         logger.info(f"User {user_id} already received batch 1 reward.")
    elif referral_count >= 10 and reward_sent_count >= 2:
         logger.info(f"User {user_id} already received all eligible rewards.")
