"""
Uzbek language texts for Mathematics Course Bot
"""

# Registration Flow
ASK_SUB_START = (
    "👋 Assalomu alaykum, {full_name}!\n"
    "<b>📚 BEPUL MATEMATIKA DARSLARI</b> botiga xush kelibsiz!\n"
    "Pastdagi kanal va guruhga a'zo bo'ling va tasdiqlash tugmani bosing 👇"
)

ASK_PHONE_TEMPLATE = (
    "🤖 Botdan foydalanish uchun telefon raqamingizni tasdiqlashingiz kerak.\n"
    "Quyidagi '📞 Raqamni yuborish' tugmasini bosing:"
)

MSG_LEFT_NOTIFICATION = (
    "⚠️ <b>Diqqat!</b>\n\n"
    "Siz <b>{channel_name}</b> kanalidan/guruhidan chiqib ketdingiz.\n"
    "Botdan foydalanishni davom ettirish uchun iltimos qayta a'zo bo'ling!"
)

MSG_SUB_SPECIFIC = (
    "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart!</b>\n\n"
    "Iltimos, ushbu manbalarga a'zo bo'ling va '✅ Tasdiqlash' tugmasini bosing:"
)

ASK_NAME = (
    "1️⃣ F.I.Sh kiriting.\n"
    "📌 <b>Eslatma:</b> Ism familiya pasport/ID karta bilan bir xil bo'lishi kerak!\n"
    "Namuna: Xolmatov Jumanazar"
)

SUB_CHECK_MSG = "📌 Tanlovda ishtirok etish uchun quyidagi kanallarga obuna bo'ling:"

MSG_REG_COMPLETED_WELCOME = (
    "Assalomu aleykum, yaxshimisiz?\n"
    "⚡️ Sizni ko'rib turganimdan xursandman😄\n"
    "📌 Siz bilan Milliy Sertifikat va Attestatsiya imtihonlariga tayyorlanamiz, quyidagi menyudan kerakli bo'limni tanlang 👇👇👇👇"
)

# Contest Info
MSG_CONDITIONS = (
    "✅ <b>Bepul Marafonda ishtirok etish uchun shartlar bilan to'liq tanishamiz📌</b>\n\n"
    "✅ Siz Milliy sertifikat va Attestatsiyaga tayyorlanib yurgan va Tayyorlanish istagida bo'lgan tanishlaringizni taklif qilishingiz kerak\n\n"
    "✅ <b>1-Shart:</b> Bot siz uchun alohida taklif havolasi beradi va siz eng kamida <b>5 ta do'stingizni</b> taklif qilasiz 😊 va sizga darslarimizda qatnashish uchun <b>Avtomatik Yopiq guruh uchun link</b> yuboriladi.\n\n"
    "✅ <b>2-Shart:</b> Agar siz taklif qilgan odamlar qo'shilgan kanaldan chiqib ketadigan bo'lsa siz to'plagan ballaringizdan chegirilib boriladi va ballaringiz soni <b>5 balldan kam</b> bo'lib qolsa siz avtomatik bizning yopiq kanal va guruhimizdagi Bepul darslarimizdan chetlashtirilasiz😔\n\n"
    "📍 <b>Maslahat:</b> Bizning <b>YOPIQ KANAL va GURUHimizda</b> muntazam qolish uchun 5 tadan ko'proq odam taklif qilishni maslahat beraman 😊\n\n"
    "✅ Tayyor bo'lsangiz menyudan <b>Taklif havolasi</b> tugmasini bosing 🤝"
)

