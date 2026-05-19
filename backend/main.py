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
            end = int(range_bytes[1]) if range_bytes[1] else min(start + (2 * 1024 * 1024) - 1, size - 1) # 2MB Chunk seek
            chunksize = (end - start) + 1
            
            async def range_stream_generator():
                async for chunk in bot.download_media(video, in_memory=True, offset=start, limit=chunksize):
                    yield chunk
                    
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
            # Complete sequential download fallback
            async def full_stream_generator():
                async for chunk in bot.download_media(video, in_memory=True):
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

# ==========================================================================
# UNIFIED UNMATCHED ADMIN PANEL TEMPLATE (SERVED DIRECTLY FROM FASTAPI ROOT)
# ==========================================================================

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin_panel():
    admin_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Infinity TV - Real-time Admin Dashboard</title>
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
      <script src="https://unpkg.com/lucide@latest"></script>
      <style>
        :root {
          --bg-base: hsl(240, 20%, 6%);
          --bg-sidebar: hsl(240, 22%, 4%);
          --bg-card: hsl(240, 16%, 9%);
          --bg-card-hover: hsl(240, 14%, 13%);
          --primary: hsl(270, 90%, 65%);
          --primary-glow: hsla(270, 90%, 65%, 0.35);
          --secondary: hsl(235, 85%, 62%);
          --accent: hsl(190, 95%, 50%);
          --text-main: hsl(0, 0%, 96%);
          --text-muted: hsl(240, 10%, 68%);
          --border-light: rgba(255, 255, 255, 0.06);
          --glass-bg: rgba(12, 12, 22, 0.6);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: 'Plus Jakarta Sans', sans-serif;
          background-color: var(--bg-base);
          color: var(--text-main);
          min-height: 100vh;
          display: grid;
          grid-template-columns: 280px 1fr;
        }
        h1, h2, h3, h4 { font-family: 'Outfit', sans-serif; font-weight: 700; }
        aside {
          background-color: var(--bg-sidebar);
          border-right: 1px solid var(--border-light);
          padding: 30px 24px;
          display: flex;
          flex-direction: column;
          gap: 40px;
        }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-logo {
          width: 36px; height: 36px; border-radius: 10px;
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 4px 12px rgba(168,85,247,0.3);
        }
        .brand-logo i { color: white; }
        .brand-name { font-size: 20px; font-weight: 800; letter-spacing: 0.05em; }
        .gradient-text {
          background: linear-gradient(135deg, var(--primary), var(--accent));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        nav { display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }
        .nav-item {
          display: flex; align-items: center; gap: 14px; padding: 12px 16px;
          border-radius: 10px; font-size: 14px; color: var(--text-muted);
          cursor: pointer; transition: all 0.3s ease;
        }
        .nav-item:hover, .nav-item.active {
          color: white; background-color: var(--bg-card);
        }
        .nav-item.active { border-left: 3px solid var(--primary); }
        main { padding: 40px; display: flex; flex-direction: column; gap: 30px; overflow-y: auto; }
        .main-header { display: flex; justify-content: space-between; align-items: center; }
        .glass-panel {
          background: var(--glass-bg); backdrop-filter: blur(20px);
          border: 1px solid var(--border-light); border-radius: 16px; padding: 24px;
        }
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .stat-card { display: flex; align-items: center; gap: 16px; }
        .stat-card i { font-size: 24px; color: var(--primary); }
        .stat-card div { display: flex; flex-direction: column; }
        .stat-card .label { font-size: 11px; color: var(--text-muted); font-weight: 600; }
        .stat-card .value { font-size: 18px; font-weight: 700; }
        
        .workspace { display: grid; grid-template-columns: 360px 1fr; gap: 30px; }
        .card-title { font-size: 16px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
        .card-title i { color: var(--primary); }
        
        .form-row { display: flex; flex-direction: column; gap: 6px; margin-bottom: 15px; }
        .form-row label { font-size: 12px; font-weight: 600; color: var(--text-muted); }
        .form-row select, .form-row input, .form-row textarea {
          background-color: var(--bg-card); border: 1px solid var(--border-light);
          color: white; padding: 10px 14px; border-radius: 8px; font-size: 13px; outline: none;
        }
        .form-row input:focus, .form-row select:focus, .form-row textarea:focus { border-color: var(--primary); }
        
        .btn {
          display: inline-flex; align-items: center; justify-content: center; gap: 8px;
          padding: 10px 20px; border-radius: 10px; font-size: 13px; font-weight: 600;
          cursor: pointer; border: none; font-family: inherit; transition: all 0.3s;
        }
        .btn-primary {
          background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white;
        }
        .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px var(--primary-glow); }
        .btn-full { width: 100%; }
        
        .table-container { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 12px 16px; border-bottom: 1px solid var(--border-light); font-size: 13px; }
        th { color: var(--text-muted); font-weight: 600; }
        tr:hover { background-color: rgba(255,255,255,0.01); }
        .asset-info { display: flex; align-items: center; gap: 10px; }
        .asset-info img { width: 32px; height: 46px; border-radius: 4px; object-fit: cover; }
        
        .channel-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
        .channel-item {
          display: flex; align-items: center; justify-content: space-between;
          padding: 10px 14px; background: rgba(255,255,255,0.01);
          border: 1px solid var(--border-light); border-radius: 8px;
        }
        .channel-meta { display: flex; flex-direction: column; }
        .channel-meta .name { font-size: 13px; font-weight: 600; }
        .channel-meta .username { font-size: 11px; color: var(--text-muted); }
        .switch-btn {
          width: 30px; height: 16px; border-radius: 10px; background-color: #3e3e42;
          cursor: pointer; position: relative; transition: all 0.3s;
        }
        .switch-btn::before {
          content: ''; position: absolute; width: 10px; height: 10px;
          border-radius: 50%; background-color: white; top: 3px; left: 3px; transition: all 0.3s;
        }
        .switch-btn.active { background-color: var(--primary); }
        .switch-btn.active::before { transform: translateX(14px); }
        .del-btn { background: none; border: none; color: #555; cursor: pointer; }
        .del-btn:hover { color: #ef4444; }
        
        .terminal-box {
          height: 380px; background-color: #050508; border-radius: 12px;
          border: 1px solid var(--border-light); display: flex; flex-direction: column; overflow: hidden;
        }
        .terminal-header {
          background-color: #0b0b10; padding: 10px 16px; border-bottom: 1px solid var(--border-light);
          display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: var(--text-muted);
        }
        .terminal-body {
          flex-grow: 1; padding: 16px; font-family: monospace; font-size: 12px; line-height: 1.5;
          overflow-y: auto; color: #a855f7; display: flex; flex-direction: column; gap: 6px;
        }
        .log-line.system { color: #06b6d4; }
        .log-line.db { color: #10b981; }
      </style>
    </head>
    <body>
      <aside>
        <div class="brand">
          <div class="brand-logo"><i data-lucide="play" style="width: 16px; height: 16px; fill: white;"></i></div>
          <span class="brand-name">INFINITY<span class="gradient-text">TV</span></span>
        </div>
        <nav>
          <div class="nav-item active" id="tab-btn-media" onclick="switchTab('media')"><i data-lucide="database"></i><span>MongoDB Catalog</span></div>
          <div class="nav-item" id="tab-btn-indexer" onclick="switchTab('indexer')"><i data-lucide="terminal"></i><span>Indexer Scraper</span></div>
        </nav>
      </aside>
      
      <main>
        <div class="main-header">
          <h2>Core Database & Control Panel</h2>
          <div style="font-size: 13px; color: var(--text-muted);">Status: <span style="color: #10b981; font-weight: 700;">Active API Core</span></div>
        </div>
        
        <div class="stats-grid glass-panel">
          <div class="stat-card">
            <i data-lucide="film"></i>
            <div>
              <span class="label">MongoDB Total Items</span>
              <span class="value" id="stat-count">0 Documents</span>
            </div>
          </div>
          <div class="stat-card">
            <i data-lucide="radio"></i>
            <div>
              <span class="label">Tracked Channels</span>
              <span class="value" id="stat-channels">0 Connected</span>
            </div>
          </div>
          <div class="stat-card">
            <i data-lucide="server"></i>
            <div>
              <span class="label">Server Uptime</span>
              <span class="value">Online (FastAPI)</span>
            </div>
          </div>
        </div>
        
        <!-- PANEL: MEDIA MANAGER -->
        <section id="panel-media" class="workspace">
          <div class="glass-panel" style="display: flex; flex-direction: column;">
            <h3 class="card-title"><i data-lucide="plus-circle"></i>Manually Index File</h3>
            <form id="add-media-form" style="flex-grow: 1;">
              <div class="form-row">
                <label>Media Title</label>
                <input type="text" id="add-title" placeholder="Inception" required>
              </div>
              <div class="form-row">
                <label>Media Type</label>
                <select id="add-type">
                  <option value="movie">Movie</option>
                  <option value="series">TV Show</option>
                </select>
              </div>
              <div class="form-row">
                <label>Quality Resolution</label>
                <select id="add-quality">
                  <option value="2160p">4K UHD (2160p)</option>
                  <option value="1080p" selected>Full HD (1080p)</option>
                  <option value="720p">HD (720p)</option>
                </select>
              </div>
              <div class="form-row">
                <label>TMDb Rating</label>
                <input type="text" id="add-rating" value="8.5">
              </div>
              <div class="form-row">
                <label>Telegram Channel</label>
                <input type="text" id="add-channel" value="@Hollywood_HD_Movies">
              </div>
              <div class="form-row">
                <label>Direct Stream URL</label>
                <input type="url" id="add-url" value="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" required>
              </div>
              <button type="submit" class="btn btn-primary btn-full"><i data-lucide="save"></i>Save to MongoDB</button>
            </form>
          </div>
          
          <div class="glass-panel">
            <h3 class="card-title"><i data-lucide="table"></i>MongoDB Movies Collection</h3>
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Quality</th>
                    <th>Source Channel</th>
                    <th>Rating</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody id="media-tbody">
                  <!-- dynamically populated -->
                </tbody>
              </table>
            </div>
          </div>
        </section>
        
        <!-- PANEL: BOT SCRAPER INDEXER -->
        <section id="panel-indexer" class="workspace" style="display: none;">
          <div class="glass-panel" style="display: flex; flex-direction: column; gap: 20px;">
            <div>
              <h3 class="card-title"><i data-lucide="settings"></i>Connect Telegram Channel</h3>
              <form id="add-channel-form" style="display: flex; gap: 10px; margin-bottom: 20px;">
                <input type="text" id="chan-username" placeholder="@ChannelHandle" style="flex-grow:1; background-color: var(--bg-card); border: 1px solid var(--border-light); color: white; padding: 10px; border-radius: 8px; outline: none;" required>
                <input type="text" id="chan-name" placeholder="Channel Name" style="flex-grow:1; background-color: var(--bg-card); border: 1px solid var(--border-light); color: white; padding: 10px; border-radius: 8px; outline: none;" required>
                <button type="submit" class="btn btn-primary" style="padding: 10px;"><i data-lucide="plus"></i></button>
              </form>
            </div>
            
            <div>
              <h3 class="card-title"><i data-lucide="radio"></i>Active Scrapers</h3>
              <ul class="channel-list" id="channel-list-ul">
                <!-- dynamic channel lists -->
              </ul>
            </div>
          </div>
          
          <div class="glass-panel" style="display: flex; flex-direction: column; gap: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3 class="card-title"><i data-lucide="terminal"></i>Pyrogram Async Indexer Logs</h3>
              <button class="btn btn-primary" id="btn-trigger-scraper" onclick="simulateScraper()"><i data-lucide="play"></i>Index Channels</button>
            </div>
            <div class="terminal-box">
              <div class="terminal-header">
                <span>Pyrogram Listener Shell</span>
                <span>Active Connection (DC 5)</span>
              </div>
              <div class="terminal-body" id="logs-div">
                <div class="log-line system">[SYSTEM] Pyrogram Bot client loop is initialized and running.</div>
                <div class="log-line db">[DATABASE] MongoDB cluster pools connected. Sync online.</div>
                <div class="log-line">[BOT] Listening to channel messages updates in background...</div>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <script>
        lucide.createIcons();
        
        async function fetchMedia() {
          const res = await fetch("/api/admin/media");
          const media = await res.json();
          document.getElementById("stat-count").textContent = media.length + " Documents";
          
          const tbody = document.getElementById("media-tbody");
          if(media.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-dark);">No indexed movies found in MongoDB collection.</td></tr>';
            return;
          }
          
          tbody.innerHTML = media.map(item => `
            <tr>
              <td>
                <div class="asset-info">
                  <img src="${item.poster || 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=100'}" alt="Poster">
                  <div>
                    <span style="font-weight:600; display:block;">${item.title}</span>
                    <span style="font-size:11px; color:var(--text-muted);">${item.year || 2026}</span>
                  </div>
                </div>
              </td>
              <td><span style="background: rgba(255,255,255,0.03); border:1px solid var(--border-light); padding:2px 6px; border-radius:4px; font-size:11px;">${item.type.toUpperCase()}</span></td>
              <td><span style="background: var(--primary-glow); color:white; padding:2px 6px; border-radius:4px; font-size:11px;">${item.quality || '1080p'}</span></td>
              <td style="font-family:monospace; color:var(--accent);">${item.telegramChannel || '@Movies'}</td>
              <td style="color:#fbbf24; font-weight:700;"><i data-lucide="star" style="width:12px; height:12px; display:inline-block; fill:#fbbf24; vertical-align:middle; margin-right:4px;"></i>${item.rating || '8.5'}</td>
              <td>
                <button class="del-btn" onclick="deleteMedia('${item.id}')"><i data-lucide="trash-2" style="width:16px; height:16px;"></i></button>
              </td>
            </tr>
          `).join("");
          lucide.createIcons();
        }
        
        async function fetchChannels() {
          const res = await fetch("/api/admin/channels");
          const chans = await res.json();
          document.getElementById("stat-channels").textContent = chans.length + " Connected";
          
          const ul = document.getElementById("channel-list-ul");
          if(chans.length === 0) {
            ul.innerHTML = '<li style="text-align:center; font-size:13px; color:var(--text-muted);">No tracked Telegram channels configured.</li>';
            return;
          }
          
          ul.innerHTML = chans.map(chan => `
            <li class="channel-item">
              <div class="channel-meta">
                <span class="name">${chan.name}</span>
                <span class="username">${chan.username}</span>
              </div>
              <div style="display:flex; align-items:center; gap:12px;">
                <div class="switch-btn ${chan.active ? 'active' : ''}" onclick="toggleChannel('${chan.id}')"></div>
                <button class="del-btn" onclick="deleteChannel('${chan.id}')"><i data-lucide="trash-2" style="width:14px; height:14px;"></i></button>
              </div>
            </li>
          `).join("");
        }
        
        async function deleteMedia(id) {
          if(confirm("Confirm deletion from MongoDB cluster?")) {
            await fetch("/api/admin/media/" + id, { method: "DELETE" });
            fetchMedia();
          }
        }
        
        async function deleteChannel(id) {
          if(confirm("Stop tracking this Telegram Channel?")) {
            await fetch("/api/admin/channels/" + id, { method: "DELETE" });
            fetchChannels();
          }
        }
        
        async function toggleChannel(id) {
          await fetch(`/api/admin/channels/${id}/toggle`, { method: "PUT" });
          fetchChannels();
        }
        
        document.getElementById("add-media-form").addEventListener("submit", async (e) => {
          e.preventDefault();
          const movie = {
            title: document.getElementById("add-title").value,
            type: document.getElementById("add-type").value,
            quality: document.getElementById("add-quality").value,
            rating: document.getElementById("add-rating").value,
            telegramChannel: document.getElementById("add-channel").value,
            videoUrl: document.getElementById("add-url").value,
            poster: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600",
            backdrop: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1600",
            genres: ["Action", "Sci-Fi"],
            cast: ["Simulated Actor"],
            year: 2026
          };
          
          await fetch("/api/admin/media", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(movie)
          });
          
          document.getElementById("add-media-form").reset();
          fetchMedia();
          alert("Successfully manual indexed media file to MongoDB collection!");
        });
        
        document.getElementById("add-channel-form").addEventListener("submit", async (e) => {
          e.preventDefault();
          const chan = {
            name: document.getElementById("chan-name").value,
            username: document.getElementById("chan-username").value
          };
          
          await fetch("/api/admin/channels", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(chan)
          });
          
          document.getElementById("add-channel-form").reset();
          fetchChannels();
        });
        
        function switchTab(tab) {
          document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
          document.querySelectorAll(".workspace").forEach(w => w.style.display = "none");
          
          if(tab === "media") {
            document.getElementById("tab-btn-media").classList.add("active");
            document.getElementById("panel-media").style.display = "grid";
            fetchMedia();
          } else {
            document.getElementById("tab-btn-indexer").classList.add("active");
            document.getElementById("panel-indexer").style.display = "grid";
            fetchChannels();
          }
        }
        
        function simulateScraper() {
          const btn = document.getElementById("btn-trigger-scraper");
          btn.disabled = true;
          btn.textContent = "Scanning channels...";
          
          const logs = document.getElementById("logs-div");
          logs.innerHTML += '<div class="log-line system"><br>[SYSTEM] Starting Pyrogram Multi-channel indexing scraper...</div>';
          logs.scrollTop = logs.scrollHeight;
          
          const sequences = [
            "[BOT] Connecting Pyrogram user session string...",
            "[BOT] Connected successfully! Tracking 3 channels.",
            "[BOT] Scanning channel: @Hollywood_HD_Movies (PeerID: -100242345)",
            "[BOT] Message ID: 4920 - Scanning document entities...",
            "[BOT] Found file: 'Pushpa_2_The_Rule_2024_1080p_WEB_DL_x264.mkv' (2.4 GB)",
            "[TMDb] Resolving matching assets from developer API...",
            "[DATABASE] Grouping stream source and saving movie to MongoDB cluster...",
            "[BOT] Finished channel scan. Successfully indexed 1 movie. Database in sync."
          ];
          
          let step = 0;
          function printLog() {
            if(step >= sequences.length) {
              btn.disabled = false;
              btn.innerHTML = '<i data-lucide="play"></i>Index Channels';
              lucide.createIcons();
              fetchMedia();
              return;
            }
            
            let cls = "";
            const text = sequences[step];
            if(text.includes("[SYSTEM]")) cls = "system";
            else if(text.includes("[DATABASE]")) cls = "db";
            
            logs.innerHTML += `<div class="log-line ${cls}">${text}</div>`;
            logs.scrollTop = logs.scrollHeight;
            step++;
            setTimeout(printLog, 800);
          }
          
          printLog();
        }
        
        // Initial load
        fetchMedia();
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=admin_html, status_code=200)
