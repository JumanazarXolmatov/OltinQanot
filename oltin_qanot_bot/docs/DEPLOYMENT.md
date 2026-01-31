# 🚀 Telegram Botni Serverga Joylash (Deployment)

Ushbu qo'llanma botni VPS (Virtual Private Server) yoki boshqa serverga **Docker** yordamida joylashni o'rgatadi.

## 📋 Talablar
Serveringizda quyidagilar o'rnatilgan bo'lishi kerak:
- **Git**
- **Docker** va **Docker Compose**

## 🛠 1-qadam: Kodni Serverga Yuklash
Serveringiz terminaliga kiring va quyidagi buyruqlarni bering:

```bash
# Loyihani klonlash (kochirib olish)
git clone https://github.com/JumanazarXolmatov/OltinQanot.git

# Papkaga kirish
cd OltinQanot/oltin_qanot_bot
```

## ⚙️ 2-qadam: Sozlamalar (.env)
Serverda tokenlarni kiritish uchun `.env` faylini yaratish kerak:

```bash
# Namuna faylidan nusxa olish
cp .env.example .env

# Faylni tahrirlash
nano .env
```

`nano` ichida:
1. `BOT_TOKEN` ni o'zgartiring.
2. `ADMIN_IDS` ga o'z ID raqamingizni yozing.
3. Kerakli kanal va guruh IDlarini kiriting.
4. *CTRL+X*, keyin *Y*, keyin *Enter* bosib saqlang.

## 🚀 3-qadam: Ishga Tushirish
Docker yordamida botni ishga tushirish juda oson:

```bash
docker-compose up -d --build
```
Bu buyruq:
1. Barcha kerakli dasturlarni o'rnatadi.
2. Botni "container" ichida ishga tushiradi.
3. Agar server o'chib yonsa, bot avtomatik qayta yonadi.

## 📊 Boshqarish

**Loglarni ko'rish (xatoliklarni tekshirish):**
```bash
docker-compose logs -f
```

**Botni to'xtatish:**
```bash
docker-compose down
```

**Botni yangilash (kod o'zgarganda):**
```bash
# Yangi kodni olish
git pull

# Qayta ishga tushirish
docker-compose up -d --build
```
