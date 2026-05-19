# Infinity TV - Telegram OTT Streaming & Auto-Indexer System

यह एक **Premium OTT Web Application & Real-time Scraper Bot** का पूरा आर्किटेक्चर और रेडी-टू-डिप्लॉय कोडबेस है। इसमें एक **Visual Web App (Interactive Prototype)** है जो ब्राउज़र में तुरंत चलता है, और एक **Production-Grade Python Backend** है जिसे आप VPS, Render, या local machine पर होस्ट कर सकते हैं।

---

## 📂 Directory Structure

```text
show app/
├── index.html          # Dynamic OTT Dashboard & Simulator Interface
├── style.css           # Modern Aether-Dark/Cyber-Purple Glassmorphic Styles
├── database.js         # LocalStorage Database synchronizer & initial movies dataset
├── app.js              # Tab controller, Custom player controllers, Indexer typewriter logs
└── backend/            # Production Python Backend codebase
    ├── requirements.txt # Python dependency configuration
    ├── config.py       # Security credentials loader
    ├── database.py     # Asynchronous Motor (MongoDB) CRUD wrappers
    ├── bot.py          # Pyrogram Channel stream video listener bot & TMDb API parser
    ├── main.py         # REST Web API endpoints & Telegram streaming video proxy
    └── run.py          # Async Launcher script to run bot and server concurrently
```

---

## ✨ System Features (सिस्टम की खूबियाँ)

### 1. **Modern OTT Web App Frontend Dashboard**
* **Cyber Purple Glassmorphism**: Harman HSL कलर पैलेट, आउटफिट/प्लस जकार्ता सैंस फॉन्ट, और निऑन होवर ग्लो इफेक्ट्स से लैस प्रीमियम लुक्स।
* **Responsive Category Grids**: मूवीज, वेब सीरीज़ और एनिमे के सेग्मेंटेड सेक्शन्स।
* **Advanced Global Search**: कीवर्ड, जॉनर (Genre), रिलीज ईयर, चैनल ओरिजिन, या टेलीग्राम मैसेज ID से इंस्टेंट सर्च।
* **Dynamic Watchlist**: ब्राउज़र लोकल स्टोरेज के साथ सिंक्रोनाइज्ड बुकमार्क लिस्ट।
* **Continue Watching History**: वीडियो प्लेयर की प्रोग्रेस को ट्रैक कर दोबारा वहीं से रेज़्यूमे करने की सुविधा।

### 2. **Telegram Bot Indexer Simulator**
* index.html में एक **Interactive Pyrogram Terminal Simulator** लगाया गया है। 
* जब आप **"Start Pyrogram Scraper"** पर क्लिक करेंगे, तो यह लाइव स्क्रॉलिंग लॉगर शो करेगा:
  1. टेलीग्राम मैसेज फ़ाइल नेम स्कैनिंग (`Avatar.The.Way.of.Water.2022.1080p.mkv`).
  2. फ़ाइल नेम से टाइटल, ईयर, रिज़ॉल्यूशन पार्सिंग।
  3. TMDb डेवलपर API से कनेक्ट होकर बैकड्रॉप, पोस्टर, स्टार कास्ट, और समरी डाउनलोड करना।
  4. डेटा को डेटाबेस में सेव करना।
* स्कैन पूरा होते ही नए मूवीज़ आपके होम पेज, सर्च कैटलॉग और एडमिन डेटाबेस मैनेजर में तुरंत दिखने लगेंगे!

### 3. **Custom Advanced HTML5 Media Player**
* ब्राउज़र के बोरिंग डिफ़ॉल्ट प्लेयर को बदल कर बनाया गया एक शानदार वीडियो प्लेयर:
  * निऑन प्रोग्रेस स्लाइडर (Timeline Scrubbing)।
  * रीवाइंड 10s / फॉरवर्ड 10s शॉर्टकट।
  * म्यूट और वॉल्यूम स्लाइड कंट्रोलर।
  * प्लेबैक स्पीड चेंजर (0.5x से 2.0x)।
  * क्वालिटी सेलेक्टर (1080p source / 720p / 480p proxy routes)।
  * कीबोर्ड कीज़ (Space to Play/Pause, Key F to Fullscreen, Esc to Exit)。

