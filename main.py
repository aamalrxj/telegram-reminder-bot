import os
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))  # This should be set in Railway's environment

bot = Bot(token=BOT_TOKEN)
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

# Time to delete message after (5 minutes)
DELETE_AFTER_SECONDS = 5 * 60

# Food reminders (Indian time)
food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 It's lunch time! Fuel your body.",
    (20, 0): "🍽️ Dinner time! Eat light and healthy."
}

# Water reminders every 2 hours from 7 AM to 9 PM
water_hours = [7, 9, 11, 13, 15, 17, 19, 21]

# Function to send and delete messages
async def send_and_delete(text):
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return  # Skip outside active hours

    message = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"⚠️ Failed to delete message: {e}")

# Schedule all reminders
def schedule_reminders():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=minute, args=[msg])

    for hour in water_hours:
        scheduler.add_job(send_and_delete, "cron", hour=hour, minute=0, args=["💧 Time to drink water!"])

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = f"""
👋 Hello {update.effective_user.first_name}!

✅ This is your Health Reminder Bot.

⏰ Schedule:
• 💧 Water every 2 hours (7 AM to 9 PM)
• 🍽️ Meals:
  - Breakfast: 8:30 AM
  - Lunch: 1:00 PM
  - Dinner: 8:00 PM

🕓 Bot only sends messages between 7 AM and 11 PM.
💬 Your Chat ID: <code>{update.effective_chat.id}</code>
"""
    await update.message.reply_text(welcome_text, parse_mode="HTML")

# /id command
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your Chat ID is: <code>{update.effective_chat.id}</code>", parse_mode="HTML")

# Telegram bot setup
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))

    schedule_reminders()
    scheduler.start()

    print("✅ Bot is running with reminders and /start command")
    app.run_polling()
