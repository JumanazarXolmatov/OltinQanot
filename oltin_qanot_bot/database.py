"""
Enhanced database module for Oltin Qanot Bot
Includes migrations, backups, and advanced queries
"""
import aiosqlite
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from config import Config
from utils.logger import logger


class Database:
    """Database manager with migration support"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Config.get_database_path())
    
    async def init_db(self):
        """Initialize database with schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    phone_number TEXT,
                    referrer_id INTEGER,
                    referral_count INTEGER DEFAULT 0,
                    is_referral_counted BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    language TEXT DEFAULT 'uz',
                    referral_batch INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create schema_version table for migrations
            await db.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create reward_invites table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reward_invites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    invite_link TEXT,
                    batch INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create reward_usage table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reward_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invite_link TEXT,
                    joined_user_id INTEGER,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def create_indexes(self):
        """Create indexes on existing columns"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_referral_count ON users(referral_count DESC)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_status ON users(status)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON users(created_at DESC)"
            )
            await db.commit()
            logger.info("Indexes created")

    
    async def get_schema_version(self) -> int:
        """Get current schema version"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute("SELECT MAX(version) FROM schema_version") as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result[0] else 0
            except:
                return 0
    
    async def apply_migration(self, version: int, sql: str):
        """Apply a database migration"""
        async with aiosqlite.connect(self.db_path) as db:
            current_version = await self.get_schema_version()
            
            if current_version >= version:
                logger.info(f"Migration {version} already applied")
                return
            
            try:
                await db.executescript(sql)
                await db.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (version,)
                )
                await db.commit()
                logger.info(f"Migration {version} applied successfully")
            except Exception as e:
                logger.error(f"Migration {version} failed: {e}")
                raise
    
    async def migrate(self):
        """Run all pending migrations and ensure schema is up to date"""
        async with aiosqlite.connect(self.db_path) as db:
            # Columns to add
            migrations = [
                ("status", "TEXT DEFAULT 'active'"),
                ("language", "TEXT DEFAULT 'uz'"),
                ("created_at", "TIMESTAMP"),
                ("updated_at", "TIMESTAMP"),
                ("reward_sent", "BOOLEAN DEFAULT 0"),
                ("reward_sent_count", "INTEGER DEFAULT 0"),
                ("referral_batch", "INTEGER DEFAULT 0")
            ]
            
            for column, definition in migrations:
                try:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
                    logger.info(f"Added column {column} to users table")
                    
                    # If it's a timestamp, set a default value for existing rows
                    if column in ["created_at", "updated_at"]:
                        await db.execute(f"UPDATE users SET {column} = CURRENT_TIMESTAMP WHERE {column} IS NULL")
                except Exception as e:
                    # Ignore if column already exists
                    logger.debug(f"Migration for {column} skipped or failed: {e}")
                    pass
            
            await db.commit()
            logger.info("Migrations completed")
    
    async def handle_referral_unsubscribe(self, user_id: int, referrer_id: int) -> bool:
        """
        Handle case when a referred user unsubscribes:
        1. Set user's is_referral_counted = 0
        2. Decrement referrer's referral_count
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # 1. Update referred user status
                await db.execute(
                    "UPDATE users SET is_referral_counted = 0, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                
                # 2. Update referrer count
                # First check current count to avoid negative numbers
                async with db.execute("SELECT referral_count FROM users WHERE user_id = ?", (referrer_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row and row[0] > 0:
                        await db.execute(
                            "UPDATE users SET referral_count = referral_count - 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                            (referrer_id,)
                        )
                
                await db.commit()
                logger.info(f"Handled unsubscribe for user {user_id}, referrer {referrer_id} count decremented")
                return True
            except Exception as e:
                logger.error(f"Error handling unsubscribe for {user_id}: {e}")
                return False

    async def mark_reward_sent(self, user_id: int, count: int = 1):
        """Update that reward links have been sent to the user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET reward_sent = 1, reward_sent_count = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (count, user_id)
            )
            await db.commit()

    async def add_reward_invite(self, referrer_id: int, invite_link: str, batch: int):
        """Track generated invite link"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO reward_invites (referrer_id, invite_link, batch) VALUES (?, ?, ?)",
                (referrer_id, invite_link, batch)
            )
            await db.commit()

    async def log_reward_usage(self, invite_link: str, joined_user_id: int):
        """Track who used which invite link"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO reward_usage (invite_link, joined_user_id) VALUES (?, ?)",
                (invite_link, joined_user_id)
            )
            await db.commit()

    async def get_reward_beneficiary(self, referrer_id: int, batch: int) -> Optional[int]:
        """Get the user ID who joined via a specific referrer's batch link"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT ru.joined_user_id 
                   FROM reward_usage ru
                   JOIN reward_invites ri ON ru.invite_link = ri.invite_link
                   WHERE ri.referrer_id = ? AND ri.batch = ?
                   ORDER BY ru.joined_at DESC LIMIT 1""",
                (referrer_id, batch)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    
    async def backup_database(self) -> str:
        """
        Create a backup of the database
        
        Returns:
            Path to backup file
        """
        backup_dir = Config.get_backup_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"oltin_qanot_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    # User Management
    
    async def get_user(self, user_id: int) -> Optional[Tuple]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT user_id, username, full_name, referrer_id, referral_count, 
                          created_at, is_referral_counted, phone_number, status, language, 
                          reward_sent, reward_sent_count, referral_batch
                   FROM users WHERE user_id = ?""",
                (user_id,)
            ) as cursor:
                return await cursor.fetchone()
    
    async def add_user(self, user_id: int, username: str, referrer_id: Optional[int] = None) -> bool:
        """Add new user or update existing user's referrer"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Check if user exists
                async with db.execute("SELECT is_referral_counted, referrer_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        is_counted, current_referrer = row
                        # If user exists but referral not counted, updates referrer if provided
                        if not is_counted and referrer_id and referrer_id != user_id and referrer_id != current_referrer:
                            await db.execute(
                                "UPDATE users SET referrer_id = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                                (referrer_id, user_id)
                            )
                            await db.commit()
                            logger.info(f"Updated referrer for user {user_id} to {referrer_id}")
                        return False
                
                await db.execute(
                    """INSERT INTO users (user_id, username, referrer_id, is_referral_counted, status)
                       VALUES (?, ?, ?, 0, 'active')""",
                    (user_id, username, referrer_id)
                )
                await db.commit()
                logger.info(f"User {user_id} added successfully")
                return True
            except Exception as e:
                logger.error(f"Error adding user {user_id}: {e}")
                return False
    
    async def update_full_name(self, user_id: int, full_name: str):
        """Update user's full name"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET full_name = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (full_name, user_id)
            )
            await db.commit()
    
    async def update_phone_number(self, user_id: int, phone_number: str):
        """Update user's phone number"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET phone_number = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (phone_number, user_id)
            )
            await db.commit()
    
    async def update_language(self, user_id: int, language: str):
        """Update user's language preference"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (language, user_id)
            )
            await db.commit()
    
    async def confirm_referral(self, user_id: int) -> bool:
        """Confirm referral and increment referrer's count"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Get referrer info
                async with db.execute(
                    "SELECT referrer_id, is_referral_counted, full_name, username FROM users WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        logger.warning(f"Could not confirm referral: User {user_id} not found in DB")
                        return False
                    
                    referrer_id, is_counted, full_name, username = row
                
                # Check if already counted or no valid referrer
                if is_counted:
                    logger.info(f"Referral for user {user_id} already counted.")
                    return False
                
                if not referrer_id or referrer_id == user_id:
                    logger.info(f"User {user_id} has no valid referrer (referrer_id={referrer_id})")
                    return False
                
                logger.info(f"Confirming referral: User {user_id} ({full_name or username}) referred by {referrer_id}")
                
                # Mark as counted
                await db.execute(
                    "UPDATE users SET is_referral_counted = 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                
                # Increment referrer count and assign batch
                batch = 0
                async with db.execute("SELECT referral_count FROM users WHERE user_id = ?", (referrer_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        current_count = row[0]
                        if current_count < 5:
                            batch = 1
                        elif current_count < 10:
                            batch = 2
                        else:
                            batch = 3 # Beyond 10, maybe just mark as 3
                        
                        await db.execute(
                            """UPDATE users SET referral_count = referral_count + 1, 
                               updated_at = CURRENT_TIMESTAMP WHERE user_id = ?""",
                            (referrer_id,)
                        )
                
                # Update referred user's batch
                await db.execute(
                    "UPDATE users SET referral_batch = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (batch, user_id)
                )
                
                await db.commit()
                logger.info(f"Referral confirmed for user {user_id}, referrer {referrer_id}")
                return True
            except Exception as e:
                logger.error(f"Error confirming referral: {e}")
                return False
    
    # Leaderboard
    
    async def get_leaderboard(self, limit: int = 10, offset: int = 0) -> List[Tuple]:
        """Get leaderboard with pagination"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT full_name, referral_count 
                   FROM users 
                   WHERE full_name IS NOT NULL AND status = 'active'
                   ORDER BY referral_count DESC 
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            ) as cursor:
                return await cursor.fetchall()
    
    async def get_user_rank(self, user_id: int) -> Optional[int]:
        """Get user's rank in leaderboard"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT COUNT(*) + 1 FROM users 
                   WHERE referral_count > (SELECT referral_count FROM users WHERE user_id = ?)
                   AND full_name IS NOT NULL AND status = 'active'""",
                (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    
    # Admin Functions
    
    async def get_statistics(self) -> Dict:
        """Get contest statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            # Total users
            async with db.execute("SELECT COUNT(*) FROM users WHERE status = 'active'") as cursor:
                stats['total_users'] = (await cursor.fetchone())[0]
            
            # Completed registrations
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE full_name IS NOT NULL AND status = 'active'"
            ) as cursor:
                stats['completed_registrations'] = (await cursor.fetchone())[0]
            
            # Total referrals
            async with db.execute(
                "SELECT SUM(referral_count) FROM users WHERE status = 'active'"
            ) as cursor:
                result = await cursor.fetchone()
                stats['total_referrals'] = result[0] if result[0] else 0
            
            # Today's registrations
            async with db.execute(
                """SELECT COUNT(*) FROM users 
                   WHERE DATE(created_at) = DATE('now') AND status = 'active'"""
            ) as cursor:
                stats['today_registrations'] = (await cursor.fetchone())[0]
            
            # Top referrer
            async with db.execute(
                """SELECT full_name, referral_count FROM users 
                   WHERE full_name IS NOT NULL AND status = 'active'
                   ORDER BY referral_count DESC LIMIT 1"""
            ) as cursor:
                top = await cursor.fetchone()
                stats['top_referrer'] = top if top else ('N/A', 0)
            
            return stats
    
    async def search_users(self, query: str, limit: int = 10) -> List[Tuple]:
        """Search users by name or username"""
        async with aiosqlite.connect(self.db_path) as db:
            search_pattern = f"%{query}%"
            async with db.execute(
                """SELECT user_id, username, full_name, referral_count, status
                   FROM users 
                   WHERE (full_name LIKE ? OR username LIKE ?) AND status = 'active'
                   LIMIT ?""",
                (search_pattern, search_pattern, limit)
            ) as cursor:
                return await cursor.fetchall()
    
    async def block_user(self, user_id: int) -> bool:
        """Block a user"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET status = 'blocked', updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                logger.info(f"User {user_id} blocked")
                return True
            except Exception as e:
                logger.error(f"Error blocking user {user_id}: {e}")
                return False
    
    async def unblock_user(self, user_id: int) -> bool:
        """Unblock a user"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET status = 'active', updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                logger.info(f"User {user_id} unblocked")
                return True
            except Exception as e:
                logger.error(f"Error unblocking user {user_id}: {e}")
                return False
    
    async def export_users_csv(self) -> str:
        """Export all users to CSV format"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT user_id, username, full_name, phone_number, referral_count, 
                          created_at, status FROM users ORDER BY created_at DESC"""
            ) as cursor:
                rows = await cursor.fetchall()
                
                csv_lines = ["User ID,Username,Full Name,Phone,Referrals,Registered,Status"]
                for row in rows:
                    csv_lines.append(','.join(str(x) if x else '' for x in row))
                
                return '\n'.join(csv_lines)


    async def get_referred_users(self, referrer_id: int) -> List[Tuple]:
        """Get list of users referred by this user who have completed registration"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT user_id, username, full_name 
                   FROM users 
                   WHERE referrer_id = ? AND is_referral_counted = 1 AND status = 'active'""",
                (referrer_id,)
            ) as cursor:
                return await cursor.fetchall()


# Global database instance
db = Database()


# Convenience functions for backward compatibility
async def init_db():
    """Initialize database"""
    await db.init_db()
    await db.migrate()
    await db.create_indexes()


async def get_user(user_id: int):
    """Get user by ID"""
    return await db.get_user(user_id)


async def add_user(user_id: int, username: str, referrer_id: Optional[int] = None):
    """Add new user"""
    return await db.add_user(user_id, username, referrer_id)


async def update_full_name(user_id: int, full_name: str):
    """Update user's full name"""
    await db.update_full_name(user_id, full_name)


async def update_phone_number(user_id: int, phone_number: str):
    """Update user's phone number"""
    await db.update_phone_number(user_id, phone_number)


async def confirm_referral(user_id: int):
    """Confirm referral"""
    return await db.confirm_referral(user_id)


async def get_leaderboard(limit: int = 10, offset: int = 0):
    """Get leaderboard"""
    return await db.get_leaderboard(limit, offset)


async def get_referral_count(user_id: int):
    """Get user's referral count"""
    user = await db.get_user(user_id)
    return user[4] if user else 0


async def get_referred_users(referrer_id: int):
    """Get list of referred users"""
    return await db.get_referred_users(referrer_id)


async def get_statistics():
    """Get contest statistics"""
    return await db.get_statistics()


async def get_user_rank(user_id: int):
    """Get user's rank in leaderboard"""
    return await db.get_user_rank(user_id)
