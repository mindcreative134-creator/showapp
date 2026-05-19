// Initialize Lucide Icons
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  showApp.init();
});

class ShowApp {
  constructor() {
    this.currentFilter = "all";
    this.selectedMovie = null;
    this.selectedSeason = 1;
    
    // Scraper Simulation Status
    this.isScraping = false;
    this.scrapeLogTimer = null;
  }

  async init() {
    // Synchronize data directly from live MongoDB Cloud instance
    await showAppDB.syncFromBackend();

    // Render initial contents
    this.renderHome();
    this.renderSearchCatalog();
    this.renderAdminTable();
    this.renderAdminChannels();
    this.populateSelectOptions();
    this.updateGlobalWatchlistStats();

    // Event Bindings
    this.bindNavigation();
    this.bindSearch();
    this.bindModals();
    this.bindForms();
    this.bindPlayer();

    // Load featured Hero banner
    this.loadHeroFeatured();
  }

  // ==========================================================================
  // TAB NAVIGATION & UTILS
  // ==========================================================================

  bindNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const panels = document.querySelectorAll(".tab-panel");

    navItems.forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.getAttribute("data-tab");

        // Set active class in sidebar
        navItems.forEach(n => n.classList.remove("active"));
        item.classList.add("active");

        // Show matching panel
        panels.forEach(panel => {
          panel.classList.remove("active");
          if (panel.id === `tab-${tab}`) {
            panel.classList.add("active");
          }
        });

