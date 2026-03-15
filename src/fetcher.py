import feedparser
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class YouTubeFetcher:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    
    def get_latest_videos(self, max_results=5):
        """Fetch latest videos from YouTube RSS feed"""
        try:
            feed = feedparser.parse(self.rss_url)
            videos = []
            
            for entry in feed.entries[:max_results]:
                video_id = entry.yt_videoid
                videos.append({
                    'id': video_id,
                    'title': entry.title,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'published': entry.published,
                    'is_live': 'live' in entry.get('media_status', {}).get('content', '').lower() if hasattr(entry, 'media_status') else False
                })
            
            return videos
        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return []
    
    def get_transcript(self, video_id):
        """Fetch English transcript or first available transcript"""
        try:
            # Try to get English transcript first
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            except:
                # Fallback to any available transcript
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all text
            full_text = ' '.join([item['text'] for item in transcript_list])
            return full_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"   Transcript error: {e}")
            return None
        except Exception as e:
            print(f"   Error fetching transcript: {e}")
            return None