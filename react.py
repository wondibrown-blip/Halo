import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions

# ==================== CONFIGURATION ====================
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
SESSION_STRING = "BQHv7HkAmmJiShBDImxMhhjJO6AFjP5-O4tTzj1_zus1kOTL2c7X8nLw64HbtK74jYfDDZZQIcumSQTwSFGp_0dKUDfQmJM0ei54OTX5BmJqrV3zVWsAI533vuEWKVzjtfiPrBhcwO9WDusWSqpkEanOOFImsOGN7-wDPBMK6BDubW6ENwoztQNNP08QdrtYc0LxgXy4J3wzIhoLsA-AxaOSA-dwmTZw9X2tfbx9EJeS_eraPvwjI8Ia5ly9k_mus0QnnPbeTzRfnLtqPxwP1RqHANj8FlFheTuR33stcMudAZVK-dzaGPUQ4EIWdzHb5zVPVKC__04cB6zlujEHRcHbftN-dAAAAAH62YR3AA"
# =======================================================

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

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

        # 2. Ambil peer chat dalam bentuk objek raw yang dikenali server Telegram
        chat_peer = await client.resolve_peer(message.chat.id)
        
        # 3. Paksa Telegram mengirim daftar user via Raw API (Maksimal 100 user)
        raw_reply = await client.invoke(
            functions.messages.GetMessageReactionsList(
                peer=chat_peer,
                id=target_msg.id,
                limit=100
            )
        )
        
        # 4. Ekstrak data user hasil paksaan dari server
        if hasattr(raw_reply, "users"):
            for raw_user in raw_reply.users:
                username = None
                
                # Cek username tunggal
                if getattr(raw_user, "username", None):
                    username = raw_user.username
                # Cek jika user punya multi-username (fitur baru Telegram)
                elif getattr(raw_user, "usernames", None):
                    for u in raw_user.usernames:
                        if getattr(u, "active", False) or getattr(u, "editable", False):
                            username = u.username
                            break
                
                if username:
                    user_list.append(f"@{username}")

    except Exception as e:
        # Jika terjadi error teknis, bot akan memberitahu letak salahnya di logs Railway
        print(f"Error: {str(e)}")

    # Bersihkan duplikasi username
    user_list = list(set(user_list))

    if not user_list:
        usernames_string = "No-Users-Detected"
    else:
        usernames_string = " ".join(user_list)

    # Template Estetik SYNC PACT kamu
    caption_template = f"`{usernames_string} ({total_react_count})`"
    

    await message.reply_text(
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v9 (Force Raw Fetcher) Aktif!")
app.run()
