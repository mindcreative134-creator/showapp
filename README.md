# Infinity TV - Live Telegram Streaming & Auto-Indexer Backend Engine

यह **Infinity TV Flutter Mobile App** के लिए डिज़ाइन किया गया एक **Production-Grade Python Backend Core & Pyrogram Channel Indexer** है। 

इस आर्किटेक्चर का प्राथमिक उद्देश्य टेलीग्राम वीडियो फ़ाइलों को बिना डाउनलोड किए सीधे मोबाइल वीडियो प्लेयर (Flutter Client) पर चंक-बाय-चंक (Chunk-by-chunk) हाई-स्पीड स्ट्रीमिंग प्रदान करना और मोंगो डेटाबेस (MongoDB Atlas) में मीडिया डेटा को ऑटो-इंडेक्स करना है।

---

## 📂 Directory Structure

```text
show app/
├── README.md               # Backend Core Setup Instructions
├── SYSTEM_SETUP_GUIDE.md   # Advanced VPS Deployment Guidelines
└── backend/                # Production Python Backend Codebase
    ├── requirements.txt    # Python dependency configuration
    ├── config.py           # Security credentials loader
    ├── database.py         # Asynchronous Motor (MongoDB Atlas) CRUD wrappers
    ├── bot.py              # Pyrogram Channel stream video listener bot & TMDb API parser
    ├── main.py             # REST Web API endpoints & Telegram streaming video proxy
    └── run.py              # Async Launcher script to run bot and server concurrently
```

---

## ✨ Features (सिस्टम की मुख्य विशेषताएं)

### 1. **Pyrogram Async Channel Indexer Bot**
* जैसे ही आपके कनेक्टेड टेलीग्राम चैनल में कोई वीडियो फ़ाइल पोस्ट होगी, बोट उसे तुरंत स्कैन करेगा।
* फ़ाइल नेम से टाइटल, क्वालिटी (1080p, 4K), और रिज़ॉल्यूशन पार्स करेगा।
* TMDb डेवलपर API से बैकड्रॉप, पोस्टर, रेटिंग, स्टार कास्ट और विवरण लेकर MongoDB में एक नया मीडिया डॉक्यूमेंट जोड़ देगा।

### 2. **Telegram Byte-Range Streaming Proxy (FastAPI)**
* टेलीग्राम एपीआई से डायरेक्ट बाइनरी रेंज रिक्वेस्ट (HTTP Byte Ranges) सपोर्ट करता है।
* यह मोबाइल प्लेयर्स (Flutter, VLC, MPV) में वीडियो सीक (Seek/Timeline Forward-Backward) को अत्यंत स्मूथ और बफ़र-मुक्त बनाता है।
* CORS एरर्स को पूरी तरह से बाईपास करता है।

### 3. **Flutter Compatible REST API Engine**
* मोबाइल क्लाइंट के लिए निम्नलिखित हाई-स्पीड REST एंडपॉइंट्स प्रदान करता है:
  * `GET /api/movies` (लेटेस्ट मूवी लिस्ट)
  * `GET /api/tvshows` (वेब सीरीज और सीजन लिस्ट)
  * `GET /api/search?query=name` (लाइव ग्लोबल सर्च)
  * `GET /stream/{channel_id}/{message_id}` (लाइव स्ट्रीमिंग प्रॉक्सी गेटवे)

---

## 🛠 Quick Installation & Run (बैकएंड सेटअप कैसे करें)

### Step 1: Requirements (ज़रूरी चीज़ें)
* Python v3.10 या उससे ऊपर का वर्शन।
* MongoDB Atlas क्लस्टर (मोंगो डेटाबेस)।
* टेलीग्राम API ID और API Hash (इसे [my.telegram.org](https://my.telegram.org) से लें)।
* टेलीग्राम बोट टोकन (@BotFather से लें)।
* TMDb API Key ([themoviedb.org](https://www.themoviedb.org) से लें)।

### Step 2: Dependencies Install करें
कमांड प्रॉम्ट / पॉवरशेल खोलें और डायरेक्टरी में आएं:
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: config.env फाइल बनाएं
`backend/config.env` नाम की फ़ाइल बनाएं और अपने क्रेडेंशियल्स डालें:
```env
API_ID=29507367
API_HASH=a99c710ea3f1530e5600d27ac8f3fe84
BOT_TOKEN=8625523630:AAEGanx-X7n4GKdIMgWFVuhdtldHVyecGXI
MONGO_URI=mongodb+srv://appdb:appdb@cluster0.neu7p0o.mongodb.net/?appName=Cluster0
DB_NAME=appdb
TMDB_API_KEY=0da8b26f661ce60b48bb5f2876e13c74
PORT=8000
HOST=0.0.0.0
BASE_URL=https://showapp-y1nd.onrender.com
```

### Step 4: रन करें (Run Ecosystem)
```bash
python run.py
```

---

## 📡 Flutter Mobile Integration (मोबाइल ऐप से कैसे जोड़ें)

आपका मोबाइल ऐप निम्नलिखित लाइव प्रॉक्सी यूआरएल पर डेटा स्ट्रीम करेगा:
```text
https://showapp-y1nd.onrender.com/stream/{channel_id}/{message_id}
```
* उदाहरण: `https://showapp-y1nd.onrender.com/stream/-1002740721681/15420`
* यह मोबाइल प्लेयर्स में बिना किसी बफरिंग के और डायरेक्ट सीकिंग (seeking) के साथ 4K और 1080p प्लेबैक का अनुभव प्रदान करेगा।
