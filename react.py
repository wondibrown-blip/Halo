import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.errors import FloodWait, RPCError

# ==================== SECURE CONFIGURATION ====================
# Mengambil kredensial secara aman dari Environment Variables Railway
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Configured for maximum network stability & Zero disk locks
app = Client(
    "my_userbot11", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    in_memory=True,
    max_concurrent_transmissions=3
)

async def process_reaction_list(client: Client, message: Message):
    """Safely extracts usernames and reaction counts with zero crash risk"""
    target_msg = message.reply_to_message
    user_list = []
    total_react_count = 0

    # 1. Fetch total counts safely
    try:
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
        if updated_msg and updated_msg.reactions:
            if hasattr(updated_msg.reactions, "reactions") and updated_msg.reactions.reactions:
                for r in updated_msg.reactions.reactions:
                    total_react_count += getattr(r, "count", 0)
            elif isinstance(updated_msg.reactions, list):
                for r in updated_msg.reactions:
                    total_react_count += getattr(r, "count", 0)
    except FloodWait as e:
        print(f"[Rate Limit] Hit FloodWait for {e.value}s while counting.")
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"[Log Warning] Safe pass count error: {e}")

    # 2. Extract User List via Telegram Raw Layer
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

    except FloodWait as e:
        print(f"[Rate Limit] Hit FloodWait for {e.value}s while fetching users.")
        await asyncio.sleep(e.value)
    except RPCError as e:
        print(f"[RPC Warning] Handled safely: {e.MESSAGE}")
    except Exception as e:
        print(f"[Log Warning] Handled user generation failure: {e}")

    # Fallback to prevent 0 counts if user strings were successfully parsed
    user_list = list(set(user_list))
    if total_react_count == 0 and len(user_list) > 0:
        total_react_count = len(user_list)

    usernames_string = "No-Users-Detected" if not user_list else " ".join(user_list)
    return usernames_string, total_react_count


# ==================== COMMANDS ====================

# Menangkap semua tipe grup (Supergroup/Channel/Grup Biasa) khusus dari akun kamu sendiri
GROUP_FILTERS = filters.me & (filters.group | filters.channel)

@app.on_message(filters.command("done", prefixes=["/", "."]) & GROUP_FILTERS)
async def cmd_done(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return
    try:
        usernames_string, total_react_count = await process_reaction_list(client, message)
        await message.reply_text(text=f"`{usernames_string} ({total_react_count})`")
    except Exception as fatal_error:
        print(f"[System Suppressed Error]: {fatal_error}")


@app.on_message(filters.command("doni", prefixes=["/", "."]) & GROUP_FILTERS)
async def cmd_doni(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /doni")
        return
    try:
        usernames_string, total_react_count = await process_reaction_list(client, message)
        caption_template = (
            "``` \n"
            "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
            "𝗦𝗬𝗡𝗖 𝗣𝗔𝗖𝗧: Mutual terms enforced.\n"
            f"Alignment forms beyond consent, presence settles refuses 2 shift. 𝘕𝘰 𝘧𝘳𝘢𝘤𝘵𝘶𝘳𝘦 𝘰𝘯𝘤𝘦 𝘪𝘵 𝘴𝘦𝘵𝘴: {usernames_string} ({total_react_count}) bound. Balanced force, no reversal (+KT9.) https://t.me/HOTROVERs/4.\n"
            "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ```"
        )
        await message.reply_text(text=caption_template, disable_web_page_preview=False)
    except Exception as fatal_error:
        print(f"[System Suppressed Error]: {fatal_error}")


# ==================== CORE SYSTEM RUNNER ====================
async def main():
    # Jeda 20 detik agar Railway bisa memutuskan koneksi lama sebelum membuat yang baru
    print("⏳ Memperbarui jaringan session socket dari Railway...")
    await asyncio.sleep(20)
    
    async with app:
        print("⚡ Userbot AKTIF dengan kredensial aman dari Railway!")
        await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("👋 System closed down gracefully.")
    except Exception as main_err:
        print(f"[Critical Fail Catch] System Auto-Recovery: {main_err}")