### 4. **Production-Grade Backend (Python FastAPI & Pyrogram)**
* **Concurreny Launch**: `run.py` के जरिए एक ही कमांड से FastAPI सर्वर और Pyrogram Bot बैकग्राउंड में एक साथ स्टार्ट हो जाते हैं।
* **Auto Indexing Bot**: जैसे ही आपके ट्रैक्ड चैनल्स में कोई वीडियो फ़ाइल पोस्ट होगी, बोट उसे तुरंत डाउनलोड किये बिना उसका नाम पार्स करके, TMDb से कवर आर्ट मैच कर MongoDB में इंडेक्स कर देगा।
* **Proxy Streaming Router**: `/api/stream/{message_id}` एंडपॉइंट वीडियो पैलोड को सीधे टेलीग्राम से चंक-बाई-चंक ब्राउज़र तक बिना डाउनलोड किए स्ट्रीम करता है, जिससे कॉर्स (CORS) एरर बाईपास हो जाते हैं।

---

## 🚀 Quick Start - Running the Visual Dashboard (Visual App कैसे चलायें)

1. इस `show app/` डायरेक्टरी को अपने कंप्यूटर में खोलें।
2. `index.html` फ़ाइल पर डबल-क्लिक करके इसे सीधे किसी भी ब्राउज़र (Chrome, Edge, Brave, Safari) में खोलें।
3. होम पेज लोड हो जायेगा। सर्च बार टेस्ट करें, किसी मूवी पोस्टर पर क्लिक करके **Direct Stream** टेस्ट करें।
4. **Telegram Indexer** टैब पर जाएं, चैनल सेलेक्ट करें और **Start Pyrogram Scraper** दबाकर देखें कि असली बोट टेलीग्राम चैनल से डेटा कैसे स्कैन करता है।
5. **Admin Panel** टैब में जाकर आप खुद मैनुअली नई मूवीज़ जोड़ सकते हैं या ट्रैक किये जा रहे चैनल्स का स्टेटस कंट्रोल कर सकते हैं।

---

## 🛠 Production Backend Deployment (असली बैकएंड कैसे होस्ट करें)

### Step 1: Requirements (ज़रूरी चीज़ें)
* Python v3.8 या उससे ऊपर का वर्शन।
* MongoDB डेटाबेस (फ्री MongoDB Atlas क्लस्टर का इस्तेमाल कर सकते हैं)।
* टेलीग्राम API ID और API Hash (इसे आप [my.telegram.org](https://my.telegram.org) से ले सकते हैं)।
* एक टेलीग्राम बोट टोकन (@BotFather से जनरेट करें)।
* TMDb API Key ([themoviedb.org](https://www.themoviedb.org) डेवलपर अकाउंट से फ्री लें)।

### Step 2: Installation & Settings Setup
कमांड प्रॉम्ट / पॉवरशेल खोलें और डायरेक्टरी में आएं:
```bash
cd backend
pip install -r requirements.txt
```

डायरेक्टरी में `config.env` नाम की फ़ाइल बनाएं और अपने क्रेडेंशियल्स डालें:
```env
API_ID=29507367
API_HASH=a99c710ea3f1530e5600d27ac8f3fe84
BOT_TOKEN=8625523630:AAEGanx-X7n4GKdIMgWFVuhdtldHVyecGXI
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/showapp_db?retryWrites=true&w=majority
TMDB_API_KEY=b3a4a1599388df2a2cc86940a02efdb4
PORT=8000
HOST=0.0.0.0
BASE_URL=http://localhost:8000
```

### Step 3: Run the Ecosystem
एप्लीकेशन को लाइव लॉन्च करने के लिए चलाएं:
```bash
python run.py
```

FastAPI का इंटरैक्टिव डॉक्यूमेंटेशन देखने के लिए ब्राउज़र में खोलें:
* `http://localhost:8000/docs`

---

## ⚠️ Important Warning & Legal Info

कॉपीराइटेड मूवीज़ या टीवी सीरीज़ को पब्लिक डोमेन में टेलीग्राम चैनल्स के जरिए स्ट्रीम करना Google Play Store पॉलिसीज़ का उल्लंघन करता है और टेलीग्राम DMCA के तहत आपका चैनल या सर्वर सस्पेंड किया जा सकता है। 
* **Safe Practice**: इस आर्किटेक्चर का इस्तेमाल हमेशा प्राइवेट कम्युनिटीज़, खुद के पर्सनल मीडिया स्टोरेज बैकअप, या एनिमे/फ्री-टू-एयर एजुकेशनल वीडियो चैनल्स के लिए ही करें।
