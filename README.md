# 🦅 Oltin Qanot Telegram Bot

A referral contest bot for the Oltin Qanot volunteer organization. Users can register, invite friends, and compete on a leaderboard for prizes.

## ✨ Features

### User Features
- 📱 Phone number verification
- 👤 Full name registration (passport-compliant)
- 📢 Channel subscription verification
- 🤝 Referral link generation
- 🏆 Real-time leaderboard with pagination
- 👥 Personal account dashboard
- 📜 Contest rules and prizes
- 🌐 Social media links

### Admin Features
- 📊 Contest statistics dashboard
- 📥 User data export (CSV)
- 💾 Database backup system
- 👤 User management (view, block, unblock)
- 📢 Broadcast messages to all users
- 🔍 User search functionality

### Technical Features
- 🔐 Secure environment variable configuration
- 📝 Comprehensive logging system
- ✅ Input validation and sanitization
- 🗄️ SQLite database with migrations
- 🔄 Automatic backups
- 🎯 Modular handler architecture
- 🌍 Multi-language support (ready)

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone or navigate to the project**
   ```bash
   cd OltinQanot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd oltin_qanot_bot
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env with your values
   # Required: BOT_TOKEN, ADMIN_IDS, REQUIRED_CHANNELS
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

## ⚙️ Configuration

Edit `.env` file with your settings:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username

# Admin IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# Required channels (comma-separated, with @)
REQUIRED_CHANNELS=@your_channel_1,@your_channel_2
```

See `.env.example` for all available options.

## 📋 Admin Commands

| Command | Description |
|---------|-------------|
| `/stats` | View contest statistics |
| `/export` | Export users to CSV |
| `/backup` | Create database backup |
| `/user <id>` | View user details |
| `/block <id>` | Block a user |
| `/unblock <id>` | Unblock a user |
| `/broadcast <message>` | Send message to all users |

## 🏗️ Project Structure

```
OltinQanot/
├── oltin_qanot_bot/
│   ├── bot.py              # Main entry point
│   ├── config.py           # Configuration management
│   ├── database.py         # Database layer
│   ├── texts.py            # Text management
│   ├── handlers/           # Command handlers
│   │   ├── registration.py # Registration flow
│   │   ├── menu.py         # Menu handlers
│   │   ├── leaderboard.py  # Leaderboard display
│   │   └── admin.py        # Admin commands
│   ├── utils/              # Utility functions
│   │   ├── logger.py       # Logging setup
│   │   ├── validators.py   # Input validation
│   │   ├── formatters.py   # Text formatting
│   │   └── subscription.py # Channel verification
│   ├── locales/            # Translations
│   │   └── uz.py           # Uzbek texts
│   └── requirements.txt    # Dependencies
├── backups/                # Database backups
├── .env                    # Environment config
└── README.md               # This file
```

## 🗄️ Database Schema

### users Table
| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER PRIMARY KEY | Telegram user ID |
| username | TEXT | Telegram username |
| full_name | TEXT | User's full name |
| phone_number | TEXT | Phone number |
| referrer_id | INTEGER | Referrer's user ID |
| referral_count | INTEGER | Number of referrals |
| is_referral_counted | BOOLEAN | Prevents double-counting |
| status | TEXT | active/blocked/deleted |
| language | TEXT | Language preference |
| created_at | TIMESTAMP | Registration date |
| updated_at | TIMESTAMP | Last update |

## 🎯 Contest Prizes

| Rank | Prize |
|------|-------|
| 🥇 1st | Diplom + Minnatdorchilik xati + Telegram Premium (1 month) |
| 🥈 2nd | Diplom + Minnatdorchilik xati + Mutolaa Premium (1 month) |
| 🥉 3rd | Diplom + Minnatdorchilik xati + Mutolaa Premium (1 month) |
| 🏅 4-8th | Sertifikat + Minnatdorchilik xati |
| 🎖 9-15th | Sertifikat |

## 🔒 Security

- ✅ No hardcoded credentials
- ✅ Environment variable configuration
- ✅ Input validation and sanitization
- ✅ SQL injection prevention (parameterized queries)
- ✅ Comprehensive error handling
- ✅ Secure logging (no sensitive data)

## 🐛 Troubleshooting

### Bot doesn't start
- Check `.env` file exists and has valid `BOT_TOKEN`
- Verify Python version (3.10+)
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Database errors
- Delete `oltin_qanot.db` and restart (creates fresh database)
- Check file permissions in project directory

### Users can't register
- Verify `REQUIRED_CHANNELS` are correct (with @)
- Check bot is admin in required channels
- Review logs in `bot.log`

## 📝 Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black oltin_qanot_bot/
flake8 oltin_qanot_bot/
```

### Creating Backups
```bash
# Automatic (on startup if enabled)
ENABLE_AUTO_BACKUP=true

# Manual (admin command)
/backup
```

## 📞 Support

- **Oltin Qanot**: https://t.me/Toshkent_vil_Oltinqanot
- **Volunteers Uzbekistan**: https://t.me/Volunteers_uz
- **Ezgu.uz**: https://t.me/www_ezgu_uz

## 📄 License

This project is created for the Oltin Qanot volunteer organization.

## 🙏 Credits

Developed with ❤️ for the Oltin Qanot community.

---

**Version**: 2.0.0 (Refactored)  
**Last Updated**: 2026-01-28

