"""
Quick check: Bot permissions in PRIVATE chats
"""
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    bot = Bot(os.getenv("BOT_TOKEN"))
    bot_info = await bot.get_me()
    
    PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID"))
    PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID"))
    
    print(f"Bot: @{bot_info.username}\n")
    
    # Check Private Group
    print("=" * 60)
    print("YOPIQ GURUH (Private Group)")
    print("=" * 60)
    try:
        chat = await bot.get_chat(PRIVATE_GROUP_ID)
        member = await bot.get_chat_member(PRIVATE_GROUP_ID, bot_info.id)
        
        print(f"Chat ID: {PRIVATE_GROUP_ID}")
        print(f"Title: {chat.title}")
        print(f"Bot Status: {member.status}")
        
        if member.status in ['administrator', 'creator']:
            print(f"✅ Bot is {member.status}")
            if hasattr(member, 'can_restrict_members'):
                if member.can_restrict_members:
                    print("✅ Can restrict members: YES")
                else:
                    print("❌ Can restrict members: NO - SHART!")
            else:
                print("⚠️  Can't check 'can_restrict_members' permission")
        else:
            print(f"❌ Bot is NOT admin! Status: {member.status}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Check Private Channel
    print("\n" + "=" * 60)
    print("YOPIQ KANAL (Private Channel)")
    print("=" * 60)
    try:
        chat = await bot.get_chat(PRIVATE_CHANNEL_ID)
        member = await bot.get_chat_member(PRIVATE_CHANNEL_ID, bot_info.id)
        
        print(f"Chat ID: {PRIVATE_CHANNEL_ID}")
        print(f"Title: {chat.title}")
        print(f"Bot Status: {member.status}")
        
        if member.status in ['administrator', 'creator']:
            print(f"✅ Bot is {member.status}")
            if hasattr(member, 'can_restrict_members'):
                if member.can_restrict_members:
                    print("✅ Can restrict members: YES")
                else:
                    print("❌ Can restrict members: NO - SHART!")
            else:
                print("⚠️  Can't check 'can_restrict_members' permission")
        else:
            print(f"❌ Bot is NOT admin! Status: {member.status}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("NATIJA:")
    print("Agar bot admin bo'lmasa yoki 'Ban users' huquqi bo'lmasa,")
    print("foydalanuvchilarni chiqarib yuborolmaydi!")
    print("=" * 60)

asyncio.run(main())
