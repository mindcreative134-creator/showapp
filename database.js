// Production MongoDB API Base URL
const API_BASE_URL = "https://showapp-y1nd.onrender.com";

// Default empty arrays (No mock data allowed by default)
const DEFAULT_MOVIES = [];
const DEFAULT_CHANNELS = [];

// Initialize LocalStorage database helper synced with live MongoDB Core API
class ShowAppDatabase {
  constructor() {
    if (!localStorage.getItem("showapp_movies")) {
      localStorage.setItem("showapp_movies", JSON.stringify(DEFAULT_MOVIES));
    }
    if (!localStorage.getItem("showapp_channels")) {
      localStorage.setItem("showapp_channels", JSON.stringify(DEFAULT_CHANNELS));
    }
    if (!localStorage.getItem("showapp_watchlist")) {
      localStorage.setItem("showapp_watchlist", JSON.stringify([]));
    }
    if (!localStorage.getItem("showapp_history")) {
      localStorage.setItem("showapp_history", JSON.stringify([]));
    }
  }

  /**
   * Synchronizes local storage caches with live MongoDB database collections
   */
  async syncFromBackend() {
    try {
      console.log("[SYNC] Synchronizing UI state with MongoDB backend...");
      
      // 1. Fetch movies/shows from MongoDB
      const resMedia = await fetch(`${API_BASE_URL}/api/admin/media`);
      if (resMedia.ok) {
        const media = await resMedia.json();
        localStorage.setItem("showapp_movies", JSON.stringify(media));
        console.log(`[SYNC] Mapped ${media.length} media records from MongoDB collection.`);
      }

      // 2. Fetch tracked channels from MongoDB
      const resChans = await fetch(`${API_BASE_URL}/api/admin/channels`);
      if (resChans.ok) {
        const chans = await resChans.json();
        localStorage.setItem("showapp_channels", JSON.stringify(chans));
        console.log(`[SYNC] Mapped ${chans.length} active Telegram channels from MongoDB.`);
      }
    } catch (e) {
      console.error("[SYNC] Cloud synchronization failed. Operating in offline mode:", e);
    }
  }

  getMovies() {
    return JSON.parse(localStorage.getItem("showapp_movies")) || [];
  }

  saveMovies(movies) {
    localStorage.setItem("showapp_movies", JSON.stringify(movies));
  }

  async addMovie(movie) {
    try {
      console.log(`[MONGODB] Adding manual indexed asset: '${movie.title}'...`);
      const res = await fetch(`${API_BASE_URL}/api/admin/media`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(movie)
      });
      if (res.ok) {
        const data = await res.json();
        await this.syncFromBackend();
        return data.movie;
      }
    } catch (e) {
      console.error("[MONGODB] Failed to write media asset to MongoDB:", e);
    }
    return null;
  }

  async deleteMovie(id) {
    try {
      console.log(`[MONGODB] Deleting movie asset: ${id}...`);
      const res = await fetch(`${API_BASE_URL}/api/admin/media/${id}`, {
        method: "DELETE"
      });
      if (res.ok) {
        await this.syncFromBackend();
        return true;
      }
    } catch (e) {
      console.error("[MONGODB] Failed to delete media asset from MongoDB:", e);
    }
    return false;
  }

  getChannels() {
    return JSON.parse(localStorage.getItem("showapp_channels")) || [];
  }

  saveChannels(channels) {
    localStorage.setItem("showapp_channels", JSON.stringify(channels));
  }

  async addChannel(chan) {
    try {
      console.log(`[MONGODB] Connecting tracked channel: '${chan.username}'...`);
      const res = await fetch(`${API_BASE_URL}/api/admin/channels`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(chan)
      });
      if (res.ok) {
        await this.syncFromBackend();
        return true;
      }
    } catch (e) {
      console.error("[MONGODB] Failed to add tracked channel to MongoDB:", e);
    }
    return false;
  }

  async toggleChannel(id) {
    try {
      console.log(`[MONGODB] Toggling active status for channel: ${id}...`);
      const res = await fetch(`${API_BASE_URL}/api/admin/channels/${id}/toggle`, {
        method: "PUT"
      });
      if (res.ok) {
        await this.syncFromBackend();
        return true;
      }
    } catch (e) {
      console.error("[MONGODB] Failed to toggle channel status:", e);
    }
    return false;
  }

  async deleteChannel(id) {
    try {
      console.log(`[MONGODB] Disconnecting tracked channel: ${id}...`);
      const res = await fetch(`${API_BASE_URL}/api/admin/channels/${id}`, {
        method: "DELETE"
      });
      if (res.ok) {
        await this.syncFromBackend();
        return true;
      }
    } catch (e) {
      console.error("[MONGODB] Failed to delete tracked channel from MongoDB:", e);
    }
    return false;
  }

  getWatchlist() {
    return JSON.parse(localStorage.getItem("showapp_watchlist")) || [];
  }

  toggleWatchlist(movieId) {
    let list = this.getWatchlist();
    const idx = list.indexOf(movieId);
    if (idx === -1) {
      list.push(movieId);
    } else {
      list.splice(idx, 1);
    }
    localStorage.setItem("showapp_watchlist", JSON.stringify(list));
    return idx === -1; // returns true if added, false if removed
  }

  getHistory() {
    return JSON.parse(localStorage.getItem("showapp_history")) || [];
  }

  updateHistory(movieId, time, duration, title, poster) {
    let history = this.getHistory();
    history = history.filter(h => h.movieId !== movieId);
    const progress = Math.min(100, Math.floor((time / duration) * 100)) || 0;
    
    history.unshift({
      movieId,
      title,
      poster,
      time,
      duration,
      progress,
      updatedAt: Date.now()
    });

    if (history.length > 10) history.pop();
    localStorage.setItem("showapp_history", JSON.stringify(history));
  }

  clearHistoryItem(movieId) {
    let history = this.getHistory();
    history = history.filter(h => h.movieId !== movieId);
    localStorage.setItem("showapp_history", JSON.stringify(history));
  }
}

const showAppDB = new ShowAppDatabase();
