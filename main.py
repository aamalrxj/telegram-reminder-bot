import os
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Should be set in Railway's environment

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID must be set in environment variables.")
CHAT_ID = int(CHAT_ID)

bot = Bot(token=BOT_TOKEN)
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

DELETE_AFTER_SECONDS = 5 * 60

food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 It's lunch time! Fuel your body.",
    (20, 0): "🍽️ Dinner time! Eat light and healthy."
}

water_hours = [7, 9, 11, 13, 15, 17, 19, 21]

# Function for reminders
async def send_and_delete(text):
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return  # Only send between 7 AM and 11 PM

    message = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"⚠️ Failed to delete message: {e}")

# Good Night message at 11 PM
async def send_good_night():
    text = "🌙 Good Night! Sleep well and recharge."
    message = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"⚠️ Failed to delete message: {e}")

# Good Morning message at 7 AM
async def send_good_morning():
    text = "☀️ Good Morning! Time to start your day fresh."
    message = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"⚠️ Failed to delete message: {e}")

def schedule_reminders():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=minute, args=[msg])
    for hour in water_hours:
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=0, args=["💧 Time to drink water!"])
    scheduler.add_job(send_good_night, "cron", hour=23, minute=0)
    scheduler.add_job(send_good_morning, "cron", hour=7, minute=0)
    # Add a one-time sample reminder at 12:25 AM IST (adjust as needed)
    scheduler.add_job(send_and_delete, "date", run_date="2025-07-10 00:25:00", args=["🔔 This is your custom 12:25 reminder!"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Hello!\n\n"
        "✅ This is your Health Reminder Bot.\n\n"
        "⏰ Schedule:\n"
        "• 💧 Water every 2 hours (7 AM to 9 PM)\n"
        "• 🍽️ Meals:\n"
        "  - Breakfast: 8:30 AM\n"
        "  - Lunch: 1:00 PM\n"
        "  - Dinner: 8:00 PM\n\n"
        "🕓 Bot only sends messages between 7 AM and 11 PM.\n"
        "🌙 You'll get a Good Night message at 11 PM and a Good Morning message at 7 AM."
    )
    sample_text = "✅ The bot is active! You'll start receiving reminders soon."
    sample_water = "💧 Time to drink water! (Sample Reminder)"

    await update.message.reply_text(welcome_text, parse_mode="HTML")
    await update.message.reply_text(sample_text, parse_mode="HTML")
    await update.message.reply_text(sample_water, parse_mode="HTML")

async def on_startup(app):
    scheduler.start()
    print("✅ Scheduler started.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    schedule_reminders()
    app.post_init = on_startup
    print("✅ Bot is running with reminders and /start command")
    app.run_polling()
