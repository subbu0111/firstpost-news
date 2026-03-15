import os

class Config:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.channel_id = os.getenv('CHANNEL_ID', 'UCrC-7fsdgcz1fwZxW9dCeUw')  # Firstpost default
        
        self.validate()
    
    def validate(self):
        required = ['GEMINI_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")