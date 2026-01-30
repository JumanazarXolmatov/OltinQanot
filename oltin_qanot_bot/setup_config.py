import os
import sys

def update_env(group_id, channel_id):
    env_path = ".env"
    lines = []
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    # Remove existing lines for these keys
    lines = [line for line in lines if not line.startswith("PRIVATE_GROUP_ID") and not line.startswith("PRIVATE_CHANNEL_ID")]
    
    # Add new values
    lines.append(f"PRIVATE_GROUP_ID={group_id}\n")
    lines.append(f"PRIVATE_CHANNEL_ID={channel_id}\n")
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"✅ Updated {env_path}")
    print(f"   PRIVATE_GROUP_ID={group_id}")
    print(f"   PRIVATE_CHANNEL_ID={channel_id}")
    print("\n🚀 Now restart your bot: pkill -f bot.py && python3 bot.py")

if __name__ == "__main__":
    print("--- Oltin Qanot Config Updater ---")
    g_id = input("Enter Private Group ID (e.g. -100...): ").strip()
    c_id = input("Enter Private Channel ID (e.g. -100...): ").strip()
    
    if not g_id or not c_id:
        print("❌ Error: Both IDs are required.")
    else:
        update_env(g_id, c_id)
