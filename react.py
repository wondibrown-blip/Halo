import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions

#configuration 
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def get_reaction_list(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    target_msg = message.reply_to_message
    chat_peer = await client.resolve_peer(message.chat.id)
    
    user_list = []
    total_react_count = 0

    try:
        # ambil raw tele
        reaction_list_raw = await client.invoke(
            functions.messages.GetMessageReactionsList(
                peer=chat_peer,
                id=target_msg.id,
                limit=100
            )
        )
        
        if hasattr(reaction_list_raw, "users"):
            for raw_user in reaction_list_raw.users:
                username = None
                
                # cek usn
                if getattr(raw_user, "username", None):
                    username = raw_user.username
                
                # multi usn
                elif getattr(raw_user, "usernames", None):
                    for u in raw_user.usernames:
                        if getattr(u, "editable", False) or getattr(u, "active", False):
                            username = u.username
                            break
                
                # berhasil
                if username:
                    user_list.append(f"@{username}")
                else:
                    # kalau gagal
                    try:
                        user_id = getattr(raw_user, "id", None)
                        if user_id:
                            fetched_user = await client.get_users(user_id)
                            if fetched_user.username:
                                user_list.append(f"@{fetched_user.username}")
                    except Exception:
                        pass

        # Hitung jumlah total reaksi
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
        if updated_msg.reactions and updated_msg.reactions.reactions:
            for r in updated_msg.reactions.reactions:
                total_react_count += r.count

    except Exception as e:
        await message.reply_text(f"Bntr ada yang salah: {str(e)}")
        return

    user_list = list(set(user_list))

    if not user_list:
        await message.reply_text("Gagal, adminin dulu gw di gc.")
        return

    usernames_string = " ".join(user_list)

    # PERBAIKAN: Ditambahkan f-string dan dibungkus backtick agar font menjadi monospace (mono)
    caption_template = f"`{usernames_string} ({total_react_count})`"

    await client.send_message(
        chat_id=message.chat.id,
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v5 (Mono Format) Aktif!")
app.run()
