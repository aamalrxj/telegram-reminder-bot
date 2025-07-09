from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7239493799:AAHCzIkR7Tb0BVivyyuTLLAT4sK4B2-MvUo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Your Chat ID is: {chat_id}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", start))

print("🤖 Bot is running. Open Telegram and type /start or /id to get chat ID.")
app.run_polling()
