import asyncio
import os
import shutil
import database as db

async def test_logic():
    print("Testing Oltin Qanot Bot Logic...")
    
    # Reset DB for testing
    if os.path.exists("oltin_qanot.db"):
        os.remove("oltin_qanot.db")
        
    await db.init_db()
    print("[OK] Database initialized.")

    # 1. Add User A (First user, no referrer)
    success = await db.add_user(1001, "UserA")
    assert success == True
    await db.update_full_name(1001, "Ali Valiev")
    print("[OK] User A added.")

    # 2. Add User B (Referred by A)
    success = await db.add_user(1002, "UserB", referrer_id=1001)
    assert success == True
    await db.update_full_name(1002, "Vali Aliev")
    
    # Check count for A (should be 0 before confirmation)
    count_a = await db.get_referral_count(1001)
    print(f"User A referral count (pre-confirm): {count_a}")
    assert count_a == 0
    print("[OK] Referral count deferred correctly.")

    # 3. Confirm B
    await db.confirm_referral(1002)
    count_a = await db.get_referral_count(1001)
    print(f"User A referral count (post-confirm): {count_a}")
    assert count_a == 1
    print("[OK] Referral confirmed and counted.")

    # 4. Confirm B again (should ignore)
    await db.confirm_referral(1002)
    count_a = await db.get_referral_count(1001)
    assert count_a == 1
    print("[OK] Double confirmation prevented.")

    # 5. Leaderboard Check
    await db.get_leaderboard() # Just ensure no crash
    print("[OK] Leaderboard query works.")

if __name__ == "__main__":
    asyncio.run(test_logic())
