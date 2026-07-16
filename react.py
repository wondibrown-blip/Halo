import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.raw import functions

# ==================== CONFIGURATION ====================
# ⚠️ WARNING: Revoke this session in your Telegram settings ASAP, as it is exposed!
API_ID = 34004937         
API_HASH = "804cec5c31b7cd051030833989b71f72"  
SESSION_STRING = "BQIG38kASVFcay-u6HS8j-tc49b7D-bRhp2PaezMH1pBgFzkb-HQed79D088PRi3QPv8C4H7AzDKhhkyK-6hc_iMo7OjPVc4nVuJs-HBP5_OxIHdZwBTOPkanpWZpZ-VLGUBEHJyHNV-zJwiolmYJ-J4Amo0Ldv540Tg-dbBYopqD8JZyzrEc1_vVj_nd9TbdBv2gEsjIf8H7PBTc6N-DNXbK809ZtJhCcl36KBPOvvs5TVlrxkD-qCYzf-gyqhqFis2XfUMQcYuthUiJ24rVVtWyjfE65ECU4iniZ5uhK9pMx09PicMXstr44u3vmSySuS-HySga5Y9aKvRcH2X-uy0h-7JOgAAAAH62YR3AA"

app = Client("my_userbot11", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

async def process_reaction_list(client: Client, message: Message):
    """Fungsi helper untuk mengambil list user & total react"""
    target_msg = message.reply_to_message
    user_list = []
    total_react_count = 0

    # 1. Ambil pesan terbaru & hitung reaksinya secara aman
    try:
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
        if updated_msg and updated_msg.reactions:
            if hasattr(updated_msg.reactions, "reactions") and updated_msg.reactions.reactions:
                for r in updated_msg.reactions.reactions:
                    total_react_count += getattr(r, "count", 0)
            elif isinstance(updated_msg.reactions, list):
                for r in updated_msg.reactions:
                    total_react_count += getattr(r, "count", 0)
            else:
                total_react_count = getattr(updated_msg.reactions, "count", 0)
    except Exception as e:
        print(f"[Log] Gagal mengambil total reaksi: {str(e)}")

    # 2. Ambil daftar user menggunakan API Telegram secara dinamis
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
                if not username and getattr(raw_user, "usernames", None):
                    for u in raw_user.usernames:
                        if getattr(u, "active", False):
                            username = u.username
                            break
                if username:
                    user_list.append(f"@{username}")

    except Exception as e:
        print(f"[Log] Gagal mengambil daftar user: {str(e)}")

    # 3. Validasi & Hitung Cadangan
    user_list = list(set(user_list))
    if total_react_count == 0 and len(user_list) > 0:
        total_react_count = len(user_list)

    usernames_string = "No-Users-Detected" if not user_list else " ".join(user_list)
    return usernames_string, total_react_count


# ==================== COMMANDS ====================

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def cmd_done(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    usernames_string, total_react_count = await process_reaction_list(client, message)
    caption_template = f"`{usernames_string} ({total_react_count})`"
    
    await message.reply_text(text=caption_template)


@app.on_message(filters.command("doni", prefixes=["/", "."]) & filters.group)
async def cmd_doni(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /doni")
        return

    usernames_string, total_react_count = await process_reaction_list(client, message)
    
    caption_template = (
        "``` \n"
        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
        "𝗦𝗬𝗡𝗖 𝗣𝗔𝗖𝗧: Mutual terms enforced.\n"
        f"Alignment forms beyond consent, presence settles refuses 2 shift. 𝘕𝘰 𝘧𝘳𝘢𝘤𝘵𝘶𝘳𝘦 𝘰𝘯𝘤𝘦 𝘪𝘵 𝘴𝘦𝘵𝘴: {usernames_string} ({total_react_count}) bound. Balanced force, no reversal (+KT9.) https://t.me/HOTROVERs/4.\n"
        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ```"
    )
    
    await message.reply_text(text=caption_template, disable_web_page_preview=False)


# ==================== RUNNER ====================
async def main():
    print("⏳ Menunggu stabilitas alokasi jaringan (6 detik)...")
    await asyncio.sleep(6)
    
    async with app:
        print("⚡ Userbot /done & /doni AKTIF & STABIL 24/7 di Railway!")
        # Menggunakan idle() bawaan pyrogram agar background task berjalan lancar tanpa terputus loop manual
        await idle()

if __name__ == "__main__":
    asyncio.run(main())