        // Trigger contextual rendering
        if (tab === "home") {
          this.renderHome();
        } else if (tab === "search-tab") {
          this.renderSearchCatalog();
        } else if (tab === "admin") {
          this.renderAdminTable();
          this.renderAdminChannels();
        } else if (tab === "watchlist-tab") {
          this.renderWatchlist();
        }
      });
    });

    // Categories filter tabs (Home)
    const categoryBtns = document.querySelectorAll(".category-tabs .tab-btn");
    categoryBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        categoryBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.currentFilter = btn.getAttribute("data-filter");
        this.renderHome(this.currentFilter);
      });
    });
  }

  updateGlobalWatchlistStats() {
    const watchlist = showAppDB.getWatchlist();
    document.getElementById("watchlist-count").textContent = watchlist.length;
  }

  populateSelectOptions() {
    const channels = showAppDB.getChannels();
    
    // Scraper selection dropdown
    const scrapeSelect = document.getElementById("scrape-channel");
    scrapeSelect.innerHTML = channels.map(c => 
      `<option value="${c.username}">${c.name} (${c.username})</option>`
    ).join("");

    // Filter dropdown in search
    const filterSelect = document.getElementById("filter-channel");
    filterSelect.innerHTML = `<option value="all">All Channels</option>` + channels.map(c => 
      `<option value="${c.username}">${c.name}</option>`
    ).join("");
  }

  // ==========================================================================
  // RENDER DYNAMIC UI CAROUSELS / GRIDS
  // ==========================================================================

  loadHeroFeatured() {
    const movies = showAppDB.getMovies().filter(m => m.type === "movie");
    if (movies.length === 0) return;
    
    // Choose first as featured
    const featured = movies[0];
    
    const banner = document.getElementById("hero-showcase");
    banner.style.backgroundImage = `url('${featured.backdrop}')`;
    
    document.getElementById("hero-title").textContent = featured.title;
    document.getElementById("hero-desc").textContent = featured.description;
    document.getElementById("hero-rating").textContent = featured.rating;
    document.getElementById("hero-quality").textContent = featured.quality + " Source";

    // Play action
    const playBtn = document.getElementById("hero-play-btn");
    playBtn.onclick = () => this.startPlayer(featured.title, featured.videoUrl, featured.id);

    // Watchlist action
    const wlBtn = document.getElementById("hero-watchlist-btn");
    const watchlist = showAppDB.getWatchlist();
    const isInWatchlist = watchlist.includes(featured.id);
    wlBtn.innerHTML = isInWatchlist 
      ? `<i data-lucide="bookmark-check"></i> In Watchlist` 
      : `<i data-lucide="bookmark-plus"></i> Add Watchlist`;
    lucide.createIcons({attrs: {class: "lucide"}});

    wlBtn.onclick = () => {
      const added = showAppDB.toggleWatchlist(featured.id);
      wlBtn.innerHTML = added 
        ? `<i data-lucide="bookmark-check"></i> In Watchlist` 
        : `<i data-lucide="bookmark-plus"></i> Add Watchlist`;
      lucide.createIcons({attrs: {class: "lucide"}});
      this.updateGlobalWatchlistStats();
    };

    // Details action
    document.getElementById("hero-info-btn").onclick = () => this.openModal(featured.id);
  }

  renderHome(filter = "all") {
    let movies = showAppDB.getMovies();
    if (filter !== "all") {
      movies = movies.filter(m => m.type === filter);
    }

    // Continue Watching Row
    this.renderContinueWatching();

    // 1. Trending Blockbusters
    const trendingList = movies.filter(m => m.type === "movie").sort((a,b) => parseFloat(b.rating) - parseFloat(a.rating));
    this.renderCarousel("trending-movies-carousel", trendingList);

    // 2. TV Shows Row
    const tvList = movies.filter(m => m.type === "series");
    this.renderCarousel("tv-shows-carousel", tvList);

    // 3. Anime spotlight
    const animeList = movies.filter(m => m.type === "anime");
    this.renderCarousel("anime-carousel", animeList);
  }

  renderCarousel(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (items.length === 0) {
      container.innerHTML = `<div class="empty-row-msg">No indexed media files available in this category yet.</div>`;
      return;
    }

    container.innerHTML = items.map(item => `
      <div class="media-card" onclick="showApp.openModal('${item.id}')">
        <img src="${item.poster}" alt="${item.title}" class="media-card-poster" loading="lazy">
        <div class="media-card-overlay">
          <h4 class="media-card-title">${item.title}</h4>
          <div class="media-card-meta">
            <span class="media-card-rating">
              <i data-lucide="star"></i> ${item.rating}
            </span>
            <span class="quality-badge">${item.quality}</span>
          </div>
        </div>
      </div>
    `).join("");

    lucide.createIcons();
  }

  renderContinueWatching() {
    const section = document.getElementById("continue-watching-section");
    const carousel = document.getElementById("continue-watching-carousel");
    const history = showAppDB.getHistory();

    if (!history || history.length === 0) {
      section.style.display = "none";
      return;
    }

    section.style.display = "flex";
    carousel.innerHTML = history.map(item => `
      <div class="history-card" onclick="showApp.resumePlayback('${item.movieId}', ${item.time})">
        <img src="${item.poster}" class="history-card-img">
        <div class="history-card-btn">
          <i data-lucide="play"></i>
        </div>
        <div class="history-details">
          <span class="history-title">${item.title}</span>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: ${item.progress}%"></div>
          </div>
        </div>
      </div>
    `).join("");

    lucide.createIcons();
  }

  resumePlayback(movieId, time) {
    const movie = showAppDB.getMovies().find(m => m.id === movieId);
    if (movie) {
      this.startPlayer(movie.title, movie.videoUrl, movie.id, time);
    }
  }

  renderWatchlist() {
    const watchlistIds = showAppDB.getWatchlist();
    const movies = showAppDB.getMovies().filter(m => watchlistIds.includes(m.id));
    const container = document.getElementById("watchlist-results-grid");
    const sub = document.getElementById("watchlist-subtitle");

    sub.textContent = `You have saved ${movies.length} movies/TV shows to index stream`;

    if (movies.length === 0) {
      container.innerHTML = `
        <div class="empty-state-box" style="grid-column: 1/-1; text-align: center; padding: 50px 0; color: var(--text-muted)">
          <i data-lucide="bookmark" style="width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
          <h3>Watchlist is Empty</h3>
          <p>Browse Home catalog and bookmark media titles to stream later.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    container.innerHTML = movies.map(item => `
      <div class="media-card" onclick="showApp.openModal('${item.id}')">
        <img src="${item.poster}" alt="${item.title}" class="media-card-poster">
        <div class="media-card-overlay">
          <h4 class="media-card-title">${item.title}</h4>
          <div class="media-card-meta">
            <span class="media-card-rating">
              <i data-lucide="star"></i> ${item.rating}
            </span>
            <span class="quality-badge">${item.quality}</span>
          </div>
        </div>
      </div>
    `).join("");

    lucide.createIcons();
  }

  // ==========================================================================
  // MAIN SEARCH ENGINE (INSTANT MULTI-KEY SEARCH)
  // ==========================================================================

  bindSearch() {
    const globalSearch = document.getElementById("global-search");
    const clearBtn = document.getElementById("clear-search-btn");

    globalSearch.addEventListener("input", (e) => {
      const q = e.target.value.trim();
      if (q.length > 0) {
        clearBtn.style.display = "flex";
      } else {
        clearBtn.style.display = "none";
      }
      
      // Auto switch to Search Tab if typed while in another tab
      const activeTab = document.querySelector(".nav-item.active").getAttribute("data-tab");
      if (activeTab !== "search-tab" && q.length > 0) {
        document.querySelector(".nav-item[data-tab='search-tab']").click();
      }

      this.renderSearchCatalog(q);
    });

    clearBtn.addEventListener("click", () => {
      globalSearch.value = "";
      clearBtn.style.display = "none";
      this.renderSearchCatalog();
    });

    // Dropdown filters
    document.getElementById("filter-quality").addEventListener("change", () => this.renderSearchCatalog(globalSearch.value));
    document.getElementById("filter-channel").addEventListener("change", () => this.renderSearchCatalog(globalSearch.value));
  }

  renderSearchCatalog(query = "") {
    const movies = showAppDB.getMovies();
    const qualityFilter = document.getElementById("filter-quality").value;
    const channelFilter = document.getElementById("filter-channel").value;

    let filtered = movies;

    // Apply text matching search (Title, genres, year, cast, channel, description, or telegram message id)
    if (query.trim() !== "") {
      const q = query.toLowerCase();
      filtered = filtered.filter(m => 
        m.title.toLowerCase().includes(q) ||
        m.genres.some(g => g.toLowerCase().includes(q)) ||
        m.year.includes(q) ||
        m.quality.toLowerCase().includes(q) ||
        m.telegramChannel.toLowerCase().includes(q) ||
        m.cast.some(actor => actor.toLowerCase().includes(q)) ||
        (m.messageId && m.messageId.toString() === q)
      );
    }

    // Apply select drop filters
    if (qualityFilter !== "all") {
      filtered = filtered.filter(m => m.quality === qualityFilter);
    }
    if (channelFilter !== "all") {
      filtered = filtered.filter(m => m.telegramChannel === channelFilter);
    }

    // Update Counter
    document.getElementById("search-result-count").textContent = `Found ${filtered.length} indexed media files across connected channels`;

    const grid = document.getElementById("search-results-grid");
    
    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="empty-state-box" style="grid-column: 1/-1; text-align: center; padding: 60px 0; color: var(--text-muted);">
          <i data-lucide="search-x" style="width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
          <h3>No matches found</h3>
          <p>Try searching different terms or clearing filters.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    grid.innerHTML = filtered.map(item => `
      <div class="media-card" onclick="showApp.openModal('${item.id}')">
        <img src="${item.poster}" alt="${item.title}" class="media-card-poster">
        <div class="media-card-overlay">
          <h4 class="media-card-title">${item.title}</h4>
          <div class="media-card-meta">
            <span class="media-card-rating">
              <i data-lucide="star"></i> ${item.rating}
            </span>
            <span class="quality-badge">${item.quality}</span>
          </div>
        </div>
      </div>
    `).join("");

    lucide.createIcons();
  }

  // ==========================================================================
  // DETAILED MODAL VIEWER
  // ==========================================================================

  bindModals() {
    const modal = document.getElementById("media-modal");
    const closeBtn = document.getElementById("media-modal-close");

    // Close on click close btn
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });

    // Close on click backdrop
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });

    // Season change dropdown for series
    const seasonSelect = document.getElementById("modal-season-select");
    seasonSelect.addEventListener("change", (e) => {
      this.selectedSeason = parseInt(e.target.value);
      this.renderEpisodes(this.selectedMovie, this.selectedSeason);
    });
  }

  openModal(movieId) {
    const movie = showAppDB.getMovies().find(m => m.id === movieId);
    if (!movie) return;

    this.selectedMovie = movie;
    this.selectedSeason = 1;

    const modal = document.getElementById("media-modal");
    
    // Set text contents
    document.getElementById("modal-hero-bg").style.backgroundImage = `url('${movie.backdrop}')`;
    document.getElementById("modal-poster").src = movie.poster;
    document.getElementById("modal-title").textContent = movie.title;
    document.getElementById("modal-rating").textContent = movie.rating;
    document.getElementById("modal-year").textContent = movie.year;
    document.getElementById("modal-desc").textContent = movie.description;
    document.getElementById("modal-genres").textContent = movie.genres.join(", ");
    document.getElementById("modal-cast").textContent = movie.cast.join(", ");

    // Type tags styling
    document.getElementById("modal-type-badge").textContent = movie.type.toUpperCase();
    document.getElementById("modal-quality-badge").textContent = movie.quality;

    // Telegram details
    document.getElementById("meta-telegram-channel").textContent = movie.telegramChannel;
    document.getElementById("meta-telegram-msgid").textContent = movie.messageId || "N/A";
    document.getElementById("meta-telegram-size").textContent = movie.fileSize || "1.4 GB";

    const dlLink = document.getElementById("meta-telegram-link");
    dlLink.href = `https://t.me/${movie.telegramChannel.substring(1)}/${movie.messageId || 1}`;
    
    const dlBtn = document.getElementById("modal-download-btn");
    dlBtn.href = movie.videoUrl;

    // Display TV controls / Season controls if series
    const moviePlayContainer = document.getElementById("movie-play-container");
    const tvSelectorContainer = document.getElementById("tv-series-episodes-container");

    if (movie.type === "series") {
      moviePlayContainer.style.display = "none";
      tvSelectorContainer.style.display = "flex";

      // Render season dropdown options
      const seasonSelect = document.getElementById("modal-season-select");
      seasonSelect.innerHTML = movie.seasons.map(s => 
        `<option value="${s.seasonNumber}">Season ${s.seasonNumber}</option>`
      ).join("");

      this.renderEpisodes(movie, 1);
    } else {
      moviePlayContainer.style.display = "block";
      tvSelectorContainer.style.display = "none";

      // Bind plain movie play trigger
      document.getElementById("modal-play-btn").onclick = () => {
        modal.style.display = "none";
        this.startPlayer(movie.title, movie.videoUrl, movie.id);
      };
    }

    // Bookmark Toggle button logic
    const wlBtn = document.getElementById("modal-watchlist-toggle-btn");
    this.updateModalWatchlistBtn(movie.id, wlBtn);

    wlBtn.onclick = () => {
      showAppDB.toggleWatchlist(movie.id);
      this.updateModalWatchlistBtn(movie.id, wlBtn);
      this.updateGlobalWatchlistStats();
    };

    // Show modal
    modal.style.display = "flex";
    lucide.createIcons();
  }

  updateModalWatchlistBtn(movieId, btn) {
    const list = showAppDB.getWatchlist();
    const isBookmarked = list.includes(movieId);
    
    btn.innerHTML = isBookmarked 
      ? `<i data-lucide="bookmark-minus"></i> Remove Watchlist` 
      : `<i data-lucide="bookmark-plus"></i> Add to Watchlist`;
    
    if (isBookmarked) {
      btn.classList.add("btn-glass");
      btn.classList.remove("btn-secondary");
    } else {
      btn.classList.add("btn-secondary");
      btn.classList.remove("btn-glass");
    }
    lucide.createIcons({attrs: {class: "lucide"}});
  }

  renderEpisodes(movie, seasonNum) {
    const list = document.getElementById("modal-episode-list");
    const season = movie.seasons.find(s => s.seasonNumber === seasonNum);
    
    if (!season || !season.episodes || season.episodes.length === 0) {
      list.innerHTML = `<li class="episode-item">No episodes found.</li>`;
      return;
    }

    list.innerHTML = season.episodes.map(ep => `
      <li class="episode-item" onclick="showApp.playEpisode('${movie.title}', 'Season ${seasonNum} Ep ${ep.episodeNumber}: ${ep.title}', '${ep.videoUrl}', '${movie.id}')">
        <div class="episode-left">
          <span class="episode-num">E${ep.episodeNumber}</span>
          <span class="episode-title">${ep.title}</span>
        </div>
        <i data-lucide="play" style="width: 14px; height: 14px; fill: white"></i>
      </li>
    `).join("");
    
    lucide.createIcons();
  }

  playEpisode(seriesTitle, epFullTitle, videoUrl, movieId) {
    document.getElementById("media-modal").style.display = "none";
    this.startPlayer(`${seriesTitle} - ${epFullTitle}`, videoUrl, movieId);
  }

  // ==========================================================================
  // CUSTOM ADVANCED STREAMING VIDEO PLAYER CONTROLS
  // ==========================================================================

  bindPlayer() {
    const video = document.getElementById("stream-video");
    const playBtn = document.getElementById("play-pause-btn");
    const muteBtn = document.getElementById("mute-btn");
    const speedToggle = document.getElementById("speed-toggle");
    const speedMenu = document.getElementById("speed-menu");
    const qualityToggle = document.getElementById("quality-toggle");
    const qualityMenu = document.getElementById("quality-menu");
    const fullscreenBtn = document.getElementById("fullscreen-btn");
    const closeBtn = document.getElementById("player-close-btn");

    // Close Player overlay
    closeBtn.addEventListener("click", () => {
      this.closePlayer();
    });

    // Play/Pause toggler
    playBtn.addEventListener("click", () => this.togglePlay());
    video.addEventListener("click", () => this.togglePlay());

    // Update Progress
    video.addEventListener("timeupdate", () => this.updatePlayerProgress());
    video.addEventListener("loadedmetadata", () => {
      document.getElementById("time-duration").textContent = this.formatTime(video.duration);
    });

    // Seek Timeline
    const timeline = document.getElementById("timeline-container");
    timeline.addEventListener("click", (e) => {
      const rect = timeline.getBoundingClientRect();
      const pos = (e.clientX - rect.left) / rect.width;
      video.currentTime = pos * video.duration;
    });

    // Skip Buttons
    document.getElementById("rewind-btn").addEventListener("click", () => video.currentTime -= 10);
    document.getElementById("forward-btn").addEventListener("click", () => video.currentTime += 10);

    // Mute Toggler
    muteBtn.addEventListener("click", () => {
      video.muted = !video.muted;
      this.updateVolumeUI();
    });

    // Volume Slide Bar
    const volBar = document.getElementById("volume-slider-bar");
    volBar.addEventListener("click", (e) => {
      const rect = volBar.getBoundingClientRect();
      const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      video.volume = pos;
      video.muted = false;
      this.updateVolumeUI();
    });

    // Speed Selection Menu
    speedToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      speedMenu.classList.toggle("active");
      qualityMenu.classList.remove("active");
    });

    speedMenu.querySelectorAll("li").forEach(item => {
      item.addEventListener("click", (e) => {
        const speed = parseFloat(item.getAttribute("data-speed"));
        video.playbackRate = speed;
        speedToggle.textContent = item.textContent;
        speedMenu.querySelectorAll("li").forEach(l => l.classList.remove("active"));
        item.classList.add("active");
        speedMenu.classList.remove("active");
      });
    });

    // Quality selection (Simulated logs inside player)
    qualityToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      qualityMenu.classList.toggle("active");
      speedMenu.classList.remove("active");
    });

    qualityMenu.querySelectorAll("li").forEach(item => {
      item.addEventListener("click", () => {
        qualityMenu.querySelectorAll("li").forEach(l => l.classList.remove("active"));
        item.classList.add("active");
        qualityMenu.classList.remove("active");
        
        // Show quality change alert in controls
        const titleBadge = document.querySelector(".player-badge");
        titleBadge.textContent = "Re-routing via proxy stream...";
        titleBadge.style.backgroundColor = "var(--accent)";
        
        setTimeout(() => {
          titleBadge.textContent = item.textContent.split(" ")[0] + " Active";
          titleBadge.style.backgroundColor = "var(--primary)";
        }, 1200);
      });
    });

    // Close menus on body clicks
    document.addEventListener("click", () => {
      speedMenu.classList.remove("active");
      qualityMenu.classList.remove("active");
    });

    // Fullscreen Controls
    fullscreenBtn.addEventListener("click", () => this.toggleFullscreen());
    
    // Keybind listeners
    window.addEventListener("keydown", (e) => {
      const player = document.getElementById("player-modal");
      if (player.style.display === "flex") {
        if (e.code === "Space") {
          e.preventDefault();
          this.togglePlay();
        } else if (e.code === "ArrowRight") {
          video.currentTime += 10;
        } else if (e.code === "ArrowLeft") {
          video.currentTime -= 10;
        } else if (e.code === "KeyF") {
          this.toggleFullscreen();
        } else if (e.code === "Escape") {
          this.closePlayer();
        }
      }
    });
  }

  startPlayer(title, videoUrl, movieId, resumeTime = 0) {
    const player = document.getElementById("player-modal");
    const video = document.getElementById("stream-video");

    this.activePlayerMovieId = movieId;

    document.getElementById("player-stream-title").textContent = title;
    video.src = videoUrl;
    video.currentTime = resumeTime;

    player.style.display = "flex";
    video.play().catch(e => console.log("Auto-play blocked by browser. User interaction required."));
    
    this.updateVolumeUI();
    this.showPlayerControlsBriefly();
  }

  togglePlay() {
    const video = document.getElementById("stream-video");
    const iconBtn = document.getElementById("play-pause-btn");

    if (video.paused) {
      video.play();
      iconBtn.innerHTML = `<i data-lucide="pause"></i>`;
    } else {
      video.pause();
      iconBtn.innerHTML = `<i data-lucide="play"></i>`;
    }
    lucide.createIcons();
    this.showPlayerControlsBriefly();
  }

  updatePlayerProgress() {
    const video = document.getElementById("stream-video");
    if (!video.duration) return;

    const percent = (video.currentTime / video.duration) * 100;
    document.getElementById("timeline-progress").style.width = `${percent}%`;
    document.getElementById("time-current").textContent = this.formatTime(video.currentTime);

    // Save history periodically
    if (this.activePlayerMovieId && Math.floor(video.currentTime) % 4 === 0) {
      const movie = showAppDB.getMovies().find(m => m.id === this.activePlayerMovieId);
      if (movie) {
        showAppDB.updateHistory(movie.id, video.currentTime, video.duration, movie.title, movie.poster);
      }
    }
  }

  updateVolumeUI() {
    const video = document.getElementById("stream-video");
    const iconBtn = document.getElementById("mute-btn");
    const progress = document.getElementById("volume-progress");

    progress.style.width = `${video.muted ? 0 : video.volume * 100}%`;

    if (video.muted || video.volume === 0) {
      iconBtn.innerHTML = `<i data-lucide="volume-x"></i>`;
    } else if (video.volume < 0.5) {
      iconBtn.innerHTML = `<i data-lucide="volume-1"></i>`;
    } else {
      iconBtn.innerHTML = `<i data-lucide="volume-2"></i>`;
    }
    lucide.createIcons();
  }

  toggleFullscreen() {
    const player = document.getElementById("player-modal");
    if (!document.fullscreenElement) {
      player.requestFullscreen().catch(err => console.log(err));
    } else {
      document.exitFullscreen();
    }
  }

  showPlayerControlsBriefly() {
    const controls = document.getElementById("player-controls");
    controls.classList.add("active");
    clearTimeout(this.controlsTimeout);
    this.controlsTimeout = setTimeout(() => {
      controls.classList.remove("active");
    }, 3000);
  }

  closePlayer() {
    const video = document.getElementById("stream-video");
    video.pause();
    video.src = "";
    document.getElementById("player-modal").style.display = "none";
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }

    // Refresh history grid
    this.renderHome();
  }

  formatTime(secs) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  // ==========================================================================
  // INDEXER TERMINAL SIMULATOR LOGS (REAL-TIME PYROGRAM EMULATOR)
  // ==========================================================================

  bindForms() {
    // Indexer Form Submit
    const indexerForm = document.getElementById("indexer-run-form");
    indexerForm.addEventListener("submit", (e) => {
      e.preventDefault();
      this.runIndexerSimulation();
    });

    document.getElementById("btn-clear-logs").addEventListener("click", () => {
      const logs = document.getElementById("indexer-terminal-logs");
      logs.innerHTML = `<div class="log-line system">[SYSTEM] Terminal log cleared. Ready.</div>`;
    });

    // Table quickscan
    document.getElementById("btn-trigger-quickscan").addEventListener("click", () => {
      document.querySelector(".nav-item[data-tab='indexer']").click();
      this.runIndexerSimulation();
    });

    // Add manual form
    const addForm = document.getElementById("admin-add-form");
    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const newMedia = {
        title: document.getElementById("add-title").value,
        type: document.getElementById("add-type").value,
        quality: document.getElementById("add-quality").value,
        year: document.getElementById("add-year").value,
        rating: document.getElementById("add-rating").value,
        telegramChannel: document.getElementById("add-channel").value,
        videoUrl: document.getElementById("add-videourl").value,
        description: document.getElementById("add-description").value,
        releaseDate: `${document.getElementById("add-year").value}-01-01`,
        messageId: Math.floor(Math.random() * 5000) + 100,
        fileSize: "1.6 GB"
      };

      // Perform TMDb Enrichment simulation (Quick scan match)
      const enrichment = MOCK_TMDB_API.search(newMedia.title);
      newMedia.poster = enrichment.poster;
      newMedia.backdrop = enrichment.backdrop;
      newMedia.cast = enrichment.cast;
      newMedia.genres = enrichment.genres;
      if (!newMedia.description || newMedia.description.trim() === "") {
        newMedia.description = enrichment.description;
      }
      
      if (newMedia.type === "series") {
        newMedia.seasons = [
          {
            seasonNumber: 1,
            episodes: [
              { episodeNumber: 1, title: "Episode 1: Pilot Spec", videoUrl: newMedia.videoUrl },
              { episodeNumber: 2, title: "Episode 2: Index Discovery", videoUrl: newMedia.videoUrl }
            ]
          }
        ];
      }

      const added = await showAppDB.addMovie(newMedia);
      if (added) {
        alert(`Successfully manual indexed '${newMedia.title}' to MongoDB! Auto matched TMDb cover details.`);
        addForm.reset();
        await showAppDB.syncFromBackend();
        this.renderAdminTable();
        this.renderHome();
      } else {
        alert("Failed to save media asset to MongoDB database.");
      }
    });

    // Add channel form
    const chanForm = document.getElementById("admin-channel-form");
    chanForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("chan-username").value.trim();
      const name = document.getElementById("chan-name").value.trim();

      const chan = {
        name,
        username: username.startsWith("@") ? username : "@" + username
      };

      await showAppDB.addChannel(chan);
      chanForm.reset();
      await showAppDB.syncFromBackend();
      this.renderAdminChannels();
      this.populateSelectOptions();
    });

    // Header Manual Add modal triggers
    document.getElementById("btn-manual-upload").addEventListener("click", () => {
      document.querySelector(".nav-item[data-tab='admin']").click();
      document.getElementById("add-title").focus();
    });
  }

  runIndexerSimulation() {
    if (this.isScraping) return;
    
    this.isScraping = true;
    const btn = document.getElementById("btn-start-scraper");
    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="refresh-cw" class="loading-spin"></i> Indexing Channel...`;
    lucide.createIcons();

    const targetChan = document.getElementById("scrape-channel").value;
    const limit = parseInt(document.getElementById("scrape-limit").value);
    
    const logs = document.getElementById("indexer-terminal-logs");
    logs.innerHTML += `<div class="log-line system"><br>[SYSTEM] Starting Pyrogram indexing task on ${targetChan}...</div>`;
    logs.scrollTop = logs.scrollHeight;

    const templates = [
      { file: "Avatar.The.Way.of.Water.2022.1080p.WEBRip.x264.mkv", title: "Avatar: The Way of Water" },
      { file: "The_Dark_Knight_2008_IMAX_2160p_HEVC_Atmos_HDR.mkv", title: "The Dark Knight" },
      { file: "Wednesday.S01E01.1080p.NF.WEBRip.DDP5.1.x264.mkv", title: "Wednesday" }
    ];

    let currentStep = 0;

    const logSequence = [
      () => `[BOT] Pyrogram version 2.0.12 connecting...`,
      () => `[BOT] Joined channel session for ${targetChan}. Fetching history (Limit: ${limit}).`,
      () => `[BOT] Msg ID: 15420 - Scanning entities... Found video: "${templates[0].file}"`,
      () => `[BOT] File description matches film keyword. Fetching TMDb developer API index...`,
      () => `[TMDb API] Querying endpoint: https://api.themoviedb.org/3/search/movie?query=${encodeURIComponent(templates[0].title)}`,
      () => `[TMDb API] MATCH verified! ID: 766007. Title: "${templates[0].title}". Rating: 7.6/10.`,
      () => `[DATABASE] Connecting MongoDB cluster pool. Updating document schema...`,
      () => `[DATABASE] Document inserted: '${templates[0].title}' successfully mapped to message ID 15420.`,
      () => `[BOT] Msg ID: 15421 - Scanning entities... No video attachment, text message. (Skipped)`,
      () => `[BOT] Msg ID: 15422 - Scanning entities... Found video: "${templates[1].file}"`,
      () => `[BOT] File contains high-def tags. Contacting TMDb...`,
      () => `[TMDb API] MATCH verified! ID: 155. Title: "${templates[1].title}". Rating: 9.0/10.`,
      () => `[DATABASE] Document inserted: '${templates[1].title}' added to cluster index.`,
      () => `[BOT] Msg ID: 15423 - Scanning entities... Found video: "${templates[2].file}"`,
      () => `[BOT] Series match pattern detected. Compiling Season 1 Episode data...`,
      () => `[TMDb API] MATCH verified! ID: 119051. Title: "${templates[2].title}". Genres: Fantasy, Mystery.`,
      () => `[DATABASE] Document inserted: '${templates[2].title}' TV Series indexed with simulated seasons.`,
      () => `[BOT] Sync finished. Total messages scanned: ${limit}. Added/Updated: 3 items. MongoDB synchronized.`
    ];

    const runNextLog = async () => {
      if (currentStep >= logSequence.length) {
        // Index files in actual DB
        for (const t of templates) {
          const enrich = MOCK_TMDB_API.search(t.title);
          const item = {
            title: t.title,
            year: enrich.year,
            rating: enrich.rating,
            genres: enrich.genres,
            description: enrich.description,
            poster: enrich.poster,
            backdrop: enrich.backdrop,
            cast: enrich.cast,
            releaseDate: enrich.releaseDate,
            quality: t.file.includes("2160p") ? "2160p" : "1080p",
            telegramChannel: targetChan,
            messageId: Math.floor(Math.random() * 8000) + 1200,
            fileSize: t.file.includes("2160p") ? "4.2 GB" : "1.8 GB"
          };

          if (t.title === "Wednesday") {
            item.type = "series";
            item.seasons = [
              {
                seasonNumber: 1,
                episodes: [
                  { episodeNumber: 1, title: "Chapter I: Wednesday's Child Is Full of Woe", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" },
                  { episodeNumber: 2, title: "Chapter II: Woe Is the Loneliest Number", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4" }
                ]
              }
            ];
          } else {
            item.type = "movie";
            item.videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";
          }

          await showAppDB.addMovie(item);
        }

        await showAppDB.syncFromBackend();

        // Finished Scrape
        this.isScraping = false;
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="play"></i> Start Pyrogram Scraper`;
        
        // Update stats
        const moviesCount = showAppDB.getMovies().length;
        document.getElementById("stat-total-indexed").textContent = `${moviesCount} Indexed`;
        
        this.renderHome();
        this.renderSearchCatalog();
        this.renderAdminTable();
        lucide.createIcons();
        return;
      }

      const logText = logSequence[currentStep]();
      let logClass = "bot";
      if (logText.includes("[SYSTEM]")) logClass = "system";
      else if (logText.includes("[DATABASE]")) logClass = "db";
      else if (logText.includes("[TMDb")) logClass = "log-line";

      logs.innerHTML += `<div class="log-line ${logClass}">${logText}</div>`;
      logs.scrollTop = logs.scrollHeight;

      currentStep++;
      
      // Delay multiplier for typing realism
      setTimeout(runNextLog, Math.random() * 600 + 400);
    };

    runNextLog();
  }

  // ==========================================================================
  // ADMIN PANEL CONTROLS
  // ==========================================================================

  renderAdminTable() {
    const movies = showAppDB.getMovies();
    const tbody = document.getElementById("admin-media-tbody");

    if (movies.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dark);">No movies or shows indexed in local database.</td></tr>`;
      return;
    }

    tbody.innerHTML = movies.map(movie => `
      <tr id="table-row-${movie.id}">
        <td>
          <div class="table-asset-info">
            <img src="${movie.poster}" alt="Thumb">
            <div class="asset-title-group">
              <span class="title">${movie.title}</span>
              <span class="year">${movie.year} &bull; ${movie.genres.join(", ")}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="badge-tag outline-badge">${movie.type.toUpperCase()}</span>
        </td>
        <td>
          <span class="quality-badge">${movie.quality}</span>
        </td>
        <td>
          <span style="font-family: monospace; font-size: 12px; color: var(--accent)">${movie.telegramChannel}</span>
        </td>
        <td>
          <span style="font-weight: 700; color: #fbbf24;"><i data-lucide="star" style="width: 12px; height: 12px; display: inline-block; vertical-align: middle; fill: #fbbf24; margin-right: 4px;"></i>${movie.rating}</span>
        </td>
        <td>
          <div style="display: flex; gap: 8px;">
            <button class="action-row-btn edit" onclick="showApp.editAdminMovie('${movie.id}')" title="Edit Metadata"><i data-lucide="edit-3" style="width:16px;height:16px;"></i></button>
            <button class="action-row-btn delete" onclick="showApp.deleteAdminMovie('${movie.id}')" title="Delete Asset"><i data-lucide="trash-2" style="width:16px;height:16px;"></i></button>
          </div>
        </td>
      </tr>
    `).join("");

    lucide.createIcons();
  }

  async editAdminMovie(id) {
    const movie = showAppDB.getMovies().find(m => m.id === id);
    if (!movie) return;

    // Fill form
    document.getElementById("add-title").value = movie.title;
    document.getElementById("add-type").value = movie.type;
    document.getElementById("add-quality").value = movie.quality;
    document.getElementById("add-year").value = movie.year;
    document.getElementById("add-rating").value = movie.rating;
    document.getElementById("add-channel").value = movie.telegramChannel;
    document.getElementById("add-videourl").value = movie.videoUrl;
    document.getElementById("add-description").value = movie.description;

    // Focus title
    document.getElementById("add-title").focus();

    // Delete existing on save to overwrite
    await showAppDB.deleteMovie(movie.id);
  }

  async deleteAdminMovie(id) {
    if (confirm("Are you sure you want to delete this indexed media asset from the database?")) {
      await showAppDB.deleteMovie(id);
      await showAppDB.syncFromBackend();
      this.renderAdminTable();
      this.renderHome();
      this.renderSearchCatalog();
    }
  }

  renderAdminChannels() {
    const list = document.getElementById("admin-channel-list");
    const channels = showAppDB.getChannels();

    list.innerHTML = channels.map(chan => `
      <li class="channel-item">
        <div class="channel-meta">
          <span class="chan-title">${chan.name}</span>
          <span class="chan-username">${chan.username}</span>
        </div>
        <div class="channel-actions">
          <div class="switch-btn ${chan.active ? 'active' : ''}" onclick="showApp.toggleChannelActive('${chan.id}')" title="Toggle Channel Scraper Sync"></div>
          <button class="chan-del-btn" onclick="showApp.deleteChannel('${chan.id}')" title="Delete Channel"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i></button>
        </div>
      </li>
    `).join("");

    lucide.createIcons();
  }

  async toggleChannelActive(id) {
    await showAppDB.toggleChannel(id);
    await showAppDB.syncFromBackend();
    this.renderAdminChannels();
    this.populateSelectOptions();
  }

  async deleteChannel(id) {
    if (confirm("Are you sure you want to stop tracking this channel?")) {
      await showAppDB.deleteChannel(id);
      await showAppDB.syncFromBackend();
      this.renderAdminChannels();
      this.populateSelectOptions();
    }
  }
}

const showApp = new ShowApp();
