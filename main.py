#!/usr/bin/env python3
"""Firstpost YouTube Monitor - Main Entry Point"""

import json
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pytz
from config import Config
from fetcher import YouTubeFetcher
from summarizer import GeminiSummarizer
from notifier import TelegramNotifier
from generator import SiteGenerator

def is_quiet_hours():
    """Check if current time is between 12AM-6AM IST (India time)."""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return 0 <= now.hour < 6  # 12AM to 6AM IST

def is_live_video(title: str) -> bool:
    """Detect if video is a live broadcast based on title."""
    title_upper = title.upper()
    return any(keyword in title_upper for keyword in ['LIVE:', 'LIVE |', '[LIVE]', '(LIVE)', 'LIVE STREAM', 'WATCH LIVE'])

def load_processed_videos(data_file: str) -> set:
    """Load set of already processed video IDs."""
    if not os.path.exists(data_file):
        return set()
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            return {video['id'] for video in data}
    except:
        return set()

def save_video(data_file: str, video_data: dict):
    """Append video to JSON database."""
    data = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except:
            pass
    
    # Add new video at beginning
    data.insert(0, video_data)
    
    # Keep only last 100 videos to prevent repo bloat
    data = data[:100]
    
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    print(f"🚀 Starting Firstpost Monitor at {datetime.now()}")
    
    # Initialize components
    fetcher = YouTubeFetcher(Config.CHANNEL_ID)
    summarizer = GeminiSummarizer(Config.GEMINI_API_KEY)
    notifier = TelegramNotifier(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID)
    generator = SiteGenerator(Config.DATA_FILE, Config.HTML_FILE)
    
    # Load processed videos to avoid duplicates
    processed = load_processed_videos(Config.DATA_FILE)
    print(f"📚 Found {len(processed)} previously processed videos")
    
    # Fetch recent videos
    try:
        videos = fetcher.get_recent_videos(limit=Config.MAX_VIDEOS)
    except Exception as e:
        print(f"❌ Failed to fetch RSS: {e}")
        sys.exit(1)
    
    new_videos = 0
    
    for video in videos:
        if video['id'] in processed:
            print(f"⏩ Skipping already processed: {video['title'][:50]}...")
            continue
        
        print(f"\n🎬 Processing: {video['title'][:60]}...")
        
        # Check if it's a live video first (before fetching transcript)
        live_status = is_live_video(video['title'])
        
        # Get transcript
        transcript = fetcher.get_transcript(video['id'])
        
        # Handle cases where transcript is not available
        if not transcript:
            if live_status:
                # RULE 1: Live video - Send notification without summary
                print(f"🔴 Live video detected: {video['id']}")
                
                message = f"""🔴 <b>LIVE NOW on Firstpost</b>

<b>{video['title']}</b>

⚡ <i>Live broadcast in progress. Summary will be available once stream ends.</i>

<a href="{video['link']}">▶ Watch Live</a>"""
                
                notifier.send_notification(message, video['thumbnail'])
                
                # Save to database
                video_record = {
                    'id': video['id'],
                    'title': video['title'],
                    'link': video['link'],
                    'published': video['published'],
                    'thumbnail': video['thumbnail'],
                    'category': 'LIVE',
                    'summary': 'Live broadcast in progress - transcript not yet available',
                    'key_points': ['Live stream currently ongoing'],
                    'processed_at': datetime.now().isoformat()
                }
                save_video(Config.DATA_FILE, video_record)
                new_videos += 1
                processed.add(video['id'])
                print(f"✅ Live alert sent for: {video['title'][:50]}...")
                
            else:
                # RULE 2: No transcript available (not live) - Send headline only
                print(f"⚠️ No transcript for non-live video: {video['id']}")
                
                message = f"""📰 <b>Firstpost News Update</b>

<b>{video['title']}</b>

⚠️ <i>Transcript not available for this video. Click below to watch.</i>

<a href="{video['link']}">▶ Watch Video</a>"""
                
                notifier.send_notification(message, video['thumbnail'])
                
                # Save to database
                video_record = {
                    'id': video['id'],
                    'title': video['title'],
                    'link': video['link'],
                    'published': video['published'],
                    'thumbnail': video['thumbnail'],
                    'category': 'News',
                    'summary': 'Transcript not available for this video',
                    'key_points': ['Video published without captions or transcript disabled'],
                    'processed_at': datetime.now().isoformat()
                }
                save_video(Config.DATA_FILE, video_record)
                new_videos += 1
                processed.add(video['id'])
                print(f"✅ No-transcript alert sent for: {video['title'][:50]}...")
            
            continue  # Skip to next video
        
        # If we have transcript, proceed with AI summarization (existing logic)
        summary_raw = summarizer.summarize(transcript, video['title'])
        
        if not summary_raw:
            print(f"⚠️ Failed to generate summary for: {video['id']}")
            # Fallback: Send basic notification with transcript snippet
            message = f"""📰 <b>Firstpost News</b>

<b>{video['title']}</b>

<i>Summary generation failed, but transcript is available.</i>

<a href="{video['link']}">▶ Watch Video</a>"""
            notifier.send_notification(message, video['thumbnail'])
            
            video_record = {
                'id': video['id'],
                'title': video['title'],
                'link': video['link'],
                'published': video['published'],
                'thumbnail': video['thumbnail'],
                'category': 'News',
                'summary': transcript[:300] + "..." if len(transcript) > 300 else transcript,
                'key_points': ['AI summary failed - raw transcript available'],
                'processed_at': datetime.now().isoformat()
            }
            save_video(Config.DATA_FILE, video_record)
            new_videos += 1
            processed.add(video['id'])
            continue
        
        # Parse structured summary
        category = "News"
        summary_text = summary_raw
        key_points = []
        
        lines = summary_raw.split('\n')
        for line in lines:
            if line.startswith('CATEGORY:'):
                category = line.replace('CATEGORY:', '').strip()
            elif line.startswith('SUMMARY:'):
                summary_text = line.replace('SUMMARY:', '').strip()
            elif line.startswith('•'):
                key_points.append(line.replace('•', '').strip())
        
        # Prepare video record
        video_record = {
            'id': video['id'],
            'title': video['title'],
            'link': video['link'],
            'published': video['published'],
            'thumbnail': video['thumbnail'],
            'category': category,
            'summary': summary_text,
            'key_points': key_points,
            'processed_at': datetime.now().isoformat()
        }
        
        # Send Telegram notification
        telegram_msg = summarizer.format_for_telegram(
            summary_raw, video['title'], video['link']
        )
        notifier.send_notification(telegram_msg, video['thumbnail'])
        
        # Save to database
        save_video(Config.DATA_FILE, video_record)
        new_videos += 1
        processed.add(video['id'])
        
        print(f"✅ AI Summary sent for: {video['title'][:50]}...")
    
    # Regenerate site
    if new_videos > 0 or not os.path.exists(Config.HTML_FILE):
        generator.generate_html()
        print(f"🌐 Site regenerated with {len(processed)} total videos")
    
    print(f"\n✨ Complete! Processed {new_videos} new videos.")

if __name__ == "__main__":
    # Quiet hours check: 12AM-6AM IST (no processing)
    if is_quiet_hours():
        print("🌙 Quiet hours (12AM-6AM IST). Skipping run.")
        sys.exit(0)
    
    main()