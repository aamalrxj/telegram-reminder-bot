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

# Food reminders (Indian time)
food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 It's lunch time! Fuel your body right.",
    (20, 0): "🍽️ Dinner time! Wrap up your day with a light meal."
}

# Water reminders at 2-hour intervals from 7 AM to 9 PM
water_hours = [7, 9, 11, 13, 15, 17, 19, 21]

async def send_and_delete(text):
    now = datetime.now().time()
    if now.hour < 7 or now.hour >= 23:
        return  # Don't run outside 7 AM – 11 PM
    message = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(DELETE_AFTER_SECONDS)
    try:
        await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

def schedule_reminders():
    # Schedule food
    for (hour, minute), msg in food_reminders.items():
        scheduler.add_job(send_and_delete, 'cron', hour=hour, minute=minute, args=[msg])

    # Schedule water
    for hour in water_hours:
        scheduler.add_job(send_and_delete, 'cron', hour=hour, minute=0, args=["💧 Time to drink water!"])

async def main():
    schedule_reminders()
    scheduler.start()
    print("✅ Reminder bot is running...")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
