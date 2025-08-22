import logging
import os
import psycopg2
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB Connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE,
    points INT DEFAULT 0
);
""")
conn.commit()

# Bot setup
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IMGFLIP_USER = os.getenv("IMGFLIP_USER")
IMGFLIP_PASS = os.getenv("IMGFLIP_PASS")
app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING;", (user_id,))
    conn.commit()
    await update.message.reply_text("Welcome to the Fun Bot! Use /daily, /refer, /memes")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cur.execute("UPDATE users SET points = points + 10 WHERE user_id = %s;", (user_id,))
    conn.commit()
    await update.message.reply_text("You claimed 10 daily points!")

async def memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get("https://api.imgflip.com/get_memes").json()
    memes = response["data"]["memes"][:5]
    reply = "\n".join([m["url"] for m in memes])
    await update.message.reply_text("Here are some meme templates:\n" + reply)

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", daily))
app.add_handler(CommandHandler("memes", memes))

if __name__ == "__main__":
    logger.info("Bot started...")
    app.run_polling()
