from pyrogram import Client, filters

# 🔹 Telegram API Details
API_ID = 24043364  # Yahan apna API_ID daalein (my.telegram.org se milega)
API_HASH = "b27094593db92b4e76ad1be7fb4ec817"  # Apna API_HASH daalein
BOT_TOKEN = "7507479675:AAGnbw9YuMi6q9V0DUuWsK6DYuEKKJwju0U"  # Yahan BotFather se mila Token daalein
CHAT_ID = -1002165000013  # Yahan apne private channel ka ID daalein (negative me hoga)

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
    file_id = message.document.file_id if message.document else message.video.file_id if message.video else message.photo.file_id
    sent_message = bot.send_document(CHAT_ID, file_id, caption="📂 Stored File")
    
    file_link = f"https://t.me/{bot.me.username}?start=file_{sent_message.message_id}"  
    message.reply_text(f"📁 File uploaded successfully!\n🆔 Message ID: {sent_message.message_id}\n🔗 Download: {file_link}")

# 🔗 Get Direct Download Link
@bot.on_message(filters.command("getlink"))
def get_link(client, message):
    try:
        msg_id = int(message.command[1])
        file_message = bot.get_messages(CHAT_ID, msg_id)
        
        if not file_message.document and not file_message.video and not file_message.photo:
            message.reply_text("❌ This message does not contain a file.")
            return
        
        # ✅ Get Direct File Link from Telegram
        file_path = bot.get_file(file_message.document.file_id if file_message.document else file_message.video.file_id if file_message.video else file_message.photo.file_id).file_path
        direct_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        message.reply_text(f"📂 Direct Download Link:\n🔗 {direct_link}")
    
    except Exception as e:
        message.reply_text("❌ Error! Provide a valid message ID.")

# 🔥 Start Bot
bot.run()
