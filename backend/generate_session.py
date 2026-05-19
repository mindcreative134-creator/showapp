import asyncio
from pyrogram import Client

async def generate():
    print("====================================================")
    print("🔥 Pyrogram Session String Generator for Infinity TV")
    print("====================================================\n")
    
    api_id_input = input("Enter your Telegram API_ID (from my.telegram.org): ").strip()
    api_hash_input = input("Enter your Telegram API_HASH: ").strip()
    
    if not api_id_input or not api_hash_input:
        print("❌ Error: API_ID and API_HASH cannot be blank!")
        return

    try:
        api_id = int(api_id_input)
    except ValueError:
        print("❌ Error: API_ID must be a valid integer number!")
        return

    print("\nℹ️ Starting Pyrogram interactive login. You will be prompted to enter your phone number (+countrycode), followed by the OTP sent to your Telegram app.")
    
    # Initialize Pyrogram client in-memory to prevent session file clutter
    async with Client(
        "infinity_userbot_session",
        api_id=api_id,
        api_hash=api_hash_input,
        in_memory=True
    ) as app:
        # Export the Pyrogram-specific session string
        session_str = await app.export_session_string()
        
        print("\n🎉 SUCCESS! Your Pyrogram Session String has been generated:")
        print("====================================================")
        print(session_str)
        print("====================================================\n")
        print("👉 Copy the entire string above and paste it as SESSION_STRING in your 'config.env' file.")

if __name__ == "__main__":
    try:
        asyncio.run(generate())
    except KeyboardInterrupt:
        print("\n❌ Session generation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
