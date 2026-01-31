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
    
    results = []
    results.append(f"Bot: @{bot_info.username}\n")
    
    # Check Private Group
    results.append("=" * 60)
    results.append("PRIVATE GROUP CHECK")
    results.append("=" * 60)
    try:
        chat = await bot.get_chat(PRIVATE_GROUP_ID)
        member = await bot.get_chat_member(PRIVATE_GROUP_ID, bot_info.id)
        
        results.append(f"Chat ID: {PRIVATE_GROUP_ID}")
        results.append(f"Title: {chat.title}")
        results.append(f"Bot Status: {member.status}")
        
        if member.status in ['administrator', 'creator']:
            results.append(f"OK: Bot is {member.status}")
            if hasattr(member, 'can_restrict_members'):
                if member.can_restrict_members:
                    results.append("OK: Can restrict members = YES")
                else:
                    results.append("ERROR: Can restrict members = NO (REQUIRED!)")
            else:
                results.append("WARNING: Cannot check can_restrict_members")
        else:
            results.append(f"ERROR: Bot is NOT admin! Status: {member.status}")
    except Exception as e:
        results.append(f"ERROR: {e}")
    
    # Check Private Channel
    results.append("\n" + "=" * 60)
    results.append("PRIVATE CHANNEL CHECK")
    results.append("=" * 60)
    try:
        chat = await bot.get_chat(PRIVATE_CHANNEL_ID)
        member = await bot.get_chat_member(PRIVATE_CHANNEL_ID, bot_info.id)
        
        results.append(f"Chat ID: {PRIVATE_CHANNEL_ID}")
        results.append(f"Title: {chat.title}")
        results.append(f"Bot Status: {member.status}")
        
        if member.status in ['administrator', 'creator']:
            results.append(f"OK: Bot is {member.status}")
            if hasattr(member, 'can_restrict_members'):
                if member.can_restrict_members:
                    results.append("OK: Can restrict members = YES")
                else:
                    results.append("ERROR: Can restrict members = NO (REQUIRED!)")
            else:
                results.append("WARNING: Cannot check can_restrict_members")
        else:
            results.append(f"ERROR: Bot is NOT admin! Status: {member.status}")
    except Exception as e:
        results.append(f"ERROR: {e}")
    
    results.append("\n" + "=" * 60)
    results.append("SUMMARY:")
    results.append("Bot MUST be admin with 'Ban users' permission")
    results.append("in both private group and channel!")
    results.append("=" * 60)
    
    # Write to file
    with open("permissions_check.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    print("Results written to: permissions_check.txt")
    for line in results:
        print(line)

asyncio.run(main())
