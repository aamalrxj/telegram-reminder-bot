import os
import asyncio
import json
from datetime import datetime
import logging
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Logging setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS_FILE = "chat_ids.json"  # File to store chat IDs

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

# --- Chat ID storage ---
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

# --- Reminder sending functions ---
async def send_and_delete(text):
    chat_ids = get_all_chat_ids()
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return  # Only send between 7 AM and 11 PM
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

# --- Scheduler setup ---
def schedule_reminders():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=minute, args=[msg])
    for hour in water_hours:
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=0, args=["💧 Time to drink water!"])
    scheduler.add_job(send_good_night, "cron", hour=23, minute=0)
    scheduler.add_job(send_good_morning, "cron", hour=7, minute=0)

# --- Telegram command handlers ---
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
        "🌙 You'll get a Good Night message at 11 PM and a Good Morning message at 7 AM."
    )
    sample_text = "✅ The bot is active! You'll start receiving reminders soon."
    sample_water = "💧 Time to drink water!"
    await update.message.reply_text(welcome_text, parse_mode="HTML")
    await update.message.reply_text(sample_text, parse_mode="HTML")
    await update.message.reply_text(sample_water, parse_mode="HTML")

# --- Global error handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# --- Startup hook ---
async def on_startup(app):
    scheduler.start()
    logger.info("✅ Scheduler started.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)
    schedule_reminders()
    app.post_init = on_startup
    logger.info("✅ Bot is running with reminders and /start command")
    app.run_polling()
