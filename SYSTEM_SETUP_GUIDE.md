# 🚀 Infinity TV - MongoDB Backend, Web Admin & Flutter Mobile App Setup Guide

नमस्ते! आपकी ऑडियो रिक्वेस्ट के अनुसार, हमने पूरे सिस्टम को री-आर्किटेक्ट कर दिया है:
1. **Web Streaming App** की जगह अब आपका **Flutter Mobile App (`Infinity-TV`)** मुख्य क्लाइंट है।
2. डेटाबेस को **Firebase Firestore** से बदलकर **MongoDB Cluster** कर दिया गया है।
3. एक **Unified Premium Web Admin Panel** सीधा आपके FastAPI सर्वर पर होस्ट कर दिया गया है, जिसे आप `http://localhost:8000/admin` पर खोल सकते हैं।

---

## 📂 Architecture Map (आर्किटेक्चर नक्शा)

```text
show app/ (Workspace)
├── backend/
│   ├── config.py       # environment credentials loader
│   ├── database.py     # MongoDB async wrappers
│   ├── bot.py          # Pyrogram Telegram indexing bot
│   ├── main.py         # REST API & Web Admin Panel (http://localhost:8000/admin)
│   └── run.py          # Unified concurrency launcher
└── SYSTEM_SETUP_GUIDE.md # यह गाइड

infinity tv/
└── Infinity-TV/        # आपका Flutter Mobile App प्रोजेक्ट
    └── lib/
        └── api/
            └── filmy4uhd_service.dart # अब यह MongoDB FastAPI सर्वर से कनेक्टेड है!
```

---

## 🛠️ Step 1: Python FastAPI & Scraper Bot Setup (बैकएंड सेटअप)

### 1. Requirements (ज़रूरी चीजें)
* Python v3.8 या उससे ऊपर इंस्टॉल होना चाहिए।
* एक क्रियाशील MongoDB Connection URI (जैसे MongoDB Atlas का फ्री क्लस्टर URL)।
* टेलीग्राम API क्रेडेंशियल्स (API ID, API Hash और Bot Token)।

### 2. Dependencies Install (लायब्रेरी इंस्टॉल करें)
अपना कमांड प्रॉम्ट (CMD) या पॉवरशेल खोलें और रन करें:
```bash
cd "c:\Users\91700\Downloads\show app\backend"
pip install -r requirements.txt
```

### 3. Connection Config (क्रेडेंशियल्स डालें)
`c:\Users\91700\Downloads\show app\backend` फोल्डर में `config.env` नाम की फाइल बनाएं और उसमें अपना MongoDB कलेक्टिव क्रेडेंशियल्स दर्ज करें:
```env
API_ID=29507367
API_HASH=a99c710ea3f1530e5600d27ac8f3fe84
BOT_TOKEN=8625523630:AAEGanx-X7n4GKdIMgWFVuhdtldHVyecGXI
MONGO_URI=mongodb+srv://mindcreative:mind134@cluster0.b7mha.mongodb.net/?retryWrites=true&w=majority
TMDB_API_KEY=b3a4a1599388df2a2cc86940a02efdb4
PORT=8000
HOST=0.0.0.0
BASE_URL=http://localhost:8000
```

---

## 🖥️ Step 2: Run the Server & Scraper (सिस्टम चालू करें)

बैकएंड और स्क्रैपर बोट को एक साथ चालू करने के लिए कमांड चलाएं:
```bash
python run.py
```
* **FastAPI Backend Server**: `http://localhost:8000` पर लाइव हो जाएगा।
* **Pyrogram Auto-Indexer Bot**: बैकग्राउंड में एक्टिव होकर आपके चैनल्स को रियल-टाइम स्कैन करेगा।

---

## 👑 Step 3: Access the Unified Web Admin Panel (एडमिन पैनल)

आपको कोई भी अलग वेब-एप सेटअप करने की ज़रुरत नहीं है! बूट होने के बाद सीधा अपने ब्राउज़र में खोलें:
👉 **[http://localhost:8000/admin](http://localhost:8000/admin)**

वहां से आप:
1. **Live MongoDB Database**: मोंगो कलेक्शन में सेव की गई मूवीज/वेबसीरीज को देख और डिलीट कर सकते हैं।
2. **Manual Indexing**: नया वीडियो टाइटल और वीडियो URL डालकर सीधे डेटाबेस में सेव कर सकते हैं (यह TMDb API से कवर आर्ट ऑटोमैटिक डाउनलोड कर लेता है)।
3. **Indexer Controller**: बोट स्कैनिंग ट्रिगर कर सकते हैं और लाइव स्क्रॉलिंग Pyrogram कंसोल लॉगर देख सकते हैं।

---

## 📱 Step 4: Configure the Flutter Mobile App (मोबाइल ऐप)

हमने पहले ही ऐप की क्रेडेंशियल फाइल `lib/api/filmy4uhd_service.dart` को मॉडिफाई कर दिया है ताकि वह नए मोंगो-फास्टएपीआई सर्वर से बात कर सके:
* **Target File**: `c:\Users\91700\Downloads\infinity tv\Infinity-TV\lib\api\filmy4uhd_service.dart`
* **Local Backend Endpoint**: `http://localhost:8000` (Android एमुलेटर में टेस्ट करते समय इसे `http://10.0.2.2:8000` पर सेट करें)।

### App Run command (ऐप चलाने के लिए):
```bash
cd "c:\Users\91700\Downloads\infinity tv\Infinity-TV"
flutter pub get
flutter run
```

---

## 💡 System Design Highlights (सिस्टम की मुख्य विशेषताएं)

* **HTTP range requests streaming**: जब मोबाइल ऐप वीडियो प्लेबैक करेगा, तो हमारा स्ट्रीमिंग एंडपॉइंट (`/stream/{channel_id}/{message_id}`) टेलीग्राम सर्वर से डायरेक्ट चंक डाउनलोड कर सेंड करेगा। यह वीडियो के बीच में **Seek Forward/Rewind** करने के लिए अत्यंत आवश्यक है।
* **Flutter Auto Mapping Serializer**: डेटाबेस से फेच की गई जानकारी को यह बंडल फ़ॉर्मेट में मोबाइल ऐप के ओरिजिनल `Filmy4uHDMedia` मॉडल के अनुरूप ढाल देता है।