MSG_ABOUT_COURSE = (
    "🎓 <b>Assalomu alaykum, hurmatli Matematika ustozlari va o'quvchi abituriyentlar!</b>\n\n"
    "✅ Milliy sertifikat va Attestatsiya imtihoniga tayyorlayapsizmi? Va Bu safar imtihon savollari qiyin bo'ladi deyishyaptimi?\n\n"
    "✅ Unda Bizning <b>Bepul guruhimizga</b> qo'shiling\n\n"
    "✅ Bepul Marafonda har kuni imtihonda tushadigan testlar va ularning <b>Jonli tahlillari</b> va <b>Video darslarda</b> qatnashishingiz mumkin.\n\n"
    "👨‍💻 Tahlillar va Video darslar hozirga qadar <b>1500+</b> Ustozlar va Abituriyentlar <b>0 dan</b> Milliy va Xalqaro sertifikatlar olib chiqgan hamda Nufuzli Oliygohlar talabasi bo'lishga hissa qo'shgan <b>GRE/SAT/Milliy sertifikatlar</b> sohiblari <b>Ulug'bek Xushbaqov</b> va <b>Javohir Nazirov</b> tomonidan olib boriladi.\n\n"
    "🔘 ⏬ <b>Darsda qatnashish</b> ⏬ 🔘"
)

SHARE_TEXT_TEMPLATE = (
    "🔥 BEPUL MATEMATIKA MARAFONI 🔥\n\n"
    "📌 Milliy sertifikat va Attestatsiya uchun:\n"
    "✅ Mavzular sodda tushuntiriladi\n"
    "✅ Testlar va tahlillar\n"
    "✅ Imtihonga yo'naltirilgan darslar\n"
    "🔒 Yopiq guruhda bepul\n\n"
    "Shart oddiy:\n"
    "➡️ 5 ta do'stni taklif qiling\n"
    "➡️ Yopiq guruhga kiring\n\n"
    "👉 Havola:\n"
    "🔗 {link}\n\n"
    "⏳ Joylar cheklangan!"
)

# Button Labels (Reply Keyboard)
BTN_SEND_PHONE = "📞 Raqamni yuborish"
BTN_ABOUT_COURSE = "📚Bepul kurs haqida"
BTN_CONDITIONS = "📑Darsda qatnashish sharti📑"
BTN_INVITE = "🔗Taklif havolasi🔗"
BTN_MY_POINTS = "Ballarim📊"
BTN_CHANNELS = "Bizning kanallar🤖"
BTN_PARTNERS = "🤝 Hamkorlik uchun"
BTN_SEND_MESSAGE = "✍️ Xabar yuborish"

# Button Labels (Inline)
BTN_SUBSCRIBED = "✅ Tasdiqlash"
BTN_SUB_CHANNEL = "📢 MATEMATIKA DARSLARI"
BTN_SUB_GROUP = "💬 Matematika guruhi"
BTN_SHARE = "📤 Ulashish"
BTN_PREV = "⬅️ Oldingi"
BTN_NEXT = "➡️ Keyingi"

# Menu Messages
MSG_MAIN_MENU = "Asosiy menyu:"
MSG_MY_POINTS_TEMPLATE = (
    "👤 <b>Mening hisobim</b>\n\n"
    "👤 F.I.Sh: <b>{full_name}</b>\n"
    "🆔 ID: <code>{user_id}</code>\n"
    "👥 Taklif qilganlaringiz: <b>{referral_count}</b> ta\n"
    "🏆 O'riningiz: <b>{rank}</b>-o'rin\n\n"
    "{referrals_list}"
    "🎁 Kursga kirish uchun yana <b>{remaining}</b> ta do'stingizni taklif qilishingiz kerak."
)
MSG_REFERRALS_LIST_TITLE = "📋 <b>Siz taklif qilgan do'stlaringiz:</b>\n"
MSG_REFERRAL_ITEM = "• {username} ({full_name})\n"
MSG_REFERRAL_ITEM_NO_USERNAME = "• {full_name} (Username yo'q)\n"
MSG_NO_REFERRALS = "Siz hali hech kimni taklif qilmadingiz.\n\n"

MSG_SOCIALS = "✅ Bizning rasmiy kanallarimiz:"

