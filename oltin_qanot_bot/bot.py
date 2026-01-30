"""
Oltin Qanot Telegram Bot - Mathematics Course Entry Point
"""
import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ChatMemberHandler, ContextTypes, filters
)
from telegram.error import TelegramError

# Import configuration and utilities
from config import Config
from utils.logger import logger
import database as db
import texts

# Import handlers
from handlers.registration import get_registration_handler
from handlers.menu import (
    menu_invite, menu_my_points, menu_about_course, 
    menu_conditions, menu_channels, menu_partners, menu_send_message
)
from handlers.admin import (
    cmd_stats, cmd_export, cmd_backup, cmd_user,
    cmd_block, cmd_unblock, cmd_broadcast, cmd_test_reward, cmd_id
)
from handlers.membership import handle_chat_member_update


async def post_init(application):
    """Initialize database and perform startup tasks"""
    try:
        logger.info("Initializing database...")
        await db.init_db()
        logger.info("Database initialized successfully")
        
        # Create initial backup
        if Config.ENABLE_AUTO_BACKUP:
            try:
                backup_path = await db.db.backup_database()
                logger.info(f"Startup backup created: {backup_path}")
            except Exception as e:
                logger.warning(f"Startup backup failed: {e}")
        
        logger.info("Bot initialization complete")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise



async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    
    # Notify user of error
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                texts.MSG_ERROR_GENERIC
            )
        except TelegramError:
            pass
            
async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin sends a message to the bot, it gets broadcast to all active users"""
    if not update.effective_user or update.effective_user.id not in Config.ADMIN_IDS:
        return

    if update.message and update.message.text and update.message.text.startswith('/'):
        return

    # Skip if it's a menu button text
    if update.message and update.message.text:
        text = update.message.text.strip()
        button_labels = [
            texts.BTN_ABOUT_COURSE, texts.BTN_CONDITIONS, 
            texts.BTN_INVITE, texts.BTN_MY_POINTS,
            texts.BTN_CHANNELS, texts.BTN_PARTNERS
        ]
        if text in button_labels:
            logger.info(f"Admin {update.effective_user.id} clicked menu button '{text}', skipping broadcast")
            return

    # Broadcast logic
    logger.info(f"Admin {update.effective_user.id} started automatic broadcast")
    # Get all active users
    import aiosqlite
    async with aiosqlite.connect(db.db.db_path) as conn:
        async with conn.execute("SELECT user_id FROM users WHERE status = 'active'") as cursor:
            users = await cursor.fetchall()

    sent_count = 0
    for (user_id,) in users:
        if user_id == update.effective_user.id:
            continue
        try:
            # copy_message is the best way to send "as is"
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            sent_count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi!")


def main():
    """Main bot entry point"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        sys.exit(1)
    
    logger.info("="*50)
    logger.info("Starting Mathematics Course Bot")
    logger.info("="*50)
    
    # Build application
    application = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add membership updates handler (Mandatory for tracking unsubscribes and invite usage)
    application.add_handler(ChatMemberHandler(
        handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER
    ))
    
    # Add registration conversation handler
    application.add_handler(get_registration_handler())
    
    # Add menu handlers
    application.add_handler(MessageHandler(
        filters.Regex(f"^{texts.BTN_ABOUT_COURSE}$"),
        menu_about_course
    ))
    application.add_handler(MessageHandler(
        filters.Regex(f"^{texts.BTN_CONDITIONS}$"),
        menu_conditions
    ))
    application.add_handler(MessageHandler(
        filters.Regex(f"^{texts.BTN_INVITE}$"),
        menu_invite
    ))
    application.add_handler(MessageHandler(
        filters.Regex(f"^{texts.BTN_MY_POINTS}$"),
        menu_my_points
    ))
    application.add_handler(MessageHandler(
        filters.Regex(f"^{texts.BTN_CHANNELS}$"),
        menu_channels
    ))
    application.add_handler(MessageHandler(
        filters.Regex(f"^{texts.BTN_PARTNERS}$"),
        menu_partners
    ))

    # Add admin automatic broadcast handler (High priority)
    application.add_handler(MessageHandler(
        ~filters.COMMAND & (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.Document.ALL),
        admin_broadcast_handler
    ), group=-2) # Run before other handlers
    

    # Add admin command handlers
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(CommandHandler("export", cmd_export))
    application.add_handler(CommandHandler("backup", cmd_backup))
    application.add_handler(CommandHandler("user", cmd_user))
    application.add_handler(CommandHandler("block", cmd_block))
    application.add_handler(CommandHandler("unblock", cmd_unblock))
    application.add_handler(CommandHandler("broadcast", cmd_broadcast))
    application.add_handler(CommandHandler("test_reward", cmd_test_reward))
    application.add_handler(CommandHandler("id", cmd_id))
    
    # Start bot
    logger.info("Bot is starting...")
    print("\n[OK] Mathematics Bot is running!")
    
    try:
        application.run_polling(
            allowed_updates=["message", "callback_query", "chat_member"],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
