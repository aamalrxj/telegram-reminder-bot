from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import time
import threading
import os

# === Load from environment variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# === Constants ===
DELETE_AFTER_SECONDS = 300  # Self-destruct delay: 5 minutes
START_HOUR = 7
END_HOUR = 23

# === Reminder Times ===
water_times = [7, 9, 11, 13, 15, 17, 19, 21]
food_reminders = {
    (8, 30): "🍳 Good morning! Time for a healthy breakfast.",
    (13, 0): "🍱 Lunch time! Don't skip meals.",
    (20, 0): "🍽️ Dinner time! Eat well, sleep well."
}

bot = Bot(token=BOT_TOKEN)
scheduler = BackgroundScheduler()

# === Message Sender ===
def send_and_delete_message(text):
    current_hour = time.localtime().tm_hour
    if START_HOUR <= current_hour < END_HOUR:
        print(f"Sending: {text}")
        message = bot.send_message(chat_id=CHAT_ID, text=text)
        time.sleep(DELETE_AFTER_SECONDS)
        try:
            bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id)
        except Exception as e:
            print(f"Delete failed: {e}")

# === Schedule Food Reminders ===
for (hour, minute), message in food_reminders.items():
    scheduler.add_job(
        lambda msg=message: threading.Thread(target=send_and_delete_message, args=(msg,)).start(),
        trigger='cron',
        hour=hour,
        minute=minute
    )

# === Schedule Water Reminders ===
for hour in water_times:
    scheduler.add_job(
        lambda h=hour: threading.Thread(
            target=send_and_delete_message,
            args=("💧 Time to drink water!",)
        ).start(),
        trigger='cron',
        hour=hour,
        minute=0
    )

# === Start the Scheduler ===
scheduler.start()
print("✅ Bot is running 24x7!")

# === Keep script alive ===
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("⛔ Bot stopped.")