# Status Messages
MSG_NOT_SUBSCRIBED = "Siz barcha kanallarga obuna bo'lmadingiz. Iltimos, obuna bo'lib qayta tekshiring."
MSG_WELCOME_BACK = "Qayta xush kelibsiz!"
MSG_REG_COMPLETED = "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!"
MSG_INVALID_NAME = "⚠️ Iltimos, to'liq ism familiyangizni kiriting (kamida 2 ta so'z)."

# Admin Messages
MSG_ADMIN_STATS = (
    "📊 <b>Tanlov statistikasi</b>\n\n"
    "👥 Jami foydalanuvchilar: {total_users}\n"
    "✅ To'liq ro'yxatdan o'tganlar: {completed}\n"
    "🤝 Jami taklif qilinganlar: {total_referrals}\n"
    "📅 Bugun ro'yxatdan o'tganlar: {today}\n"
    "🏆 Eng faol: {top_name} ({top_count} ta)"
)

MSG_BROADCAST_START = "📢 Xabarni yuboring (barcha foydalanuvchilarga yuboriladi):"
MSG_BROADCAST_CONFIRM = "Xabar {count} ta foydalanuvchiga yuborildi!"
MSG_USER_BLOCKED = "🚫 Foydalanuvchi bloklandi"
MSG_USER_UNBLOCKED = "✅ Foydalanuvchi blokdan chiqarildi"

# Error Messages
MSG_ERROR_GENERIC = "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
MSG_ERROR_NOT_ADMIN = "⛔ Bu buyruq faqat adminlar uchun!"
MSG_ERROR_USER_NOT_FOUND = "❌ Foydalanuvchi topilmadi"

# Course Access
MSG_CONGRATS_LINK = (
    "🎉 <b>Tabriklaymiz!</b> Siz 5 ta do'stingizni taklif qildingiz.\n\n"
    "Mana sizning yopiq guruh va kanalga kirish uchun bir martalik havolalaringiz:\n\n"
    "👥 <b>Yopiq guruh:</b> {group_link}\n"
    "📢 <b>Yopiq kanal:</b> {channel_link}\n\n"
    "⚠️ <b>Eslatma:</b> Ushbu havolalar faqat bir marta ishlaydi!"
)

MSG_POINTS_DECREASED = (
    "Afsuski sizning ballaringiz <b>1 taga kamaydi</b>, do'stlaringizdan kimdir kanaldan chiqib ketganligi sababli.\n"
    "Agar ballaringiz <b>5 tasdan kam</b> bo'lsa, siz yopiq guruhdan chetlashtirilasiz.\n"
    "Qayta qo'shilish uchun ballaringizni <b>5 taga</b> yetkazing."
)

MSG_HACKNOW = (
    "🚀 <b>HackNow – Kelajak texnologiyalari markazi!</b>\n\n"
    "O'zbekistondagi eng birinchi <b>Kiberxavfsizlik</b> va <b>Sport dasturlash</b> bo'yicha ixtisoslashgan o'quv hamda trening platformasiga xush kelibsiz!\n\n"
    "🔥 <b>HackNow nima beradi?</b>\n"
    "✅ Dunyo miqyosidagi kiberxavfsizlik ko'nikmalari\n"
    "✅ Sport dasturlash (Algoritmlar) bo'yicha professional tayyorgarlik\n"
    "✅ Amaliy laboratoriyalar va real Keyslar\n"
    "✅ Xalqaro musobaqalarga tayyorlanish imkoniyati\n\n"
    "💻 <b>IT olamida o'z o'rningizni toping va professionalga aylaning!</b>\n\n"
    "🔗 <b>Kanalimiz:</b> @hacknow_uz\n"
    "🤝 <b>Hamkorlik va Savollar:</b> @jumanazar_xolmatov"
)

MSG_SUPPORT = (
    "👋 <b>Savolingiz bormi?</b>\n\n"
    "Bot yoki kurs yuzasidan savollaringiz bo'lsa, pastdagi tugmani bosing va bot yaratuvchisiga yozing. "
    "Sizning barcha yuborgan xabarlaringiz ko'rib chiqiladi."
)

LANGUAGE_NAME = "O'zbekcha"
