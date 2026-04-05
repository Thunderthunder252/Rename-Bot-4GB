import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. PYTHON 3.14 COMPATIBILITY PATCH ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# --- 2. CONFIGURATION ---
API_ID = 37674103
API_HASH = "f9ecc621ed4865256f94f71a7dd6a1c8"
BOT_TOKEN = "8709295055:AAFDxRIDE03upWylyGjHasus9mv_ME0o5ik"
ADMIN = 5767651047 

bot = Client("my_rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary storage for user states (in-memory)
# Format: {user_id: {"file_id": "...", "thumb": "path/to/thumb.jpg"}}
user_data = {}

# --- 3. COMMAND HANDLERS ---

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        f"👋 **Hello {message.from_user.mention}!**\n\n"
        "I am a fast File Renamer Bot.\n\n"
        "📸 **Step 1:** Send a photo to set it as a thumbnail.\n"
        "📁 **Step 2:** Send the file you want to rename."
    )

@bot.on_message(filters.photo & filters.private)
async def thumb_handler(client, message):
    user_id = message.from_user.id
    path = f"thumb_{user_id}.jpg"
    
    msg = await message.reply_text("⏳ **Saving Thumbnail...**")
    await message.download(file_name=path)
    
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["thumb"] = path
    
    await msg.edit("✅ **Thumbnail Saved Successfully!**\nNow send the file you want to rename.")

@bot.on_message((filters.document | filters.video | filters.audio) & filters.private)
async def file_handler(client, message):
    user_id = message.from_user.id
    
    # Save the file reference
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]["file"] = message
    
    await message.reply_text(
        f"📝 **File Received!**\n\n"
        f"**Original Name:** `{message.document.file_name if message.document else 'Media'}`\n\n"
        "**Now send the NEW NAME for this file.**",
        reply_to_message_id=message.id
    )

@bot.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def rename_handler(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_data or "file" not in user_data[user_id]:
        return # User sent text without sending a file first

    new_name = message.text
    old_msg = user_data[user_id]["file"]
    thumb_path = user_data[user_id].get("thumb")

    status = await message.reply_text("📥 **Downloading file to server...**")
    
    # Download
    file_path = await client.download_media(old_msg)
    
    await status.edit("📤 **Uploading with new name...**")
    
    # Upload with new name and thumbnail
    await client.send_document(
        chat_id=message.chat.id,
        document=file_path,
        file_name=new_name,
        thumb=thumb_path,
        caption=f"✅ **Renamed:** `{new_name}`",
        progress=None # You can add a progress bar here later
    )
    
    await status.delete()
    os.remove(file_path) # Clean up disk space
    await message.reply_text("✨ **Done!** You can send another file.")

# --- 4. RUN BOT ---
if __name__ == "__main__":
    print("🚀 Bot is starting...")
    bot.run()
