"""
Admin command handlers for Oltin Qanot Bot
"""
from telegram import Update
from telegram.ext import ContextTypes
import database as db
import texts
from config import Config
from utils.logger import logger
from utils.formatters import format_number
from datetime import datetime


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in Config.ADMIN_IDS


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show contest statistics (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    stats = await db.db.get_statistics()
    
    text = texts.MSG_ADMIN_STATS.format(
        total_users=format_number(stats['total_users']),
        completed=format_number(stats['completed_registrations']),
        total_referrals=format_number(stats['total_referrals']),
        today=format_number(stats['today_registrations']),
        top_name=stats['top_referrer'][0],
        top_count=stats['top_referrer'][1]
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')
    logger.info(f"Admin {update.effective_user.id} viewed statistics")


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export users to CSV (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    await update.message.reply_text("📊 Eksport qilinmoqda...")
    
    try:
        csv_data = await db.db.export_users_csv()
        
        # Send as file
        filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        await update.message.reply_document(
            document=csv_data.encode('utf-8'),
            filename=filename,
            caption=f"✅ {filename} tayyor!"
        )
        logger.info(f"Admin {update.effective_user.id} exported users")
    except Exception as e:
        logger.error(f"Export failed: {e}")
        await update.message.reply_text(texts.MSG_ERROR_GENERIC)


async def cmd_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create database backup (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    try:
        backup_path = await db.db.backup_database()
        await update.message.reply_text(f"✅ Backup yaratildi:\n`{backup_path}`", parse_mode='Markdown')
        logger.info(f"Admin {update.effective_user.id} created backup")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        await update.message.reply_text(texts.MSG_ERROR_GENERIC)


async def cmd_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View user details (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Foydalanish: /user <user_id>")
        return
    
    user_id = int(context.args[0])
    user = await db.get_user(user_id)
    
    if not user:
        await update.message.reply_text(texts.MSG_ERROR_USER_NOT_FOUND)
        return
    
    rank = await db.db.get_user_rank(user_id)
    
    reward_status = "✅ Yuborilgan" if len(user) > 10 and user[10] else "❌ Yuborilmagan"
    
    text = (
        f"👤 **Foydalanuvchi ma'lumotlari**\n\n"
        f"🆔 ID: `{user[0]}`\n"
        f"👤 Username: @{user[1] or 'N/A'}\n"
        f"📝 F.I.Sh: {user[2] or 'N/A'}\n"
        f"📱 Telefon: {user[7] if len(user) > 7 else 'N/A'}\n"
        f"🤝 Taklif qilganlar: {user[4]}\n"
        f"🎁 Link: {reward_status}\n"
        f"🏅 Reyting: {rank or 'N/A'}\n"
        f"📊 Status: {user[8] if len(user) > 8 else 'active'}\n"
        f"📅 Ro'yxatdan o'tgan: {user[5]}"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')
    logger.info(f"Admin {update.effective_user.id} viewed user {user_id}")


async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a user (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Foydalanish: /block <user_id>")
        return
    
    user_id = int(context.args[0])
    success = await db.db.block_user(user_id)
    
    if success:
        await update.message.reply_text(texts.MSG_USER_BLOCKED)
        logger.info(f"Admin {update.effective_user.id} blocked user {user_id}")
    else:
        await update.message.reply_text(texts.MSG_ERROR_GENERIC)


async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unblock a user (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Foydalanish: /unblock <user_id>")
        return
    
    user_id = int(context.args[0])
    success = await db.db.unblock_user(user_id)
    
    if success:
        await update.message.reply_text(texts.MSG_USER_UNBLOCKED)
        logger.info(f"Admin {update.effective_user.id} unblocked user {user_id}")
    else:
        await update.message.reply_text(texts.MSG_ERROR_GENERIC)


async def cmd_test_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test generating reward links (Admin only)"""
    if update.effective_user.id not in Config.ADMIN_IDS:
        return
        
    await update.message.reply_text("🔍 Mukofot havolalarini yaratish testi boshlandi...")
    
    from utils.subscription import create_one_time_invite_link
    
    results = []
    
    chats = [
        ("Guruh", Config.PRIVATE_GROUP_ID),
        ("Kanal", Config.PRIVATE_CHANNEL_ID)
    ]
    
    for label, chat_id in chats:
        if not chat_id or chat_id == 0:
            results.append(f"⚠️ {label} ID si sozlanmagan (0 yoki Yo'q)")
            continue
            
        try:
            # Try to get chat info first
            chat = await context.bot.get_chat(chat_id)
            chat_info = f"{label}: <b>{chat.title}</b> (ID: {chat_id}, Type: {chat.type})"
            
            # Try to create invite link
            link = await create_one_time_invite_link(context.bot, chat_id)
            if link:
                results.append(f"✅ {chat_info}\n🔗 Havola: {link}")
            else:
                results.append(f"❌ {chat_info}\n⚠️ Havola yaratib bo'lmadi. Bot guruhda admin va 'Invite Users via Link' ruxsati bormi?")
        except Exception as e:
            results.append(f"❌ {label} (ID: {chat_id}) bilan bog'lanishda xato:\n<code>{e}</code>")
        
    if not results:
        results.append("⚠️ Hech qanday guruh yoki kanal ID si sozlanmagan!")
        
    await update.message.reply_text("\n\n".join(results), parse_mode="HTML")


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(texts.MSG_ERROR_NOT_ADMIN)
        return
    
    if not context.args:
        await update.message.reply_text(texts.MSG_BROADCAST_START)
        return
    
    message_text = ' '.join(context.args)
    
    import aiosqlite
    async with aiosqlite.connect(db.db.db_path) as conn:
        async with conn.execute("SELECT user_id FROM users WHERE status = 'active'") as cursor:
            users = await cursor.fetchall()
    
    sent_count = 0
    for (user_id,) in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message_text)
            sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast to {user_id}: {e}")
    
    await update.message.reply_text(texts.MSG_BROADCAST_CONFIRM.format(count=sent_count))
    logger.info(f"Admin {update.effective_user.id} sent broadcast to {sent_count} users")
