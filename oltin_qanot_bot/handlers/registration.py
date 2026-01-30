"""
Registration flow handlers for Mathematics Course Bot
"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import database as db
import texts
from config import Config
from utils.logger import logger
from utils.validators import validate_full_name
from utils.subscription import check_user_subscription
import html

# Conversation states
CHECK_SUB, ASK_PHONE, ASK_NAME = range(3)


async def get_main_menu_keyboard():
    """Get main menu keyboard layout"""
    return ReplyKeyboardMarkup([
        [texts.BTN_ABOUT_COURSE, texts.BTN_CONDITIONS],
        [texts.BTN_INVITE, texts.BTN_MY_POINTS],
        [texts.BTN_CHANNELS],
        [texts.BTN_PARTNERS]
    ], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    args = context.args
    referrer_id = None
    
    # Extract referrer ID from deep link
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        
        # Check if referrer is ELIGIBLE (subscribed to mandatory channels)
        is_ref_active, _ = await check_user_subscription(
            context.bot,
            referrer_id,
            Config.REQUIRED_CHANNELS
        )
        
        if not is_ref_active:
            logger.info(f"Referrer {referrer_id} is NOT eligible. Referral for {user.id} ignored.")
            referrer_id = None
        else:
            logger.info(f"User {user.id} started with active referrer {referrer_id}")
    
    # Try to add user (pending)
    await db.add_user(user.id, user.username, referrer_id)
    
    # Check if fully registered
    existing_user = await db.get_user(user.id)
    if existing_user and existing_user[2] and existing_user[7]: # Has name and phone
        # Verify they are STILL subscribed
        is_subscribed, _ = await check_user_subscription(context.bot, user.id, Config.REQUIRED_CHANNELS)
        if is_subscribed:
            await update.message.reply_text(
                texts.MSG_WELCOME_BACK,
                reply_markup=await get_main_menu_keyboard()
            )
            return ConversationHandler.END

    # Start with subscription check
    keyboard = []
    # User requested specific labels: 
    # 1. Matematika darslari (channel)
    # 2. Matematika guruhi (group)
    
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
    
    keyboard.append([InlineKeyboardButton(texts.BTN_SUBSCRIBED, callback_data="check_sub")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Welcome message with safe name
    name = user.first_name or user.full_name or "Foydalanuvchi"
    # Escape name for HTML
    name = html.escape(name)
    welcome_msg = texts.ASK_SUB_START.format(full_name=name)
    
    await update.message.reply_text(
        welcome_msg, 
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return CHECK_SUB


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription verification"""
    query = update.callback_query
    user_id = query.from_user.id
    
    is_subscribed, not_subscribed = await check_user_subscription(
        context.bot,
        user_id,
        Config.REQUIRED_CHANNELS
    )
    
    if not is_subscribed:
        # Show specific buttons for missing channels/groups
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
        
        keyboard.append([InlineKeyboardButton(texts.BTN_SUBSCRIBED, callback_data="check_sub")])
        
        await query.answer(text=texts.MSG_NOT_SUBSCRIBED, show_alert=True)
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
        return CHECK_SUB
    
    await query.answer()
    
    # If subscribed, move to next step (Phone)
    keyboard = [[KeyboardButton(texts.BTN_SEND_PHONE, request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.delete()
    await query.message.reply_text(
        texts.ASK_PHONE_TEMPLATE,
        reply_markup=reply_markup
    )
    return ASK_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number submission"""
    user_id = update.effective_user.id
    
    # Strict check: Must be a shared contact
    if not update.message.contact:
        await update.message.reply_text(
            "⚠️ <b>Iltimos, telefon raqamingizni yozib yubormang!</b>\n\n"
            "Pastdagi <b>'📞 Raqamni yuborish'</b> tugmasini bosing 👇",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(texts.BTN_SEND_PHONE, request_contact=True)]], 
                resize_keyboard=True, 
                one_time_keyboard=True
            ),
            parse_mode="HTML"
        )
        return ASK_PHONE

    contact = update.message.contact
    phone_number = contact.phone_number
    
    await db.update_phone_number(user_id, phone_number)
    
    await update.message.reply_text(
        texts.ASK_NAME,
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name submission"""
    full_name = update.message.text
    user_id = update.effective_user.id
    
    is_valid, error_msg = validate_full_name(full_name)
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error_msg}")
        return ASK_NAME
    
    await db.update_full_name(user_id, full_name)
    
    # Final confirmation
    is_confirmed = await db.confirm_referral(user_id)
    
    if is_confirmed:
        # Notify referrer
        user_data = await db.get_user(user_id)
        if user_data and user_data[3]: # referrer_id is index 3
            referrer_id = user_data[3]
            try:
                # Escape name for notification
                safe_full_name = html.escape(full_name)
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 <b>Tabriklaymiz!</b>\n\nSizning havolangiz orqali <b>{safe_full_name}</b> ({update.effective_user.mention_html()}) ro'yxatdan o'tdi!",
                    parse_mode="HTML"
                )
                
                # Check if referrer reached 5 and send reward automatically
                # Import here to avoid circular dependencies if any, or strict order
                from utils.rewards import check_and_send_reward
                await check_and_send_reward(context.bot, referrer_id)
                
            except Exception as e:
                logger.error(f"Failed to notify/reward referrer {referrer_id}: {e}")

    # Welcome to main menu
    await update.message.reply_text(
        texts.MSG_REG_COMPLETED_WELCOME,
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END


def get_registration_handler():
    """Create and return registration conversation handler"""
    from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
    
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHECK_SUB: [CallbackQueryHandler(check_subscription, pattern="^check_sub$")],
            ASK_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), receive_phone)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
