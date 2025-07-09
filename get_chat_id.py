from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7239493799:AAHCzIkR7Tb0BVivyyuTLLAT4sK4B2-MvUo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    welcome_message = f"""
👋 Hello {update.effective_user.first_name}!

✅ This is your personal Health Reminder Bot.

🔔 It will automatically:
- Remind you to 💧 drink water every 2 hours (from 7 AM to 9 PM)
- Remind you to 🍽️ eat food at:
    • 8:30 AM (Breakfast)
    • 1:00 PM (Lunch)
    • 8:00 PM (Dinner)

🕓 All reminders are active between 7 AM and 11 PM.
🧼 Each reminder will delete itself after 5 minutes.

"""

    await update.message.reply_text(welcome_message, parse_mode="HTML")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", start))  # Optional: both /id and /start show the same

print("🤖 Bot is running. Send /start in Telegram to test.")
app.run_polling()
