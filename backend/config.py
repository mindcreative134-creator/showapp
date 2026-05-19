import os
from dotenv import load_dotenv

# Load config.env or .env file
load_dotenv("config.env")
load_dotenv()

class Config:
    # Telegram API Credentials
    API_ID = int(os.getenv("API_ID", "29507367"))
    API_HASH = os.getenv("API_HASH", "a99c710ea3f1530e5600d27ac8f3fe84")
    
    # Telegram Bot Settings
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8625523630:AAEGanx-X7n4GKdIMgWFVuhdtldHVyecGXI")
    SESSION_STRING = os.getenv("SESSION_STRING", "") # Pyrogram session string for Userbot client (optional)
    OWNER_ID = int(os.getenv("OWNER_ID", "7045947967"))
    
    # MongoDB Database Connection URI
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://appdb:appdb@cluster0.neu7p0o.mongodb.net/?appName=Cluster0")
    DB_NAME = os.getenv("DB_NAME", "appdb")
    
    # TMDb Developer API Key (For automatically fetching Posters, Cast, Backdrops)
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "0da8b26f661ce60b48bb5f2876e13c74")
    
    # Stream Server Configuration
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
