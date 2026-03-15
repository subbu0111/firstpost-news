import asyncio
from telegram import Bot

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
    
    def send_message(self, message):
        """Send message to Telegram"""
        try:
            # Truncate if too long (Telegram limit is 4096)
            if len(message) > 4000:
                message = message[:3997] + "..."
            
            asyncio.run(self._send_async(message))
            print(f"   📨 Telegram notification sent")
            return True
        except Exception as e:
            print(f"   ❌ Telegram error: {e}")
            return False
    
    async def _send_async(self, message):
        """Async send method"""
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )