import requests
from typing import Optional

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_notification(self, message: str, thumbnail_url: Optional[str] = None) -> bool:
        """Send message to Telegram with optional image."""
        try:
            if thumbnail_url:
                # Send photo with caption
                response = requests.post(
                    f"{self.base_url}/sendPhoto",
                    data={
                        'chat_id': self.chat_id,
                        'photo': thumbnail_url,
                        'caption': message,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': False
                    },
                    timeout=30
                )
            else:
                # Send text only
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    data={
                        'chat_id': self.chat_id,
                        'text': message,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': False
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                print("✅ Telegram notification sent")
                return True
            else:
                print(f"❌ Telegram API error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False