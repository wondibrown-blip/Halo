import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ==================== CONFIGURATION ====================
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
# Tempel teks panjang (String Session) dari Termux di dalam tanda kutip di bawah ini:
SESSION_STRING = "BQHv7HkAmmJiShBDImxMhhjJO6AFjP5-O4tTzj1_zus1kOTL2c7X8nLw64HbtK74jYfDDZZQIcumSQTwSFGp_0dKUDfQmJM0ei54OTX5BmJqrV3zVWsAI533vuEWKVzjtfiPrBhcwO9WDusWSqpkEanOOFImsOGN7-wDPBMK6BDubW6ENwoztQNNP08QdrtYc0LxgXy4J3wzIhoLsA-AxaOSA-dwmTZw9X2tfbx9EJeS_eraPvwjI8Ia5ly9k_mus0QnnPbeTzRfnLtqPxwP1RqHANj8FlFheTuR33stcMudAZVK-dzaGPUQ4EIWdzHb5zVPVKC__04cB6zlujEHRcHbftN-dAAAAAH62YR3AA"
# =======================================================

# Menggunakan session_string, Railway tidak butuh file .session lagi!
app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

reaction_tracker = {}

@app.on_raw_update()
async def track_live_reactions(client: Client, update, users, chats):
    class_name = update.__class__.__name__
    if "UpdateMessageReactions" in class_name or "UpdateBotMessageReactions" in class_name:
        msg_id = getattr(update, "msg_id", None) or getattr(update, "id", None)
        if not msg_id:
            return
            
        if msg_id not in reaction_tracker:
            reaction_tracker[msg_id] = {"total": 0, "users": set()}
            
        if hasattr(update, "reactions") and hasattr(update.reactions, "results"):
            total_count = sum(r.count for r in update.reactions.results)
            reaction_tracker[msg_id]["total"] = total_count
            
        for u_id, u_obj in users.items():
            if hasattr(u_obj, "username") and u_obj.username:
                reaction_tracker[msg_id]["users"].add(f"@{u_obj.username}")

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def get_reaction_list(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    target_msg = message.reply_to_message
    msg_id = target_msg.id
    
    user_list = []
    total_react_count = 0

    if msg_id in reaction_tracker:
        user_list = list(reaction_tracker[msg_id]["users"])
        total_react_count = reaction_tracker[msg_id]["total"]
    
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

    user_list = list(set(user_list))
    usernames_string = "No-Users-Detected" if not user_list else " ".join(user_list)
    caption_template = f"`{usernames_string} (`{total_react_count})`"

    await client.send_message(
        chat_id=message.chat.id,
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v7 (String Session Cloud) Aktif!")
app.run()
