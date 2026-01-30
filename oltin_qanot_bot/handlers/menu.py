"""
Menu handlers for Mathematics Course Bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
from config import Config
from utils.logger import logger
from utils.subscription import create_one_time_invite_link
from utils.formatters import format_referral_link
import texts
import os
import html


async def menu_about_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'About Course' button"""
    await update.message.reply_text(
        texts.MSG_ABOUT_COURSE,
        parse_mode="HTML"
    )


async def menu_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Conditions' button"""
    await update.message.reply_text(
        texts.MSG_CONDITIONS,
        parse_mode="HTML"
    )


from utils.rewards import check_and_send_reward


async def menu_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Invite Friends' button"""
    user_id = update.effective_user.id
    
    # Get user data to ensure latest points
    user = await db.get_user(user_id)
    # We no longer need to pass 'user' data to the new check_and_send_reward, 
    # it fetches fresh data itself, but for now let's just call it with ID.
    if user:
         await check_and_send_reward(context.bot, user_id)
    
    # Generate unique referral link
    link = format_referral_link(user_id, Config.BOT_USERNAME)
    
    # Text for the caption (with HTML)
    caption = texts.SHARE_TEXT_TEMPLATE.format(link=link)
    
    # Text for sharing (URL encoded plain text)
    import urllib.parse
    share_text = texts.SHARE_TEXT_TEMPLATE.format(link=link)
    # Remove any stray HTML if present (though we just removed it from uz.py)
    import re
    share_text_plain = re.sub(r'<[^>]*>', '', share_text)
    share_text_encoded = urllib.parse.quote(share_text_plain)
    
    keyboard = [[
        InlineKeyboardButton(
            texts.BTN_SHARE, 
            url=f"https://t.me/share/url?url={link}&text={share_text_encoded}"
        )
    ]]
    
    caption = texts.SHARE_TEXT_TEMPLATE.format(link=link)
    
    try:
        # Check if banner exists and send photo
        banner_path = r"c:\Users\juman\Downloads\OltinQanot\assets\banner.jpg"
        if os.path.exists(banner_path):
            await update.message.reply_photo(
                photo=open(banner_path, 'rb'),
                caption=caption,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                caption,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Error sending invite menu: {e}")
        await update.message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def menu_my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'My Points' button"""
    user_id = update.effective_user.id
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text(texts.MSG_ERROR_USER_NOT_FOUND)
        return

    # Check for reward
    await check_and_send_reward(context.bot, user_id)
    
    # Get rank
    stats = await db.get_statistics()
    # Simple rank estimation or full leaderboard check
    # For now, just show the data we have
    rank = "---" # We can implement a proper rank helper if needed
    
    # Get referred users
    referred_users = await db.get_referred_users(user_id)
    
    # Format referral list
    if referred_users:
        referrals_str = texts.MSG_REFERRALS_LIST_TITLE
        for ref in referred_users:
            # ref = (user_id, username, full_name)
            r_username = ref[1]
            r_fullname = ref[2] if ref[2] else "Noma'lum"
            
            # Escape HTML characters in user input to prevent parsing errors
            r_fullname = html.escape(r_fullname)
            
            if r_username:
                # Add @ to username only if it's there
                r_username = html.escape(r_username)
                referrals_str += texts.MSG_REFERRAL_ITEM.format(
                    username=f"@{r_username}",
                    full_name=r_fullname
                )
            else:
                referrals_str += texts.MSG_REFERRAL_ITEM_NO_USERNAME.format(
                    full_name=r_fullname
                )
        referrals_str += "\n"
    else:
        referrals_str = texts.MSG_NO_REFERRALS

    referral_count = user_data[4]
    remaining = max(0, 5 - referral_count)
    
    # Escape user's own name
    my_fullname = html.escape(user_data[2]) if user_data[2] else "Kiritilmagan"
    
    await update.message.reply_text(
        texts.MSG_MY_POINTS_TEMPLATE.format(
            full_name=my_fullname,
            user_id=user_data[0],
            referral_count=referral_count,
            referrals_list=referrals_str,
            remaining=remaining
        ),
        parse_mode="HTML"
    )


async def menu_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Our Channels' button"""
    keyboard = []
    
    # First link (Channel)
    keyboard.append([InlineKeyboardButton(
        f"📢 MATEMATIKA DARSLARI",
        url=f"https://t.me/Matematika_darslari_dtm"
    )])
    
    # Second link (Group)
    keyboard.append([InlineKeyboardButton(
        f"💬 Matematika guruhi",
        url=f"https://t.me/matematika2021u"
    )])
        
    await update.message.reply_text(
        texts.MSG_SOCIALS,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu_partners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Partners' button"""
    keyboard = [
        [InlineKeyboardButton("📢 Kanalimizga obuna bo'ling", url="https://t.me/hacknow_uz")],
        [InlineKeyboardButton("👨‍💻 Bot yaratuvchisi", url="https://t.me/jumanazar_xolmatov")]
    ]
    
    caption = texts.MSG_HACKNOW
    
    try:
        # Check if HackNow image exists
        image_path = r"c:\Users\juman\Downloads\OltinQanot\oltin_qanot_bot\assets\hacknow.png"
        if os.path.exists(image_path):
            await update.message.reply_photo(
                photo=open(image_path, 'rb'),
                caption=caption,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                caption,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Error sending partners menu: {e}")
        await update.message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def menu_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Send Message' button"""
    keyboard = [
        [InlineKeyboardButton("✍️ Adminga yozish", url="https://t.me/jumanazar_xolmatov")]
    ]
    await update.message.reply_text(
        "👋 <b>Adminga murojaat:</b>\n\n"
        "Kurs yoki bot yuzasidan savollaringiz bo'lsa, pastdagi tugmani bosing va adminga yozing.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
