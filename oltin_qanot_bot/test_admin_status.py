"""
Test script to check bot admin status in all required channels
"""
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNELS = ["@Matematika_darslari_dtm", "@matematika2021u"]
PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID", 0))
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID", 0))

async def check_bot_status():
    bot = Bot(token=BOT_TOKEN)
    bot_info = await bot.get_me()
    
    print(f"🤖 Bot: @{bot_info.username} (ID: {bot_info.id})")
    print("="*70)
    
    # Check REQUIRED CHANNELS (mandatory for users)
    print("\n📢 MAJBURIY KANALLAR (Required Channels):")
    print("-"*70)
    
    for channel in REQUIRED_CHANNELS:
        try:
            chat = await bot.get_chat(chat_id=channel)
            member = await bot.get_chat_member(chat_id=channel, user_id=bot_info.id)
            
            print(f"\n{channel}")
            print(f"  Chat ID: {chat.id}")
            print(f"  Title: {chat.title}")
            print(f"  Bot Status: {member.status}")
            
            if hasattr(member, 'can_restrict_members'):
                print(f"  ✅ Can restrict members: {member.can_restrict_members}")
            if hasattr(member, 'can_manage_chat'):
                print(f"  ✅ Can manage chat: {member.can_manage_chat}")
            
            # Check if bot can see member updates
            if member.status not in ['administrator', 'creator']:
                print(f"  ⚠️  WARNING: Bot is NOT admin! Cannot see member updates!")
            
        except Exception as e:
            print(f"\n{channel}")
            print(f"  ❌ ERROR: {e}")
    
    # Check PRIVATE CHATS (rewards)
    print("\n\n🎁 YOPIQ CHATLAR (Private Reward Chats):")
    print("-"*70)
    
    for chat_id, name in [(PRIVATE_GROUP_ID, "Private Group"), (PRIVATE_CHANNEL_ID, "Private Channel")]:
        try:
            chat = await bot.get_chat(chat_id=chat_id)
            member = await bot.get_chat_member(chat_id=chat_id, user_id=bot_info.id)
            
            print(f"\n{name} ({chat_id})")
            print(f"  Title: {chat.title}")
            print(f"  Bot Status: {member.status}")
            
            if hasattr(member, 'can_restrict_members'):
                print(f"  ✅ Can restrict members: {member.can_restrict_members}")
            if hasattr(member, 'can_manage_chat'):
                print(f"  ✅ Can manage chat: {member.can_manage_chat}")
            
            if member.status not in ['administrator', 'creator']:
                print(f"  ⚠️  WARNING: Bot is NOT admin!")
            elif not (hasattr(member, 'can_restrict_members') and member.can_restrict_members):
                print(f"  ⚠️  WARNING: Bot cannot restrict members!")
                
        except Exception as e:
            print(f"\n{name} ({chat_id})")
            print(f"  ❌ ERROR: {e}")
    
    print("\n" + "="*70)
    print("\n✅ XULOSA:")
    print("Bot majburiy kanallarda admin bo'lishi SHART!")
    print("Bot yopiq chatlarda 'Ban users' huquqiga ega bo'lishi SHART!")

if __name__ == "__main__":
    asyncio.run(check_bot_status())
