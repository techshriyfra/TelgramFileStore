from pyrogram import Client, filters
import os

# 🔹 Telegram API Details
API_ID = 1234567  # Replace with your API ID
API_HASH = "your_api_hash"  # Replace with your API HASH
BOT_TOKEN = "your_bot_token"  # Replace with your BotFather Token
CHANNEL_USERNAME = "@your_channel_username"  # Use your channel username (or ID)

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

# ✅ Resolving Chat ID (Fixes Peer ID Error)
def get_channel_id():
    try:
        chat = bot.get_chat(CHANNEL_USERNAME)
        return chat.id
    except Exception as e:
        print(f"Error Resolving Channel ID: {e}")
        return None

# 📤 File Upload Handler
@bot.on_message(filters.document | filters.video | filters.photo)
def upload_file(client, message):
    chat_id = get_channel_id()
    if not chat_id:
        message.reply_text("❌ Error! Cannot resolve channel ID. Ensure the bot is an admin in your channel.")
        return

    file_id = message.document.file_id if message.document else message.video.file_id if message.video else message.photo.file_id

    try:
        sent_message = bot.send_document(chat_id, file_id, caption="📂 Stored File")
        file_link = f"https://t.me/{bot.me.username}?start=file_{sent_message.message_id}"
        message.reply_text(f"📁 File uploaded successfully!\n🆔 Message ID: {sent_message.message_id}\n🔗 Download: {file_link}")

    except Exception as e:
        message.reply_text(f"❌ Error Uploading File: {e}")

# 📥 Retrieve Files
@bot.on_message(filters.command("files"))
def get_files(client, message):
    chat_id = get_channel_id()
    if not chat_id:
        message.reply_text("❌ Error! Cannot resolve channel ID.")
        return

    try:
        updates = client.get_chat_history(chat_id, limit=5)  # Last 5 Files
        response = "📂 Last Stored Files:\n\n"
        for msg in updates:
            response += f"📌 File ID: {msg.message_id}\n🔗 Download: https://t.me/{bot.me.username}?start=file_{msg.message_id}\n"
        message.reply_text(response)

    except Exception as e:
        message.reply_text(f"❌ Error Fetching Files: {e}")

# 🔗 Get Direct Download Link
@bot.on_message(filters.command("getlink"))
def get_link(client, message):
    chat_id = get_channel_id()
    if not chat_id:
        message.reply_text("❌ Error! Cannot resolve channel ID.")
        return

    try:
        msg_id = int(message.command[1])
        file_message = bot.get_messages(chat_id, msg_id)

        if not file_message.document and not file_message.video and not file_message.photo:
            message.reply_text("❌ This message does not contain a file.")
            return
        
        # ✅ Get Direct File Link from Telegram
        file_path = bot.get_file(file_message.document.file_id if file_message.document else file_message.video.file_id if file_message.video else file_message.photo.file_id).file_path
        direct_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        message.reply_text(f"📂 Direct Download Link:\n🔗 {direct_link}")

    except Exception as e:
        message.reply_text(f"❌ Error Fetching Link: {e}")

# 🗑 Delete File Handler
@bot.on_message(filters.command("delete"))
def delete_file(client, message):
    chat_id = get_channel_id()
    if not chat_id:
        message.reply_text("❌ Error! Cannot resolve channel ID.")
        return

    try:
        msg_id = int(message.command[1])  # Message ID Input
        client.delete_messages(chat_id, msg_id)
        message.reply_text(f"✅ File (Message ID: {msg_id}) deleted successfully!")
    except Exception as e:
        message.reply_text(f"❌ Error! Invalid Message ID or No Permission: {e}")

# ✅ Fix Session Issues (Deletes Old Session File)
if os.path.exists("storage_bot.session"):
    os.remove("storage_bot.session")

# 🔥 Start Bot
bot.run()
