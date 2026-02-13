import pandas as pd
import requests
from io import StringIO
import datetime
import random
import os
import asyncio

# ===================== Telegram import =====================
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===================== Sozlamalar =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_ID = int(os.environ.get("GROUP_ID"))

CSV_URL = "https://docs.google.com/spreadsheets/d/14Y5SwUSgO00VTgLYAZR73XoQGg3V-p8M/export?format=csv&gid=1184571774"

MOTIVATION_MESSAGES = [
    "🚆 Bugun yo‘llar tinch, vagonlar tartibli, siz esa fidoyi xodim sifatida o‘z ishini mukammal bajarishda davom etyapsiz! 💪",
    "⚡️ Har bir temir yo‘l uzelining harakati sizning mehnatingiz bilan bog‘liq. Bugun yangi marralarga intiling! 🚄",
    "🌟 Sizning mas’uliyatli va e’tiborli mehnatingiz tufayli yurtimiz taraqqiyotga intilmoqda. Bugun ham shunday davom eting!",
    "🚧 Vagonlar, relslar, stansiyalar… hammasi sizning mehnatingiz bilan tinch va xavfsiz ishlaydi. Rahmat sizga!",
    "🎯 Har bir to‘xtovsiz harakat, har bir belgilangan vaqtni bajarish – bu sizning fidoyiligingiz! Bugun yangi marralarni zabt eting!",
    "💡 Yangi loyihalar, yangi imkoniyatlar – temir yo‘l sohasi doimo yangilanadi. Siz ham yangilikka tayyormisiz?",
    "🛤 Bugun hech kim tug‘ilgan kunini nishonlamasa ham, jamoamiz faol va yo‘llar xavfsiz! Sizning mehnatingiz buning garovi!",
    "🌈 Har bir kun – yangi imkoniyat. Bugun biror yangilikni o‘zingiz yaratib, hamkasblaringizni ilhomlantiring!",
    "🏅 Sizning mas’uliyatli mehnatingiz temir yo‘l infratuzilmasini mukammal ishlashini ta’minlaydi. Bugun ham shunday davom eting!",
    "🚀 Fidoyi xodimlar yo‘llarimizni xavfsiz qiladi va taraqqiyotga hissa qo‘shadi. Bugun yangi marralarga intiling!"
]

thank_count = 0

# ===================== Tug‘ilgan kunlarni tekshirish =====================
async def check_birthdays():
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = [c.strip().lower() for c in df.columns]

        today = datetime.datetime.now().strftime("%d.%m")
        df['tugulgan_kun'] = df['tugulgan_kun'].astype(str).str[:5]
        today_birthdays = df[df['tugulgan_kun'] == today]

        if not today_birthdays.empty:
            names = [f"{row['ism']} ({row['bolim']})" for _, row in today_birthdays.iterrows()]
            if len(names) == 1:
                message = f"Hurmatli {names[0]} temir yo‘l sohasining fidoyi xodimi.\n\n" \
                          "Sizni tug‘ilgan kuningiz bilan chin qalbimizdan tabriklaymiz. " \
                          "Mas’uliyatli va sharafli mehnatingiz bilan yurtimiz taraqqiyotiga munosib hissa qo‘shib kelmoqdasiz. " \
                          "Sizga mustahkam sog‘liq, oilaviy baxt, ishlaringizda doimiy muvaffaqiyat va xavfsiz yo‘llar tilaymiz! " \
                          "Yana bir bor tug'ulgan kunigiz bilan tabriklaymiz.\n\n" \
                          "Hurmat bilan \"Qo'qon elektr ta'minoti\" masofasi filiali!"
            else:
                message = f"Hurmatli {', '.join(names)} temir yo‘l sohasining fidoyi xodimlari.\n\n" \
                          "Sizlarni tug‘ilgan kuningiz bilan chin qalbimizdan tabriklaymiz. " \
                          "Mas’uliyatli va sharafli mehnatingiz bilan yurtimiz taraqqiyotiga munosib hissa qo‘shib kelmoqdasiz. " \
                          "Sizlarga mustahkam sog‘liq, oilaviy baxt, ishlaringizda doimiy muvaffaqiyat va xavfsiz yo‘llar tilaymiz! " \
                          "Yana bir bor tug'ulgan kunigiz bilan tabriklaymiz.\n\n" \
                          "Hurmat bilan \"Qo'qon elektr ta'minoti\" masofasi filiali!"
        else:
            message = f"Afsus! Bugun tug‘ilgan kun yo‘q! {random.choice(MOTIVATION_MESSAGES)}"

        await bot.send_message(chat_id=GROUP_ID, text=message)
    except Exception as e:
        print("Xato:", e)

# ===================== “Rahmat” javobi =====================
  async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global thank_count
    text = update.message.text.lower()
    if text in ["rahmat", "rahmad", "рахмат", "рахмад"]:
        thank_count += 1
        if thank_count == 1:
            await update.message.reply_text("🤗 Sizga doimo muvaffaqiyat tilaymiz!")
        else:
            await update.message.reply_text("😅 qaytarormen maazgii")

# ===================== BOTNI RUN QILISH =====================
async def main():
    global bot
    from telegram.ext import ApplicationBuilder
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    global bot
    bot = app.bot

    # “Rahmat” xabarlarini kuzatish
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Har kuni tug‘ilganlarni tekshirish (09:00)
    import schedule, time, threading
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(30)
    import asyncio
    schedule.every().day.at("09:00").do(lambda: asyncio.run(check_birthdays()))
    threading.Thread(target=run_schedule, daemon=True).start()

    print("Bot ishga tushdi...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
