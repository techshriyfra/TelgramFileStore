from pyrogram import Client, filters
import os

# 🔹 Telegram API Details
API_ID = 240433647  # Ensure this is an integer, not a string
API_HASH = "b27094593db92b4e76ad1be7fb4ec817"  # Ensure no spaces or typos
BOT_TOKEN = "7507479675:AAGnbw9YuMi6q9V0DUuWsK6DYuEKKJwju0U"  # Must be correct
CHANNEL_ID = -1002165000013  # Use numeric channel ID (ensure it's correct)

# 🔹 Dictionary to Store File IDs (Temporary)
file_store = {}  # {message_id: file_id}

# 🔹 Bot Client Initialize
bot = Client("storage_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 📌 Start Command
@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("🔹 Welcome to Telegram Cloud Storage Bot!\n\n"
                       "📤 Send any file to store it.\n"
                       "📥 Use /files to get stored files.\n"
                       "🔗 Use /getlink <message_id> to get a direct download link.\n"
                       "🗑 Use /delete <message_id> to remove a file.")

# 📤 File Upload Handler
@bot.on_message(filters.document | filters.video | filters.photo)
def upload_file(client, message):
    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.photo:
        file_id = message.photo.file_id

    try:
        # ✅ Using `client.send_document` instead of `bot.send_document`
        sent_message = client.send_document(CHANNEL_ID, file_id, caption="📂 Stored File")

        # ✅ Store the file_id linked to message_id
        file_store[sent_message.id] = file_id

        file_link = f"https://t.me/{bot.me.username}?start=file_{sent_message.id}"
        message.reply_text(f"📁 File uploaded successfully!\n🆔 Message ID: {sent_message.id}\n🔗 Download: {file_link}")

    except Exception as e:
        message.reply_text(f"❌ Error Uploading File: {e}")

# 📥 Retrieve Files (Fix: Bots cannot use get_chat_history in private channels)
@bot.on_message(filters.command("files"))
def get_files(client, message):
    if not file_store:
        message.reply_text("📂 No files stored yet!")
        return

    response = "📂 Stored Files:\n\n"
    for msg_id, _ in list(file_store.items())[-5:]:  # Get last 5 files
        response += f"📌 Message ID: {msg_id}\n🔗 Download: https://t.me/{bot.me.username}?start=file_{msg_id}\n"

    message.reply_text(response)

# 🔗 Get Direct Download Link
@bot.on_message(filters.command("getlink"))
def get_link(client, message):
    try:
        if len(message.command) < 2:
            message.reply_text("❌ Usage: /getlink <message_id>")
            return

        msg_id = int(message.command[1])

        if msg_id not in file_store:
            message.reply_text("❌ Error! Invalid Message ID or file not found.")
            return

        file_id = file_store[msg_id]

        # ✅ Get Direct File Link from Telegram
        file_path = client.get_file(file_id).file_path
        direct_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        message.reply_text(f"📂 Direct Download Link:\n🔗 {direct_link}")

    except Exception as e:
        message.reply_text(f"❌ Error Fetching Link: {e}")

# 🗑 Delete File Handler
@bot.on_message(filters.command("delete"))
def delete_file(client, message):
    try:
        if len(message.command) < 2:
            message.reply_text("❌ Usage: /delete <message_id>")
            return

        msg_id = int(message.command[1])

        if msg_id not in file_store:
            message.reply_text("❌ Error! Invalid Message ID or file not found.")
            return

        client.delete_messages(CHANNEL_ID, msg_id)
        del file_store[msg_id]  # Remove from the stored list
        message.reply_text(f"✅ File (Message ID: {msg_id}) deleted successfully!")

    except Exception as e:
        message.reply_text(f"❌ Error! Invalid Message ID or No Permission: {e}")

# ✅ Fix Session Issues (Deletes Old Session File)
if os.path.exists("storage_bot.session"):
    os.remove("storage_bot.session")

# 🔥 Start Bot
bot.run()
