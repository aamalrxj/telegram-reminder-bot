import asyncio
import os
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

DELETE_AFTER_SECONDS = 300  # 5 minutes

# Reminder Times (IST)
water_hours = [7, 9, 11, 13, 15, 17, 19, 21]
food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 Lunch time! Don’t skip meals.",
    (20, 0): "🍽️ Dinner time! Eat well, sleep well."
}

async def send_and_delete(text):
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return  # Only run between 7 AM and 11 PM

    message = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete message: {e}")

def schedule_all():
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, 'cron', hour=hour, minute=minute, args=[msg])

    for hour in water_hours:
        scheduler.add_job(send_and_delete, 'cron', hour=hour, minute=0, args=["💧 Time to drink water!"])

async def main():
    schedule_all()
    scheduler.start()
    print("✅ Bot is running...")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
