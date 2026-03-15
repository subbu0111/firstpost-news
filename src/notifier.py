import requests

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """Send message to Telegram using HTTP API (no async issues)"""
        try:
            # Truncate if too long (Telegram limit is 4096)
            if len(message) > 4000:
                message = message[:3997] + "..."
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            print(f"   📨 Telegram notification sent")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Telegram HTTP error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Telegram error: {e}")
            return False