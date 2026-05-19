import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from bson import ObjectId

logger = logging.getLogger("showapp.database")

# Setup async MongoDB client
try:
    client = AsyncIOMotorClient(Config.MONGO_URI)
    db = client[Config.DB_NAME]
    
    # Collections
    movies_col = db["movies"]
    channels_col = db["channels"]
    
    logger.info("Successfully connected to MongoDB Cluster.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# Helper helper serializes BSON ObjectId to string
def serialize_doc(doc):
    if not doc:
        return None
    doc["id"] = str(doc.get("_id"))
    del doc["_id"]
    return doc

# ==========================================================================
# DB HELPER METHODS FOR MOVIES/SERIES
# ==========================================================================

async def db_get_movies(query: str = "", media_type: str = "all", quality: str = "all", channel: str = "all"):
    filter_dict = {}
    
    if media_type != "all":
        filter_dict["type"] = media_type
        
    if quality != "all":
        filter_dict["quality"] = quality
        
    if channel != "all":
        filter_dict["telegramChannel"] = channel
        
    if query:
        # Search by Title or Genres
        filter_dict["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"genres": {"$regex": query, "$options": "i"}},
            {"cast": {"$regex": query, "$options": "i"}}
        ]
        
    cursor = movies_col.find(filter_dict).sort("releaseDate", -1)
    results = []
    async for doc in cursor:
        results.append(serialize_doc(doc))
    return results

async def db_get_movie_by_id(movie_id: str):
    try:
        doc = await movies_col.find_one({"_id": ObjectId(movie_id)})
        return serialize_doc(doc)
    except Exception:
        # Fallback if id is string instead of ObjectId
        doc = await movies_col.find_one({"id": movie_id})
        return serialize_doc(doc)

async def db_add_movie(movie_data: dict):
    # Prevent duplicate titles within the same media type
    existing = await movies_col.find_one({"title": movie_data["title"], "type": movie_data["type"]})
    if existing:
        return serialize_doc(existing)
        
    result = await movies_col.insert_one(movie_data)
    movie_data["id"] = str(result.inserted_id)
    return movie_data

async def db_delete_movie(movie_id: str):
    try:
        await movies_col.delete_one({"_id": ObjectId(movie_id)})
        return True
    except Exception:
        await movies_col.delete_one({"id": movie_id})
        return True

# ==========================================================================
# DB HELPER METHODS FOR TELEGRAM CHANNELS
# ==========================================================================

async def db_get_channels():
    cursor = channels_col.find()
    channels = []
    async for doc in cursor:
        channels.append(serialize_doc(doc))
    return channels

async def db_add_channel(channel_data: dict):
    # Prevent duplicate channel
    existing = await channels_col.find_one({"username": channel_data["username"]})
    if existing:
        return serialize_doc(existing)
        
    result = await channels_col.insert_one(channel_data)
    channel_data["id"] = str(result.inserted_id)
    return channel_data

async def db_toggle_channel(channel_id: str):
    try:
        chan = await channels_col.find_one({"_id": ObjectId(channel_id)})
        if chan:
            new_status = not chan.get("active", True)
            await channels_col.update_one({"_id": ObjectId(channel_id)}, {"$set": {"active": new_status}})
            return True
    except Exception:
        pass
    return False

async def db_delete_channel(channel_id: str):
    try:
        await channels_col.delete_one({"_id": ObjectId(channel_id)})
        return True
    except Exception:
        return False
