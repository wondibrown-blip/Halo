import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ==================== CONFIGURATION ====================
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
# =======================================================

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def get_reaction_list(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    target_msg = message.reply_to_message
    
    try:
        # Ambil ulang pesan terbaru agar sinkron dengan server Railway
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
    except Exception as e:
        await message.reply_text(f"Gagal sinkronisasi pesan: {str(e)}")
        return

    msg_reactions = updated_msg.reactions
    
    if not msg_reactions or not msg_reactions.reactions:
        await message.reply_text("Gak ada.")
        return

    user_list = []
    total_react_count = 0

    # Ekstrak data reaksi secara hybrid (kompatibel penuh dengan Railway cloud)
    for react in msg_reactions.reactions:
        total_react_count += react.count
        
        # Ambil peers pemberi reaksi
        peers = getattr(react, "added_reactions", None) or getattr(react, "recent_peers", None)
        
        if peers:
            for added in peers:
                user_obj = getattr(added, "user", added)
                user_id = getattr(user_obj, "id", None)
                
                if user_id:
                    try:
                        # Paksa ambil data profil terupdate langsung dari data ID
                        user_info = await client.get_users(user_id)
                        if user_info.username:
                            user_list.append(f"@{user_info.username}")
                    except Exception:
                        pass

    # Bersihkan duplikasi data usn
    user_list = list(set(user_list))

    if not user_list:
        await message.reply_text("Gagal, adminin dulu gw di gc")
        return

    usernames_string = " ".join(user_list)

    # Format text monospace (mono)
    caption_template = f"`{usernames_string} ({total_react_count})`"

    await client.send_message(
        chat_id=message.chat.id,
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v6 (Cloud Native) Aktif!")
app.run()
