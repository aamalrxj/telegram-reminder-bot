import os
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
bot = Bot(token=BOT_TOKEN)

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

# Auto-delete after 5 minutes
DELETE_AFTER_SECONDS = 5 * 60

# Food reminders
food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 It's lunch time! Fuel your body.",
    (20, 0): "🍽️ Dinner time! Eat light and healthy."
}

# Water reminders
water_hours = [7, 9, 11, 13, 15, 17, 19, 21]

# Send + auto-delete messages
async def send_and_delete(text):
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return

    msg = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=msg.message_id)
    except:
        pass

# Add all reminders
def schedule_reminders():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=minute, args=[msg])
    for hour in water_hours:
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=0, args=["💧 Time to drink water!"])

# Bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"""👋 Hello {update.effective_user.first_name}!
✅ Health Reminder Bot Started.

💧 Water every 2 hours (7 AM to 9 PM)
🍱 Food at:
- 8:30 AM (Breakfast)
- 1:00 PM (Lunch)
- 8:00 PM (Dinner)

🕒 Active only between 7 AM – 11 PM
🆔 Chat ID: <code>{update.effective_chat.id}</code>
""",
        parse_mode="HTML"
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your Chat ID: <code>{update.effective_chat.id}</code>", parse_mode="HTML")

# Main app
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))

    schedule_reminders()
    scheduler.start()

    print("✅ Bot is running with reminders and /start command")
    await app.run_polling()

# Use current event loop if already running (Railway-safe)
try:
    asyncio.get_running_loop().create_task(main())
except RuntimeError:
    asyncio.run(main())
