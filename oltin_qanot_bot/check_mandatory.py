"""
Check if bot is admin in MANDATORY channels
"""
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    bot = Bot(os.getenv("BOT_TOKEN"))
    bot_info = await bot.get_me()
    
    REQUIRED_CHANNELS = ["@Matematika_darslari_dtm", "@matematika2021u"]
    
    results = []
    results.append(f"Bot: @{bot_info.username} (ID: {bot_info.id})\n")
    results.append("=" * 70)
    results.append("CHECKING MANDATORY CHANNELS")
    results.append("=" * 70)
    
    all_ok = True
    
    for channel in REQUIRED_CHANNELS:
        results.append(f"\nChannel: {channel}")
        try:
            chat = await bot.get_chat(channel)
            member = await bot.get_chat_member(channel, bot_info.id)
            
            results.append(f"  Chat ID: {chat.id}")
            results.append(f"  Title: {chat.title}")
            results.append(f"  Bot Status: {member.status}")
            
            if member.status in ['administrator', 'creator']:
                results.append(f"  OK: Bot is {member.status}")
            else:
                results.append(f"  ERROR: Bot is NOT admin!")
                results.append(f"  Bot MUST be admin to receive ChatMember updates!")
                all_ok = False
                
        except Exception as e:
            results.append(f"  ERROR: {e}")
            all_ok = False
    
    results.append("\n" + "=" * 70)
    if all_ok:
        results.append("SUCCESS: Bot is admin in all mandatory channels")
        results.append("Bot CAN receive ChatMember updates (leave events)")
    else:
        results.append("PROBLEM: Bot is NOT admin in some channels!")
        results.append("Bot CANNOT receive ChatMember updates!")
        results.append("\nFIX: Add bot as admin in ALL mandatory channels:")
        for ch in REQUIRED_CHANNELS:
            results.append(f"  - {ch}")
    results.append("=" * 70)
    
    # Write to file
    with open("mandatory_channels_check.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    print("Results written to: mandatory_channels_check.txt")
    for line in results:
        print(line)

asyncio.run(main())
