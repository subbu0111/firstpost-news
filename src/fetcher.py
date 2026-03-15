import feedparser
import re
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class YouTubeFetcher:
    def __init__(self, channel_id: str):
        self.rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    
    def get_recent_videos(self, limit: int = 5) -> List[Dict]:
        """Fetch recent videos from RSS feed."""
        feed = feedparser.parse(self.rss_url)
        videos = []
        
        for entry in feed.entries[:limit]:
            video_id = entry.yt_videoid
            videos.append({
                'id': video_id,
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            })
        
        return videos
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """Fetch English transcript using youtube-transcript-api."""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['en', 'en-US', 'en-GB']
            )
            # Concatenate text entries
            full_text = " ".join([entry['text'] for entry in transcript_list])
            return full_text
        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"⚠️ No transcript available for {video_id}")
            return None
        except Exception as e:
            print(f"❌ Error fetching transcript for {video_id}: {e}")
            return None