import os
import logging
import random
from pyrogram import Client, filters, idle
from pyrogram.types import Message, ChatMemberUpdated
import google.generativeai as genai

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token_here")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Gemini AI Client Setup
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    system_instruction = (
        "You are Nisha, a super-intelligent, caring, emotional, and fun-loving AI Telegram Bot. "
        "You speak in friendly Hinglish mixed with English, like a close friend."
    )
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
else:
    model = None
    logger.warning("GEMINI_API_KEY is missing!")

# Pyrogram Client Setup
app = Client("nisha_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- HANDLERS ---
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text("Hey! Main hoon Nisha. ❤️")

@app.on_message((filters.group & (filters.mentioned | filters.reply)) | (filters.private & ~filters.command([])))
async def ai_chat_handler(client: Client, message: Message):
    if not model:
        return
    await client.send_chat_action(message.chat.id, "typing")
    try:
        response = model.generate_content(message.text or "Hello")
        await message.reply_text(response.text.strip())
    except Exception as e:
        logger.error(f"AI Error: {e}")

# --- APP START ---
async def main():
    async with app:
        print("Nisha AI Bot starting up smoothly... Ready to rock! 🎉")
        await idle()

# --- APP START ---
if __name__ == "__main__":
    # Bot ko start karne ka sahi tareeka
    app.run()
