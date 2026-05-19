import os
import logging
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from config import Config
from database import (
    movies_col, channels_col, serialize_doc,
    db_get_movies, db_get_movie_by_id, db_add_movie, db_delete_movie,
    db_get_channels, db_add_channel, db_toggle_channel, db_delete_channel
)
from bson import ObjectId
import httpx

# Setup Logger
logger = logging.getLogger("showapp.api")

app = FastAPI(
    title="Infinity TV Core REST Engine",
    version="1.5.0",
    description="Unified backend server providing FastAPI MongoDB REST endpoints, direct media proxy stream re-routing, and live administrative panels."
)

# Enable CORS for frontend clients (web apps, admin panels, Flutter mobile clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================================
# FLUTTER CLIENT COMPATIBILITY SERIALIZER
# ==========================================================================

def format_media_for_flutter(doc):
    """
    Serializes a MongoDB movie/show document into the exact schema expected by
    the Flutter mobile client in 'filmy4uhd_service.dart'.
    """
    if not doc:
        return None
        
    doc_id = str(doc.get("_id") or doc.get("id") or "")
    title = doc.get("title", "Unknown Title")
    media_type = doc.get("type", "movie")
    
    # Base fallback media arrays
    telegram_files = doc.get("telegram", [])
    if not telegram_files:
        # Migrate/format single stream properties to files array
        telegram_files = [{
            "id": str(doc.get("messageId") or "1"),
            "name": doc.get("file_name") or f"{title}.mkv",
            "quality": doc.get("quality", "1080p"),
            "size": doc.get("fileSize", "1.6 GB")
        }]
        
    seasons_raw = doc.get("seasons", [])
    seasons = []
    for s in seasons_raw:
        episodes = []
        for ep in s.get("episodes", []):
            episodes.append({
                "episode_number": ep.get("episodeNumber", 1),
                "title": ep.get("title", "Episode Title"),
                "episode_backdrop": ep.get("backdrop", doc.get("backdrop", "")),
                "telegram": ep.get("telegram", [{
                    "id": str(doc.get("messageId") or "1"),
                    "name": ep.get("title", "Episode Video") + ".mkv",
                    "quality": doc.get("quality", "1080p"),
                    "size": doc.get("fileSize", "950 MB")
                }])
            })
        seasons.append({
            "season_number": s.get("seasonNumber", 1),
            "episodes": episodes
        })

    return {
        "id": doc_id,
        "tmdb_id": doc.get("tmdbId") or doc_id,
        "title": title,
        "name": title, # fallback
        "description": doc.get("description") or doc.get("overview") or "An exciting new premium release loaded instantly from Telegram channels.",
        "overview": doc.get("description") or "An exciting new premium release loaded instantly from Telegram channels.", # fallback
        "poster_path": doc.get("poster", ""),
        "poster": doc.get("poster", ""), # fallback
        "backdrop_path": doc.get("backdrop", ""),
        "backdrop": doc.get("backdrop", ""), # fallback
        "vote_average": float(doc.get("rating", 8.5)),
        "rating": float(doc.get("rating", 8.5)), # fallback
        "release_date": str(doc.get("year", "2026")),
        "release_year": int(doc.get("year", 2026) if str(doc.get("year", "")).isdigit() else 2026), # fallback
        "media_type": "tv" if media_type == "series" else media_type,
        "type": "tv" if media_type == "series" else media_type, # fallback
        "rip": doc.get("quality", "1080p"),
        "languages": doc.get("languages", ["Hindi", "English"]),
        "genres": doc.get("genres", ["Drama", "Action"]),
        "director": doc.get("director", "Unknown Director"),
        "cast": doc.get("cast", ["Unknown Cast"]),
        "telegram": telegram_files,
        "seasons": seasons,
        "total_episodes": doc.get("total_episodes"),
        "total_seasons": len(seasons) if seasons else None,
        "runtime": doc.get("runtime")
    }

