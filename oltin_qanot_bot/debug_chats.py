import asyncio
from telegram import Bot
from config import Config
import sys

async def debug():
    print(f"--- Bot Debug Diagnostics ---")
    print(f"Token: {Config.BOT_TOKEN[:10]}...{Config.BOT_TOKEN[-5:]}")
    
    bot = Bot(Config.BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"Bot Name: @{me.username}")
    except Exception as e:
        print(f"CRITICAL: Cannot connect to Telegram: {e}")
        return

    chats = [
        ("Private Group", Config.PRIVATE_GROUP_ID),
        ("Private Channel", Config.PRIVATE_CHANNEL_ID)
    ]

    for label, chat_id in chats:
        print(f"\nChecking {label} (ID: {chat_id})...")
        if not chat_id or chat_id == 0:
            print(f"  ❌ ID is not set or is 0")
            continue
            
        try:
            chat = await bot.get_chat(chat_id)
            print(f"  ✅ Found Chat: {chat.title} ({chat.type})")
            
            # Check invite link power
            try:
                link = await bot.create_chat_invite_link(chat_id=chat_id, member_limit=1)
                print(f"  ✅ Success! Invite link generated: {link.invite_link}")
            except Exception as e:
                print(f"  ❌ Failed to create invite link: {e}")
                print(f"  👉 Tip: Make sure the bot is an ADMIN and has 'Invite Users via Link' permission.")
        except Exception as e:
            print(f"  ❌ Error getting chat info: {e}")
            print(f"  👉 Tip: The ID might be wrong, or the bot is not a member/admin.")

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        print("Error: BOT_TOKEN not found in config.")
        sys.exit(1)
    asyncio.run(debug())
