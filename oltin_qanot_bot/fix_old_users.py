"""
Manual fix: Mark old unsubscribed users as 'unsubscribed' in database
This will clean up any users who left before the status update was added
"""
import asyncio
import aiosqlite
from dotenv import load_dotenv
import os

load_dotenv()

async def fix_old_users():
    db_path = os.path.join(os.path.dirname(__file__), "oltin_qanot.db")
    
    async with aiosqlite.connect(db_path) as db:
        # Find users who have is_referral_counted = 0 but status is still 'active'
        # These are users who left but weren't marked as unsubscribed
        async with db.execute(
            "SELECT user_id, full_name, status, is_referral_counted FROM users WHERE is_referral_counted = 0 AND status = 'active'"
        ) as cursor:
            old_users = await cursor.fetchall()
        
        if not old_users:
            print("No old users to fix. All clean!")
            return
        
        print(f"Found {len(old_users)} users who left but still marked as 'active':")
        print("=" * 60)
        for user in old_users:
            print(f"  User ID: {user[0]}, Name: {user[1]}, Status: {user[2]}")
        
        # Update them to 'unsubscribed'
        confirm = input(f"\nMark these {len(old_users)} users as 'unsubscribed'? (yes/no): ")
        if confirm.lower() == 'yes':
            await db.execute(
                "UPDATE users SET status = 'unsubscribed' WHERE is_referral_counted = 0 AND status = 'active'"
            )
            await db.commit()
            print(f"✅ Updated {len(old_users)} users to 'unsubscribed' status")
        else:
            print("Cancelled.")

if __name__ == "__main__":
    asyncio.run(fix_old_users())
