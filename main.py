from pyrogram import Client, filters
import os

# 🔹 Telegram API Details
API_ID = 1234567  # Yahan apna API_ID daalein (my.telegram.org se milega)
API_HASH = "your_api_hash"  # Apna API_HASH daalein
BOT_TOKEN = "your_bot_token"  # Yahan BotFather se mila Token daalein
CHAT_ID = -1001234567890  # Yahan apne private channel ka ID daalein (negative me hoga)

# 🔹 Bot Client Initialize
bot = Client("storage_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 📌 Start Command
@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("🔹 Welcome to Telegram Cloud Storage Bot!\n\n"
                       "📤 Send any file to store it.\n"
                       "📥 Use /files to get stored files.\n"
                       "🗑 Use /delete <message_id> to remove a file.")

# 📤 File Upload Handler
@bot.on_message(filters.document | filters.video | filters.photo)
def upload_file(client, message):
    file_id = message.document.file_id if message.document else message.video.file_id if message.video else message.photo.file_id
    caption = f"✅ File Stored!\n📂 File ID: {file_id}"
    
    # File Ko Private Channel Me Store Karna
    sent_message = bot.send_document(CHAT_ID, file_id, caption="📂 Stored File")
    
    # User Ko Response
    message.reply_text(f"📁 File uploaded successfully!\n🆔 Message ID: {sent_message.message_id}")

# 📥 Retrieve Files
@bot.on_message(filters.command("files"))
def get_files(client, message):
    updates = client.get_chat_history(CHAT_ID, limit=5)  # Last 5 Files
    response = "📂 Last Stored Files:\n\n"
    
    for msg in updates:
        response += f"📌 File ID: {msg.message_id}\n"
    
    message.reply_text(response)

# 🗑 Delete File Handler
@bot.on_message(filters.command("delete"))
def delete_file(client, message):
    try:
        msg_id = int(message.command[1])  # Message ID Input
        client.delete_messages(CHAT_ID, msg_id)
        message.reply_text(f"✅ File (Message ID: {msg_id}) deleted successfully!")
    except Exception as e:
        message.reply_text("❌ Error! Invalid Message ID or No Permission.")

# 🔥 Start Bot
bot.run()