# ==========================================================================
# FLUTTER WEB API ENDPOINTS (CONNECTED TO MONGODB)
# ==========================================================================

@app.get("/")
async def root_index():
    return {
        "status": "online",
        "service": "Infinity TV Core Server",
        "database": "MongoDB Cluster Connected",
        "base_url": Config.BASE_URL
    }

@app.get("/api/movies")
async def get_movies(
    page: int = Query(1, description="Page index"),
    page_size: int = Query(20, description="Items per page"),
    sort_by: str = Query("updated_on:desc", description="Sorting criteria")
):
    try:
        # Fetch movies from MongoDB
        cursor = movies_col.find({"type": "movie"}).skip((page - 1) * page_size).limit(page_size)
        results = []
        async for doc in cursor:
            results.append(format_media_for_flutter(doc))
        return {
            "total": len(results),
            "page": page,
            "movies": results,
            "results": results # compatibility fallback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tvshows")
async def get_tv_shows(
    page: int = Query(1, description="Page index"),
    page_size: int = Query(20, description="Items per page"),
    sort_by: str = Query("updated_on:desc", description="Sorting criteria")
):
    try:
        # Fetch series/tv shows from MongoDB
        cursor = movies_col.find({"type": "series"}).skip((page - 1) * page_size).limit(page_size)
        results = []
        async for doc in cursor:
            results.append(format_media_for_flutter(doc))
        return {
            "total": len(results),
            "page": page,
            "tvshows": results,
            "results": results # compatibility fallback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/id/{media_id}")
async def get_media_details(media_id: str):
    try:
        # Search by ObjectId or fallback tmdbId key
        doc = None
        if ObjectId.is_valid(media_id):
            doc = await movies_col.find_one({"_id": ObjectId(media_id)})
        
        if not doc:
            doc = await movies_col.find_one({"tmdbId": media_id})
            
        if not doc:
            doc = await movies_col.find_one({"id": media_id})

        if not doc:
            raise HTTPException(status_code=404, detail="Requested media details not found.")
            
        return format_media_for_flutter(doc)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_media(
    query: str = Query("", description="Query keyword"),
    page: int = Query(1, description="Page index")
):
    try:
        filter_dict = {}
        if query:
            filter_dict["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"genres": {"$regex": query, "$options": "i"}},
                {"cast": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
            
        cursor = movies_col.find(filter_dict).skip((page - 1) * 20).limit(20)
        results = []
        async for doc in cursor:
            results.append(format_media_for_flutter(doc))
        return {
            "total": len(results),
            "page": page,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/similar")
async def similar_media(
    tmdb_id: str = Query("", description="Selected TMDB id"),
    media_type: str = Query("movie", description="Selected media type"),
    limit: int = Query(12, description="Output bounds")
):
    try:
        # Fetch related items based on similar media type
        db_type = "series" if media_type == "tvshow" or media_type == "tv" else "movie"
        cursor = movies_col.find({"type": db_type}).limit(limit)
        results = []
        async for doc in cursor:
            results.append(format_media_for_flutter(doc))
        return {
            "total": len(results),
            "results": results,
            "similar_media": results # compatibility fallback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================================
# ADMINISTRATIVE LIVE API CHANNELS & MEDIA CRUD (FOR ADMIN DASHBOARD)
# ==========================================================================

@app.get("/api/admin/media")
async def admin_get_all_media():
    cursor = movies_col.find()
    results = []
    async for doc in cursor:
        results.append(serialize_doc(doc))
    return results

@app.post("/api/admin/media")
async def admin_add_media(movie_data: dict):
    doc = await db_add_movie(movie_data)
    return {"success": True, "movie": doc}

@app.delete("/api/admin/media/{media_id}")
async def admin_delete_media(media_id: str):
    deleted = await db_delete_movie(media_id)
    return {"success": deleted}

@app.get("/api/admin/channels")
async def admin_get_channels():
    chans = await db_get_channels()
    return chans

@app.post("/api/admin/channels")
async def admin_add_channel(chan: dict):
    doc = await db_add_channel(chan)
    return {"success": True, "channel": doc}

@app.put("/api/admin/channels/{chan_id}/toggle")
async def admin_toggle_channel(chan_id: str):
    success = await db_toggle_channel(chan_id)
    return {"success": success}

@app.delete("/api/admin/channels/{chan_id}")
async def admin_delete_channel(chan_id: str):
    success = await db_delete_channel(chan_id)
    return {"success": success}

# ==========================================================================
# PROXY STREAMING SYSTEM (RE-ROUTING TG RANGE REQUESTS CHUNK-BY-CHUNK)
# ==========================================================================

@app.get("/stream/{channel_id}/{message_id}")
@app.get("/dl/{channel_id}/{message_id}")
async def stream_telegram_binary(channel_id: str, message_id: int, request: Request):
    """
    Streams the binary video payload directly from the Telegram message.
    Acts as a bridge/proxy server to bypass sandboxing blocks and support byte range seeks in standard player.
    """
    from bot import bot
    
    try:
        # Standardize channel Peer ID
        chat_id = channel_id.replace("@", "")
        if chat_id.isdigit():
            # If numerical ID, parse as integer
            chat_id = int(chat_id)
            if not str(chat_id).startswith("-100"):
                 chat_id = int(f"-100{chat_id}")
        else:
             chat_id = f"@{chat_id}"
             
        message = await bot.get_messages(chat_id, message_id)
        
        video = message.video or message.document
        if not video:
             raise HTTPException(status_code=404, detail="File media document not found in message.")
             
        size = video.file_size
        range_header = request.headers.get("range")
        
        # 1. Handle HTTP Seek Range Requests (Essential for Flutter Video Seek Playback)
        if range_header:
            range_bytes = range_header.replace("bytes=", "").split("-")
            start = int(range_bytes[0])
            end = int(range_bytes[1]) if range_bytes[1] else min(start + (4 * 1024 * 1024) - 1, size - 1) # 4MB Chunk seek
            chunksize = (end - start) + 1
            
            # Map byte starts to Pyrogram's 1MB chunk offsets
            chunk_size_bytes = 1024 * 1024
            start_chunk = start // chunk_size_bytes
            skip_bytes = start % chunk_size_bytes
            
            async def range_stream_generator():
                bytes_sent = 0
                async for chunk in bot.stream_media(message, offset=start_chunk):
                    if not chunk:
                        break
                    
                    # Align first chunk with the exact range start
                    if bytes_sent == 0 and skip_bytes > 0:
                        chunk = chunk[skip_bytes:]
                        
                    # Truncate to match exact requested content length
                    remaining = chunksize - bytes_sent
                    if len(chunk) > remaining:
                        chunk = chunk[:remaining]
                        
                    if not chunk:
                        break
                        
                    yield chunk
                    bytes_sent += len(chunk)
                    
                    if bytes_sent >= chunksize:
                        break
                        
            return StreamingResponse(
                range_stream_generator(),
                status_code=206,
                media_type=video.mime_type or "video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(chunksize),
                    "Content-Disposition": f'inline; filename="{video.file_name or "stream.mp4"}"'
                }
            )
        else:
            # Complete sequential download fallback using high-performance chunked streaming
            async def full_stream_generator():
                async for chunk in bot.stream_media(message):
                    yield chunk
            
            return StreamingResponse(
                full_stream_generator(),
                media_type=video.mime_type or "video/mp4",
                headers={
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(size),
                    "Content-Disposition": f'inline; filename="{video.file_name or "stream.mp4"}"'
                }
            )
    except Exception as e:
        logger.error(f"Binary stream proxy re-route failed for message {message_id} in {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy Streaming Error: {e}")


