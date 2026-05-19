import asyncio
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("showapp.scanner")

# Add backend directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from pyrogram import Client
from config import Config
from database import db_add_movie, movies_col
from bot import parse_filename, fetch_tmdb_metadata

async def scan_channel_history():
    print("==================================================")
    print("      INFINITY TV - HISTORICAL CHANNEL SCANNER    ")
    print("==================================================")
    
    # 1. Initialize Pyrogram Client
    if Config.SESSION_STRING:
        logger.info("Connecting to Pyrogram with User Session String...")
        client = Client(
            "infinity_scanner",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=Config.SESSION_STRING
        )
    else:
        logger.info("Connecting to Pyrogram with Bot Token...")
        client = Client(
            "infinity_scanner",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )
        
    await client.start()
    logger.info("Successfully connected to Pyrogram client!")
    
    # 2. Iterate through all configured channel IDs
    logger.info(f"Target channels count: {len(Config.DATABASE_CHANNELS)}")
    
    total_scanned = 0
    total_indexed = 0
    
    for chat_id in Config.DATABASE_CHANNELS:
        logger.info(f"\n--- Scanning Channel ID: {chat_id} ---")
        try:
            # Check if chat exists and get basic info
            chat = await client.get_chat(chat_id)
            logger.info(f"Connected to channel: '{chat.title}' (@{chat.username or 'Private'})")
            
            # Fetch last 50 messages from the channel
            logger.info("Fetching last 50 historical messages...")
            messages_count = 0
            
            async for message in client.get_chat_history(chat_id, limit=50):
                messages_count += 1
                video = message.video or message.document
                if not video:
                    continue
                    
                # Ensure it's a video file format
                filename = video.file_name or message.caption or ""
                if message.document and not (video.mime_type and video.mime_type.startswith("video/")):
                    continue
                if not filename:
                    filename = f"Video_Message_{message.id}"
                    
                total_scanned += 1
                
                # Check if this message_id from this channel is already indexed in MongoDB
                existing = await movies_col.find_one({"telegramChannel": f"@{chat.username}" if chat.username else str(chat_id), "messageId": message.id})
                if existing:
                    logger.info(f" - Skip: File '{filename}' (Message {message.id}) already indexed in MongoDB.")
                    continue
                
                logger.info(f" -> Found video post [{message.id}]: '{filename}' (Size: {round(video.file_size / (1024*1024), 1)} MB)")
                
                # 3. Parse filename metadata
                title, year, quality = parse_filename(filename)
                
                # 4. Fetch TMDB premium metadata
                metadata = await fetch_tmdb_metadata(title, year)
                
                # 5. Structure MongoDB document
                doc = {
                    "title": title,
                    "type": "movie",
                    "year": year,
                    "quality": quality,
                    "rating": "7.5",
                    "genres": ["Action", "Thriller"],
                    "description": f"Scraped from historical Telegram post. Message ID: {message.id}.",
                    "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600",
                    "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1600",
                    "cast": ["Unknown Starcast"],
                    "videoUrl": f"{Config.BASE_URL}/api/stream/{chat_id}/{message.id}", # Proper stream link
                    "telegramChannel": f"@{chat.username}" if chat.username else str(chat_id),
                    "messageId": message.id,
                    "fileSize": f"{round(video.file_size / (1024 * 1024 * 1024), 2)} GB",
                    "releaseDate": f"{year}-01-01"
                }
                
                if metadata:
                    doc.update({
                        "title": metadata["title"],
                        "type": metadata["type"],
                        "poster": metadata["poster"],
                        "backdrop": metadata["backdrop"],
                        "rating": metadata["rating"],
                        "description": metadata["description"],
                        "releaseDate": metadata["releaseDate"],
                        "genres": metadata["genres"],
                        "cast": metadata["cast"]
                    })
                    if metadata.get("seasons"):
                        doc["seasons"] = metadata["seasons"]
                        for s in doc["seasons"]:
                            for ep in s["episodes"]:
                                ep["videoUrl"] = f"{Config.BASE_URL}/api/stream/{chat_id}/{message.id}"
                
                # Insert into MongoDB Atlas
                inserted = await db_add_movie(doc)
                logger.info(f"   [DATABASE] Indexed: '{doc['title']}' stored successfully under ID: {inserted.get('id')}")
                total_indexed += 1
                
            logger.info(f"Channel Scan Complete! Scanned {messages_count} messages.")
            
        except Exception as e:
            logger.error(f"Failed to scan channel {chat_id}: {e}")
            
    print("\n==================================================")
    print(f" SCAN FINISHED! Scanned {total_scanned} files, indexed {total_indexed} new movies to MongoDB!")
    print("==================================================")
    await client.stop()

if __name__ == "__main__":
    asyncio.run(scan_channel_history())
