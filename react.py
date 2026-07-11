import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, MessageReactions

# ==================== CONFIGURATION ====================
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
# =======================================================

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH)

# Tempat penyimpanan catatan reaksi sementara di memori server
# Format: { message_id: { "total": 0, "users": set() } }
reaction_tracker = {}

# 1. EVENT LISTENER: Pantau setiap kali ada yang menambah/mengubah reaksi di grup
@app.on_raw_update()
async def track_live_reactions(client: Client, update, users, chats):
    # Deteksi jika ada update reaksi masuk (UpdateBotMessageReactions atau UpdateMessageReactions)
    class_name = update.__class__.__name__
    if "UpdateMessageReactions" in class_name or "UpdateBotMessageReactions" in class_name:
        msg_id = getattr(update, "msg_id", None) or getattr(update, "id", None)
        if not msg_id:
            return
            
        # Inisialisasi tempat catatan jika belum ada
        if msg_id not in reaction_tracker:
            reaction_tracker[msg_id] = {"total": 0, "users": set()}
            
        # Ambil data dari objek reaksi mentah
        if hasattr(update, "reactions") and hasattr(update.reactions, "results"):
            total_count = sum(r.count for r in update.reactions.results)
            reaction_tracker[msg_id]["total"] = total_count
            
        # Intip user mentah yang dikirim oleh Telegram saat mendeteksi event klik reaksi
        for u_id, u_obj in users.items():
            if hasattr(u_obj, "username") and u_obj.username:
                reaction_list_raw = f"@{u_obj.username}"
                reaction_tracker[msg_id]["users"].add(reaction_list_raw)

# 2. COMMAND HANDLER: Jalankan perintah /done seperti biasa
@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def get_reaction_list(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    target_msg = message.reply_to_message
    msg_id = target_msg.id
    
    user_list = []
    total_react_count = 0

    # Cek apakah pesan yang di-reply ada di dalam catatan live tracker kita
    if msg_id in reaction_tracker:
        user_list = list(reaction_tracker[msg_id]["users"])
        total_react_count = reaction_tracker[msg_id]["total"]
    
    # BACKUP SYSTEM: Jika tracker kosong, coba intip via update message standar
    if not user_list:
        try:
            updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=msg_id)
            if updated_msg.reactions and updated_msg.reactions.reactions:
                for r in updated_msg.reactions.reactions:
                    total_react_count += r.count
                
                peers = getattr(updated_msg.reactions.reactions[0], "added_reactions", None) or \
                        getattr(updated_msg.reactions.reactions[0], "recent_peers", None)
                if peers:
                    for added in peers:
                        user_obj = getattr(added, "user", added)
                        if getattr(user_obj, "username", None):
                            user_list.append(f"@{user_obj.username}")
        except Exception:
            pass

    # Bersihkan duplikasi data usn
    user_list = list(set(user_list))

    # JALAN KELUAR JIKA TETAP KOSONG: Agar format teks monospace kamu tidak hancur/gagal kirim
    if not user_list:
        usernames_string = "Gak ada."
    else:
        usernames_string = " ".join(user_list)

    # Format text monospace (mono) sesuai request kamu kemarin
    caption_template = f"`{usernames_string} ({total_react_count})`"

    await client.send_message(
        chat_id=message.chat.id,
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v7 (Anti-Privacy Live Tracker) Aktif di Railway!")
app.run()
