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
if __name__ == "__main__":
    app.start()
    print("Nisha AI Bot is running... 🎉")
    idle()
    app.stop()
    user_text = message.text
    if message.chat.type in ["group", "supergroup"]:
        user_text = user_text.replace(f"@{client.me.username}", "").strip()
    
    try:
        response = model.generate_content(user_text)
        await message.reply_text(response.text.strip())
    except Exception as e:
        logger.error(f"AI Error: {e}")

# --- APP START ---
if __name__ == "__main__":
    app.start()
    print("Nisha AI Bot is now running... Ready to rock! 🎉")
    idle()
    app.stop()
        system_instruction=system_instruction
    )
else:
    model = None
    logger.warning("GEMINI_API_KEY is missing! AI features will not work.")

# Pyrogram Client Setup
app = Client("nisha_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Warm welcomes list
WELCOME_MESSAGES = [
    "Arey wah! 😍 ✨{name}✨ group mein aa gaya/gayi! Dil se swagat hai yaar aapka. Kaisi ho/kaise ho?",
    "Hello {name}! ❤️ Hum sab aapka hi intezar kar rahe the. Group mein aakar hamari rounak badha di aapne!",
    "Arey swagat karo bhai ka/behen ka! 🎉 {name} is now here. Nisha ki taraf se aapko ek bada sa hug! 🤗"
]

# Quick reply shortcuts (mood check)
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    welcome_text = (
        "Hey there! 😍 **Main hoon Nisha** — aapki pyari, intelligent AI saheli. ❤️\n\n"
        "Main aapke mood ke hisab se baatein kar sakti hoon, shayari suna sakti hoon, "
        "aur aapke groups ko manage bhi kar sakti hoon!\n\n"
        "💬 Mujhe kisi bhi group mein add karo aur Admin banao, fir dekho kamaal! "
        "Mujhse baat karne ke liye bas mujhe mention karo ya reply do."
    )
    await message.reply_text(welcome_text)

# --- GROUP MANAGEMENT FEATURES ---

# 1. New Member Welcome
@app.on_chat_member_updated(filters.group)
async def welcome_new_member(client: Client, event: ChatMemberUpdated):
    # Check if a new member joined
    if event.new_chat_member and not event.old_chat_member:
        user = event.new_chat_member.user
        name = user.first_name or "Dost"
        welcome_txt = random.choice(WELCOME_MESSAGES).format(name=name)
        await client.send_message(chat_id=event.chat.id, text=welcome_txt)

# 2. Ban Command (Admin only)
@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client: Client, message: Message):
    # Check if sender is admin
    sender = await message.chat.get_member(message.from_user.id)
    if sender.status not in ["administrator", "creator"]:
        await message.reply_text("Arey re! 🙈 Yeh command sirf mere Admins use kar sakte hain. Aap pehle admin bano!")
        return
        
    if not message.reply_to_message:
        await message.reply_text("Bhai, kisko ban karna hai? Uske message par reply karke `/ban` likho!")
        return

    target_user = message.reply_to_message.from_user
    try:
        await message.chat.ban_member(target_user.id)
        await message.reply_text(f"Chalo bye-bye! 👋 **{target_user.first_name}** ko group se nikaal diya gaya hai. Galti ki saza toh milegi hi!")
    except Exception as e:
        await message.reply_text(f"Opps! Mujhse unhe ban nahi kiya gaya. Shayad wo mujhse bade admin hain! 😅 Error: {e}")

# 3. Kick Command (Admin only)
@app.on_message(filters.command("kick") & filters.group)
async def kick_user(client: Client, message: Message):
    sender = await message.chat.get_member(message.from_user.id)
    if sender.status not in ["administrator", "creator"]:
        await message.reply_text("Sirf Admins hi kisi ko kick kar sakte hain! Aap chup-chap dosti badhao pehle. 😉")
        return

    if not message.reply_to_message:
        await message.reply_text("Kisko kick karna hai? Uske message par reply karke `/kick` likho!")
        return

    target_user = message.reply_to_message.from_user
    try:
        await message.chat.ban_member(target_user.id)
        await message.chat.unban_member(target_user.id) # Unban right after ban to make it a 'kick'
        await message.reply_text(f"Chalo beta, ghum ke aao! 🚪 **{target_user.first_name}** ko group se bahar fek diya gaya hai.")
    except Exception as e:
        await message.reply_text(f"Nahi ho pa raha yaar! Wo user mujhse zyada powerful lag raha hai. 🧐 Error: {e}")

# --- AI CHAT & BRAIN SYSTEM ---

@app.on_message((filters.group & (filters.mentioned | filters.reply)) | (filters.private & ~filters.command([])))
async def ai_chat_handler(client: Client, message: Message):
    global model
    
    # Agar model configured nahi hai
    if not model:
        await message.reply_text("Yaar, mera AI dimaag (API KEY) abhi connected nahi hai. Apne developer se bolo set kare! 🧠🔌")
        return

    # User ke text ko clean karna aur mention hatana
    user_text = message.text
    if not user_text:
        return # Agar text nahi hai (jaise sirf photo ya sticker)

    # Bot ki reply typing state dikhane ke liye
    await client.send_chat_action(chat_id=message.chat.id, action="typing")

    # Group mein mention clean karna
    if message.chat.type in ["group", "supergroup"]:
        user_text = user_text.replace(f"@{client.me.username}", "").strip()

    # User ka naam aur purane message ka context (agar reply hai toh)
    user_name = message.from_user.first_name or "Dost"
    prompt = f"User: {user_name} says: '{user_text}'"
    
    if message.reply_to_message:
        replied_to = message.reply_to_message.from_user.first_name if message.reply_to_message.from_user else "someone"
        prompt = f"Context: {user_name} is replying to {replied_to}'s message: '{message.reply_to_message.text}'.\nUser text: '{user_text}'"

    try:
        # AI se response generate karwana
        response = model.generate_content(prompt)
        ai_reply = response.text.strip()
        
        # Pyaara response bejhna
        await message.reply_text(ai_reply)
        
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        error_responses = [
            "Arey yaar, thoda dimaag ghum gaya mera. Ek baar fir se bolna? 🥺",
            "Oye hoye, lagta hai mere server mein kuch gudgudi ho rahi hai. 🙈 Thodi der mein baat karein?",
            "Nisha thodi thak gayi hai abhi. Par tension mat lo, aapki baat mere dil tak pahonch gayi! ❤️"
        ]
        await message.reply_text(random.choice(error_responses))

# --- APP START ---
# --- APP START ---
async def main():
    async with app:
        print("Nisha AI Bot starting up smoothly... Ready to rock! 🎉")
        await idle()

if __name__ == "__main__":
    from pyrogram import idle
    app.run(main())
