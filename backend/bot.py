import re
import httpx
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database import db_add_movie, db_get_channels

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("showapp.bot")

# Initialize Pyrogram Client (Userbot Session String if provided, else falls back to Bot Token)
if Config.SESSION_STRING:
    logger.info("Initializing Pyrogram with User Session String (Userbot active).")
    bot = Client(
        "infinity_userbot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        session_string=Config.SESSION_STRING
    )
else:
    logger.info("Initializing Pyrogram with Bot Token.")
    bot = Client(
        "infinity_bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN
    )

# Regex patterns to clean filenames and parse meta tags
YEAR_PATTERN = re.compile(r'\b(19\d\d|20\d\d)\b')
QUALITY_PATTERN = re.compile(r'\b(2160p|1080p|720p|480p|HDRip|WEBRip|BluRay)\b', re.IGNORECASE)

def parse_filename(filename: str):
    """
    Parses a raw filename into a structured title, year, and quality.
    Example: 'Avatar.The.Way.of.Water.2022.1080p.mkv' -> ('Avatar The Way of Water', '2022', '1080p')
    """
    # Clean extensions and symbols
    name_clean = filename.rsplit('.', 1)[0]
    name_clean = name_clean.replace('.', ' ').replace('_', ' ').replace('-', ' ')
    
    # Extract year
    year_match = YEAR_PATTERN.search(name_clean)
    year = year_match.group(1) if year_match else "2024"
    
    # Extract quality
    quality_match = QUALITY_PATTERN.search(name_clean)
    quality = quality_match.group(1) if quality_match else "1080p"
    
    # Extract Title before the year or quality indicator
    split_indices = []
    if year_match:
        split_indices.append(year_match.start())
    if quality_match:
        split_indices.append(quality_match.start())
        
    title = name_clean
    if split_indices:
        first_indicator = min(split_indices)
        title = name_clean[:first_indicator].strip()
        
    # Clean double spaces
    title = re.sub(r'\s+', ' ', title).strip()
    return title, year, quality

async def fetch_tmdb_metadata(title: str, year: str = ""):
    """
    Asynchronously queries TMDb Developer APIs to fetch premium metadata.
    """
    if not Config.TMDB_API_KEY:
        return None
        
    url = "https://api.themoviedb.org/3/search/multi"
    params = {
        "api_key": Config.TMDB_API_KEY,
        "query": title,
        "language": "en-US",
        "page": 1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results:
                    return None
                    
                # Pick the highest relevant match (Movie or TV show)
                match = results[0]
                media_type = match.get("media_type", "movie")
                
                # Fetch details based on media type
                tmdb_id = match.get("id")
                poster_path = match.get("poster_path")
                backdrop_path = match.get("backdrop_path")
                
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600"
                backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1600"
                
                # Extract details
                rating = str(round(match.get("vote_average", 7.5), 1))
                overview = match.get("overview", f"No detailed overview found for '{title}'.")
                
                # Dynamic genre mappings
                genre_ids = match.get("genre_ids", [])
                genres = ["Drama", "Sci-Fi"] # Default fallback
                
                # TV Specific episode arrays if needed
                seasons = []
                if media_type == "tv":
                    seasons = [
                        {
                            "seasonNumber": 1,
                            "episodes": [
                                {"episodeNumber": 1, "title": "Pilot Spec", "videoUrl": ""}
                            ]
                        }
                    ]
                
                return {
                    "title": match.get("title") or match.get("name") or title,
                    "type": "series" if media_type == "tv" else "movie",
                    "poster": poster_url,
                    "backdrop": backdrop_url,
                    "rating": rating,
                    "genres": genres,
                    "cast": ["Actor A", "Actor B"], # TMDb credits endpoint fetch can expand this
                    "description": overview,
                    "releaseDate": match.get("release_date") or match.get("first_air_date") or f"{year}-01-01",
                    "seasons": seasons
                }
    except Exception as e:
        logger.error(f"TMDb integration failed to scrap metadata: {e}")
    return None

# ==========================================================================
# REAL-TIME BOT STREAM SCANNER LISTENER
# ==========================================================================

@bot.on_message(filters.channel)
async def handle_new_channel_post(client: Client, message: Message):
    """
    Triggers automatically when a new post arrives in tracked telegram channels.
    """
    # Check if this channel is in our tracked database
    tracked_channels = await db_get_channels()
    tracked_usernames = [c["username"].lower() for c in tracked_channels if c.get("active", True)]
    
    chat = message.chat
    if not chat.username or f"@{chat.username}".lower() not in tracked_usernames:
        return # Skip untracked channels
        
    # Check if message contains media
    video = message.video or message.document
    if not video:
        return
        
    filename = video.file_name or message.caption or "Unknown_Movie"
    # Ensure it's a video file format
    if message.document and not video.mime_type.startswith("video/"):
        return
        
    logger.info(f"Indexing new movie file found in {chat.username}: {filename}")
    
    # 1. Parse filename metadata
    title, year, quality = parse_filename(filename)
    
    # 2. Scrape premium TMDb details
    metadata = await fetch_tmdb_metadata(title, year)
    
    # 3. Structure Document
    doc = {
        "title": title,
        "type": "movie",
        "year": year,
        "quality": quality,
        "rating": "7.5",
        "genres": ["Action", "Thriller"],
        "description": f"Raw media file scraped from Telegram post. Message ID: {message.id}.",
        "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600",
        "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1600",
        "cast": ["Unknown Starcast"],
        "videoUrl": f"{Config.BASE_URL}/api/stream/{message.id}", # Re-routed streaming proxy link
        "telegramChannel": f"@{chat.username}",
        "messageId": message.id,
        "fileSize": f"{round(video.file_size / (1024 * 1024 * 1024), 2)} GB",
        "releaseDate": f"{year}-01-01"
      }
      
    # Overwrite default fallback with TMDb metadata if scraped successfully
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
            # Fill video url inside season ep
            for s in doc["seasons"]:
                for ep in s["episodes"]:
                    ep["videoUrl"] = f"{Config.BASE_URL}/api/stream/{message.id}"
                    
    # Save to MongoDB
    inserted = await db_add_movie(doc)
    logger.info(f"Database sync successful: '{doc['title']}' saved under ID: {inserted.get('id')}")
