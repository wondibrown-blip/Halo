import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.raw.types import InputPeerChannel, InputPeerChat

# ==================== CONFIGURATION ====================
API_ID = 32500857         
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
SESSION_STRING = "BQHv7HkAdUsbSGBOokXtih-kpCUxfjRrjbHaPK8UCepJzQIhvqFPSbzzavkecEd5PyFc-LNyAgeWaGh7_kHZz3U6GzLEk29Bex-AR21jE-qQ-OfQjDzvcPa5WWYyLccPF4GUfxTs-yArztALQE7CEpuah2UjdIHadgrzj5fbPxuoCixb_oub2VUdronPn3UK_qeXOrRjh7SxEpUDc4GSGHB9NipiFHp4Q8MJdTpnFUIA2xOUZFxXfBCvx7R37lN-pjIXOw9g1OVm4jmBA37evYG1CeBXoPCR2THx8vjnFfdsC9ArAS3MR3DXB8yidUv02UoGO2PY4Trm0TEkcsMxJAUMoZ8vTAAAAAH62YR3AA"

app = Client("my_userbot11", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

async def process_reaction_list(client: Client, message: Message):
    """Fungsi helper yang aman dari crash thread untuk mengambil list user & total react"""
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
        # Gunakan client.resolve_peer secara aman
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

    # 3. Validasi & Hitung Cadangan (mencegah angka 0 jika data user terbaca)
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
    
    await message.reply_text(text=caption_template, disable_web_page_preview=False)


@app.on_message(filters.command("doni", prefixes=["/", "."]) & filters.group)
async def cmd_doni(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /doni")
        return

    usernames_string, total_react_count = await process_reaction_list(client, message)
    
    # Template Estetik SYNC PACT sesuai permintaan
    caption_template = (
        "``` \n"
        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
        "𝗦𝗬𝗡𝗖 𝗣𝗔𝗖𝗧: Mutual terms enforced.\n"
        f"Alignment forms beyond consent, presence settles refuses 2 shift. 𝘕𝘰 𝘧𝘳𝘢𝘤𝘵𝘶𝘳𝘦 𝘰𝘯𝘤𝘦 𝘪𝘵 𝘴𝘦𝘵𝘴: {usernames_string} ({total_react_count}) bound. Balanced force, no reversal (+KT9.) https://t.me/HOTROVERs/4.\n"
        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ```"
    )
    
    await message.reply_text(text=caption_template, disable_web_page_preview=False)


# Menjalankan bot secara non-blocking asinkron agar aman dari thread crash
async def start_bot():
    # Berikan jeda 5 detik saat start untuk memastikan sesi lama di platform 
    # benar-benar dilepas/dimatikan sebelum sesi baru melakukan handshake ke Telegram.
    print("⏳ Menunggu stabilitas network (5 detik)...")
    await asyncio.sleep(5)
    
    await app.start()
    print("⚡ Userbot /amey & /amer v11 Aktif Stabil di Railway!")
    
    # Menjaga bot tetap hidup tanpa menggunakan app.run() yang memicu loop-crash
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
