import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

async def check_bot():
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    print(f"Checking token: {token[:10]}...")
    bot = Bot(token)
    try:
        me = await bot.get_me()
        print(f"Bot Name: {me.first_name}")
        print(f"Bot Username: @{me.username}")
        print(f"Bot ID: {me.id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_bot())
