import os
import asyncio
import json
from datetime import datetime, time as dt_time, timedelta
import logging
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS_FILE = "chat_ids.json"
CUSTOM_REMINDERS_FILE = "custom_reminders.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment variables.")

bot = Bot(token=BOT_TOKEN)
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
DELETE_AFTER_SECONDS = 5 * 60

food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 It's lunch time! Fuel your body.",
    (20, 0): "🍽️ Dinner time! Eat light and healthy."
}
water_hours = [7, 9, 11, 13, 15, 17, 19, 21]

def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        return set()
    with open(CHAT_IDS_FILE, "r") as f:
        return set(json.load(f))

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w") as f:
        json.dump(list(chat_ids), f)

def add_chat_id(chat_id):
    chat_ids = load_chat_ids()
    chat_ids.add(chat_id)
    save_chat_ids(chat_ids)

def get_all_chat_ids():
    return load_chat_ids()

def load_custom_reminders():
    if not os.path.exists(CUSTOM_REMINDERS_FILE):
        return []
    with open(CUSTOM_REMINDERS_FILE, "r") as f:
        return json.load(f)

def save_custom_reminders(reminders):
    with open(CUSTOM_REMINDERS_FILE, "w") as f:
        json.dump(reminders, f)

async def send_and_delete(text):
    chat_ids = get_all_chat_ids()
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return
    for chat_id in chat_ids:
        try:
            message = await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
            await asyncio.sleep(DELETE_AFTER_SECONDS)
            await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        except Exception as e:
            logger.error(f"Failed to send/delete message to {chat_id}: {e}")

async def send_good_night():
    await send_and_delete("🌙 Good Night! Sleep well and recharge.")

async def send_good_morning():
    await send_and_delete("☀️ Good Morning! Time to start your day fresh.")

def schedule_reminders():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=minute, args=[msg])
    for hour in water_hours:
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=0, args=["💧 Time to drink water!"])
    scheduler.add_job(send_good_night, "cron", hour=23, minute=0)
    scheduler.add_job(send_good_morning, "cron", hour=7, minute=0)
    # Schedule existing custom reminders
    for reminder in load_custom_reminders():
        schedule_custom_reminder(reminder["time"], reminder["message"])

def schedule_custom_reminder(reminder_time, message):
    now = datetime.now()
    hour, minute = map(int, reminder_time.split(":"))
    run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if run_time < now:
        run_time += timedelta(days=1)
    scheduler.add_job(send_and_delete, "date", run_date=run_time, args=[f"🔔 {message}"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_chat_id(chat_id)
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
        "🌙 You'll get a Good Night message at 11 PM and a Good Morning message at 7 AM.\n\n"
        "➕ To add a custom reminder for all users, use:\n"
        "<code>/addreminder HH:MM Your message</code>\n"
        "Example: <code>/addreminder 15:30 Meeting with team</code>"
    )
    sample_text = "✅ The bot is active! You'll start receiving reminders soon."
    sample_water = "💧 Time to drink water!"
    await update.message.reply_text(welcome_text, parse_mode="HTML")
    await update.message.reply_text(sample_text, parse_mode="HTML")
    await update.message.reply_text(sample_water, parse_mode="HTML")

async def addreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_chat_id(chat_id)
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addreminder HH:MM Your message\nExample: /addreminder 15:30 Meeting with team")
        return
    reminder_time = context.args[0]
    message = " ".join(context.args[1:])
    # Validate time
    try:
        hour, minute = map(int, reminder_time.split(":"))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except Exception:
        await update.message.reply_text("Invalid time format. Use HH:MM in 24-hour format.")
        return
    # Store and schedule
    reminders = load_custom_reminders()
    reminders.append({"time": reminder_time, "message": message})
    save_custom_reminders(reminders)
    schedule_custom_reminder(reminder_time, message)
    await update.message.reply_text(f"✅ Reminder set for {reminder_time}: {message}\nAll users will receive this reminder.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

async def on_startup(app):
    scheduler.start()
    logger.info("✅ Scheduler started.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addreminder", addreminder))
    app.add_error_handler(error_handler)
    schedule_reminders()
    app.post_init = on_startup
    logger.info("✅ Bot is running with reminders and /start command")
    app.run_polling()
