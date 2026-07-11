import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.raw.types import InputPeerChannel, InputPeerChat

# ==================== CONFIGURATION ====================
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
SESSION_STRING = "BQHv7HkAsZfViv2vvFXCdFiVqWpgnF2RbHfcVUfqMjA8juxQ9PeyDWVYLxNeHXjXbYKuf1eEr75SQaaRxG8u-6vlmIatHqCnnynNaWfTUPyaybJCFlHWuqIqp8H34MpUXihZ2JUkE1cq6jQZbtuC9rAokLM1bUzAxMFemOuMlK2EzfBFxjDMJ2k0LhXomh3KX8lMwvvZ3_BhD1sJNm1D3qtOdnNV6vtHGgbqz6rMX5Byw78-Tlx6jze4B44feumk9dteuZTVnxx2VvhsEzkvVQrmUw56Z-rJbGUaV3oioYTic4g9XYUx3xIg1-6tNTXnXQ42_HxB9TO34QB60ZwyBYFQCmDsPgAAAAH62YR3AA"


app = Client("my_userbot10", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def get_reaction_list(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    target_msg = message.reply_to_message
    
    user_list = []
    total_react_count = 0

    try:
        # 1. Ambil hitungan total reaksi aktual dari pesan
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
        if updated_msg.reactions and updated_msg.reactions.reactions:
            for r in updated_msg.reactions.reactions:
                total_react_count += r.count

        # 2. Penanganan Khusus Supergroup/Channel-Chat (Bypass MSG_ID_INVALID)
        # Kita paksa ambil bentuk peer mentah agar Telegram tahu ini struktur Supergrup
        if message.chat.type in ["supergroup", "channel"]:
            # Konversi ID chat ke format internal Channel Telegram
            channel_id = int(str(message.chat.id).replace("-100", ""))
            chat_info = await client.get_chat(message.chat.id)
            access_hash = chat_info.linked_chat.access_hash if getattr(chat_info, "linked_chat", None) else 0
            
            # Jika access_hash standar gagal diperoleh, gunakan resolver bawaan Pyrogram
            if not access_hash:
                resolved_peer = await client.resolve_peer(message.chat.id)
                access_hash = getattr(resolved_peer, "access_hash", 0)
                
            chat_peer = InputPeerChannel(channel_id=channel_id, access_hash=access_hash)
        else:
            # Grup normal biasa
            chat_peer = await client.resolve_peer(message.chat.id)
        
        # 3. Ambil daftar user secara paksa dari database inti Telegram
        raw_reply = await client.invoke(
            functions.messages.GetMessageReactionsList(
                peer=chat_peer,
                id=target_msg.id,
                limit=100
            )
        )
        
        # 4. Ekstrak data username
        if hasattr(raw_reply, "users"):
            for raw_user in raw_reply.users:
                username = None
                if getattr(raw_user, "username", None):
                    username = raw_user.username
                elif getattr(raw_user, "usernames", None):
                    for u in raw_user.usernames:
                        if getattr(u, "active", False) or getattr(u, "editable", False):
                            username = u.username
                            break
                
                if username:
                    user_list.append(f"@{username}")

    except Exception as e:
        print(f"Error: {str(e)}")

    # Bersihkan duplikasi username
    user_list = list(set(user_list))

    if not user_list:
        usernames_string = "No-Users-Detected"
    else:
        usernames_string = " ".join(user_list)

    # Template Estetik SYNC PACT
    caption_template = f"`{usernames_string} ({total_react_count})`"
    
    await message.reply_text(
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v10 (Supergroup Fixed) Aktif!")
app.run()
