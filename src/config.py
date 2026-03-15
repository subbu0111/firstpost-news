import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "UC_gUM8rL-Lrg6O3adPW9K1g")
    MAX_VIDEOS = int(os.getenv("MAX_VIDEOS_PER_RUN", "5"))
    
    RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    DATA_FILE = "data/videos.json"
    HTML_FILE = "docs/index.html"
    
    @classmethod
    def validate(cls):
        missing = []
        for attr in ['GEMINI_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']:
            if not getattr(cls, attr):
                missing.append(attr)
        if missing:
            raise ValueError(f"Missing env vars: {', '.join(missing)}")