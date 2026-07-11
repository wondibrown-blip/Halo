import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ==================== CONFIGURATION ====================
API_ID = 32500857            
API_HASH = "777a8c5d7b009d027a2d3b64b67652f1"  
# Tempel teks panjang (String Session) hasil dari gen.py di bawah ini:
SESSION_STRING = "BQHv7HkAmmJiShBDImxMhhjJO6AFjP5-O4tTzj1_zus1kOTL2c7X8nLw64HbtK74jYfDDZZQIcumSQTwSFGp_0dKUDfQmJM0ei54OTX5BmJqrV3zVWsAI533vuEWKVzjtfiPrBhcwO9WDusWSqpkEanOOFImsOGN7-wDPBMK6BDubW6ENwoztQNNP08QdrtYc0LxgXy4J3wzIhoLsA-AxaOSA-dwmTZw9X2tfbx9EJeS_eraPvwjI8Ia5ly9k_mus0QnnPbeTzRfnLtqPxwP1RqHANj8FlFheTuR33stcMudAZVK-dzaGPUQ4EIWdzHb5zVPVKC__04cB6zlujEHRcHbftN-dAAAAAH62YR3AA"
# =======================================================

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.command("done", prefixes=["/", "."]) & filters.group)
async def get_reaction_list(client: Client, message: Message):
    # Pastikan kamu me-reply suatu pesan saat mengetik /done
    if not message.reply_to_message:
        await message.reply_text("Rep terus /done")
        return

    # Pesan yang kamu reply (misal pesan bbc)
    target_msg = message.reply_to_message
    
    user_list = []
    total_react_count = 0

    try:
        # Ambil ulang data pesan target langsung dari server Telegram agar datanya fresh
        updated_msg = await client.get_messages(chat_id=message.chat.id, message_ids=target_msg.id)
        
        if updated_msg.reactions and updated_msg.reactions.reactions:
            for r in updated_msg.reactions.reactions:
                total_react_count += r.count
            
            # Coba ambil peer (user) yang memberikan reaksi baru-baru ini
            # Menggunakan metode hybrid fallback untuk fleksibilitas cloud
            for r in updated_msg.reactions.reactions:
                peers = getattr(r, "added_reactions", None) or getattr(r, "recent_peers", None)
                if peers:
                    for added in peers:
                        user_obj = getattr(added, "user", added)
                        if getattr(user_obj, "username", None):
                            user_list.append(f"@{user_obj.username}")
    except Exception:
        pass

    # Bersihkan duplikasi data username
    user_list = list(set(user_list))

    # Jika tidak terdeteksi, berikan teks cadangan agar format teks tidak pecah
    if not user_list:
        usernames_string = "No-Users-Detected"
    else:
        usernames_string = " ".join(user_list)

    # Format text monospace (mono) sesuai request kamu: `text` (`total`)
    caption_template = f"`{usernames_string} ({total_react_count})`"

    # PERBAIKAN ALUR: Bot sekarang membalas (reply) ke pesan /done milikmu, bukan kirim pesan lepas
    await message.reply_text(
        text=caption_template,
        disable_web_page_preview=False
    )

print("⚡ Userbot /done v8 (Reply Target Format) Aktif!")
app.run()
