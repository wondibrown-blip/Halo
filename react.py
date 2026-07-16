import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.errors import FloodWait, RPCError

# ==================== KREDENSIAL AMAN ====================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Menggunakan setelan koneksi mentah yang paling agresif agar update langsung dipaksa masuk
app = Client(
    "my_userbot11", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    in_memory=True,
    workers=4
)

async def process_reaction_list(client: Client, message: Message):
    target_msg = message.reply_to_message
    user_list = []
    total_react_count = 0

    try:
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
        if updated_msg and updated_msg.reactions:
            if hasattr(updated_msg.reactions, "reactions") and updated_msg.reactions.reactions:
                for r in updated_msg.reactions.reactions:
                    total_react_count += getattr(r, "count", 0)
    except Exception as e:
        print(f"[Log Warning] Gagal hitung reaksi: {e}")

    try:
        chat_peer = await client.resolve_peer(message.chat.id)
        raw_reply = await client.invoke(
            functions.messages.GetMessageReactionsList(
                peer=chat_peer,
                id=target_msg.id,
                limit=100
            )
        )
        if raw_reply and hasattr(raw_reply, "users"):
            for raw_user in raw_reply.users:
                username = getattr(raw_user, "username", None)
                if username:
                    user_list.append(f"@{username}")
    except Exception as e:
        print(f"[Log Warning] Gagal ambil user: {e}")

    user_list = list(set(user_list))
    if total_react_count == 0 and len(user_list) > 0:
        total_react_count = len(user_list)

    usernames_string = "No-Users-Detected" if not user_list else " ".join(user_list)
    return usernames_string, total_react_count

# ==================== MONITORING GLOBAL (DETEKSI SINYAL) ====================

# Paling Penting: Jika filter ini menangkap ketikanmu, log Railway AKAN mencetaknya
@app.on_message(filters.me)
async def global_logger(client: Client, message: Message):
    print(f" -> [SINYAL MASUK DETEKSI] Teks: {message.text} | Tipe Chat: {message.chat.type}")
    
    # Trigger manual tanpa filter grup rumit untuk tes awal
    if message.text == "/done" or message.text == ".done":
        if not message.reply_to_message:
            await message.reply_text("Silahkan reply ke pesan target!")
            return
        usernames_string, total_react_count = await process_reaction_list(client, message)
        await message.reply_text(text=f"`{usernames_string} ({total_react_count})`")

    elif message.text == "/doni" or message.text == ".doni":
        if not message.reply_to_message:
            await message.reply_text("Silahkan reply ke pesan target!")
            return
        usernames_string, total_react_count = await process_reaction_list(client, message)
        caption_template = (
            "``` \n"
            "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
            "𝗦𝗬𝗡𝗖 𝗣𝗔𝗖𝗧: Mutual terms enforced.\n"
            f"Alignment forms beyond consent, presence settles refuses 2 shift. 𝘕𝘰 𝘧𝘳𝘢𝘤𝘵𝘶𝘳𝘦 𝘰𝘯𝘤𝘦 𝘪𝘵 𝘴𝘦𝘵𝘴: {usernames_string} ({total_react_count}) bound. Balanced force, no reversal (+KT9.) https://t.me/HOTROVERs/4.\n"
            "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ```"
        )
        await message.reply_text(text=caption_template)

# ==================== CORE SYSTEM RUNNER ====================
async def main():
    print("🚀 Mencoba menyambungkan ke Telegram secara langsung...")
    try:
        await app.start()
        print("✅ KONEKSI BERHASIL! Userbot terhubung penuh dengan Telegram.")
        print("👀 Menunggu pesan masuk... Silahkan ketik /done atau /doni di Telegram.")
        await idle()
    except Exception as e:
        print(f"❌ KONEKSI GAGAL SAAT STARTUP: {str(e)}")
    finally:
        if app.is_connected:
            await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
