#!/usr/bin/env python3
import os
import sys
import pytz
from datetime import datetime
from src.config import Config
from src.fetcher import YouTubeFetcher
from src.summarizer import GeminiSummarizer
from src.notifier import TelegramNotifier
from src.generator import WebsiteGenerator

def is_quiet_hours():
    """Check if current time is between 12AM-6AM IST"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return 0 <= now.hour < 6

def main():
    print(f"🚀 Starting Firstpost Monitor at {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST")
    
    # Check quiet hours
    if is_quiet_hours():
        print("😴 Quiet hours (12AM-6AM IST). Skipping run.")
        return False 
    
    # Initialize components
    config = Config()
    fetcher = YouTubeFetcher(config.channel_id)
    summarizer = GeminiSummarizer(config.gemini_api_key)
    notifier = TelegramNotifier(config.telegram_bot_token, config.telegram_chat_id)
    generator = WebsiteGenerator()
    
    print("📺 Fetching latest videos from Firstpost...")
    videos = fetcher.get_latest_videos()
    
    if not videos:
        print("⚠️ No videos found")
        return
    
    print(f"🎯 Found {len(videos)} videos to process")
    
    for video in videos:
        video_id = video['id']
        title = video['title']
        url = video['url']
        
        print(f"\n🎬 Processing: {title[:60]}...")
        
        # Check if already processed
        if generator.video_exists(video_id):
            print(f"   ⏭️ Already processed, skipping")
            continue
        
        # Handle live streams
        if video.get('is_live', False):
            print(f"   🔴 LIVE STREAM detected")
            message = f"🔴 <b>LIVE NOW</b>\n\n<b>{title}</b>\n\n<a href='{url}'>Watch on YouTube</a>"
            notifier.send_message(message)
            generator.save_video({
                'id': video_id,
                'title': title,
                'url': url,
                'published': video['published'],
                'status': 'live',
                'summary': 'Live stream'
            })
            continue
        
        # Get transcript
        print(f"   📝 Fetching transcript...")
        transcript = fetcher.get_transcript(video_id)
        
        if not transcript:
            print(f"   ⚠️ No transcript available")
            message = f"📝 <b>No Transcript Available</b>\n\n<b>{title}</b>\n\n<a href='{url}'>Watch on YouTube</a>"
            notifier.send_message(message)
            generator.save_video({
                'id': video_id,
                'title': title,
                'url': url,
                'published': video['published'],
                'status': 'no_transcript',
                'summary': 'No transcript available'
            })
            continue
        
        # Generate AI summary
        print(f"   🤖 Generating AI summary...")
        try:
            summary = summarizer.summarize(transcript, title)
            print(f"   ✅ Summary generated ({len(summary)} chars)")
            
            # Send Telegram notification
            message = f"🎥 <b>{title[:200]}</b>\n\n{summary[:800]}\n\n<a href='{url}'>Watch on YouTube</a>"
            notifier.send_message(message)
            
            # Save to data
            generator.save_video({
                'id': video_id,
                'title': title,
                'url': url,
                'published': video['published'],
                'status': 'summarized',
                'summary': summary
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            message = f"⚠️ <b>Error processing video</b>\n\n<b>{title}</b>\n\n<a href='{url}'>Watch on YouTube</a>"
            notifier.send_message(message)
    
    # Generate website
    print("\n🌐 Generating website...")
    generator.generate_html()
    print("✅ Done!")
    
if __name__ == "__main__":
    main()