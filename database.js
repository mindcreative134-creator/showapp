// Mock database of movies, TV shows, and Telegram channels
const DEFAULT_MOVIES = [
  {
    id: "m1",
    title: "Interstellar",
    type: "movie",
    year: "2014",
    quality: "1080p",
    rating: "8.7",
    genres: ["Sci-Fi", "Adventure", "Drama"],
    description: "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
    poster: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
    backdrop: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1600&auto=format&fit=crop&q=80",
    cast: ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    telegramChannel: "@Hollywood_HD_Movies",
    messageId: 2045,
    fileSize: "2.4 GB",
    releaseDate: "2014-11-07"
  },
  {
    id: "m2",
    title: "Inception",
    type: "movie",
    year: "2010",
    quality: "1080p",
    rating: "8.8",
    genres: ["Action", "Sci-Fi", "Thriller"],
    description: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O., but his tragic past may doom the project.",
    poster: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
    backdrop: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=1600&auto=format&fit=crop&q=80",
    cast: ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy"],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    telegramChannel: "@Hollywood_HD_Movies",
    messageId: 1089,
    fileSize: "1.8 GB",
    releaseDate: "2010-07-16"
  },
  {
    id: "m3",
    title: "Spider-Man: Into the Spider-Verse",
    type: "movie",
    year: "2018",
    quality: "2160p",
    rating: "8.4",
    genres: ["Animation", "Action", "Adventure"],
    description: "Teen Miles Morales becomes the Spider-Man of his universe, and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.",
    poster: "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=600&auto=format&fit=crop&q=80",
    backdrop: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1600&auto=format&fit=crop&q=80",
    cast: ["Shameik Moore", "Jake Johnson", "Hailee Steinfeld", "Mahershala Ali"],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    telegramChannel: "@Anime_Infinity_Group",
    messageId: 442,
    fileSize: "3.2 GB",
    releaseDate: "2018-12-14"
  },
  {
    id: "s1",
    title: "Stranger Things",
    type: "series",
    year: "2016",
    quality: "1080p",
    rating: "8.7",
    genres: ["Drama", "Fantasy", "Horror"],
    description: "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl.",
    poster: "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=600&auto=format&fit=crop&q=80",
    backdrop: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1600&auto=format&fit=crop&q=80",
    cast: ["Winona Ryder", "David Harbour", "Millie Bobby Brown", "Finn Wolfhard"],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    telegramChannel: "@WebSeries_Zone",
    messageId: 8550,
    fileSize: "950 MB/ep",
    releaseDate: "2016-07-15",
    seasons: [
      {
        seasonNumber: 1,
        episodes: [
          { episodeNumber: 1, title: "Chapter One: The Vanishing of Will Byers", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" },
          { episodeNumber: 2, title: "Chapter Two: The Weirdo on Maple Street", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" },
          { episodeNumber: 3, title: "Chapter Three: Holly, Jolly", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4" }
        ]
      },
      {
        seasonNumber: 2,
        episodes: [
          { episodeNumber: 1, title: "Chapter One: Madmax", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" },
          { episodeNumber: 2, title: "Chapter Two: Trick or Treat, Freak", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" }
        ]
      }
    ]
  },
  {
    id: "s2",
    title: "Breaking Bad",
    type: "series",
    year: "2008",
    quality: "1080p",
    rating: "9.5",
    genres: ["Crime", "Drama", "Thriller"],
    description: "A chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine with a former student in order to secure his family's future.",
    poster: "https://images.unsplash.com/photo-1568832359672-e36cf5d74f54?w=600&auto=format&fit=crop&q=80",
    backdrop: "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=1600&auto=format&fit=crop&q=80",
    cast: ["Bryan Cranston", "Aaron Paul", "Anna Gunn", "Bob Odenkirk"],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    telegramChannel: "@WebSeries_Zone",
    messageId: 991,
    fileSize: "1.1 GB/ep",
    releaseDate: "2008-01-20",
    seasons: [
      {
        seasonNumber: 1,
        episodes: [
          { episodeNumber: 1, title: "Pilot", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4" },
          { episodeNumber: 2, title: "Cat's in the Bag...", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" },
          { episodeNumber: 3, title: "...And the Bag's in the River", videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" }
        ]
      }
    ]
  },
  {
    id: "m4",
    title: "Demon Slayer: Mugen Train",
    type: "anime",
    year: "2020",
    quality: "1080p",
    rating: "8.2",
    genres: ["Action", "Fantasy", "Animation"],
    description: "After a string of mysterious disappearances aboard a train, the Demon Slayer Corps sends formidable Flame Hashira Kyojuro Rengoku alongside Tanjiro, Nezuko, Zenitsu, and Inosuke to eliminate the threat.",
    poster: "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&auto=format&fit=crop&q=80",
    backdrop: "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1600&auto=format&fit=crop&q=80",
    cast: ["Natsuki Hanae", "Akari Kito", "Yoshitsugu Matsuoka", "Hiro Shimono"],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    telegramChannel: "@Anime_Infinity_Group",
    messageId: 1205,
    fileSize: "1.4 GB",
    releaseDate: "2020-10-16"
  }
];

const DEFAULT_CHANNELS = [
  { id: "c1", name: "Hollywood HD Movies", username: "@Hollywood_HD_Movies", fileCount: 420, active: true },
  { id: "c2", name: "WebSeries Zone", username: "@WebSeries_Zone", fileCount: 285, active: true },
  { id: "c3", name: "Anime Infinity", username: "@Anime_Infinity_Group", fileCount: 198, active: true },
  { id: "c4", name: "South Indian Action HD", username: "@South_HD_Cinema", fileCount: 154, active: false }
];

// TMDb mock generator for new scraper simulation
const MOCK_TMDB_API = {
  search: function(query) {
    const q = query.toLowerCase();
    
    const results = [
      {
        title: "Avatar: The Way of Water",
        year: "2022",
        rating: "7.6",
        genres: ["Sci-Fi", "Action", "Adventure"],
        description: "Jake Sully lives with his newfound family formed on the extrasolar moon Pandora. Once a familiar threat returns to finish what was previously started, Jake must work with Neytiri and the army of the Na'vi race to protect their home.",
        poster: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
        backdrop: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1600&auto=format&fit=crop&q=80",
        cast: ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver", "Kate Winslet"],
        releaseDate: "2022-12-16"
      },
      {
        title: "The Dark Knight",
        year: "2008",
        rating: "9.0",
        genres: ["Action", "Crime", "Drama"],
        description: "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        poster: "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600&auto=format&fit=crop&q=80",
        backdrop: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1600&auto=format&fit=crop&q=80",
        cast: ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Maggie Gyllenhaal"],
        releaseDate: "2008-07-18"
      },
      {
        title: "Wednesday",
        year: "2022",
        rating: "8.1",
        genres: ["Comedy", "Fantasy", "Mystery"],
        description: "Follows Wednesday Addams' years as a student at Nevermore Academy as she attempts to master her emerging psychic ability, thwart a monstrous killing spree, and solve the mystery that embroiled her parents.",
        poster: "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=600&auto=format&fit=crop&q=80",
        backdrop: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1600&auto=format&fit=crop&q=80",
        cast: ["Jenna Ortega", "Gwendoline Christie", "Riki Lindhome", "Christina Ricci"],
        releaseDate: "2022-11-23"
      }
    ];

    // Attempt match
    const match = results.find(item => item.title.toLowerCase().includes(q));
    if (match) return match;
    
    // Default fallback generator if search is empty or random
    return {
      title: query.split('.')[0].replace(/_/g, ' ').replace(/-/g, ' '),
      year: "2024",
      rating: "7.5",
      genres: ["Action", "Drama"],
      description: `A fast-paced media asset titled '${query}' scraped from indexed Telegram message. Automatically enriched with TMDb Smart Meta Tagging API.`,
      poster: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&auto=format&fit=crop&q=80",
      backdrop: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1600&auto=format&fit=crop&q=80",
      cast: ["Simulated Actor A", "Simulated Actor B"],
      releaseDate: "2024-05-19"
    };
  }
};

// Initialize LocalStorage database helper
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

  getMovies() {
    return JSON.parse(localStorage.getItem("showapp_movies"));
  }

  saveMovies(movies) {
    localStorage.setItem("showapp_movies", JSON.stringify(movies));
  }

  addMovie(movie) {
    const movies = this.getMovies();
    // Prevent duplicate title / type
    if (movies.find(m => m.title.toLowerCase() === movie.title.toLowerCase() && m.type === movie.type)) {
      return false;
    }
    movie.id = 'm_' + Date.now();
    movies.unshift(movie);
    this.saveMovies(movies);
    return movie;
  }

  updateMovie(updated) {
    const movies = this.getMovies();
    const idx = movies.findIndex(m => m.id === updated.id);
    if (idx !== -1) {
      movies[idx] = updated;
      this.saveMovies(movies);
      return true;
    }
    return false;
  }

  deleteMovie(id) {
    let movies = this.getMovies();
    movies = movies.filter(m => m.id !== id);
    this.saveMovies(movies);
  }

  getChannels() {
    return JSON.parse(localStorage.getItem("showapp_channels"));
  }

  saveChannels(channels) {
    localStorage.setItem("showapp_channels", JSON.stringify(channels));
  }

  addChannel(chan) {
    const channels = this.getChannels();
    chan.id = 'c_' + Date.now();
    chan.fileCount = 0;
    chan.active = true;
    channels.push(chan);
    this.saveChannels(channels);
    return chan;
  }

  toggleChannel(id) {
    const channels = this.getChannels();
    const c = channels.find(ch => ch.id === id);
    if (c) {
      c.active = !c.active;
      this.saveChannels(channels);
    }
  }

  deleteChannel(id) {
    let channels = this.getChannels();
    channels = channels.filter(c => c.id !== id);
    this.saveChannels(channels);
  }

  getWatchlist() {
    return JSON.parse(localStorage.getItem("showapp_watchlist"));
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
    return JSON.parse(localStorage.getItem("showapp_history"));
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

    // Keep only last 10 entries
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
