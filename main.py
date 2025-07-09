import asyncio
import os
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
DELETE_AFTER_SECONDS = 300  # 5 minutes

# Food reminders
food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 It's lunch time! Fuel your body right.",
    (20, 0): "🍽️ Dinner time! Wrap up your day with a light meal."
}

# Water reminders every 2 hours from 7 AM to 9 PM
water_hours = [7, 9, 11, 13, 15, 17, 19, 21]


async def send_and_delete(text):
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return  # Only active between 7 AM and 11 PM
    msg = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=msg.message_id)
    except Exception as e:
        print(f"Failed to delete message: {e}")


def schedule_reminders():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=minute, args=[msg])
    for hour in water_hours:
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=0, args=["💧 Time to drink water!"])


# ------------------- COMMAND HANDLERS -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = f"""
👋 Hello {update.effective_user.first_name}!

✅ This is your personal Health Reminder Bot.

🔔 It will automatically:
• Remind you to 💧 drink water every 2 hours (7 AM to 9 PM)
• Remind you to 🍽️ eat food at:
  - 8:30 AM (Breakfast)
  - 1:00 PM (Lunch)
  - 8:00 PM (Dinner)

🕓 Reminders run only between 7 AM and 11 PM.
💬 Your Chat ID: <code>{update.effective_chat.id}</code>
"""
    await update.message.reply_text(welcome, parse_mode=ParseMode.HTML)


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your chat ID is: <code>{update.effective_chat.id}</code>", parse_mode="HTML")


# ------------------- MAIN -------------------

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Schedule reminders
    schedule_reminders()
    scheduler.start()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))

    print("✅ Bot is running with /start and scheduled reminders")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Schedule reminders
    schedule_reminders()
    scheduler.start()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))

    print("✅ Bot is running with /start and scheduled reminders")
    app.run_polling()  # ✅ No need to wrap in asyncio.run()