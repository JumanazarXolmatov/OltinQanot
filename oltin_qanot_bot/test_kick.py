"""
Test script to verify bot can kick users from private chats
"""
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID", 0))
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID", 0))

# Test user ID (sizning ID'ingiz)
TEST_USER_ID = 5916834937

async def test_permissions():
    bot = Bot(token=BOT_TOKEN)
    
    print(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
    print(f"👥 Private Group ID: {PRIVATE_GROUP_ID}")
    print(f"📢 Private Channel ID: {PRIVATE_CHANNEL_ID}")
    print(f"👤 Test User ID: {TEST_USER_ID}")
    print("\n" + "="*50)
    
    # Test PRIVATE GROUP
    print("\n📋 Testing PRIVATE GROUP permissions...")
    try:
        # Check bot's permissions
        chat_member = await bot.get_chat_member(chat_id=PRIVATE_GROUP_ID, user_id=(await bot.get_me()).id)
        print(f"✅ Bot status in group: {chat_member.status}")
        
        if hasattr(chat_member, 'can_restrict_members'):
            print(f"   Can restrict members: {chat_member.can_restrict_members}")
        
        # Try to kick test user
        print(f"\n🔨 Attempting to kick user {TEST_USER_ID} from group...")
        await bot.ban_chat_member(chat_id=PRIVATE_GROUP_ID, user_id=TEST_USER_ID)
        print(f"✅ Successfully banned user")
        
        await bot.unban_chat_member(chat_id=PRIVATE_GROUP_ID, user_id=TEST_USER_ID)
        print(f"✅ Successfully unbanned user")
        
    except Exception as e:
        print(f"❌ ERROR with group: {e}")
    
    # Test PRIVATE CHANNEL
    print("\n📋 Testing PRIVATE CHANNEL permissions...")
    try:
        # Check bot's permissions
        chat_member = await bot.get_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=(await bot.get_me()).id)
        print(f"✅ Bot status in channel: {chat_member.status}")
        
        if hasattr(chat_member, 'can_restrict_members'):
            print(f"   Can restrict members: {chat_member.can_restrict_members}")
        
        # Try to kick test user
        print(f"\n🔨 Attempting to kick user {TEST_USER_ID} from channel...")
        await bot.ban_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=TEST_USER_ID)
        print(f"✅ Successfully banned user")
        
        await bot.unban_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=TEST_USER_ID)
        print(f"✅ Successfully unbanned user")
        
    except Exception as e:
        print(f"❌ ERROR with channel: {e}")
    
    print("\n" + "="*50)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_permissions())
