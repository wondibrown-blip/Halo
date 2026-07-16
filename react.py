import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.errors import FloodWait, RPCError

# ==================== CONFIGURATION ====================
API_ID = 34004937         
API_HASH = "804cec5c31b7cd051030833989b71f72"  
SESSION_STRING = "BQIG38kAgvWExx7Y_lvUUlsGp05lxhClChKvrVvkyhh64xVhZrwjzNOzQ7CKn1amIxcLZW2iRyiIyUxW-h4qCPp40RdobU3cVQhBLthkOej9xKOOG2vsvTK1hk-TmFHPQmXoKW7JztTz2bMNeoyz67o6fTt5OD77se-kUpIq_omWiuj3t-0dT_FZ6hS12OpuIKu4rpgNBbWvbiI6CZi0S5_YUw1QOwlbT86GkD8-8cFbtcJuBvb_Nw5e0_2TVrwdRytiCj6gK5ydTXRqh-qZ-p5Vsju2nmcuiD8cwfWq8gh_39bTrUjHepHyjK8Na4mCzbQCDj-BFgkuSfYRU2-erWFAN-uJVAAAAAH62YR3AA"

app = Client(
    "my_userbot11", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    in_memory=True
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
            elif isinstance(updated_msg.reactions, list):
                for r in updated_msg.reactions:
                    total_react_count += getattr(r, "count", 0)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"[Log] Failed to get reactions: {str(e)}")

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
        await asyncio.sleep(e.value)
    except RPCError as e:
        print(f"[Telegram RPC Error] {e.MESSAGE}")
    except Exception as e:
        print(f"[Log] Failed to get user list: {str(e)}")

    user_list = list(set(user_list))
    if total_react_count == 0 and len(user_list) > 0:
        total_react_count = len(user_list)

    usernames_string = "No-Users-Detected" if not user_list else " ".join(user_list)
    return usernames_string, total_react_count


# ==================== COMMANDS ====================
# Updated filters to capture Supergroups/Channels and only execute if triggered by YOU

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.me & (filters.group | filters.channel))
async def cmd_done(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return
    try:
        usernames_string, total_react_count = await process_reaction_list(client, message)
        await message.reply_text(text=f"`{usernames_string} ({total_react_count})`")
    except Exception as e:
        print(f"[Error Handler Done] {e}")


@app.on_message(filters.command("doni", prefixes=["/", "."]) & filters.me & (filters.group | filters.channel))
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
    except Exception as e:
        print(f"[Error Handler Doni] {e}")


# ==================== RUNNER ====================
async def main():
    print("⏳ Waiting 15 seconds for network session allocation...")
    await asyncio.sleep(15)
    
    async with app:
        print("⚡ Userbot ACTIVE. Listening ONLY to your account updates across all group types.")
        await idle()

if __name__ == "__main__":
    asyncio.run(main())
