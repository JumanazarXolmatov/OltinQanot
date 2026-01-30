"""
Leaderboard handlers for Oltin Qanot Bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
import texts
from utils.logger import logger


async def show_leaderboard(update_or_query, context, offset=0, edit=False):
    """Display leaderboard with pagination"""
    # Determine message object
    if isinstance(update_or_query, Update) and update_or_query.message:
        message = update_or_query.message
    elif hasattr(update_or_query, 'message'):
        message = update_or_query.message
    else:
        message = update_or_query
    
    # Get top users
    top_users = await db.get_leaderboard(limit=10, offset=offset)
    
    # Build message
    msg = "🏆 Reyting:\n\n"
    users_msg = ""
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (name, count) in enumerate(top_users):
        rank = offset + i + 1
        
        # Assign medal based on rank
        if i < 3 and offset == 0:
            medal = medals[i]
        elif rank <= 8:
            medal = "🏅"
        else:
            medal = "🎖"
        
        users_msg += f"{medal} {rank}. {name} — {count} ta\n"
    
    if not users_msg:
        users_msg = "Hozircha hech kim yo'q."
    
    # Build navigation keyboard
    keyboard = []
    nav_row = []
    
    if offset > 0:
        nav_row.append(InlineKeyboardButton(texts.BTN_PREV, callback_data=f"leaderboard_{offset-10}"))
    
    # Check if there are more users
    next_batch = await db.get_leaderboard(limit=1, offset=offset+10)
    if next_batch:
        nav_row.append(InlineKeyboardButton(texts.BTN_NEXT, callback_data=f"leaderboard_{offset+10}"))
    
    if nav_row:
        keyboard.append(nav_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Send or edit message
    if edit:
        await message.edit_text(msg + users_msg, reply_markup=reply_markup)
    else:
        await message.reply_text(msg + users_msg, reply_markup=reply_markup)


async def menu_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rating button - show leaderboard"""
    await show_leaderboard(update, context)
    logger.info(f"User {update.effective_user.id} viewed leaderboard")


async def leaderboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle leaderboard pagination callbacks"""
    query = update.callback_query
    await query.answer()
    
    try:
        data = query.data.split("_")
        offset = int(data[1]) if len(data) > 1 else 0
    except ValueError:
        offset = 0
    
    await show_leaderboard(query, context, offset=offset, edit=True)
    logger.info(f"User {query.from_user.id} navigated leaderboard to offset {offset}")
